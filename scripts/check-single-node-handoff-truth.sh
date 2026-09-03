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
  'ASGARD_MASTER.md'
)

for token in "${required[@]}"; do
  grep -Fq "$token" "$DOC" || { echo "missing required accepted reference: $token" >&2; exit 1; }
done

obsolete=(
  'Backup/restore: NOT VERIFIED.'
  'It does not prove Kafka outage recovery'
  'backup/restore; Kubernetes/HA'
)
for token in "${obsolete[@]}"; do
  if grep -Fq "$token" "$DOC"; then
    echo "obsolete pre-progression handoff claim remains: $token" >&2
    exit 1
  fi
done

# The handoff must preserve explicit non-claims for the most material boundaries.
nonclaims=(
  'Production readiness'
  'production SLA/SLO'
  'PITR'
  'RPO/RTO'
  'Kafka multi-broker/cluster failover'
  'PostgreSQL replication/HA'
  'cloud-provider execution'
  'unattended autonomous operations'
)
for token in "${nonclaims[@]}"; do
  grep -Fq "$token" "$DOC" || { echo "missing required non-claim boundary: $token" >&2; exit 1; }
done

# Guard against obvious claim broadening in the delivery-facing document.
forbidden=(
  'production-ready'
  'production ready'
  'high availability is verified'
  'disaster recovery is verified'
  'SLA guaranteed'
  'RPO guaranteed'
  'RTO guaranteed'
  'cloud execution verified'
)
for token in "${forbidden[@]}"; do
  if grep -Fiq "$token" "$DOC"; then
    echo "forbidden overclaim wording found: $token" >&2
    exit 1
  fi
done

echo 'M10 handoff truth contract: PASS'
