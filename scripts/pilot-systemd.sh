#!/usr/bin/env bash
set -Eeuo pipefail

# D7-01 bounded systemd ownership of the configured persistent pilot.
# This wrapper only renders/installs one unit that delegates to the accepted
# D5 surface (scripts/pilot-configured.sh start|stop). It does not change the
# accepted D3-D6 lifecycle scripts.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
ACTION="${1:-help}"
UNIT_NAME="asgard-pilot.service"
UNIT_FILE="/etc/systemd/system/$UNIT_NAME"
VERSION_FILE="$ROOT_DIR/delivery/single-node-candidate/VERSION"

log() { printf '[asgard-pilot-systemd] %s\n' "$*"; }
fail() { printf '[asgard-pilot-systemd] FAIL: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: ASGARD_PILOT_HOME=/absolute/operator/path bash scripts/pilot-systemd.sh <render|preflight|install|uninstall|status>

D7-01 bounded systemd ownership of the configured persistent pilot.
- install writes and enables one system unit (asgard-pilot.service) that runs as the
  installing operator and delegates to scripts/pilot-configured.sh start/stop.
  It does not start the unit. Privileged steps use sudo unless already root.
- The unit is ordered after docker.service and wanted by multi-user.target.
- The unit carries the pilot-home path, the release root, and a PATH recorded at
  install time. Configured secrets stay in $ASGARD_PILOT_HOME/config/pilot.env.
- A systemd-owned start never claims a pilot home: it fails closed when the home is
  unclaimed, purged, or owned by another/stale release.
- uninstall stops and disables the unit and removes the unit file. Pilot state,
  configuration and release ownership are preserved.
- render prints the unit without installing it. status reports the installed unit
  and fails when it is missing, disabled, or records another/stale release.
- Not verified: an actual host reboot or power cycle, application crash supervision
  or automatic restart, monitoring/alerting/unattended operations, offline boot,
  rootless Docker or Docker Desktop, more than one pilot per host, production readiness.
EOF
}

case "$ACTION" in
  help|-h|--help) usage; exit 0 ;;
  render|preflight|install|uninstall|status) ;;
  *) fail "unknown action: $ACTION" ;;
esac

PILOT_HOME_RAW="${ASGARD_PILOT_HOME:-}"
[[ -n "$PILOT_HOME_RAW" ]] || fail "ASGARD_PILOT_HOME is required"
[[ -d "$PILOT_HOME_RAW" ]] || fail "pilot home does not exist: $PILOT_HOME_RAW"
PILOT_HOME="$(cd "$PILOT_HOME_RAW" && pwd -P)"
STATE_DIR="$PILOT_HOME/state"
OWNER_FILE="$PILOT_HOME/active-release.env"

# Paths are written into a unit file unquoted. Refuse anything that systemd
# could interpret (whitespace, quotes, %, $, backslash) instead of escaping it.
safe_path() { [[ "$1" =~ ^/[A-Za-z0-9._/+@-]*$ ]]; }

release_version() {
  [[ -f "$VERSION_FILE" ]] || fail "delivery candidate VERSION missing from release"
  local value
  value="$(tr -d '\r\n' < "$VERSION_FILE")"
  [[ "$value" =~ ^[A-Za-z0-9._-]+$ ]] || fail "delivery candidate VERSION is empty or invalid"
  printf '%s' "$value"
}

release_commit() {
  if [[ -f "$ROOT_DIR/PROVENANCE.txt" ]]; then
    local value
    value="$(awk -F= '$1=="commit" {print $2; exit}' "$ROOT_DIR/PROVENANCE.txt")"
    [[ "$value" =~ ^[0-9a-f]{40}$ ]] && { printf '%s' "$value"; return 0; }
  fi
  if git -C "$ROOT_DIR" rev-parse --verify HEAD >/dev/null 2>&1; then
    git -C "$ROOT_DIR" rev-parse HEAD
    return 0
  fi
  fail "release commit provenance unavailable"
}

