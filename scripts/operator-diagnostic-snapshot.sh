#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION_FILE="${1:-}"
OUTPUT_DIR="${2:-$ROOT_DIR/operator-diagnostic-snapshot}"

fail() { printf '[asgard-diagnostic] FAIL: %s\n' "$*" >&2; exit 1; }
log() { printf '[asgard-diagnostic] %s\n' "$*"; }

[[ -n "$SESSION_FILE" ]] || fail "usage: $0 <retained-session.env> [output-dir]"
[[ -f "$SESSION_FILE" ]] || fail "retained session file not found: $SESSION_FILE"

# retained-session.env is repository-owned metadata emitted by scripts/local-proof.sh.
# It intentionally contains process/container identifiers and paths only, not credentials.
# shellcheck disable=SC1090
source "$SESSION_FILE"

: "${COMPOSE_PROJECT:?missing COMPOSE_PROJECT in retained session}"
: "${WORK_DIR:?missing WORK_DIR in retained session}"

SUMMARY_FILE="${ASGARD_DIAG_SUMMARY_FILE:-$WORK_DIR/local-proof-summary.json}"
[[ -f "$SUMMARY_FILE" ]] || fail "local proof summary not found: $SUMMARY_FILE"

for cmd in curl docker python3 sha256sum; do
  command -v "$cmd" >/dev/null 2>&1 || fail "missing required command: $cmd"
done

mkdir -p "$OUTPUT_DIR"
RAW_METRICS="$OUTPUT_DIR/metrics.raw"
HEIMDALL_TAIL="$OUTPUT_DIR/heimdall.tail"
BIFROST_TAIL="$OUTPUT_DIR/bifrost.tail"
JSON_OUT="$OUTPUT_DIR/diagnostic-snapshot.json"
MD_OUT="$OUTPUT_DIR/diagnostic-snapshot.md"

JOB_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["jobId"])' "$SUMMARY_FILE")"
[[ -n "$JOB_ID" ]] || fail "jobId missing from local proof summary"

http_ok() {
  local url=$1
  if curl --fail --silent --max-time 5 "$url" >/dev/null 2>&1; then printf 'true'; else printf 'false'; fi
}

HEIMDALL_HEALTH="$(http_ok http://127.0.0.1:8080/actuator/health)"
BIFROST_HEALTH="$(http_ok http://127.0.0.1:8000/health)"
OLLAMA_HEALTH="$(http_ok http://127.0.0.1:11434/api/tags)"

if docker compose -p "$COMPOSE_PROJECT" exec -T postgres pg_isready -U asgard >/dev/null 2>&1; then
  POSTGRES_HEALTH=true
else
  POSTGRES_HEALTH=false
fi

if docker compose -p "$COMPOSE_PROJECT" exec -T kafka kafka-broker-api-versions --bootstrap-server kafka:29092 >/dev/null 2>&1; then
  KAFKA_HEALTH=true
else
  KAFKA_HEALTH=false
fi

JOB_ROW="$(docker compose -p "$COMPOSE_PROJECT" exec -T postgres psql -U asgard -d heimdall -At -F '|' -c \
  "SELECT job_id::text,status,attempt_count,COALESCE(result_ref::text,''),COALESCE(trace_id,''),created_at::text,COALESCE(finished_at::text,'') FROM analysis_jobs WHERE job_id='${JOB_ID}'::uuid;")"
[[ -n "$JOB_ROW" ]] || fail "target job not found in persisted state: $JOB_ID"

curl --fail --silent --max-time 5 http://127.0.0.1:8080/actuator/prometheus > "$RAW_METRICS" || fail "unable to read Heimdall Prometheus endpoint"

grep -E '^(ai_job_requested_total|ai_job_success_total|ai_job_failed_total|ai_job_redriven_total)(\{|[[:space:]])' "$RAW_METRICS" > "$OUTPUT_DIR/lifecycle-metrics.txt" || true

tail -n 40 "$WORK_DIR/heimdall.log" 2>/dev/null > "$HEIMDALL_TAIL" || :
tail -n 40 "$WORK_DIR/bifrost.log" 2>/dev/null > "$BIFROST_TAIL" || :

SESSION_FILE="$SESSION_FILE" SUMMARY_FILE="$SUMMARY_FILE" JOB_ID="$JOB_ID" JOB_ROW="$JOB_ROW" \
HEIMDALL_HEALTH="$HEIMDALL_HEALTH" BIFROST_HEALTH="$BIFROST_HEALTH" OLLAMA_HEALTH="$OLLAMA_HEALTH" \
POSTGRES_HEALTH="$POSTGRES_HEALTH" KAFKA_HEALTH="$KAFKA_HEALTH" OUTPUT_DIR="$OUTPUT_DIR" \
python3 - <<'PY'
import hashlib, json, os, re
from pathlib import Path

out = Path(os.environ["OUTPUT_DIR"])
parts = os.environ["JOB_ROW"].strip().split("|")
if len(parts) != 7:
    raise SystemExit(f"unexpected persisted job row: {parts}")

secret_patterns = [
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)\S+"),
    re.compile(r"(?i)(password\s*[:=]\s*)\S+"),
    re.compile(r"(?i)(jwt[_-]?secret\s*[:=]\s*)\S+"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)\S+"),
    re.compile(r"(?i)(token\s*[:=]\s*)\S+"),
]

