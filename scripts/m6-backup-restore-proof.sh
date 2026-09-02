#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PROOF_ID="${ASGARD_M6_PROOF_ID:-m6-backup-restore-$$}"
SAFE_ID="$(printf '%s' "$PROOF_ID" | tr -c '[:alnum:]_' '_' | tr '[:upper:]' '[:lower:]')"
RESTORE_DB="m6_restore_${SAFE_ID}"
WORK_DIR="${ASGARD_M6_WORK_DIR:-$(mktemp -d)}"
EVIDENCE_DIR="${ASGARD_M6_EVIDENCE_DIR:-$ROOT_DIR/m6-backup-restore-evidence}"
BACKUP_FILE="$WORK_DIR/heimdall.dump"
LOCAL_SUMMARY="$WORK_DIR/local-proof-summary.json"
LOCAL_EVIDENCE="$WORK_DIR/local-proof-evidence"
LOCAL_SESSION_DIR="$WORK_DIR/local-session"
SESSION_FILE="$LOCAL_SESSION_DIR/retained-session.env"
COMPOSE_PROJECT=""
HEIMDALL_PID=""
BIFROST_PID=""
OLLAMA_CONTAINER=""
JOB_ID=""
LOG_ID=""

log() { printf '[asgard-m6] %s\n' "$*"; }
fail() { printf '[asgard-m6] FAIL: %s\n' "$*" >&2; exit 1; }

cleanup() {
  local rc=$?
  set +e
  if [[ -f "$SESSION_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$SESSION_FILE"
  fi
  if [[ -n "${HEIMDALL_PID:-}" ]]; then kill "$HEIMDALL_PID" 2>/dev/null || true; fi
  if [[ -n "${BIFROST_PID:-}" ]]; then kill "$BIFROST_PID" 2>/dev/null || true; fi
  if [[ -n "${COMPOSE_PROJECT:-}" ]]; then
    docker compose -p "$COMPOSE_PROJECT" exec -T postgres dropdb -U asgard --if-exists "$RESTORE_DB" >/dev/null 2>&1 || true
    docker compose -p "$COMPOSE_PROJECT" down -v --remove-orphans >/dev/null 2>&1 || true
  fi
  if [[ -n "${OLLAMA_CONTAINER:-}" ]]; then docker rm -f "$OLLAMA_CONTAINER" >/dev/null 2>&1 || true; fi
  exit "$rc"
}
trap cleanup EXIT

mkdir -p "$WORK_DIR" "$EVIDENCE_DIR" "$LOCAL_SESSION_DIR"

log "creating accepted Local-first persisted state"
ASGARD_PROOF_ID="${PROOF_ID}-seed" \
ASGARD_PROOF_KEEP=1 \
ASGARD_PROOF_WORK_DIR="$LOCAL_SESSION_DIR" \
ASGARD_PROOF_OUTPUT="$LOCAL_SUMMARY" \
ASGARD_PROOF_EVIDENCE_DIR="$LOCAL_EVIDENCE" \
bash scripts/local-proof.sh

[[ -f "$SESSION_FILE" ]] || fail "retained session metadata missing"
# shellcheck disable=SC1090
source "$SESSION_FILE"
[[ -n "${COMPOSE_PROJECT:-}" ]] || fail "COMPOSE_PROJECT missing from retained session"

JOB_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["jobId"])' "$LOCAL_SUMMARY")"
LOG_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["logId"])' "$LOCAL_SUMMARY")"
[[ -n "$JOB_ID" && -n "$LOG_ID" ]] || fail "seed identifiers missing"

# Freeze writes before taking the bounded backup snapshot.
kill "$HEIMDALL_PID" 2>/dev/null || true
kill "$BIFROST_PID" 2>/dev/null || true
wait "$HEIMDALL_PID" 2>/dev/null || true
wait "$BIFROST_PID" 2>/dev/null || true
HEIMDALL_PID=""
BIFROST_PID=""

psql_original() {
  docker compose -p "$COMPOSE_PROJECT" exec -T postgres psql -U asgard -d heimdall -Atqc "$1"
}
psql_restored() {
  docker compose -p "$COMPOSE_PROJECT" exec -T postgres psql -U asgard -d "$RESTORE_DB" -Atqc "$1"
}

ORIGINAL_JOB="$(psql_original "SELECT status || '|' || COALESCE(result_ref::text,'') || '|' || attempt_count::text FROM analysis_jobs WHERE job_id='${JOB_ID}'::uuid;")"
[[ "$ORIGINAL_JOB" == SUCCEEDED\|* ]] || fail "original target job is not a persisted success: $ORIGINAL_JOB"
ORIGINAL_RESULT_COUNT="$(psql_original "SELECT count(*) FROM analysis_results WHERE id=(SELECT result_ref FROM analysis_jobs WHERE job_id='${JOB_ID}'::uuid);")"
ORIGINAL_AUDIT_COUNT="$(psql_original "SELECT count(*) FROM redrive_audit_logs WHERE job_id='${JOB_ID}'::uuid;")"
[[ "$ORIGINAL_RESULT_COUNT" == "1" ]] || fail "expected one persisted result before backup, found $ORIGINAL_RESULT_COUNT"

