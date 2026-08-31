#!/usr/bin/env bash
set -Eeuo pipefail

STAGE="preflight"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PROOF_ID="${ASGARD_PROOF_ID:-local-proof-$$}"
COMPOSE_PROJECT="asgard-proof-${PROOF_ID//[^a-zA-Z0-9_-]/-}"
MODEL="${ASGARD_PROOF_MODEL:-smollm:135m}"
OUTPUT="${ASGARD_PROOF_OUTPUT:-$ROOT_DIR/local-proof-summary.json}"
EVIDENCE_DIR="${ASGARD_PROOF_EVIDENCE_DIR:-$ROOT_DIR/local-proof-evidence}"
KEEP="${ASGARD_PROOF_KEEP:-0}"
WORK_DIR="${ASGARD_PROOF_WORK_DIR:-$(mktemp -d)}"
OWN_OLLAMA=0
HEIMDALL_PID=""
BIFROST_PID=""
JOB_ID=""
FINAL_STATUS=""
POLL_ATTEMPT=0

log() { printf '[asgard-proof] %s\n' "$*"; }
fail() { printf '[asgard-proof] FAIL stage=%s: %s\n' "$STAGE" "$*" >&2; exit 1; }

preserve_failure_evidence() {
  local rc=$1
  mkdir -p "$EVIDENCE_DIR" 2>/dev/null || return 0
  printf '{\n  "proof": "v1.1-m1-local-proof",\n  "status": "FAIL",\n  "exitCode": %s,\n  "stage": "%s",\n  "proofId": "%s",\n  "model": "%s",\n  "jobId": "%s",\n  "finalJobStatus": "%s",\n  "pollAttempt": %s\n}\n' \
    "$rc" "$STAGE" "$PROOF_ID" "$MODEL" "$JOB_ID" "$FINAL_STATUS" "$POLL_ATTEMPT" \
    > "$EVIDENCE_DIR/failure-context.json" 2>/dev/null || true
  for name in heimdall.log bifrost.log ollama-pull.json job-final.json; do
    [[ -f "$WORK_DIR/$name" ]] && cp "$WORK_DIR/$name" "$EVIDENCE_DIR/$name" 2>/dev/null || true
  done
  if [[ "$OWN_OLLAMA" == "1" ]]; then
    docker logs "$PROOF_ID-ollama" > "$EVIDENCE_DIR/ollama.log" 2>&1 || true
  fi
  log "failure diagnostics retained at $EVIDENCE_DIR"
}

cleanup() {
  local rc=$?
  set +e
  if [[ "$rc" != "0" ]]; then
    preserve_failure_evidence "$rc"
  fi
  if [[ "$KEEP" != "1" ]]; then
    [[ -n "$HEIMDALL_PID" ]] && kill "$HEIMDALL_PID" 2>/dev/null || true
    [[ -n "$BIFROST_PID" ]] && kill "$BIFROST_PID" 2>/dev/null || true
    [[ "$OWN_OLLAMA" == "1" ]] && docker rm -f "$PROOF_ID-ollama" >/dev/null 2>&1 || true
    docker compose -p "$COMPOSE_PROJECT" down -v --remove-orphans >/dev/null 2>&1 || true
    rm -rf "$WORK_DIR"
  else
    log "KEEP=1; work dir retained at $WORK_DIR"
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'fail "command failed at line $LINENO"' ERR

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

STAGE="preflight"
for cmd in docker java python3 curl; do need_cmd "$cmd"; done
docker info >/dev/null 2>&1 || fail "Docker daemon is not available"
docker compose version >/dev/null 2>&1 || fail "Docker Compose plugin is required"
JAVA_MAJOR="$(java -version 2>&1 | awk -F'[".]' '/version/ {print $2; exit}')"
[[ "$JAVA_MAJOR" == "21" ]] || fail "Java 21 required; detected ${JAVA_MAJOR:-unknown}"
python3 - <<'PY' || fail "Python 3.8+ required"
import sys
assert sys.version_info >= (3, 8), sys.version
PY
python3 -m venv "$WORK_DIR/venv" || fail "python venv creation failed"
for port in 5432 6379 8080 8000 9091 9200; do
  if command -v ss >/dev/null 2>&1 && ss -ltn "sport = :$port" | grep -q LISTEN; then
    fail "required port already in use: $port"
  fi
done
log "preflight PASS (Java 21, Python, Docker, Compose, curl)"

STAGE="build"
chmod +x ./gradlew
./gradlew :heimdall:bootJar --no-daemon --console=plain
"$WORK_DIR/venv/bin/python" -m pip install --quiet --upgrade pip setuptools wheel
"$WORK_DIR/venv/bin/python" -m pip install --quiet -r bifrost/requirements.txt
"$WORK_DIR/venv/bin/python" -m pip install --quiet -e bifrost

STAGE="infrastructure"
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

STAGE="ollama"
if curl --fail --silent http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  log "using existing local Ollama endpoint"
else
  docker run -d --name "$PROOF_ID-ollama" -p 11434:11434 ollama/ollama:latest >/dev/null
  OWN_OLLAMA=1
  wait_http "Ollama" "http://127.0.0.1:11434/api/tags" 30
fi
curl --fail --silent --show-error -H 'Content-Type: application/json' \
  -d "{\"name\":\"$MODEL\",\"stream\":false}" \
  http://127.0.0.1:11434/api/pull > "$WORK_DIR/ollama-pull.json"
curl --fail --silent http://127.0.0.1:11434/api/tags | grep -q "${MODEL%%:*}" || fail "Ollama model not visible after pull: $MODEL"

