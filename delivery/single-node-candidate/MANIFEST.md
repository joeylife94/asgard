# Asgard Versioned Single-node Delivery Candidate

Version source: `delivery/single-node-candidate/VERSION`.

This candidate packages the already accepted D1/D2 Local-first single-node operator assets and the accepted D3–D6 persistent pilot command surfaces. It does not broaden any v1.0 or D1–D6 claim or convert the pilot into a production/enterprise claim.

## Provenance

The CI-produced bundle MUST record `GITHUB_SHA` in `PROVENANCE.txt`. Acceptance is valid only for that exact artifact-producing commit.

The bundle is a **provenance-matched tracked repository snapshot** of that exact commit, plus generated `PROVENANCE.txt`. This is intentional: the accepted Gradle/build inputs, Heimdall/Bifrost sources, Compose definitions, and operator scripts resolve from repository-relative paths. A partial helper-script archive is not a valid delivery candidate.

## Persistent pilot operator path — D3-01 accepted

For a technical operator who wants the bounded persistent single-host pilot, the primary lifecycle surface is now:

```bash
bash scripts/pilot.sh validate
bash scripts/pilot.sh start
bash scripts/pilot.sh status
bash scripts/pilot.sh job
bash scripts/pilot.sh inspect
bash scripts/pilot.sh restart
bash scripts/pilot.sh stop
```

`stop` is persistence-preserving. Destructive removal is deliberately separate:

```bash
bash scripts/pilot.sh purge
```

Do not substitute `purge` for normal shutdown. The accepted D3-01 boundary is one supported Linux host, Local Ollama, one technical operator, repository-owned pilot state/resources, and one bounded application restart. It does not establish systemd/automatic boot, unattended operations, HA, public production deployment, SLA/SLO, DR/PITR/RPO/RTO, cloud-provider execution, or enterprise identity/RBAC.

## Operator-owned pilot surfaces — D4/D5/D6 accepted

The same lifecycle actions are available through two wrappers that keep pilot state outside the extracted release. Both require an absolute operator-chosen `ASGARD_PILOT_HOME`.

```bash
export ASGARD_PILOT_HOME=/absolute/operator/path

# D4-01: release-independent pilot home with recorded release ownership
bash scripts/pilot-release.sh <claim|release|validate|start|status|job|inspect|restart|stop|purge>

# D5-01: the same, with operator-owned configuration from $ASGARD_PILOT_HOME/config/pilot.env
bash scripts/pilot-configured.sh <config-check|claim|release|validate|start|status|job|inspect|restart|stop|purge>

# D6-01: manual backup and clean-target restore verification over the configured pilot
bash scripts/pilot-maintenance.sh <backup|restore-verify>
```

- `scripts/pilot-configured.sh` is the supported path for a pilot whose state is meant to be kept. Create its configuration from `delivery/single-node-candidate/PILOT_CONFIG.example`; the file is parsed as data and validated fail-closed.
- A release that does not match the recorded owner of the pilot home fails closed. `claim` moves ownership to a compatible release only while the previous release's application processes are stopped. Accepted evidence covers one same-schema compatible A→B transition.
- `scripts/pilot-maintenance.sh backup` stops the pilot, writes a digest-recorded PostgreSQL dump under the pilot home, and leaves the pilot stopped. `restore-verify` restores into a temporary clean database, verifies the recorded Job/result/audit invariants, and leaves the source database untouched. It is not an in-place restore.

Read `docs/SINGLE_NODE_HANDOFF.md` before operating the pilot; it is the delivery-facing source for prerequisites, lifecycle semantics, accepted support/backup evidence, troubleshooting, and explicit limitations.

## Existing bounded support/evidence assets

The persistent pilot does not erase or retroactively rewrite earlier accepted evidence:

1. **Ephemeral proof / regression path** — `scripts/local-proof.sh`. This remains the accepted proof runner and regression asset; it is not the normal persistent pilot lifecycle.
2. **Inspect/recovery/audit evidence** — accepted operator console/recovery paths documented by `docs/SINGLE_NODE_HANDOFF.md` and their accepted workflows.
3. **Diagnostics** — `scripts/operator-diagnostic-snapshot.sh` against the supported retained/proof session boundary documented by the handoff. D3-02 does not claim a new generic production monitoring surface.
4. **Bounded PostgreSQL backup/restore where claimed** — `scripts/m6-backup-restore-proof.sh`; this remains the accepted bounded M6 proof, not continuous backup, PITR, or DR. `scripts/pilot-maintenance.sh` is the operator path that reuses it for the configured pilot.
5. **Retained proof cleanup** — `scripts/cleanup-retained-proof.sh <retained-session.env>` for older retained proof sessions. This is distinct from persistent pilot `stop`/`purge` semantics.

## Required bundle surface

The archive must preserve the tracked exact-commit repository layout. At minimum its verification gate checks:

- `delivery/single-node-candidate/VERSION`
- `delivery/single-node-candidate/MANIFEST.md`
- generated `PROVENANCE.txt`
- `ASGARD_MASTER.md`
- `docs/SINGLE_NODE_HANDOFF.md`
- Gradle wrapper/build inputs including `gradlew`
- `docker-compose.yml`
- Heimdall and Bifrost sources/build inputs
- `scripts/pilot.sh`
- `scripts/pilot-release.sh`
- `scripts/pilot-configured.sh`
- `scripts/pilot-maintenance.sh`
- `docker-compose.pilot.yml`
- `delivery/single-node-candidate/PILOT_CONFIG.example`
- `scripts/local-proof.sh`
- `scripts/operator-diagnostic-snapshot.sh`
- `scripts/m6-backup-restore-proof.sh`
- `scripts/cleanup-retained-proof.sh`

Because the candidate packages the tracked exact-commit tree, its delivery workflow runs for every pull request rather than using a partial path filter that could miss a packaged dependency change.

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
- Systemd/automatic boot ownership is not verified.
- Version upgrade/rollback beyond one same-schema compatible A→B transition is not verified.
- Cross-schema migration and production rollback are not verified.
- Scheduled or unattended backup/recovery is not verified.
- In-place restore of the live pilot database is not verified.
- Secret-manager integration is not verified.

Packaging/versioning this candidate and exposing the accepted persistent pilot command surface does not convert any of those non-claims into accepted capabilities.