read_owner_value() {
  local key=$1
  awk -F= -v wanted="$key" '$1==wanted {sub(/^[^=]*=/, ""); print; exit}' "$OWNER_FILE"
}

config_check() {
  ASGARD_PILOT_HOME="$PILOT_HOME" bash "$ROOT_DIR/scripts/pilot-configured.sh" config-check >/dev/null
}

assert_claimed_by_current_release() {
  [[ -f "$OWNER_FILE" ]] || fail "pilot home is unclaimed; start or claim it from the intended release before systemd ownership"
  [[ "$(read_owner_value VERSION)" == "$(release_version)" ]] || fail "pilot home is owned by another/stale release; refusing systemd operation"
  [[ "$(read_owner_value COMMIT)" == "$(release_commit)" ]] || fail "pilot home is owned by another/stale release; refusing systemd operation"
  [[ "$(read_owner_value ROOT)" == "$ROOT_DIR" ]] || fail "pilot home is owned by another/stale release; refusing systemd operation"
}

assert_applications_stopped() {
  local file pid
  for file in "$STATE_DIR/heimdall.pid" "$STATE_DIR/bifrost.pid"; do
    [[ -f "$file" ]] || continue
    pid="$(cat "$file" 2>/dev/null || true)"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
      fail "pilot applications are live; run the persistence-preserving stop before handing start/stop to systemd"
    fi
  done
}

operator_user() {
  local user
  user="$(id -un)"
  [[ "$user" =~ ^[a-z_][a-z0-9_-]*$ ]] || fail "unsupported operator user name for a unit file: $user"
  printf '%s' "$user"
}

