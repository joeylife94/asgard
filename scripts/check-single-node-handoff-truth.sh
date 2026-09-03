#!/usr/bin/env bash
set -euo pipefail

DOC="${1:-docs/SINGLE_NODE_HANDOFF.md}"
[[ -f "$DOC" ]] || { echo "missing handoff doc: $DOC" >&2; exit 1; }

required=(
  '.github/workflows/v11-m4-bifrost-restart.yml'
  'scripts/m6-backup-restore-proof.sh'
  '.github/workflows/v11-m6-backup-restore.yml'
  'scripts/operator-diagnostic-snapshot.sh'
  '.github/workflows/v11-m7-operator-diagnostic.yml'
  '.github/workflows/v11-m8-kafka-restart.yml'
  '.github/workflows/v11-m9-postgres-restart.yml'
  'scripts/cleanup-retained-proof.sh'
  'ASGARD_MASTER.md'
  'retained-session.env'
)

for token in "${required[@]}"; do
  grep -Fq "$token" "$DOC" || { echo "missing required accepted reference: $token" >&2; exit 1; }
done

obsolete=(
  'Backup/restore: NOT VERIFIED.'
  'It does not prove Kafka outage recovery'
  'backup/restore; Kubernetes/HA'
  'docker compose -p "$COMPOSE_PROJECT" down -v --remove-orphans'
)
for token in "${obsolete[@]}"; do
  if grep -Fq "$token" "$DOC"; then
    echo "obsolete handoff text remains: $token" >&2
    exit 1
  fi
done

nonclaims=(
  'Production readiness is not verified.'
  'Production SLA/SLO is not verified.'
  'Continuous backup and PITR are not verified.'
  'Disaster-recovery certification and RPO/RTO are not verified.'
  'Kafka multi-broker/cluster failover is not verified.'
  'PostgreSQL replication/HA is not verified.'
  'Cloud-provider execution is not verified.'
  'Unattended autonomous operations are not verified.'
)
for statement in "${nonclaims[@]}"; do
  grep -Fq -- "$statement" "$DOC" || { echo "missing explicit non-claim boundary: $statement" >&2; exit 1; }
done

forbidden=(
  'production-ready'
  'production ready'
  'Production readiness is verified'
  'Production SLA/SLO is verified'
  'Kafka multi-broker/cluster failover is verified'
  'PostgreSQL replication/HA is verified'
  'Cloud-provider execution is verified'
  'Unattended autonomous operations are verified'
  'high availability is verified'
  'disaster recovery is verified'
  'SLA guaranteed'
  'RPO guaranteed'
  'RTO guaranteed'
  'cloud execution verified'
)
for token in "${forbidden[@]}"; do
  if grep -Fiq -- "$token" "$DOC"; then
    echo "forbidden overclaim wording found: $token" >&2
    exit 1
  fi
done

echo 'handoff truth contract: PASS'
