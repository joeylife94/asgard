#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACTION="${1:-help}"
PILOT_HOME_RAW="${ASGARD_PILOT_HOME:-}"

log() { printf '[asgard-pilot-maintenance] %s\n' "$*"; }
fail() { printf '[asgard-pilot-maintenance] FAIL: %s\n' "$*" >&2; exit 1; }

[[ -n "$PILOT_HOME_RAW" ]] || fail "ASGARD_PILOT_HOME is required"
mkdir -p "$PILOT_HOME_RAW"
PILOT_HOME="$(cd "$PILOT_HOME_RAW" && pwd -P)"
CONFIG_FILE_RAW="${ASGARD_PILOT_CONFIG:-$PILOT_HOME/config/pilot.env}"
[[ -f "$CONFIG_FILE_RAW" ]] || fail "operator-owned pilot config missing: $CONFIG_FILE_RAW"
CONFIG_FILE="$(readlink -f -- "$CONFIG_FILE_RAW")"
[[ -n "$CONFIG_FILE" ]] || fail "unable to resolve operator-owned pilot config"
case "$CONFIG_FILE" in
  "$PILOT_HOME"/*) ;;
  *) fail "operator-owned pilot config must be inside ASGARD_PILOT_HOME" ;;
esac

# D5 remains the authority for validating the full operator-owned configuration.
ASGARD_PILOT_HOME="$PILOT_HOME" ASGARD_PILOT_CONFIG="$CONFIG_FILE" \
  bash "$ROOT_DIR/scripts/pilot-configured.sh" config-check >/dev/null

read_config_value() {
  local key=$1 value
  value="$(awk -F= -v wanted="$key" '$1==wanted {sub(/^[^=]*=/, ""); print; exit}' "$CONFIG_FILE")"
  [[ -n "$value" ]] || fail "validated config is missing $key"
  printf '%s' "$value"
}

COMPOSE_PROJECT="$(read_config_value ASGARD_PILOT_COMPOSE_PROJECT)"
DB_USER="$(read_config_value ASGARD_PILOT_DB_USER)"
DB_NAME="$(read_config_value ASGARD_PILOT_DB_NAME)"
STATE_DIR="$PILOT_HOME/state"
LAST_JOB_FILE="$STATE_DIR/last-job.json"
OWNER_FILE="$PILOT_HOME/active-release.env"
MAINTENANCE_DIR="$PILOT_HOME/maintenance"
BACKUPS_DIR="$MAINTENANCE_DIR/backups"
LATEST_FILE="$MAINTENANCE_DIR/latest-backup"

[[ "$DB_USER" == "asgard" ]] || fail "bounded pilot maintenance requires the accepted asgard database user"
[[ "$DB_NAME" =~ ^[A-Za-z0-9_]+$ ]] || fail "invalid configured database name"

postgres_container() {
  local id
  id="$(docker ps -a \
    --filter "label=com.docker.compose.project=$COMPOSE_PROJECT" \
    --filter 'label=com.docker.compose.service=postgres' \
    --format '{{.ID}}' | head -n 1)"
  [[ -n "$id" ]] || fail "pilot-owned PostgreSQL container not found for configured compose project"
  printf '%s' "$id"
}

start_postgres_only() {
  local id=$1
  docker start "$id" >/dev/null
  local i
  for i in {1..30}; do
    if docker exec "$id" pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  fail "pilot-owned PostgreSQL did not become ready"
}

stop_postgres_only() {
  local id=$1
  docker stop "$id" >/dev/null 2>&1 || true
}

sql_source() {
  local id=$1 query=$2
  docker exec "$id" psql -U "$DB_USER" -d "$DB_NAME" -Atqc "$query"
}

sql_target() {
  local id=$1 target=$2 query=$3
  docker exec "$id" psql -U "$DB_USER" -d "$target" -Atqc "$query"
}

read_owner_value() {
  local key=$1
  [[ -f "$OWNER_FILE" ]] || fail "active release provenance missing"
  awk -F= -v wanted="$key" '$1==wanted {sub(/^[^=]*=/, ""); print; exit}' "$OWNER_FILE"
}

validate_job_id() {
  [[ "$1" =~ ^[0-9a-fA-F-]{36}$ ]] || fail "last-job contains invalid job id"
}

backup() {
  [[ -f "$LAST_JOB_FILE" ]] || fail "no persisted pilot Job is available for backup verification"

  local job_id log_id
  job_id="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["jobId"])' "$LAST_JOB_FILE")"
  log_id="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["logId"])' "$LAST_JOB_FILE")"
  validate_job_id "$job_id"

  # Freeze application and infrastructure writes using the accepted persistence-preserving stop path.
  ASGARD_PILOT_HOME="$PILOT_HOME" ASGARD_PILOT_CONFIG="$CONFIG_FILE" \
    bash "$ROOT_DIR/scripts/pilot-configured.sh" stop >/dev/null

  local pg id backup_id backup_dir backup_file manifest
  pg="$(postgres_container)"
  start_postgres_only "$pg"
  trap 'stop_postgres_only "$pg"' RETURN

  local original_job original_result_count original_audit_count
  original_job="$(sql_source "$pg" "SELECT status || '|' || COALESCE(result_ref::text,'') || '|' || attempt_count::text FROM analysis_jobs WHERE job_id='${job_id}'::uuid;")"
  [[ "$original_job" == SUCCEEDED\|* ]] || fail "persisted target job is not a successful result"
  original_result_count="$(sql_source "$pg" "SELECT count(*) FROM analysis_results WHERE id=(SELECT result_ref FROM analysis_jobs WHERE job_id='${job_id}'::uuid);")"
  original_audit_count="$(sql_source "$pg" "SELECT count(*) FROM redrive_audit_logs WHERE job_id='${job_id}'::uuid;")"
  [[ "$original_result_count" == "1" ]] || fail "expected exactly one referenced persisted result"

  backup_id="$(date -u +%Y%m%dT%H%M%SZ)-$(printf '%s' "$job_id" | cut -c1-8)"
  backup_dir="$BACKUPS_DIR/$backup_id"
  mkdir -p "$backup_dir" "$MAINTENANCE_DIR"
  backup_file="$backup_dir/heimdall.dump"
  manifest="$backup_dir/manifest.json"

  log "creating bounded manual PostgreSQL backup after persistence-preserving pilot stop"
  docker exec "$pg" pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc --no-owner --no-privileges > "$backup_file"
  [[ -s "$backup_file" ]] || fail "backup artifact is empty"

  local backup_sha256 backup_bytes version commit
  backup_sha256="$(sha256sum "$backup_file" | awk '{print $1}')"
  backup_bytes="$(wc -c < "$backup_file" | tr -d ' ')"
  version="$(read_owner_value VERSION)"
  commit="$(read_owner_value COMMIT)"
  [[ "$commit" =~ ^[0-9a-f]{40}$ ]] || fail "active release commit provenance invalid"

  JOB_ID="$job_id" LOG_ID="$log_id" ORIGINAL_JOB="$original_job" \
  ORIGINAL_RESULT_COUNT="$original_result_count" ORIGINAL_AUDIT_COUNT="$original_audit_count" \
  BACKUP_SHA256="$backup_sha256" BACKUP_BYTES="$backup_bytes" VERSION_VALUE="$version" COMMIT_VALUE="$commit" \
  SOURCE_DB="$DB_NAME" MANIFEST="$manifest" python3 - <<'PY'
import json, os
payload = {
    "proof": "d6-01-bounded-pilot-maintenance-backup",
    "status": "BACKUP_CREATED",
    "sourceDatabase": os.environ["SOURCE_DB"],
    "jobId": os.environ["JOB_ID"],
    "logId": os.environ["LOG_ID"],
    "snapshot": {
        "job": os.environ["ORIGINAL_JOB"],
        "resultCount": int(os.environ["ORIGINAL_RESULT_COUNT"]),
        "redriveAuditCount": int(os.environ["ORIGINAL_AUDIT_COUNT"]),
    },
    "release": {
        "version": os.environ["VERSION_VALUE"],
        "commit": os.environ["COMMIT_VALUE"],
    },
    "backup": {
        "format": "pg_dump custom",
        "sha256": os.environ["BACKUP_SHA256"],
        "bytes": int(os.environ["BACKUP_BYTES"]),
    },
    "writeBoundary": "accepted persistence-preserving pilot stop before PostgreSQL-only snapshot access",
    "notVerified": [
        "continuous or scheduled backup",
        "point-in-time recovery",
        "RPO/RTO",
        "replication or HA",
        "cloud/off-site backup",
        "production retention/encryption policy",
        "unattended recovery",
    ],
}
with open(os.environ["MANIFEST"], "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
PY

  printf '%s\n' "$backup_dir" > "$LATEST_FILE"
  chmod 600 "$manifest" "$LATEST_FILE"
  stop_postgres_only "$pg"
  trap - RETURN
  log "backup PASS path=$backup_dir digest=$backup_sha256 bytes=$backup_bytes"
}

restore_verify() {
  local requested="${2:-}"
  if [[ -z "$requested" ]]; then
    [[ -f "$LATEST_FILE" ]] || fail "no latest bounded backup pointer exists"
    requested="$(cat "$LATEST_FILE")"
  fi
  [[ -d "$requested" ]] || fail "backup directory not found"
  local backup_dir
  backup_dir="$(cd "$requested" && pwd -P)"
  case "$backup_dir" in
    "$BACKUPS_DIR"/*) ;;
    *) fail "restore source must be a pilot-owned bounded backup directory" ;;
  esac

  local backup_file="$backup_dir/heimdall.dump" manifest="$backup_dir/manifest.json"
  [[ -s "$backup_file" && -s "$manifest" ]] || fail "backup artifact or manifest missing"

  local expected_sha actual_sha job_id expected_job expected_result_count expected_audit_count source_db
  readarray -t manifest_values < <(python3 - "$manifest" <<'PY'
import json, sys
m=json.load(open(sys.argv[1], encoding="utf-8"))
print(m["backup"]["sha256"])
print(m["jobId"])
print(m["snapshot"]["job"])
print(m["snapshot"]["resultCount"])
print(m["snapshot"]["redriveAuditCount"])
print(m["sourceDatabase"])
PY
)
  expected_sha="${manifest_values[0]}"
  job_id="${manifest_values[1]}"
  expected_job="${manifest_values[2]}"
  expected_result_count="${manifest_values[3]}"
  expected_audit_count="${manifest_values[4]}"
  source_db="${manifest_values[5]}"
  validate_job_id "$job_id"
  [[ "$source_db" == "$DB_NAME" ]] || fail "backup source database does not match configured pilot database"
  actual_sha="$(sha256sum "$backup_file" | awk '{print $1}')"
  [[ "$actual_sha" == "$expected_sha" ]] || fail "backup digest mismatch"

  local pg restore_suffix restore_db evidence
  pg="$(postgres_container)"
  start_postgres_only "$pg"
  trap 'stop_postgres_only "$pg"' RETURN
  restore_suffix="$(printf '%s' "$backup_dir" | sha256sum | cut -c1-12)"
  restore_db="d6_restore_${restore_suffix}"
  [[ "$restore_db" != "$DB_NAME" ]] || fail "recovery target must not be the live source database"

  docker exec "$pg" dropdb -U "$DB_USER" --if-exists "$restore_db" >/dev/null
  docker exec "$pg" createdb -U "$DB_USER" "$restore_db"
  cat "$backup_file" | docker exec -i "$pg" pg_restore -U "$DB_USER" -d "$restore_db" --no-owner --no-privileges

  local restored_job restored_result_count restored_audit_count
  restored_job="$(sql_target "$pg" "$restore_db" "SELECT status || '|' || COALESCE(result_ref::text,'') || '|' || attempt_count::text FROM analysis_jobs WHERE job_id='${job_id}'::uuid;")"
  restored_result_count="$(sql_target "$pg" "$restore_db" "SELECT count(*) FROM analysis_results WHERE id=(SELECT result_ref FROM analysis_jobs WHERE job_id='${job_id}'::uuid);")"
  restored_audit_count="$(sql_target "$pg" "$restore_db" "SELECT count(*) FROM redrive_audit_logs WHERE job_id='${job_id}'::uuid;")"

  [[ "$restored_job" == "$expected_job" ]] || fail "restored job invariant mismatch"
  [[ "$restored_result_count" == "$expected_result_count" ]] || fail "restored referenced result invariant mismatch"
  [[ "$restored_audit_count" == "$expected_audit_count" ]] || fail "restored audit invariant mismatch"

  evidence="$backup_dir/restore-evidence.json"
  RESTORE_DB="$restore_db" JOB_ID="$job_id" EXPECTED_SHA="$expected_sha" RESTORED_JOB="$restored_job" \
  RESTORED_RESULT_COUNT="$restored_result_count" RESTORED_AUDIT_COUNT="$restored_audit_count" EVIDENCE="$evidence" \
  python3 - <<'PY'
import json, os
payload = {
    "proof": "d6-01-bounded-pilot-maintenance-restore",
    "status": "PASS",
    "restoreTarget": os.environ["RESTORE_DB"],
    "cleanExplicitRecoveryTarget": True,
    "sourceDatabaseOverwritten": False,
    "jobId": os.environ["JOB_ID"],
    "backupSha256Verified": os.environ["EXPECTED_SHA"],
    "restored": {
        "job": os.environ["RESTORED_JOB"],
        "resultCount": int(os.environ["RESTORED_RESULT_COUNT"]),
        "redriveAuditCount": int(os.environ["RESTORED_AUDIT_COUNT"]),
    },
    "notVerified": [
        "continuous or scheduled backup",
        "point-in-time recovery",
        "RPO/RTO",
        "replication or HA",
        "DR certification",
        "cloud/off-site backup",
        "production retention/encryption policy",
    ],
}
with open(os.environ["EVIDENCE"], "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
PY

  # Recovery target is proof-owned and intentionally ephemeral; the live source remains untouched.
  docker exec "$pg" dropdb -U "$DB_USER" --if-exists "$restore_db" >/dev/null
  stop_postgres_only "$pg"
  trap - RETURN
  log "restore verification PASS backup=$backup_dir target=$restore_db source_untouched=true"
}

case "$ACTION" in
  backup) backup ;;
  restore-verify) restore_verify "$@" ;;
  help|-h|--help)
    cat <<'EOF'
Usage:
  ASGARD_PILOT_HOME=/absolute/operator/path bash scripts/pilot-maintenance.sh backup
  ASGARD_PILOT_HOME=/absolute/operator/path bash scripts/pilot-maintenance.sh restore-verify [backup-directory]

D6-01 bounded manual maintenance/recovery surface.
- Reuses the D5 operator-owned pilot configuration and D4 release provenance.
- backup first invokes the accepted persistence-preserving pilot stop, then snapshots PostgreSQL.
- restore-verify restores only into a generated clean proof-owned database, verifies Job/result/audit invariants, then removes that recovery target.
- backup artifacts, digest, provenance, and verification evidence remain under the operator-owned pilot home.
- no scheduled backup, PITR, RPO/RTO, replication, HA/DR certification, cloud/off-site backup, production retention/encryption policy, systemd, or unattended recovery claim.
EOF
    ;;
  *) fail "unknown action: $ACTION" ;;
esac