log "creating PostgreSQL custom-format backup artifact"
docker compose -p "$COMPOSE_PROJECT" exec -T postgres \
  pg_dump -U asgard -d heimdall -Fc --no-owner --no-privileges > "$BACKUP_FILE"
[[ -s "$BACKUP_FILE" ]] || fail "backup artifact is empty"
BACKUP_SHA256="$(sha256sum "$BACKUP_FILE" | awk '{print $1}')"
BACKUP_BYTES="$(wc -c < "$BACKUP_FILE" | tr -d ' ')"

log "restoring into clean proof-owned database $RESTORE_DB"
docker compose -p "$COMPOSE_PROJECT" exec -T postgres dropdb -U asgard --if-exists "$RESTORE_DB" >/dev/null
docker compose -p "$COMPOSE_PROJECT" exec -T postgres createdb -U asgard "$RESTORE_DB"
cat "$BACKUP_FILE" | docker compose -p "$COMPOSE_PROJECT" exec -T postgres \
  pg_restore -U asgard -d "$RESTORE_DB" --no-owner --no-privileges

RESTORED_JOB="$(psql_restored "SELECT status || '|' || COALESCE(result_ref::text,'') || '|' || attempt_count::text FROM analysis_jobs WHERE job_id='${JOB_ID}'::uuid;")"
RESTORED_RESULT_COUNT="$(psql_restored "SELECT count(*) FROM analysis_results WHERE id=(SELECT result_ref FROM analysis_jobs WHERE job_id='${JOB_ID}'::uuid);")"
RESTORED_AUDIT_COUNT="$(psql_restored "SELECT count(*) FROM redrive_audit_logs WHERE job_id='${JOB_ID}'::uuid;")"

[[ "$RESTORED_JOB" == "$ORIGINAL_JOB" ]] || fail "restored job mismatch: before=$ORIGINAL_JOB after=$RESTORED_JOB"
[[ "$RESTORED_RESULT_COUNT" == "$ORIGINAL_RESULT_COUNT" ]] || fail "restored result count mismatch"
[[ "$RESTORED_AUDIT_COUNT" == "$ORIGINAL_AUDIT_COUNT" ]] || fail "restored audit count mismatch"

cp "$BACKUP_FILE" "$EVIDENCE_DIR/heimdall.dump"
cp "$LOCAL_SUMMARY" "$EVIDENCE_DIR/local-proof-summary.json"
JOB_ID="$JOB_ID" LOG_ID="$LOG_ID" RESTORE_DB="$RESTORE_DB" \
ORIGINAL_JOB="$ORIGINAL_JOB" RESTORED_JOB="$RESTORED_JOB" \
ORIGINAL_RESULT_COUNT="$ORIGINAL_RESULT_COUNT" RESTORED_RESULT_COUNT="$RESTORED_RESULT_COUNT" \
ORIGINAL_AUDIT_COUNT="$ORIGINAL_AUDIT_COUNT" RESTORED_AUDIT_COUNT="$RESTORED_AUDIT_COUNT" \
BACKUP_SHA256="$BACKUP_SHA256" BACKUP_BYTES="$BACKUP_BYTES" EVIDENCE_DIR="$EVIDENCE_DIR" \
python3 - <<'PY'
import json, os
payload = {
    "proof": "v1.1-m6-persisted-state-backup-restore",
    "status": "PASS",
    "synthetic": True,
    "sourceDatabase": "heimdall",
    "restoreDatabase": os.environ["RESTORE_DB"],
    "cleanRestoreBoundary": True,
    "jobId": os.environ["JOB_ID"],
    "logId": os.environ["LOG_ID"],
    "before": {
        "job": os.environ["ORIGINAL_JOB"],
        "resultCount": int(os.environ["ORIGINAL_RESULT_COUNT"]),
        "redriveAuditCount": int(os.environ["ORIGINAL_AUDIT_COUNT"]),
    },
    "after": {
        "job": os.environ["RESTORED_JOB"],
        "resultCount": int(os.environ["RESTORED_RESULT_COUNT"]),
        "redriveAuditCount": int(os.environ["RESTORED_AUDIT_COUNT"]),
    },
    "backup": {
        "format": "pg_dump custom",
        "sha256": os.environ["BACKUP_SHA256"],
        "bytes": int(os.environ["BACKUP_BYTES"]),
        "command": "docker compose -p <proof-project> exec -T postgres pg_dump -U asgard -d heimdall -Fc --no-owner --no-privileges > heimdall.dump",
    },
    "restoreCommand": "createdb <clean-db> && pg_restore -U asgard -d <clean-db> --no-owner --no-privileges",
    "verified": [
        "target job identity exists after restore",
        "terminal job status/result_ref/attempt_count match before and after",
        "referenced analysis_result exists before and after",
        "target redrive audit count matches before and after",
        "restore target is a newly created database, not the source database",
    ],
    "notVerified": [
        "point-in-time recovery",
        "continuous or scheduled backups",
        "RPO/RTO",
        "HA or multi-node recovery",
        "cloud/off-site backup",
        "production retention or encryption policy",
    ],
}
with open(os.path.join(os.environ["EVIDENCE_DIR"], "m6-evidence.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
print(json.dumps(payload))
PY

log "PASS bounded persisted-state backup/restore verified; evidence=$EVIDENCE_DIR/m6-evidence.json"
