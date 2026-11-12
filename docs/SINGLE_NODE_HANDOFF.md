# Asgard Single-node Delivery Handoff

> Bounded post-v1.0 operator handoff for the accepted Local-first path. This document does not broaden the frozen v1.0 or D1–D6 claim boundary.

## Supported boundary

This handoff covers one technical operator on one Linux host using the repository's accepted Local-first path. It covers PostgreSQL/Kafka/Redis/Elasticsearch dependencies, Heimdall, Bifrost, real local Ollama inference, the accepted D3 persistent pilot lifecycle, the D4 release-independent pilot home, the D5 operator-owned configuration, and the D6 manual maintenance/recovery path.

Accepted post-v1.0 evidence additionally covers bounded operator/read/recovery cases for local reproduction, read-only Job inspection, controlled redrive, one Bifrost restart replay, one PostgreSQL backup/restore, one read-only diagnostic snapshot, one single-broker Kafka restart replay, one same-volume PostgreSQL restart recovery, versioned D2 packaging/provenance, one bounded persistent D3 pilot lifecycle operated from an extracted clean workspace, one same-schema compatible A→B release transition over a shared pilot home (D4), operator-owned pilot configuration (D5), and one manual backup → clean-target restore verification over that configured pilot (D6).

It does **not** claim AWS/Bedrock/OIDC/cloud execution, Kubernetes/HA/multi-node recovery, autonomous operations, production SLA/SLO, stable performance/cost, legal/security certification, multi-broker failover, PostgreSQL replication, PITR/DR certification, RPO/RTO, scheduled or unattended backup/recovery, systemd/automatic boot, cross-schema migration, production rollback, secret-manager integration, or public production deployment.

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

## Choosing the pilot command surface

Three wrappers expose the same lifecycle actions. Each one delegates to the one below it:

| Surface | Accepted by | Use it when |
|---|---|---|
| `scripts/pilot-configured.sh` | D5-01 | Normal operation of a pilot whose state you intend to keep. Requires `ASGARD_PILOT_HOME` and an operator-owned `config/pilot.env`. |
| `scripts/pilot-release.sh` | D4-01 | Pilot state must live outside the extracted release, but the release-default credentials are acceptable. Requires `ASGARD_PILOT_HOME`. |
| `scripts/pilot.sh` | D3-01 | Throwaway evaluation from a single extracted release. State lives under the release root and the release-default test credentials are used. |

`scripts/pilot-maintenance.sh` (D6-01) operates only on a pilot run through `scripts/pilot-configured.sh`.

## Release-independent pilot home — D4 accepted

`ASGARD_PILOT_HOME` is an absolute operator-chosen directory outside the extracted release. It holds the pilot state (`state/`) and the ownership record (`active-release.env`: `VERSION`, `COMMIT`, `ROOT`).

```bash
export ASGARD_PILOT_HOME=/absolute/operator/path
bash scripts/pilot-release.sh start
bash scripts/pilot-release.sh release
bash scripts/pilot-release.sh stop
```

- The first `start` or `validate` on an unclaimed pilot home records the invoking release as owner. Other actions on an unclaimed home fail.
- `release` prints the recorded version, commit, and release root.
- A release whose version, commit, or root does not match the recorded owner fails closed before any lifecycle action runs.
- `stop` remains persistence-preserving. `purge` remains explicit/destructive and also removes the ownership record.

### Compatible release transition

Accepted D4-02 evidence covers one same-schema compatible candidate A → candidate B transition over the same pilot home:

```bash
# from release A
bash scripts/pilot-release.sh stop

# from release B, same ASGARD_PILOT_HOME
bash scripts/pilot-release.sh claim
bash scripts/pilot-release.sh start
bash scripts/pilot-release.sh inspect
```

`claim` is refused while a recorded application process of the previous release is still live. After the transition the Job/result persisted under A is inspectable under B and `release` reports B.

This is not schema migration, a production rollback procedure, or a general upgrade guarantee. A B→A rollback permutation was not executed. Both candidates had identical Heimdall/Bifrost/Compose/Gradle inputs.

