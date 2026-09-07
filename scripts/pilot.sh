#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ACTION="${1:-help}"
STATE_DIR="${ASGARD_PILOT_STATE_DIR:-$ROOT_DIR/.asgard/pilot}"
WORK_DIR="$STATE_DIR/work"
COMPOSE_PROJECT="${ASGARD_PILOT_COMPOSE_PROJECT:-asgard-pilot}"
OLLAMA_CONTAINER="${ASGARD_PILOT_OLLAMA_CONTAINER:-asgard-pilot-ollama}"
OLLAMA_VOLUME="${ASGARD_PILOT_OLLAMA_VOLUME:-asgard-pilot-ollama-data}"
MODEL="${ASGARD_PILOT_MODEL:-smollm:135m}"
HEIMDALL_PID_FILE="$STATE_DIR/heimdall.pid"
BIFROST_PID_FILE="$STATE_DIR/bifrost.pid"
LAST_JOB_FILE="$STATE_DIR/last-job.json"

log() { printf '[asgard-pilot] %s\n' "$*"; }
fail() { printf '[asgard-pilot] FAIL: %s\n' "$*" >&2; exit 1; }
need_cmd() { command -v "$1" >/dev/null 2>&1 || fail "missing required command: $1"; }

wait_http() {
  local name=$1 url=$2 attempts=${3:-60}
  local i
  for ((i=1; i<=attempts; i++)); do
    if curl --fail --silent "$url" >/dev/null 2>&1; then
      log "$name ready (attempt $i)"
      return 0
    fi
    sleep 2
  done
  fail "$name did not become ready: $url"
}

pid_value() {
  local file=$1
  [[ -f "$file" ]] || return 1
  local pid
  pid="$(cat "$file")"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  printf '%s' "$pid"
}

pid_is_owned() {
  local pid=$1 kind=$2
  kill -0 "$pid" 2>/dev/null || return 1
  local cwd cmd
  cwd="$(readlink -f "/proc/$pid/cwd" 2>/dev/null || true)"
  cmd="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
  [[ "$cwd" == "$ROOT_DIR" ]] || return 1
  case "$kind" in
    heimdall) [[ "$cmd" == *"java -jar"* && "$cmd" == *"heimdall-"*".jar"* ]] ;;
    bifrost) [[ "$cmd" == *"python"* && "$cmd" == *"-m bifrost.main serve"* ]] ;;
    *) return 1 ;;
  esac
}

stop_pid() {
  local file=$1 kind=$2
  local pid
  pid="$(pid_value "$file" 2>/dev/null || true)"
  [[ -n "$pid" ]] || { rm -f "$file"; return 0; }
  if pid_is_owned "$pid" "$kind"; then
    kill "$pid" 2>/dev/null || true
    for _ in {1..30}; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 1
    done
    kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
  else
    log "refusing to signal unowned/stale $kind pid=$pid"
  fi
  rm -f "$file"
}

validate() {
  for cmd in docker java python3 curl; do need_cmd "$cmd"; done
  docker info >/dev/null 2>&1 || fail "Docker daemon is not available"
  docker compose version >/dev/null 2>&1 || fail "Docker Compose plugin is required"
  [[ "$(uname -s)" == "Linux" ]] || fail "D3-01 supports Linux hosts only"
  local java_major
  java_major="$(java -version 2>&1 | awk -F'[\".]' '/version/ {print $2; exit}')"
  [[ "$java_major" == "21" ]] || fail "Java 21 required; detected ${java_major:-unknown}"
  python3 - <<'PY' || fail "Python 3.9+ required"
import sys
assert sys.version_info >= (3, 9), sys.version
PY
  [[ -f docker-compose.yml ]] || fail "docker-compose.yml missing"
  [[ -f gradlew ]] || fail "gradlew missing"
  [[ -f bifrost/requirements.txt ]] || fail "Bifrost requirements missing"
  log "validation PASS host=Linux java=21 compose_project=$COMPOSE_PROJECT model=$MODEL"
}

ensure_build() {
  mkdir -p "$WORK_DIR"
  bash ./gradlew :heimdall:bootJar --no-daemon --console=plain
  if [[ ! -x "$WORK_DIR/venv/bin/python" ]]; then
    python3 -m venv "$WORK_DIR/venv"
  fi
  "$WORK_DIR/venv/bin/python" -m pip install --quiet --upgrade pip setuptools wheel
  "$WORK_DIR/venv/bin/python" -m pip install --quiet -r bifrost/requirements.txt
  "$WORK_DIR/venv/bin/python" -m pip install --quiet -e bifrost
}