def redact(text: str) -> str:
    for pattern in secret_patterns:
        text = pattern.sub(r"\1[REDACTED]", text)
    for literal in (
        "local-proof-admin-password",
        "local-proof-jwt-secret-at-least-32-bytes-long",
        "redis_password",
        "asgard_password",
    ):
        text = text.replace(literal, "[REDACTED]")
    return text

def read_sanitized(path: Path):
    if not path.exists():
        return []
    lines = [redact(line.rstrip()) for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    return lines[-40:]

metrics_path = out / "lifecycle-metrics.txt"
metrics = metrics_path.read_text(encoding="utf-8", errors="replace").splitlines() if metrics_path.exists() else []
heimdall = read_sanitized(out / "heimdall.tail")
bifrost = read_sanitized(out / "bifrost.tail")

snapshot = {
    "snapshot": "asgard-v1.1-m7-operator-diagnostic",
    "status": "PASS",
    "readOnly": True,
    "synthetic": True,
    "cloudExecution": False,
    "session": {
        "proofId": os.environ.get("PROOF_ID", ""),
        "composeProject": os.environ.get("COMPOSE_PROJECT", ""),
    },
    "health": {
        "heimdall": os.environ["HEIMDALL_HEALTH"] == "true",
        "bifrost": os.environ["BIFROST_HEALTH"] == "true",
        "postgres": os.environ["POSTGRES_HEALTH"] == "true",
        "kafka": os.environ["KAFKA_HEALTH"] == "true",
        "ollama": os.environ["OLLAMA_HEALTH"] == "true",
    },
    "job": {
        "jobId": parts[0],
        "status": parts[1],
        "attemptCount": int(parts[2]),
        "resultRef": parts[3] or None,
        "traceId": parts[4] or None,
        "createdAt": parts[5],
        "finishedAt": parts[6] or None,
    },
    "lifecycleMetrics": metrics,
    "logs": {
        "heimdallRecent": heimdall,
        "bifrostRecent": bifrost,
        "heimdallTailSha256": hashlib.sha256("\n".join(heimdall).encode()).hexdigest(),
        "bifrostTailSha256": hashlib.sha256("\n".join(bifrost).encode()).hexdigest(),
    },
    "limitations": [
        "bounded single-node diagnostic snapshot only",
        "no alerting or autonomous remediation",
        "no production monitoring, SLA/SLO, HA, or cloud-observability claim",
        "recent logs are bounded and redacted; absence of a log line is not proof of absence of an event",
    ],
}

if not all(snapshot["health"].values()):
    raise SystemExit(f"supported service health not all green: {snapshot['health']}")
if snapshot["job"]["jobId"] != os.environ["JOB_ID"]:
    raise SystemExit("persisted job identity mismatch")
if snapshot["job"]["status"] != "SUCCEEDED" or not snapshot["job"]["resultRef"]:
    raise SystemExit(f"unexpected target job state: {snapshot['job']}")

json_text = json.dumps(snapshot, indent=2, ensure_ascii=False)
for forbidden in (
    "local-proof-admin-password",
    "local-proof-jwt-secret-at-least-32-bytes-long",
    "redis_password",
    "asgard_password",
    "Authorization: Bearer",
):
    if forbidden in json_text:
        raise SystemExit(f"forbidden secret material present in snapshot: {forbidden}")

(out / "diagnostic-snapshot.json").write_text(json_text + "\n", encoding="utf-8")

md = [
    "# Asgard Operator Diagnostic Snapshot",
    "",
    f"- Status: **{snapshot['status']}**",
    f"- Read-only: `{str(snapshot['readOnly']).lower()}`",
    f"- Proof ID: `{snapshot['session']['proofId']}`",
    f"- Target Job: `{snapshot['job']['jobId']}` — `{snapshot['job']['status']}` — resultRef `{snapshot['job']['resultRef']}`",
    "",
    "## Supported service health",
]
for name, value in snapshot["health"].items():
    md.append(f"- {name}: {'PASS' if value else 'FAIL'}")
md += ["", "## Lifecycle metrics"]
md += [f"- `{line}`" for line in metrics] or ["- no matching lifecycle metrics emitted"]
md += [
    "",
    "## Triage logs",
    f"- Heimdall sanitized tail SHA-256: `{snapshot['logs']['heimdallTailSha256']}`",
    f"- Bifrost sanitized tail SHA-256: `{snapshot['logs']['bifrostTailSha256']}`",
    "- Bounded sanitized tails are retained in the machine-readable snapshot.",
    "",
    "## Limitations",
]
md += [f"- {item}" for item in snapshot["limitations"]]
(out / "diagnostic-snapshot.md").write_text("\n".join(md) + "\n", encoding="utf-8")
PY

rm -f "$RAW_METRICS" "$HEIMDALL_TAIL" "$BIFROST_TAIL"

# Final artifact-level secret scan. This is intentionally fail-closed for the proof-owned known credentials.
if grep -R -n -E 'local-proof-admin-password|local-proof-jwt-secret-at-least-32-bytes-long|redis_password|asgard_password|Authorization:[[:space:]]*Bearer' "$OUTPUT_DIR"; then
  fail "diagnostic output contains forbidden secret material"
fi

log "PASS snapshot=$JSON_OUT summary=$MD_OUT"