Accepted evidence: `.github/workflows/d4-01-release-independent-pilot.yml` and the `d4-02-transition` job in `.github/workflows/d2-single-node-delivery-candidate.yml`.

## Operator-owned configuration — D5 accepted

The supported configured path reads `$ASGARD_PILOT_HOME/config/pilot.env`. Start from the packaged template:

```bash
mkdir -p "$ASGARD_PILOT_HOME/config"
cp delivery/single-node-candidate/PILOT_CONFIG.example "$ASGARD_PILOT_HOME/config/pilot.env"
chmod 600 "$ASGARD_PILOT_HOME/config/pilot.env"
# replace every <placeholder>, then:
bash scripts/pilot-configured.sh config-check
bash scripts/pilot-configured.sh start
```

Every lifecycle action of `scripts/pilot-release.sh` is available through `scripts/pilot-configured.sh` (`claim`, `release`, `validate`, `start`, `status`, `job`, `inspect`, `restart`, `stop`, `purge`).

Contract enforced before any application start:

- The file is parsed as data with an explicit key allow-list. It is never sourced as shell code. An unknown key, a malformed line, or an empty value fails closed.
- All nine keys in the template are required. Values inherited from the environment do not satisfy a key missing from the file.
- The resolved file path must stay inside `ASGARD_PILOT_HOME`; a symlink that escapes the pilot home is rejected.
- `ASGARD_PILOT_DB_USER` must be `asgard`. Database and Redis passwords are 12–128 characters from `A-Z a-z 0-9 . _ ~ -`. The JWT secret is at least 32 characters. The admin password is at least 12 characters.
- The wrapper does not print the configured sensitive values.

The same configuration file stays authoritative across `restart` and across a compatible D4-style release transition.

This is not Vault or cloud secret-manager integration, credential rotation, enterprise identity/SSO, or a production secrets policy. Accepted evidence: the `d5-01-config` job in `.github/workflows/d2-single-node-delivery-candidate.yml`.

## Manual maintenance and recovery — D6 accepted

`scripts/pilot-maintenance.sh` promotes the M6 backup/restore primitives into one manual path over the configured pilot. It needs at least one successful Job created with `job`, and it refuses to run unless the pilot home is owned by the invoking release.

```bash
bash scripts/pilot-maintenance.sh backup
bash scripts/pilot-maintenance.sh restore-verify
bash scripts/pilot-configured.sh start
```

`backup`:

- runs the persistence-preserving pilot stop first, so the pilot is **stopped when the command returns**; start it again when finished;
- writes a PostgreSQL custom-format dump to `$ASGARD_PILOT_HOME/maintenance/backups/<backup-id>/heimdall.dump`;
- writes `manifest.json` beside it with the SHA-256 digest, size, active release version/commit, and the Job/result/audit snapshot used for later verification;
- updates `$ASGARD_PILOT_HOME/maintenance/latest-backup`.

`restore-verify [backup-directory]`:

- uses the latest backup when no directory is given, and fails if the application processes are live;
- checks the dump against the recorded digest;
- restores into a generated clean database on the pilot PostgreSQL instance, verifies the recorded Job/result/audit invariants, writes `restore-evidence.json`, then removes that recovery database;
- leaves the source database untouched.

`restore-verify` proves that a backup is restorable. It does **not** replace the live pilot database, and this handoff contains no accepted in-place restore procedure.

This is not scheduled or continuous backup, PITR, RPO/RTO, replication, off-site durability, a retention/encryption policy, or unattended recovery. Backup files are not encrypted by this path. Accepted evidence: `.github/workflows/d6-bounded-maintenance-recovery.yml`.

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