ensure_infra() {
  docker compose -p "$COMPOSE_PROJECT" up -d postgres zookeeper kafka redis elasticsearch
  for i in {1..30}; do
    docker compose -p "$COMPOSE_PROJECT" exec -T postgres pg_isready -U asgard >/dev/null 2>&1 && break
    [[ "$i" == "30" ]] && fail "PostgreSQL readiness failed"
    sleep 2
  done
  for i in {1..45}; do
    docker compose -p "$COMPOSE_PROJECT" exec -T kafka kafka-broker-api-versions --bootstrap-server kafka:29092 >/dev/null 2>&1 && break
    [[ "$i" == "45" ]] && fail "Kafka readiness failed"
    sleep 2
  done
  wait_http "Elasticsearch" "http://127.0.0.1:9200/_cluster/health" 60
}

ensure_ollama() {
  if docker container inspect "$OLLAMA_CONTAINER" >/dev/null 2>&1; then
    docker start "$OLLAMA_CONTAINER" >/dev/null 2>&1 || true
  else
    docker volume create "$OLLAMA_VOLUME" >/dev/null
    docker run -d --name "$OLLAMA_CONTAINER" -p 11434:11434 -v "$OLLAMA_VOLUME:/root/.ollama" ollama/ollama:latest >/dev/null
  fi
  wait_http "Ollama" "http://127.0.0.1:11434/api/tags" 30
  curl --fail --silent --show-error -H 'Content-Type: application/json' \
    -d "{\"name\":\"$MODEL\",\"stream\":false}" \
    http://127.0.0.1:11434/api/pull > "$WORK_DIR/ollama-pull.json"
}

export_runtime_env() {
  export SPRING_PROFILES_ACTIVE=dev
  export SPRING_DATASOURCE_URL=jdbc:postgresql://127.0.0.1:5432/heimdall
  export SPRING_DATASOURCE_USERNAME=asgard
  export SPRING_DATASOURCE_PASSWORD=asgard_password
  export SPRING_KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
  export JWT_SECRET=asgard-pilot-jwt-secret-at-least-32-bytes-long
  export HEIMDALL_SECURITY_ADMIN_USERNAME=admin
  export HEIMDALL_SECURITY_ADMIN_PASSWORD=asgard-pilot-admin-password
  export HEIMDALL_SECURITY_ADMIN_ROLES=ADMIN,USER
  export HEIMDALL_ANALYSIS_AUTO_REQUEST=false
  export REDIS_HOST=127.0.0.1 REDIS_PORT=6379 REDIS_PASSWORD=redis_password GRPC_PORT=9091
  export KAFKA_ENABLED=true HEIMDALL_ENABLED=true KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
  export HEIMDALL_DATABASE_URL=postgresql://asgard:asgard_password@127.0.0.1:5432/heimdall
  export BIFROST_OLLAMA_URL=http://127.0.0.1:11434 BIFROST_OLLAMA_MODEL="$MODEL" BIFROST_OLLAMA_ALLOW_FALLBACK=false BIFROST_OLLAMA_NUM_PREDICT=256
}

start_apps() {
  export_runtime_env
  local jar
  jar="$(find heimdall/build/libs -maxdepth 1 -name 'heimdall-*.jar' -type f | head -n 1)"
  [[ -n "$jar" ]] || fail "Heimdall bootJar not found"
  nohup java -jar "$jar" > "$WORK_DIR/heimdall.log" 2>&1 & echo $! > "$HEIMDALL_PID_FILE"
  nohup "$WORK_DIR/venv/bin/python" -m bifrost.main serve > "$WORK_DIR/bifrost.log" 2>&1 & echo $! > "$BIFROST_PID_FILE"
  wait_http "Heimdall" "http://127.0.0.1:8080/actuator/health" 90
  wait_http "Bifrost" "http://127.0.0.1:8000/health" 60
}

start() {
  validate
  mkdir -p "$STATE_DIR" "$WORK_DIR"
  if status_quiet; then
    log "pilot already running"
    return 0
  fi
  stop_pid "$HEIMDALL_PID_FILE" heimdall
  stop_pid "$BIFROST_PID_FILE" bifrost
  ensure_build
  ensure_infra
  ensure_ollama
  start_apps
  printf '%s\n' "$COMPOSE_PROJECT" > "$STATE_DIR/compose-project"
  printf '%s\n' "$MODEL" > "$STATE_DIR/model"
  log "pilot start PASS state_dir=$STATE_DIR"
}

