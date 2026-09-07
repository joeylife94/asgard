# Asgard Single-node Delivery Handoff

> Bounded post-v1.0 operator handoff for the accepted Local-first path. This document does not broaden the frozen v1.0, D1, or D2 claim boundary.

## Supported boundary

This handoff covers one technical operator on one Linux host using the repository's accepted Local-first path. It covers PostgreSQL/Kafka/Redis/Elasticsearch dependencies, Heimdall, Bifrost, real local Ollama inference, and the accepted D3-01 persistent pilot lifecycle.

Accepted post-v1.0 evidence additionally covers bounded operator/read/recovery cases for local reproduction, read-only Job inspection, controlled redrive, one Bifrost restart replay, one PostgreSQL backup/restore, one read-only diagnostic snapshot, one single-broker Kafka restart replay, one same-volume PostgreSQL restart recovery, versioned D2 packaging/provenance, and one bounded persistent D3-01 pilot lifecycle.

It does **not** claim AWS/Bedrock/OIDC/cloud execution, Kubernetes/HA/multi-node recovery, autonomous operations, production SLA/SLO, stable performance/cost, legal/security certification, multi-broker failover, PostgreSQL replication, PITR/DR certification, RPO/RTO, systemd/automatic boot, version upgrade/rollback, or public production deployment.

## Prerequisites

The accepted persistent pilot command surface is `scripts/pilot.sh`. Its supported Linux path requires:

- Linux shell with Bash;
- Docker daemon and Docker Compose plugin;
- Java 21;
- Python 3.9+ with `venv` support;
- `curl`;
- free local ports required by the pilot services;
- repository-local tracked sources/build inputs from the versioned candidate.

Validate before starting:

```bash
bash -n scripts/pilot.sh
bash scripts/pilot.sh validate
```

Do not bypass a failed prerequisite/config validation and call the pilot accepted.

## Persistent pilot lifecycle — D3-01 accepted

Start and inspect the bounded Local-first pilot:

```bash
bash scripts/pilot.sh start
bash scripts/pilot.sh status
```

Execute and inspect one real Local Ollama-backed Analysis Job:

```bash
bash scripts/pilot.sh job
bash scripts/pilot.sh inspect
```

The accepted job path is Heimdall → Kafka → Bifrost → Ollama → persisted Job/result state. Code existence or agent self-report is not a substitute for executable evidence.

One bounded application restart is exposed by:

```bash
bash scripts/pilot.sh restart
bash scripts/pilot.sh status
bash scripts/pilot.sh inspect
```

D3-01 accepted evidence verifies that the same Job/result remains inspectable across that restart boundary. This is not HA, automatic failover, recovery-time, or production durability evidence.

### Stop versus purge

Normal stop is persistence-preserving:

```bash
bash scripts/pilot.sh stop
```

The pilot-owned persisted state is intentionally retained so a later `start` can reuse the accepted state boundary.

Destructive cleanup is explicit and separate:

```bash
bash scripts/pilot.sh purge
```

`purge` is not normal shutdown. Use it only when the operator deliberately wants to remove the pilot-owned persistent resources/state. Do not silently replace `stop` with `purge`.

## Ephemeral proof / regression path remains separate

`scripts/local-proof.sh` remains the accepted proof/regression runner. It is useful for ephemeral proof execution and CI evidence but is **not** the normal persistent D3 pilot lifecycle.

For retained proof inspection only:

```bash
ASGARD_PROOF_KEEP=1 \
ASGARD_PROOF_OUTPUT="$PWD/local-proof-summary.json" \
ASGARD_PROOF_EVIDENCE_DIR="$PWD/local-proof-evidence" \
bash scripts/local-proof.sh
```

When `KEEP=1` is used, the proof runner writes bounded session metadata for later cleanup. That retained proof session is distinct from D3 pilot ownership/state semantics.

## Accepted bounded recovery and support evidence

### Bifrost process restart — M4

`.github/workflows/v11-m4-bifrost-restart.yml` proves one bounded single-node replay case in which Bifrost is interrupted during processing, confirmed down, restarted with the same consumer-group semantics, and the target persisted Job reaches `SUCCEEDED` with a result reference.

This is not a general HA, autonomous retry, recovery-time, or distributed-delivery guarantee.

### PostgreSQL backup/restore — M6

`scripts/m6-backup-restore-proof.sh` and `.github/workflows/v11-m6-backup-restore.yml` prove one bounded PostgreSQL backup/restore case for accepted Asgard-owned Job/result/audit state. The proof creates a concrete `pg_dump` artifact, restores it into a distinct proof-owned database, and verifies bounded persisted state parity.

This is **not** PITR, continuous backup, disaster-recovery certification, off-site durability, HA, RPO/RTO, or a production retention/encryption policy. D3-02 only preserves and points to this existing evidence; it does not claim a new pilot backup regime.

### Operator diagnostic snapshot — M7

`scripts/operator-diagnostic-snapshot.sh` and `.github/workflows/v11-m7-operator-diagnostic.yml` prove one bounded read-only support bundle covering supported service health, persisted Job state, lifecycle metrics, proof/session correlation metadata, and sanitized bounded logs. The evidence contract fails closed on known proof-secret leakage.

This is not a generic monitoring platform, alerting system, autonomous remediation layer, production monitoring certification, or SLA/SLO evidence. D3-02 does not broaden the diagnostic snapshot into a production pilot monitoring claim.

### Kafka broker restart — M8

