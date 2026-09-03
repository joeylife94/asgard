#!/usr/bin/env bash
set -Eeuo pipefail

log() { printf '[asgard-cleanup] %s\n' "$*"; }
fail() { printf '[asgard-cleanup] FAIL: %s\n' "$*" >&2; exit 1; }

SESSION_FILE="${1:-}"
[[ -n "$SESSION_FILE" ]] || fail "usage: bash scripts/cleanup-retained-proof.sh /path/to/retained-session.env"
[[ -f "$SESSION_FILE" ]] || fail "session file not found: $SESSION_FILE"
CLEANED_MARKER="${SESSION_FILE}.cleaned"
if [[ -f "$CLEANED_MARKER" ]]; then
  log "PASS already cleaned session=$SESSION_FILE"
  exit 0
fi

# retained-session.env is repository-generated shell assignment data. Reject
# anything outside the exact bounded key set before sourcing it so malformed
# metadata cannot become an arbitrary command channel.
allowed='^(PROOF_ID|COMPOSE_PROJECT|HEIMDALL_PID|BIFROST_PID|OLLAMA_CONTAINER|ROOT_DIR|WORK_DIR)='
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -n "$line" ]] || continue
  [[ "$line" =~ $allowed ]] || fail "unexpected session metadata line"
  case "$line" in
    *'$('*|*'`'*|*';'*|*'&&'*|*'||'*|*'<'*|*'>') fail "unsafe token in session metadata" ;;
  esac
done < "$SESSION_FILE"

# shellcheck disable=SC1090
source "$SESSION_FILE"

: "${PROOF_ID:?missing PROOF_ID}"
: "${COMPOSE_PROJECT:?missing COMPOSE_PROJECT}"
: "${ROOT_DIR:?missing ROOT_DIR}"
: "${WORK_DIR:?missing WORK_DIR}"
HEIMDALL_PID="${HEIMDALL_PID:-}"
BIFROST_PID="${BIFROST_PID:-}"
OLLAMA_CONTAINER="${OLLAMA_CONTAINER:-}"

[[ "$PROOF_ID" =~ ^[A-Za-z0-9_.-]+$ ]] || fail "invalid PROOF_ID"
[[ "$COMPOSE_PROJECT" == "asgard-proof-${PROOF_ID//[^a-zA-Z0-9_-]/-}" ]] || fail "COMPOSE_PROJECT does not match proof ownership boundary"
[[ -z "$HEIMDALL_PID" || "$HEIMDALL_PID" =~ ^[0-9]+$ ]] || fail "invalid HEIMDALL_PID"
[[ -z "$BIFROST_PID" || "$BIFROST_PID" =~ ^[0-9]+$ ]] || fail "invalid BIFROST_PID"
[[ -z "$OLLAMA_CONTAINER" || "$OLLAMA_CONTAINER" == "$PROOF_ID-ollama" ]] || fail "OLLAMA_CONTAINER does not match proof ownership boundary"
[[ -d "$ROOT_DIR" ]] || fail "ROOT_DIR does not exist: $ROOT_DIR"
[[ -f "$ROOT_DIR/docker-compose.yml" || -f "$ROOT_DIR/compose.yml" || -f "$ROOT_DIR/compose.yaml" ]] || fail "ROOT_DIR is not an Asgard Compose checkout"
command -v docker >/dev/null 2>&1 || fail "missing required command: docker"
docker info >/dev/null 2>&1 || fail "Docker daemon is not available"
docker compose version >/dev/null 2>&1 || fail "Docker Compose plugin is required"

stop_recorded_pid() {
  local name=$1 pid=$2
  [[ -n "$pid" ]] || { log "$name pid not recorded; skip"; return 0; }
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    for _ in {1..20}; do
      kill -0 "$pid" 2>/dev/null || { log "$name stopped pid=$pid"; return 0; }
      sleep 0.25
    done
    fail "$name did not stop cleanly pid=$pid"
  else
    log "$name already stopped pid=$pid"
  fi
}

stop_recorded_pid "Heimdall" "$HEIMDALL_PID"
stop_recorded_pid "Bifrost" "$BIFROST_PID"

if [[ -n "$OLLAMA_CONTAINER" ]]; then
  if docker container inspect "$OLLAMA_CONTAINER" >/dev/null 2>&1; then
    docker rm -f "$OLLAMA_CONTAINER" >/dev/null
    log "proof-owned Ollama removed container=$OLLAMA_CONTAINER"
  else
    log "proof-owned Ollama already absent container=$OLLAMA_CONTAINER"
  fi
else
  log "external/operator Ollama was reused; leave untouched"
fi

(
  cd "$ROOT_DIR"
  docker compose -p "$COMPOSE_PROJECT" down -v --remove-orphans
)

printf 'proof=%s\ncompose_project=%s\ncleaned_at=%s\n' \
  "$PROOF_ID" "$COMPOSE_PROJECT" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$CLEANED_MARKER"
log "PASS proof=$PROOF_ID compose_project=$COMPOSE_PROJECT work_dir_retained=$WORK_DIR"