status_quiet() {
  local hp bp
  hp="$(pid_value "$HEIMDALL_PID_FILE" 2>/dev/null || true)"
  bp="$(pid_value "$BIFROST_PID_FILE" 2>/dev/null || true)"
  [[ -n "$hp" && -n "$bp" ]] || return 1
  pid_is_owned "$hp" heimdall || return 1
  pid_is_owned "$bp" bifrost || return 1
  curl --fail --silent http://127.0.0.1:8080/actuator/health >/dev/null 2>&1 || return 1
  curl --fail --silent http://127.0.0.1:8000/health >/dev/null 2>&1 || return 1
  docker compose -p "$COMPOSE_PROJECT" exec -T postgres pg_isready -U asgard >/dev/null 2>&1 || return 1
  docker compose -p "$COMPOSE_PROJECT" exec -T kafka kafka-broker-api-versions --bootstrap-server kafka:29092 >/dev/null 2>&1 || return 1
  curl --fail --silent http://127.0.0.1:11434/api/tags >/dev/null 2>&1 || return 1
}

status() {
  if status_quiet; then
    log "status RUNNING heimdall=healthy bifrost=healthy postgres=ready kafka=ready ollama=ready"
  else
    log "status NOT_RUNNING_OR_UNHEALTHY"
    return 1
  fi
}

login_token() {
  local login_json
  login_json="$(curl --fail --silent --show-error -H 'Content-Type: application/json' \
    -d '{"username":"admin","password":"asgard-pilot-admin-password"}' \
    http://127.0.0.1:8080/api/v1/auth/login)"
  python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])' <<<"$login_json"
}