`.github/workflows/v11-m8-kafka-restart.yml` proves one bounded single-node persisted-request replay case. A target request is published before Bifrost startup, the proof-owned Kafka broker is actually stopped and independently confirmed unavailable, the same broker/storage boundary is restarted, and Bifrost then completes the request to a single accepted persisted result.

This is not multi-broker Kafka, cluster failover, HA, cross-node recovery, autonomous failover, recovery-time, or production durability evidence.

### PostgreSQL same-volume restart — M9

`.github/workflows/v11-m9-postgres-restart.yml` proves one bounded same-volume PostgreSQL restart/recovery case. A real Local-first persisted Job/result is established, the proof-owned PostgreSQL service is actually stopped and confirmed unavailable, the same service and data volume are restarted, and persisted Job/result parity plus supported Heimdall read behavior are verified after recovery.

This is not replication, managed-database failover, HA, PITR, DR certification, RPO/RTO, recovery-time, SLA/SLO, production durability, Kubernetes operator, or cloud execution evidence.

## Diagnostic use

For the already accepted retained proof/session support boundary, `scripts/operator-diagnostic-snapshot.sh` remains the repository-owned read-only diagnostic path. Treat its bounded JSON/Markdown output as support evidence for that supported session only. Do not generalize one snapshot into production observability or autonomous pilot monitoring.

## Persistence and cleanup boundaries

- D3 pilot Job/result state is persisted through the accepted Heimdall/PostgreSQL path.
- `scripts/pilot.sh stop` preserves pilot-owned persisted state by default.
- `scripts/pilot.sh purge` is explicit destructive removal.
- M6 proves one bounded PostgreSQL backup/restore case only.
- M8 proves one bounded single-broker restart/replay case.
- M9 proves one bounded same-volume PostgreSQL service restart/recovery case.
- The older local proof runner has different cleanup semantics and may remove proof-owned Compose volumes unless retained mode is requested.

For an older retained proof session, use the generated `retained-session.env` rather than guessing process/container identities:

```bash
bash scripts/cleanup-retained-proof.sh /path/to/retained-session.env
```

The retained-proof cleanup command validates its recorded proof ownership boundary before acting. It is separate from the D3 persistent pilot `stop`/`purge` contract.

## Troubleshooting

| Symptom | Bounded action |
|---|---|
| `missing required command` | Install the named prerequisite and rerun `bash scripts/pilot.sh validate`. |
| Docker daemon unavailable | Start/fix the local Docker daemon; do not bypass the check. |
| Docker Compose plugin unavailable | Install/enable Compose v2 and rerun validation. |
| Java/Python prerequisite failure | Select the required runtime before rerunning validation. |
| required port already in use | Stop the conflicting local process or use a clean host/session. |
| pilot status/readiness failure | Run `bash scripts/pilot.sh status`; inspect bounded local evidence before changing runtime code. |
| Ollama/model failure | Inspect local Ollama diagnostics; do not substitute a cloud provider and call the Local-first gate PASS. |
| normal pilot shutdown | Run `bash scripts/pilot.sh stop`; persisted pilot state should remain. |
| deliberate destructive pilot cleanup | Run `bash scripts/pilot.sh purge`; do not use this as normal shutdown. |
| retained proof cleanup needed | Run `bash scripts/cleanup-retained-proof.sh /path/to/retained-session.env`; do not guess proof-owned resource identities. |
| Bifrost interruption/restart question | Use `.github/workflows/v11-m4-bifrost-restart.yml` as the exact bounded evidence. |
| backup/restore question | Use `scripts/m6-backup-restore-proof.sh` / `.github/workflows/v11-m6-backup-restore.yml`; do not generalize to DR/PITR. |
| support snapshot needed | Use `scripts/operator-diagnostic-snapshot.sh`; keep it read-only and bounded. |
| Kafka restart question | Use `.github/workflows/v11-m8-kafka-restart.yml`; do not generalize to multi-broker/HA. |
| PostgreSQL restart question | Use `.github/workflows/v11-m9-postgres-restart.yml`; do not generalize to replication/HA/DR. |
| broad Heimdall Checkstyle RED | Known pre-existing R-002 unless a selected milestone makes that gate material; do not mass-fix as handoff work. |

## Exact references

- Persistent pilot lifecycle: `scripts/pilot.sh`
- Ephemeral/regression proof runner: `scripts/local-proof.sh`
- Retained proof cleanup: `scripts/cleanup-retained-proof.sh`
- D3-01 pilot acceptance: `.github/workflows/d3-01-persistent-pilot.yml`
- M1 local proof: `.github/workflows/v11-m1-local-proof.yml`
- M4 Bifrost restart: `.github/workflows/v11-m4-bifrost-restart.yml`
- M6 backup/restore: `scripts/m6-backup-restore-proof.sh`, `.github/workflows/v11-m6-backup-restore.yml`
- M7 diagnostic snapshot: `scripts/operator-diagnostic-snapshot.sh`, `.github/workflows/v11-m7-operator-diagnostic.yml`
- M8 Kafka restart: `.github/workflows/v11-m8-kafka-restart.yml`
- M9 PostgreSQL restart: `.github/workflows/v11-m9-postgres-restart.yml`
- Versioned delivery manifest: `delivery/single-node-candidate/MANIFEST.md`
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
- Systemd/automatic boot is not verified.
- Version upgrade/rollback is not verified.
- Public production deployment is not verified.
