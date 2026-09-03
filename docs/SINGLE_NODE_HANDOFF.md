# Asgard Single-node Delivery Handoff

> Bounded post-v1.0 operator handoff for the accepted Local-first path. This document does not broaden the frozen v1.0 claim boundary.

## Supported boundary

This handoff covers one technical operator on one Linux host using the repository's accepted Local-first proof path. It covers PostgreSQL/Kafka/Redis/Elasticsearch dependencies, Heimdall, Bifrost, and real local Ollama inference.

Accepted post-v1.0 evidence additionally covers bounded operator/read/recovery cases for local reproduction, read-only Job inspection, controlled redrive, one Bifrost restart replay, one PostgreSQL backup/restore, one read-only diagnostic snapshot, one single-broker Kafka restart replay, and one same-volume PostgreSQL restart recovery.

It does **not** claim AWS/Bedrock/OIDC/cloud execution, Kubernetes/HA/multi-node recovery, autonomous operations, production SLA/SLO, stable performance/cost, legal/security certification, multi-broker failover, PostgreSQL replication, PITR/DR certification, or RPO/RTO.

## Prerequisites

The executable source of truth for the Local-first proof is `scripts/local-proof.sh`. Its accepted Linux path requires:

- Linux shell with Bash;
- Docker daemon and Docker Compose plugin;
- Java 21;
- Python 3.9+ with `venv` support;
- `curl`;
- free local ports required by the proof services.

The proof runner builds Heimdall, creates an isolated Python environment for Bifrost, starts the required Compose infrastructure, and uses real Ollama inference. The accepted CI wrapper is `.github/workflows/v11-m1-local-proof.yml`.

## Start and execute one real Local AI Job

```bash
bash -n scripts/local-proof.sh
bash scripts/local-proof.sh
```

A successful run must end with the script's PASS summary and a real Local-first Job path through Heimdall → Kafka → Bifrost → Ollama → persisted final Job state. Code existence or an agent report is not a substitute for the executable result.

For retained inspection:

```bash
ASGARD_PROOF_KEEP=1 \
ASGARD_PROOF_OUTPUT="$PWD/local-proof-summary.json" \
ASGARD_PROOF_EVIDENCE_DIR="$PWD/local-proof-evidence" \
bash scripts/local-proof.sh
```

When `KEEP=1` is used, the runner writes bounded session metadata for later cleanup. This retained session does not itself replace the dedicated accepted interruption/recovery workflows below.

## Accepted bounded recovery and support evidence

### Bifrost process restart — M4

`.github/workflows/v11-m4-bifrost-restart.yml` proves one bounded single-node replay case in which Bifrost is interrupted during processing, confirmed down, restarted with the same consumer-group semantics, and the target persisted Job reaches `SUCCEEDED` with a result reference.

This is not a general HA, autonomous retry, recovery-time, or distributed-delivery guarantee.

### PostgreSQL backup/restore — M6

`scripts/m6-backup-restore-proof.sh` and `.github/workflows/v11-m6-backup-restore.yml` prove one bounded PostgreSQL backup/restore case for accepted Asgard-owned Job/result/audit state. The proof creates a concrete `pg_dump` artifact, restores it into a distinct proof-owned database, and verifies bounded persisted state parity.

This is **not** PITR, continuous backup, disaster-recovery certification, off-site durability, HA, RPO/RTO, or a production retention/encryption policy.

### Operator diagnostic snapshot — M7

`scripts/operator-diagnostic-snapshot.sh` and `.github/workflows/v11-m7-operator-diagnostic.yml` prove one bounded read-only support bundle covering supported service health, persisted Job state, lifecycle metrics, proof/session correlation metadata, and sanitized bounded logs. The evidence contract fails closed on known proof-secret leakage.

This is not a generic monitoring platform, alerting system, autonomous remediation layer, production monitoring certification, or SLA/SLO evidence.

### Kafka broker restart — M8

`.github/workflows/v11-m8-kafka-restart.yml` proves one bounded single-node persisted-request replay case. A target request is published before Bifrost startup, the proof-owned Kafka broker is actually stopped and independently confirmed unavailable, the same broker/storage boundary is restarted, and Bifrost then completes the request to a single accepted persisted result.

This is not multi-broker Kafka, cluster failover, HA, cross-node recovery, autonomous failover, recovery-time, or production durability evidence.

### PostgreSQL same-volume restart — M9

`.github/workflows/v11-m9-postgres-restart.yml` proves one bounded same-volume PostgreSQL restart/recovery case. A real Local-first persisted Job/result is established, the proof-owned PostgreSQL service is actually stopped and confirmed unavailable, the same service and data volume are restarted, and persisted Job/result parity plus supported Heimdall read behavior are verified after recovery.

This is not replication, managed-database failover, HA, PITR, DR certification, RPO/RTO, recovery-time, SLA/SLO, production durability, Kubernetes operator, or cloud execution evidence.

