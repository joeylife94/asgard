#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-help}"
PILOT_HOME_RAW="${ASGARD_PILOT_HOME:-}"
[[ -n "$PILOT_HOME_RAW" ]] || { printf '[asgard-pilot-release] FAIL: ASGARD_PILOT_HOME is required\n' >&2; exit 1; }
mkdir -p "$PILOT_HOME_RAW"
PILOT_HOME="$(cd "$PILOT_HOME_RAW" && pwd -P)"
STATE_DIR="$PILOT_HOME/state"
OWNER_FILE="$PILOT_HOME/active-release.env"

log() { printf '[asgard-pilot-release] %s\n' "$*"; }
fail() { printf '[asgard-pilot-release] FAIL: %s\n' "$*" >&2; exit 1; }

release_version() {
  [[ -f "$ROOT_DIR/VERSION" ]] || fail "VERSION missing from release"
  tr -d '\r\n' < "$ROOT_DIR/VERSION"
}

release_commit() {
  if [[ -f "$ROOT_DIR/PROVENANCE.txt" ]]; then
    local value
    value="$(awk -F= '$1=="GITHUB_SHA" {print $2; exit}' "$ROOT_DIR/PROVENANCE.txt")"
    [[ "$value" =~ ^[0-9a-f]{40}$ ]] && { printf '%s' "$value"; return 0; }
  fi
  if git -C "$ROOT_DIR" rev-parse --verify HEAD >/dev/null 2>&1; then
    git -C "$ROOT_DIR" rev-parse HEAD
    return 0
  fi
  fail "release commit provenance unavailable"
}

current_root() { cd "$ROOT_DIR" && pwd -P; }

read_owner_value() {
  local key=$1
  [[ -f "$OWNER_FILE" ]] || return 1
  awk -F= -v wanted="$key" '$1==wanted {sub(/^[^=]*=/, ""); print; exit}' "$OWNER_FILE"
}

validate_owner_file() {
  [[ -f "$OWNER_FILE" ]] || return 0
  local key value
  while IFS='=' read -r key value; do
    case "$key" in
      VERSION|COMMIT|ROOT) ;;
      '') continue ;;
      *) fail "invalid ownership metadata key: $key" ;;
    esac
    [[ -n "$value" ]] || fail "empty ownership metadata value for $key"
  done < "$OWNER_FILE"
  [[ "$(read_owner_value VERSION || true)" != "" ]] || fail "ownership VERSION missing"
  [[ "$(read_owner_value COMMIT || true)" =~ ^[0-9a-f]{40}$ ]] || fail "ownership COMMIT invalid"
  [[ "$(read_owner_value ROOT || true)" == /* ]] || fail "ownership ROOT invalid"
}

live_recorded_pid_exists() {
  local file pid
  for file in "$STATE_DIR/heimdall.pid" "$STATE_DIR/bifrost.pid"; do
    [[ -f "$file" ]] || continue
    pid="$(cat "$file" 2>/dev/null || true)"
    [[ "$pid" =~ ^[0-9]+$ ]] || continue
    kill -0 "$pid" 2>/dev/null && return 0
  done
  return 1
}

owner_matches_current_release() {
  [[ -f "$OWNER_FILE" ]] || return 1
  [[ "$(read_owner_value VERSION || true)" == "$(release_version)" ]] || return 1
  [[ "$(read_owner_value COMMIT || true)" == "$(release_commit)" ]] || return 1
  [[ "$(read_owner_value ROOT || true)" == "$(current_root)" ]] || return 1
}

assert_owner_or_unclaimed() {
  validate_owner_file
  [[ -f "$OWNER_FILE" ]] || return 0
  owner_matches_current_release || fail "pilot home is owned by another/stale release; refusing operation"
}

write_owner() {
  mkdir -p "$PILOT_HOME" "$STATE_DIR"
  local tmp="$OWNER_FILE.tmp.$$"
  {
    printf 'VERSION=%s\n' "$(release_version)"
    printf 'COMMIT=%s\n' "$(release_commit)"
    printf 'ROOT=%s\n' "$(current_root)"
  } > "$tmp"
  mv "$tmp" "$OWNER_FILE"
}

claim() {
  validate_owner_file
  if live_recorded_pid_exists; then
    fail "cannot claim pilot home while recorded application process is live"
  fi
  write_owner
  log "pilot home claimed version=$(release_version) commit=$(release_commit) root=$(current_root)"
}

show_release() {
  validate_owner_file
  [[ -f "$OWNER_FILE" ]] || fail "pilot home has no active release ownership metadata"
  printf 'pilot_home=%s\n' "$PILOT_HOME"
  printf 'version=%s\n' "$(read_owner_value VERSION)"
  printf 'commit=%s\n' "$(read_owner_value COMMIT)"
  printf 'release_root=%s\n' "$(read_owner_value ROOT)"
}

run_pilot() {
  assert_owner_or_unclaimed
  if [[ ! -f "$OWNER_FILE" ]]; then
    case "$ACTION" in
      start|validate) write_owner ;;
      *) fail "pilot home is unclaimed; run claim or start from the intended release first" ;;
    esac
  fi
  ASGARD_PILOT_STATE_DIR="$STATE_DIR" bash "$ROOT_DIR/scripts/pilot.sh" "$ACTION"
  if [[ "$ACTION" == "purge" ]]; then
    rm -f "$OWNER_FILE"
    rmdir "$PILOT_HOME" 2>/dev/null || true
  fi
}

case "$ACTION" in
  claim) claim ;;
  release) show_release ;;
  validate|start|status|job|inspect|restart|stop|purge) run_pilot ;;
  help|-h|--help)
    cat <<'EOF'
Usage: ASGARD_PILOT_HOME=/absolute/operator/path bash scripts/pilot-release.sh <claim|release|validate|start|status|job|inspect|restart|stop|purge>

D4-01 release-independent pilot ownership wrapper.
- ASGARD_PILOT_HOME owns persistent pilot metadata/state independently of the extracted release root.
- release records VERSION, exact commit provenance, and owning release root.
- a mismatched/stale release fails closed before delegating to pilot.sh.
- claim is explicit and allowed only when recorded application PIDs are not live.
- stop remains persistence-preserving; purge remains explicit/destructive.
- this does not establish a general upgrade/rollback, schema migration, production, HA, cloud, systemd, unattended-operation, SLA/SLO, RBAC, DR/PITR, or compliance claim.
EOF
    ;;
  *) fail "unknown action: $ACTION" ;;
esac