This is **not** PITR, continuous backup, disaster-recovery certification, off-site durability, HA, RPO/RTO, or a production retention/encryption policy. For the configured persistent pilot, the operator path is `scripts/pilot-maintenance.sh` (D6, above); the M6 proof remains the underlying accepted primitive.

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
- With `ASGARD_PILOT_HOME` set, pilot state, ownership record, configuration, and maintenance backups live under that directory rather than under the release root.
- `purge` through `scripts/pilot-release.sh` or `scripts/pilot-configured.sh` removes the pilot-owned Compose resources and volumes, the state directory, and the ownership record. It does not remove `config/` or `maintenance/backups/` under the pilot home; those files, including the configured secrets and unencrypted dumps, stay until the operator deletes them.
- M6 proves one bounded PostgreSQL backup/restore case only; D6 proves one manual backup → clean-target restore verification over the configured pilot.
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
| `ASGARD_PILOT_HOME is required` | Export an absolute operator-owned directory outside the release before using `pilot-release.sh`, `pilot-configured.sh`, or `pilot-maintenance.sh`. |
| `pilot home is owned by another/stale release` | Run `bash scripts/pilot-release.sh release` to see the recorded owner. Operate from that release, or stop it and run `claim` from the intended compatible release. |
| `cannot claim pilot home while recorded application process is live` | Stop the pilot from the owning release first; do not delete the ownership record by hand. |
| `operator-owned pilot config missing` or a config validation failure | Create or fix `$ASGARD_PILOT_HOME/config/pilot.env` from `delivery/single-node-candidate/PILOT_CONFIG.example`; rerun `config-check`. Do not fall back to the release-default credentials and call the configured pilot accepted. |
| `no persisted pilot Job is available for backup verification` | Run `bash scripts/pilot-configured.sh job` and confirm it succeeded before `backup`. |
| `restore verification requires the persistence-preserving pilot stop path first` | Run `bash scripts/pilot-configured.sh stop`, then rerun `restore-verify`. |
| retained proof cleanup needed | Run `bash scripts/cleanup-retained-proof.sh /path/to/retained-session.env`; do not guess proof-owned resource identities. |
| Bifrost interruption/restart question | Use `.github/workflows/v11-m4-bifrost-restart.yml` as the exact bounded evidence. |
| backup/restore question | For the configured pilot use `scripts/pilot-maintenance.sh`; the underlying bounded proof is `scripts/m6-backup-restore-proof.sh` / `.github/workflows/v11-m6-backup-restore.yml`. Do not generalize to DR/PITR. |
| support snapshot needed | Use `scripts/operator-diagnostic-snapshot.sh`; keep it read-only and bounded. |
| Kafka restart question | Use `.github/workflows/v11-m8-kafka-restart.yml`; do not generalize to multi-broker/HA. |
| PostgreSQL restart question | Use `.github/workflows/v11-m9-postgres-restart.yml`; do not generalize to replication/HA/DR. |
| broad Heimdall Checkstyle RED | Known pre-existing R-002 unless a selected milestone makes that gate material; do not mass-fix as handoff work. |

## Exact references

- Persistent pilot lifecycle: `scripts/pilot.sh`
- Release-independent pilot home: `scripts/pilot-release.sh`
- Operator-owned configuration: `scripts/pilot-configured.sh`, `delivery/single-node-candidate/PILOT_CONFIG.example`
- Manual maintenance/recovery: `scripts/pilot-maintenance.sh`
- Ephemeral/regression proof runner: `scripts/local-proof.sh`
- Retained proof cleanup: `scripts/cleanup-retained-proof.sh`
- D3-01 pilot acceptance: `.github/workflows/d3-01-persistent-pilot.yml`
- D3-03 fresh-host candidate: `.github/workflows/d3-03-fresh-host-candidate.yml`
- D4-01 release-independent pilot: `.github/workflows/d4-01-release-independent-pilot.yml`
- D4-02 transition and D5-01 configuration: `.github/workflows/d2-single-node-delivery-candidate.yml`
- D6-01 maintenance/recovery: `.github/workflows/d6-bounded-maintenance-recovery.yml`
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
- Version upgrade/rollback beyond one same-schema compatible A→B transition is not verified.
- Cross-schema migration and production rollback are not verified.
- Scheduled or unattended backup/recovery is not verified.
- In-place restore of the live pilot database is not verified.
- Secret-manager integration is not verified.
- Public production deployment is not verified.