## Diagnostic use

For a retained accepted proof session, `scripts/operator-diagnostic-snapshot.sh` is the repository-owned read-only diagnostic path. Treat its bounded JSON/Markdown output as support evidence for that session only. Do not generalize one snapshot into a production observability claim.

## Persistence and cleanup

- Job/result state is persisted through the accepted Heimdall/PostgreSQL path.
- Kafka participates in request/result handoff.
- M6 proves one bounded PostgreSQL backup/restore case.
- M8 proves one bounded single-broker restart/replay case.
- M9 proves one bounded same-volume PostgreSQL service restart/recovery case.
- The default local proof cleanup removes proof-owned Compose volumes intentionally; retained inspection requires `ASGARD_PROOF_KEEP=1`.

For a retained proof session, use the generated `retained-session.env` rather than guessing process/container identities. Run the repository-owned bounded cleanup command:

```bash
bash scripts/cleanup-retained-proof.sh /path/to/retained-session.env
```

The command validates the recorded proof ownership boundary before acting, stops only the recorded Heimdall/Bifrost processes, removes a proof-owned Ollama container only when one was created, and tears down the recorded proof-owned Compose project and volumes. A successful cleanup writes a sidecar `.cleaned` marker so a repeated invocation returns safely without acting on stale recorded PIDs.

If the proof reused an already-running operator-owned Ollama endpoint, `OLLAMA_CONTAINER` is empty and cleanup deliberately leaves that external Ollama process untouched. The retained work directory is evidence/workspace data and remains separate; remove it only after the operator no longer needs it.

Missing or malformed session metadata is a fail-closed condition. Do not replace it with guessed `kill`, broad `docker rm`, or generic Compose/project deletion commands.

## Troubleshooting

| Symptom | Bounded action |
|---|---|
| `missing required command` | Install the named prerequisite and rerun preflight. |
| Docker daemon unavailable | Start/fix the local Docker daemon; do not bypass the check. |
| Docker Compose plugin unavailable | Install/enable Compose v2 and rerun. |
| Java/Python prerequisite failure | Select the required runtime before rerunning. |
| required port already in use | Stop the conflicting local process or use a clean host/session. |
| infrastructure/readiness failure | Inspect configured local-proof evidence before changing runtime code. |
| Ollama/model failure | Check retained Ollama/pull diagnostics; do not substitute a cloud provider and call the Local-first gate PASS. |
| retained cleanup needed | Run `bash scripts/cleanup-retained-proof.sh /path/to/retained-session.env`; do not guess proof-owned resource identities. |
| Bifrost interruption/restart question | Use `.github/workflows/v11-m4-bifrost-restart.yml` as the exact bounded evidence. |
| backup/restore question | Use `scripts/m6-backup-restore-proof.sh` / `.github/workflows/v11-m6-backup-restore.yml`; do not generalize to DR/PITR. |
| support snapshot needed | Use `scripts/operator-diagnostic-snapshot.sh`; keep it read-only. |
| Kafka restart question | Use `.github/workflows/v11-m8-kafka-restart.yml`; do not generalize to multi-broker/HA. |
| PostgreSQL restart question | Use `.github/workflows/v11-m9-postgres-restart.yml`; do not generalize to replication/HA/DR. |
| broad Heimdall Checkstyle RED | Known pre-existing R-002 unless a selected milestone makes that gate material; do not mass-fix as handoff work. |

## Exact references

- Local proof runner: `scripts/local-proof.sh`
- Retained proof cleanup: `scripts/cleanup-retained-proof.sh`
- M1 local proof: `.github/workflows/v11-m1-local-proof.yml`
- M4 Bifrost restart: `.github/workflows/v11-m4-bifrost-restart.yml`
- M6 backup/restore: `scripts/m6-backup-restore-proof.sh`, `.github/workflows/v11-m6-backup-restore.yml`
- M7 diagnostic snapshot: `scripts/operator-diagnostic-snapshot.sh`, `.github/workflows/v11-m7-operator-diagnostic.yml`
- M8 Kafka restart: `.github/workflows/v11-m8-kafka-restart.yml`
- M9 PostgreSQL restart: `.github/workflows/v11-m9-postgres-restart.yml`
- Authoritative progression/claim contract: `ASGARD_MASTER.md`

## Explicitly not verified by this handoff

- Production readiness is not verified.
- Production SLA/SLO is not verified.
- Stable performance/cost is not verified.
- Continuous backup and PITR are not verified.
- Disaster-recovery certification and RPO/RTO are not verified.
- Kafka multi-broker/cluster failover is not verified.
- PostgreSQL replication/HA is not verified.
- Kubernetes/HA/multi-node recovery is not verified.
- Cloud-provider execution is not verified.
- Enterprise identity/RBAC is not verified.
- Legal/security certification is not verified.
- Unattended autonomous operations are not verified.
- Generic monitoring/admin-platform capability is not verified.