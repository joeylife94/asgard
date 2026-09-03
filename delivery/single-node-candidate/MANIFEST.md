# Asgard Versioned Single-node Delivery Candidate

Version source: `delivery/single-node-candidate/VERSION`.

This candidate packages the already accepted D1 Local-first single-node operator path. It does not create a new runtime capability or broaden any v1.0/D1 claim.

## Provenance

The CI-produced bundle MUST record `GITHUB_SHA` in `PROVENANCE.txt`. Acceptance is valid only for that exact artifact-producing commit.

The bundle is a **provenance-matched tracked repository snapshot** of that exact commit, plus generated `PROVENANCE.txt`. This is intentional: the accepted proof runner resolves Gradle/build inputs, Heimdall/Bifrost sources, Compose definitions, and operator scripts from repository-relative paths. A partial helper-script archive is not a valid D2 delivery candidate.

## Coherent operator path

1. **Preflight / start / real Local AI job** — `scripts/local-proof.sh` (use `ASGARD_PROOF_KEEP=1` when subsequent retained-session inspection/support/cleanup is required).
2. **Inspect job/result state and controlled recovery/audit** — accepted operator console/recovery paths documented by `docs/SINGLE_NODE_HANDOFF.md` and their accepted workflows.
3. **Diagnostics** — `scripts/operator-diagnostic-snapshot.sh` against a retained accepted proof session.
4. **Bounded PostgreSQL backup/restore where claimed** — `scripts/m6-backup-restore-proof.sh`; this is the accepted bounded M6 proof, not PITR/DR.
5. **Cleanup** — `scripts/cleanup-retained-proof.sh <retained-session.env>`.

The bundle is an executable handoff surface: operators should read `docs/SINGLE_NODE_HANDOFF.md` for prerequisites, exact boundaries, troubleshooting, and accepted evidence references.

## Required bundle surface

The archive must preserve the tracked exact-commit repository layout required by the accepted local proof. At minimum its verification gate checks:

- `delivery/single-node-candidate/VERSION`
- `delivery/single-node-candidate/MANIFEST.md`
- generated `PROVENANCE.txt`
- `ASGARD_MASTER.md`
- `docs/SINGLE_NODE_HANDOFF.md`
- Gradle wrapper/build inputs including `gradlew`
- `docker-compose.yml`
- Heimdall and Bifrost sources/build inputs
- `scripts/local-proof.sh`
- `scripts/operator-diagnostic-snapshot.sh`
- `scripts/m6-backup-restore-proof.sh`
- `scripts/cleanup-retained-proof.sh`

Because the candidate packages the tracked exact-commit tree, its D2 workflow runs for every pull request rather than using a partial path filter that could miss a packaged dependency change.

## Limitations / non-claims

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

Packaging/versioning this candidate does not convert any of those non-claims into accepted capabilities.
