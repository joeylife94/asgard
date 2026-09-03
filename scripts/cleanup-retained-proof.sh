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

# Decode the restricted output grammar emitted by `printf %q` without eval or
# source. Plain characters and one-character backslash escapes are supported;
# shell-expansion forms such as $'...' are deliberately rejected.
decode_q_value() {
  local encoded=$1 out="" ch
  if [[ "$encoded" == "''" ]]; then
    printf '%s' ""
    return 0
  fi
  [[ "$encoded" != *'$'* && "$encoded" != *'`'* ]] || return 1
  while [[ -n "$encoded" ]]; do
    ch=${encoded:0:1}
    encoded=${encoded:1}
    if [[ "$ch" == '\\' ]]; then
      [[ -n "$encoded" ]] || return 1
      ch=${encoded:0:1}
      encoded=${encoded:1}
      [[ "$ch" != $'\n' && "$ch" != $'\r' ]] || return 1
    fi
    [[ "$ch" != $'\n' && "$ch" != $'\r' ]] || return 1
    out+="$ch"
  done
  printf '%s' "$out"
}

PROOF_ID=""
COMPOSE_PROJECT=""
HEIMDALL_PID=""
BIFROST_PID=""
OLLAMA_CONTAINER=""
ROOT_DIR=""
WORK_DIR=""
declare -A SEEN=()

while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -n "$line" ]] || continue
  [[ "$line" == *=* ]] || fail "unexpected session metadata line"
  key=${line%%=*}
  encoded=${line#*=}
  case "$key" in
    PROOF_ID|COMPOSE_PROJECT|HEIMDALL_PID|BIFROST_PID|OLLAMA_CONTAINER|ROOT_DIR|WORK_DIR) ;;
    *) fail "unexpected session metadata key: $key" ;;
  esac
  [[ -z "${SEEN[$key]:-}" ]] || fail "duplicate session metadata key: $key"
  SEEN[$key]=1
  value="$(decode_q_value "$encoded")" || fail "unsafe or unsupported encoding for session metadata key: $key"
  case "$key" in
    PROOF_ID) PROOF_ID=$value ;;
    COMPOSE_PROJECT) COMPOSE_PROJECT=$value ;;
    HEIMDALL_PID) HEIMDALL_PID=$value ;;
    BIFROST_PID) BIFROST_PID=$value ;;
    OLLAMA_CONTAINER) OLLAMA_CONTAINER=$value ;;
    ROOT_DIR) ROOT_DIR=$value ;;
    WORK_DIR) WORK_DIR=$value ;;
  esac
done < "$SESSION_FILE"

: "${PROOF_ID:?missing PROOF_ID}"
: "${COMPOSE_PROJECT:?missing COMPOSE_PROJECT}"
: "${ROOT_DIR:?missing ROOT_DIR}"
: "${WORK_DIR:?missing WORK_DIR}"

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

verify_recorded_pid() {
  local name=$1 pid=$2 expected_log=$3 cmdline cwd stdout_target
  [[ -n "$pid" ]] || return 0
  kill -0 "$pid" 2>/dev/null || return 1
  [[ -r "/proc/$pid/cmdline" && -e "/proc/$pid/cwd" && -e "/proc/$pid/fd/1" ]] || fail "$name pid identity is not inspectable pid=$pid"
  cmdline="$(tr '\0' ' ' < "/proc/$pid/cmdline")"
  cwd="$(readlink -f "/proc/$pid/cwd")"
  stdout_target="$(readlink -f "/proc/$pid/fd/1")"
  [[ "$cwd" == "$(readlink -f "$ROOT_DIR")" ]] || fail "$name pid ownership mismatch: cwd pid=$pid"
  [[ "$stdout_target" == "$(readlink -f "$expected_log")" ]] || fail "$name pid ownership mismatch: stdout pid=$pid"
  case "$name" in
    Heimdall) [[ "$cmdline" == *"java -jar "*"heimdall-"*".jar"* ]] || fail "$name pid ownership mismatch: command pid=$pid" ;;
    Bifrost) [[ "$cmdline" == *"python"*" -m bifrost.main serve"* ]] || fail "$name pid ownership mismatch: command pid=$pid" ;;
    *) fail "unknown retained process identity: $name" ;;
  esac
}

stop_recorded_pid() {
  local name=$1 pid=$2 expected_log=$3
  [[ -n "$pid" ]] || { log "$name pid not recorded; skip"; return 0; }
  if ! kill -0 "$pid" 2>/dev/null; then
    log "$name already stopped pid=$pid"
    return 0
  fi

  verify_recorded_pid "$name" "$pid" "$expected_log"
  log "$name ownership verified; stopping pid=$pid"
  kill "$pid"
  for _ in {1..40}; do
    kill -0 "$pid" 2>/dev/null || { log "$name stopped pid=$pid"; return 0; }
    sleep 0.25
  done

  # Only the already-verified exact proof-owned PID can reach this fallback.
  log "$name did not stop after TERM; forcing verified pid=$pid"
  kill -KILL "$pid" 2>/dev/null || true
  for _ in {1..20}; do
    kill -0 "$pid" 2>/dev/null || { log "$name force-stopped pid=$pid"; return 0; }
    sleep 0.25
  done
  fail "$name still present after bounded TERM/KILL pid=$pid"
}

stop_recorded_pid "Heimdall" "$HEIMDALL_PID" "$WORK_DIR/heimdall.log"
stop_recorded_pid "Bifrost" "$BIFROST_PID" "$WORK_DIR/bifrost.log"

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