# The unit does not inherit the operator's login environment. Record where the
# required commands live now, plus the standard system directories.
runtime_path() {
  local cmd resolved dir path=""
  for cmd in java python3 docker curl; do
    resolved="$(command -v "$cmd" || true)"
    [[ "$resolved" == /* ]] || fail "missing required command: $cmd"
    dir="$(dirname "$resolved")"
    safe_path "$dir" || fail "unsupported characters in the directory of $cmd: $dir"
    case ":$path:" in
      *":$dir:"*) ;;
      *) path="${path:+$path:}$dir" ;;
    esac
  done
  for dir in /usr/local/sbin /usr/local/bin /usr/sbin /usr/bin /sbin /bin; do
    case ":$path:" in
      *":$dir:"*) ;;
      *) path="$path:$dir" ;;
    esac
  done
  printf '%s' "$path"
}

render_unit() {
  local bash_bin user path version commit
  safe_path "$ROOT_DIR" || fail "unsupported characters in release root for a unit file: $ROOT_DIR"
  safe_path "$PILOT_HOME" || fail "unsupported characters in pilot home for a unit file: $PILOT_HOME"
  bash_bin="$(command -v bash)"
  safe_path "$bash_bin" || fail "unsupported bash location: $bash_bin"
  user="$(operator_user)"
  path="$(runtime_path)"
  version="$(release_version)"
  commit="$(release_commit)"
  cat <<EOF
# Managed by scripts/pilot-systemd.sh (Asgard D7-01). Reinstall instead of editing.
# asgard-pilot-home=$PILOT_HOME
# asgard-release-root=$ROOT_DIR
# asgard-release-version=$version
# asgard-release-commit=$commit
[Unit]
Description=Asgard bounded single-node Local-first pilot
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=$user
WorkingDirectory=$ROOT_DIR
Environment=ASGARD_PILOT_HOME=$PILOT_HOME
Environment=PATH=$path
ExecStartPre=$bash_bin $ROOT_DIR/scripts/pilot-systemd.sh preflight
ExecStart=$bash_bin $ROOT_DIR/scripts/pilot-configured.sh start
ExecStop=$bash_bin $ROOT_DIR/scripts/pilot-configured.sh stop
TimeoutStartSec=1800
TimeoutStopSec=300

[Install]
WantedBy=multi-user.target
EOF
}

require_systemd_host() {
  command -v systemctl >/dev/null 2>&1 || fail "missing required command: systemctl"
  [[ -d /run/systemd/system ]] || fail "host is not booted with systemd"
}

priv() {
  if [[ "$EUID" -eq 0 ]]; then
    "$@"
  else
    command -v sudo >/dev/null 2>&1 || fail "missing required command: sudo"
    sudo "$@"
  fi
}

installed_value() {
  local key=$1
  sed -n "s/^# asgard-$key=//p" "$UNIT_FILE" | head -n 1
}

assert_installed_unit_is_ours() {
  [[ "$(installed_value pilot-home)" == "$PILOT_HOME" ]] || fail "installed $UNIT_NAME belongs to another pilot home; refusing operation"
}

install_unit() {
  require_systemd_host
  systemctl cat docker.service >/dev/null 2>&1 || fail "D7-01 supports a systemd-managed docker.service only"
  config_check
  assert_claimed_by_current_release
  assert_applications_stopped
  if [[ -f "$UNIT_FILE" ]]; then
    assert_installed_unit_is_ours
    if systemctl is-active --quiet "$UNIT_NAME"; then
      fail "$UNIT_NAME is active; stop it before reinstalling"
    fi
  fi
  local tmp
  tmp="$(mktemp)"
  trap 'rm -f "$tmp"' EXIT
  render_unit > "$tmp"
  priv install -m 0644 -o root -g root "$tmp" "$UNIT_FILE"
  rm -f "$tmp"
  trap - EXIT
  priv systemctl daemon-reload
  priv systemctl enable "$UNIT_NAME" >/dev/null 2>&1 || fail "systemctl enable failed for $UNIT_NAME"
  systemctl is-enabled --quiet "$UNIT_NAME" || fail "$UNIT_NAME is not enabled after install"
  log "install PASS unit=$UNIT_NAME enabled=true started=false pilot_home=$PILOT_HOME release_commit=$(release_commit)"
}

uninstall_unit() {
  require_systemd_host
  [[ -f "$UNIT_FILE" ]] || fail "$UNIT_NAME is not installed"
  assert_installed_unit_is_ours
  priv systemctl disable --now "$UNIT_NAME" >/dev/null 2>&1 || fail "systemctl disable --now failed for $UNIT_NAME"
  priv rm -f "$UNIT_FILE"
  priv systemctl daemon-reload
  priv systemctl reset-failed "$UNIT_NAME" >/dev/null 2>&1 || true
  log "uninstall PASS unit=$UNIT_NAME removed=true pilot state, configuration and release ownership retained"
}

unit_status() {
  require_systemd_host
  [[ -f "$UNIT_FILE" ]] || fail "$UNIT_NAME is not installed"
  local enabled active
  enabled="$(systemctl is-enabled "$UNIT_NAME" 2>/dev/null || true)"
  active="$(systemctl is-active "$UNIT_NAME" 2>/dev/null || true)"
  printf 'unit=%s\n' "$UNIT_NAME"
  printf 'enabled=%s\n' "${enabled:-unknown}"
  printf 'active=%s\n' "${active:-unknown}"
  printf 'pilot_home=%s\n' "$(installed_value pilot-home)"
  printf 'release_root=%s\n' "$(installed_value release-root)"
  printf 'release_version=%s\n' "$(installed_value release-version)"
  printf 'release_commit=%s\n' "$(installed_value release-commit)"
  assert_installed_unit_is_ours
  [[ "$(installed_value release-root)" == "$ROOT_DIR" ]] || fail "installed unit records another/stale release; reinstall from the owning release"
  [[ "$(installed_value release-commit)" == "$(release_commit)" ]] || fail "installed unit records another/stale release; reinstall from the owning release"
  [[ "$enabled" == "enabled" ]] || fail "$UNIT_NAME is installed but not enabled"
}

case "$ACTION" in
  render)
    config_check
    assert_claimed_by_current_release
    render_unit
    ;;
  preflight)
    config_check
    assert_claimed_by_current_release
    log "preflight PASS pilot_home=$PILOT_HOME release_commit=$(release_commit)"
    ;;
  install) install_unit ;;
  uninstall) uninstall_unit ;;
  status) unit_status ;;
esac
