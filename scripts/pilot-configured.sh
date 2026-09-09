#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-help}"
PILOT_HOME_RAW="${ASGARD_PILOT_HOME:-}"

log() { printf '[asgard-pilot-configured] %s\n' "$*"; }
fail() { printf '[asgard-pilot-configured] FAIL: %s\n' "$*" >&2; exit 1; }

[[ -n "$PILOT_HOME_RAW" ]] || fail "ASGARD_PILOT_HOME is required"
mkdir -p "$PILOT_HOME_RAW"
PILOT_HOME="$(cd "$PILOT_HOME_RAW" && pwd -P)"
CONFIG_FILE_RAW="${ASGARD_PILOT_CONFIG:-$PILOT_HOME/config/pilot.env}"
[[ -f "$CONFIG_FILE_RAW" ]] || fail "operator-owned pilot config missing: $CONFIG_FILE_RAW"
CONFIG_FILE="$(cd "$(dirname "$CONFIG_FILE_RAW")" && pwd -P)/$(basename "$CONFIG_FILE_RAW")"
case "$CONFIG_FILE" in
  "$PILOT_HOME"/*) ;;
  *) fail "operator-owned pilot config must be inside ASGARD_PILOT_HOME" ;;
esac

allowed_key() {
  case "$1" in
    ASGARD_PILOT_COMPOSE_PROJECT|ASGARD_PILOT_MODEL|ASGARD_PILOT_DB_USER|ASGARD_PILOT_DB_PASSWORD|ASGARD_PILOT_DB_NAME|ASGARD_PILOT_REDIS_PASSWORD|ASGARD_PILOT_JWT_SECRET|ASGARD_PILOT_ADMIN_USERNAME|ASGARD_PILOT_ADMIN_PASSWORD) return 0 ;;
    *) return 1 ;;
  esac
}

load_config() {
  local line key value line_no=0
  while IFS= read -r line || [[ -n "$line" ]]; do
    line_no=$((line_no + 1))
    [[ -z "$line" || "$line" == \#* ]] && continue
    [[ "$line" == *=* ]] || fail "malformed config line $line_no"
    key="${line%%=*}"
    value="${line#*=}"
    allowed_key "$key" || fail "unsupported config key at line $line_no: $key"
    [[ -n "$value" ]] || fail "empty required config value for $key"
    printf -v "$key" '%s' "$value"
    export "$key"
  done < "$CONFIG_FILE"

  local required=(
    ASGARD_PILOT_COMPOSE_PROJECT
    ASGARD_PILOT_MODEL
    ASGARD_PILOT_DB_USER
    ASGARD_PILOT_DB_PASSWORD
    ASGARD_PILOT_DB_NAME
    ASGARD_PILOT_REDIS_PASSWORD
    ASGARD_PILOT_JWT_SECRET
    ASGARD_PILOT_ADMIN_USERNAME
    ASGARD_PILOT_ADMIN_PASSWORD
  )
  local key
  for key in "${required[@]}"; do
    [[ -n "${!key:-}" ]] || fail "missing required config key: $key"
  done

  [[ "$ASGARD_PILOT_COMPOSE_PROJECT" =~ ^[a-z0-9][a-z0-9_-]{2,48}$ ]] || fail "invalid ASGARD_PILOT_COMPOSE_PROJECT"
  [[ "$ASGARD_PILOT_MODEL" =~ ^[A-Za-z0-9._:/-]+$ ]] || fail "invalid ASGARD_PILOT_MODEL"
  [[ "$ASGARD_PILOT_DB_USER" =~ ^[A-Za-z0-9_]+$ ]] || fail "invalid ASGARD_PILOT_DB_USER"
  [[ "$ASGARD_PILOT_DB_NAME" =~ ^[A-Za-z0-9_]+$ ]] || fail "invalid ASGARD_PILOT_DB_NAME"
  [[ "$ASGARD_PILOT_DB_PASSWORD" =~ ^[A-Za-z0-9._~-]{12,128}$ ]] || fail "invalid ASGARD_PILOT_DB_PASSWORD"
  [[ "$ASGARD_PILOT_REDIS_PASSWORD" =~ ^[A-Za-z0-9._~-]{12,128}$ ]] || fail "invalid ASGARD_PILOT_REDIS_PASSWORD"
  [[ ${#ASGARD_PILOT_JWT_SECRET} -ge 32 ]] || fail "ASGARD_PILOT_JWT_SECRET must be at least 32 characters"
  [[ "$ASGARD_PILOT_ADMIN_USERNAME" =~ ^[A-Za-z0-9._-]{3,64}$ ]] || fail "invalid ASGARD_PILOT_ADMIN_USERNAME"
  [[ ${#ASGARD_PILOT_ADMIN_PASSWORD} -ge 12 ]] || fail "ASGARD_PILOT_ADMIN_PASSWORD must be at least 12 characters"
}

load_config
export ASGARD_PILOT_HOME="$PILOT_HOME"
export ASGARD_PILOT_CONFIG="$CONFIG_FILE"

case "$ACTION" in
  config-check)
    log "configuration PASS pilot_home=$PILOT_HOME compose_project=$ASGARD_PILOT_COMPOSE_PROJECT model=$ASGARD_PILOT_MODEL"
    ;;
  claim|release|validate|start|status|job|inspect|restart|stop|purge)
    exec bash "$ROOT_DIR/scripts/pilot-release.sh" "$ACTION"
    ;;
  help|-h|--help)
    cat <<'EOF'
Usage: ASGARD_PILOT_HOME=/absolute/operator/path bash scripts/pilot-configured.sh <config-check|claim|release|validate|start|status|job|inspect|restart|stop|purge>

D5-01 operator-owned pilot configuration wrapper.
- Default config path: $ASGARD_PILOT_HOME/config/pilot.env
- Config is parsed as data with an explicit key allow-list; it is not sourced as shell code.
- Required sensitive runtime values are never printed by this wrapper.
- Config must remain under the operator-owned pilot home and outside the release extraction root.
- Existing D4 pilot-release semantics remain authoritative for ownership, stop, and purge.
EOF
    ;;
  *) fail "unknown action: $ACTION" ;;
esac