STAGE="services"
HEIMDALL_JAR="$(find heimdall/build/libs -maxdepth 1 -name 'heimdall-*.jar' -type f | head -n 1)"
[[ -n "$HEIMDALL_JAR" ]] || fail "Heimdall bootJar not found"
export SPRING_PROFILES_ACTIVE=dev
export SPRING_DATASOURCE_URL=jdbc:postgresql://127.0.0.1:5432/heimdall
export SPRING_DATASOURCE_USERNAME=asgard
export SPRING_DATASOURCE_PASSWORD=asgard_password
export SPRING_KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
export JWT_SECRET=local-proof-jwt-secret-at-least-32-bytes-long
export HEIMDALL_SECURITY_ADMIN_USERNAME=admin
export HEIMDALL_SECURITY_ADMIN_PASSWORD=local-proof-admin-password
export HEIMDALL_SECURITY_ADMIN_ROLES=ADMIN,USER
# M1 proves one explicit operator-requested Job. Disable ingestion auto-request only
# in this proof process so the deterministic Job does not compete for local Ollama.
export HEIMDALL_ANALYSIS_AUTO_REQUEST=false
export REDIS_HOST=127.0.0.1 REDIS_PORT=6379 REDIS_PASSWORD=redis_password GRPC_PORT=9091
export KAFKA_ENABLED=true HEIMDALL_ENABLED=true KAFKA_BOOTSTRAP_SERVERS=127.0.0.1:9092
export HEIMDALL_DATABASE_URL=postgresql://asgard:asgard_password@127.0.0.1:5432/heimdall
export BIFROST_OLLAMA_URL=http://127.0.0.1:11434 BIFROST_OLLAMA_MODEL="$MODEL" BIFROST_OLLAMA_ALLOW_FALLBACK=false
java -jar "$HEIMDALL_JAR" > "$WORK_DIR/heimdall.log" 2>&1 & HEIMDALL_PID=$!
"$WORK_DIR/venv/bin/python" -m bifrost.main serve > "$WORK_DIR/bifrost.log" 2>&1 & BIFROST_PID=$!
wait_http "Heimdall" "http://127.0.0.1:8080/actuator/health" 90
wait_http "Bifrost" "http://127.0.0.1:8000/health" 60

STAGE="local-ai-flow"
LOGIN_JSON="$(curl --fail --silent --show-error -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"local-proof-admin-password"}' \
  http://127.0.0.1:8080/api/v1/auth/login)"
TOKEN="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])' <<<"$LOGIN_JSON")"
[[ -n "$TOKEN" ]] || fail "authentication token missing"

INGEST_JSON="$(curl --fail --silent --show-error -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"source":"local-proof","serviceName":"payment-service","environment":"proof","severity":"ERROR","logContent":"synthetic local proof gateway timeout after 3000ms","metadata":{"proof":"v1.1-m1","synthetic":true}}' \
  http://127.0.0.1:8080/api/v1/logs)"
LOG_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["logId"])' <<<"$INGEST_JSON")"
IDEMP="v11-m1-${PROOF_ID}"
ACCEPTED_JSON="$(curl --fail --silent --show-error -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -H "Idempotency-Key: $IDEMP" \
  -d "{\"idempotencyKey\":\"$IDEMP\",\"modelPolicy\":{\"source\":\"local\"}}" \
  -X POST "http://127.0.0.1:8080/api/v1/logs/$LOG_ID/analysis")"
JOB_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["jobId"])' <<<"$ACCEPTED_JSON")"
for i in {1..180}; do
  POLL_ATTEMPT=$i
  JOB_JSON="$(curl --fail --silent --show-error -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/v1/analysis/jobs/$JOB_ID")"
  printf '%s\n' "$JOB_JSON" > "$WORK_DIR/job-final.json"
  FINAL_STATUS="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])' <<<"$JOB_JSON")"
  [[ "$FINAL_STATUS" == "SUCCEEDED" ]] && break
  [[ "$FINAL_STATUS" == "FAILED" ]] && fail "analysis job failed: $JOB_ID"
  sleep 2
done
[[ "$FINAL_STATUS" == "SUCCEEDED" ]] || fail "analysis job did not succeed within timeout: $JOB_ID"
RESULT_JSON="$(curl --fail --silent --show-error -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8080/api/v1/logs/$LOG_ID/analysis")"

mkdir -p "$(dirname "$OUTPUT")"
JOB_ID="$JOB_ID" LOG_ID="$LOG_ID" MODEL_EXPECTED="$MODEL" OUTPUT="$OUTPUT" RESULT_JSON="$RESULT_JSON" \
python3 - <<'PY'
import json, os
result = json.loads(os.environ["RESULT_JSON"])
model = result.get("model") or ""
if not model or model.lower() == "fallback" or not (result.get("summary") or "").strip():
    raise SystemExit(f"invalid local result: {result}")
expected = os.environ["MODEL_EXPECTED"].split(":", 1)[0].lower()
if expected not in model.lower():
    raise SystemExit(f"unexpected model: {model}")
summary = {
    "proof": "v1.1-m1-local-proof",
    "status": "PASS",
    "jobId": os.environ["JOB_ID"],
    "logId": os.environ["LOG_ID"],
    "provider": "ollama",
    "model": model,
    "analysisId": result.get("analysisId"),
    "synthetic": True,
    "cloudExecution": False,
}
with open(os.environ["OUTPUT"], "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(json.dumps(summary, ensure_ascii=False))
PY

STAGE="complete"
log "PASS real Local-first integration completed; summary=$OUTPUT"