run_job() {
  status_quiet || fail "pilot must be running before job"
  local token ingest log_id idemp accepted job_id job_json final_status result_json
  token="$(login_token)"
  ingest="$(curl --fail --silent --show-error -H "Authorization: Bearer $token" -H 'Content-Type: application/json' \
    -d '{"source":"d3-pilot","serviceName":"payment-service","environment":"pilot","severity":"ERROR","logContent":"synthetic bounded pilot gateway timeout after 3000ms","metadata":{"destination":"d3","synthetic":true}}' \
    http://127.0.0.1:8080/api/v1/logs)"
  log_id="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["logId"])' <<<"$ingest")"
  idemp="d3-pilot-$(date +%s)-$$"
  accepted="$(curl --fail --silent --show-error -H "Authorization: Bearer $token" -H 'Content-Type: application/json' -H "Idempotency-Key: $idemp" \
    -d "{\"idempotencyKey\":\"$idemp\",\"modelPolicy\":{\"source\":\"local\"}}" \
    -X POST "http://127.0.0.1:8080/api/v1/logs/$log_id/analysis")"
  job_id="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["jobId"])' <<<"$accepted")"
  final_status=""
  for _ in {1..180}; do
    job_json="$(curl --fail --silent --show-error -H "Authorization: Bearer $token" "http://127.0.0.1:8080/api/v1/analysis/jobs/$job_id")"
    final_status="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])' <<<"$job_json")"
    [[ "$final_status" == "SUCCEEDED" ]] && break
    [[ "$final_status" == "FAILED" ]] && fail "analysis job failed: $job_id"
    sleep 2
  done
  [[ "$final_status" == "SUCCEEDED" ]] || fail "analysis job did not succeed within timeout: $job_id"
  result_json="$(curl --fail --silent --show-error -H "Authorization: Bearer $token" "http://127.0.0.1:8080/api/v1/logs/$log_id/analysis")"
  JOB_ID="$job_id" LOG_ID="$log_id" MODEL_EXPECTED="$MODEL" RESULT_JSON="$result_json" LAST_JOB_FILE="$LAST_JOB_FILE" python3 - <<'PY'
import json, os
result = json.loads(os.environ["RESULT_JSON"])
model = result.get("model") or ""
summary = result.get("summary") or ""
expected = os.environ["MODEL_EXPECTED"].split(":", 1)[0].lower()
if not model or model.lower() == "fallback" or expected not in model.lower() or not summary.strip():
    raise SystemExit(f"invalid Local Ollama result: {result}")
payload = {"jobId": os.environ["JOB_ID"], "logId": os.environ["LOG_ID"], "model": model, "provider": "ollama", "status": "SUCCEEDED", "cloudExecution": False}
with open(os.environ["LAST_JOB_FILE"], "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
print(json.dumps(payload))
PY
  log "real Local Ollama job PASS job_id=$job_id log_id=$log_id"
}

inspect_last() {
  status_quiet || fail "pilot must be running before inspect"
  [[ -f "$LAST_JOB_FILE" ]] || fail "no last-job evidence found"
  local token job_id log_id job_json result_json
  token="$(login_token)"
  job_id="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["jobId"])' "$LAST_JOB_FILE")"
  log_id="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["logId"])' "$LAST_JOB_FILE")"
  job_json="$(curl --fail --silent --show-error -H "Authorization: Bearer $token" "http://127.0.0.1:8080/api/v1/analysis/jobs/$job_id")"
  result_json="$(curl --fail --silent --show-error -H "Authorization: Bearer $token" "http://127.0.0.1:8080/api/v1/logs/$log_id/analysis")"
  JOB_JSON="$job_json" RESULT_JSON="$result_json" python3 - <<'PY'
import json, os
job = json.loads(os.environ["JOB_JSON"])
result = json.loads(os.environ["RESULT_JSON"])
if job.get("status") != "SUCCEEDED":
    raise SystemExit(f"persisted job not SUCCEEDED: {job}")
if not (result.get("summary") or "").strip():
    raise SystemExit(f"persisted result missing: {result}")
print(json.dumps({"jobId": job.get("id") or job.get("jobId"), "status": job.get("status"), "resultInspectable": True}))
PY
  log "persisted job/result inspection PASS job_id=$job_id"
}

restart_apps() {
  status_quiet || fail "pilot must be running before restart"
  stop_pid "$HEIMDALL_PID_FILE" heimdall
  stop_pid "$BIFROST_PID_FILE" bifrost
  start_apps
  log "bounded application restart PASS"
}

stop() {
  stop_pid "$HEIMDALL_PID_FILE" heimdall
  stop_pid "$BIFROST_PID_FILE" bifrost
  docker compose -p "$COMPOSE_PROJECT" stop >/dev/null 2>&1 || true
  docker stop "$OLLAMA_CONTAINER" >/dev/null 2>&1 || true
  log "pilot stopped; persisted Compose/Ollama volumes and $STATE_DIR retained"
}

purge() {
  stop
  docker info >/dev/null 2>&1 || fail "Docker daemon unavailable during purge; retained $STATE_DIR for retry"
  docker compose -p "$COMPOSE_PROJECT" down -v --remove-orphans >/dev/null 2>&1 || fail "Compose purge failed; retained $STATE_DIR for retry"
  if docker container inspect "$OLLAMA_CONTAINER" >/dev/null 2>&1; then
    docker rm -f -v "$OLLAMA_CONTAINER" >/dev/null || fail "Ollama container purge failed; retained $STATE_DIR for retry"
  fi
  if docker volume inspect "$OLLAMA_VOLUME" >/dev/null 2>&1; then
    docker volume rm "$OLLAMA_VOLUME" >/dev/null || fail "Ollama volume purge failed; retained $STATE_DIR for retry"
  fi
  if docker container inspect "$OLLAMA_CONTAINER" >/dev/null 2>&1; then
    fail "Ollama container still exists after purge; retained $STATE_DIR for retry"
  fi
  if docker volume inspect "$OLLAMA_VOLUME" >/dev/null 2>&1; then
    fail "Ollama volume still exists after purge; retained $STATE_DIR for retry"
  fi
  if docker volume ls --filter "label=com.docker.compose.project=$COMPOSE_PROJECT" -q | grep -q .; then
    fail "Compose project volumes still exist after purge; retained $STATE_DIR for retry"
  fi
  rm -rf "$STATE_DIR"
  log "DESTRUCTIVE PURGE complete"
}

case "$ACTION" in
  validate) validate ;;
  start) start ;;
  status) status ;;
  job) run_job ;;
  inspect) inspect_last ;;
  restart) restart_apps ;;
  stop) stop ;;
  purge) purge ;;
  help|-h|--help)
    cat <<'EOF'
Usage: bash scripts/pilot.sh <validate|start|status|job|inspect|restart|stop|purge>

D3-01 bounded single-node Linux pilot lifecycle.
- stop preserves pilot-owned persisted data by default.
- purge is destructive and explicit.
- no production, HA, cloud-provider, SLA/SLO, RBAC, DR/PITR, or unattended-operation claim.
EOF
    ;;
  *) fail "unknown action: $ACTION" ;;
esac
