# ASGARD MASTER

> **Authoritative execution and progression contract**
>
> Single source of truth for the frozen Asgard v1.0 Proof baseline and bounded post-v1.0 progression. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, Scheduled Task prompt text, and agent self-report.

## 0. Control

- **Frozen Baseline**: Asgard v1.0 — Wishket / Freelance Proof
- **Frozen Baseline Level**: READY TO SHOW bounded software Proof
- **Frozen v1.0 Product Direction**: **Local-first AI Operations Platform**
- **Post-v1.0 Product Destination**: **bounded single-node Local AI Operations Tool for a technical operator**
- **Current Phase**: Post-v1.0 Bounded Progression — M9 SELECTED
- **Current Batch**: M9 — Bounded PostgreSQL Restart Recovery — SELECTED / ISSUE NOT YET OPEN
- **Current Status**: **v1.0 FROZEN / M1 FROZEN / M2 FROZEN / M3 FROZEN / M4 FROZEN / M5 FROZEN / M6 FROZEN / M7 FROZEN / M8 FROZEN — M9 SELECTED**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Accepted implementation main SHA**: `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`
- **Accepted buyer-facing proof/docs main SHA**: `359b26e573e5da04b2d0ec406a56be7ecb508dbd`
- **Accepted M1 exact PR head**: `0db87a1a1feb54bf677533d88516d72f3bda73ec`
- **Accepted M1 merge main SHA**: `3e90bbd7eedca5f71c341ea91691b0cf2bc121ab`
- **Accepted M2 exact PR head**: `224e53814bc33e565189acd0b2c45866be32f2a0`
- **Accepted M2 merge main SHA**: `07875ef2c9f6784d54c23c2bb19b326d2ff6ed86`
- **Accepted M3 exact PR head**: `b4e79a00dc3677746a244a08c6fd36dfccba620c`
- **Accepted M3 merge main SHA**: `c97dfa2d79f81b7b0172833769a71164934a103e`
- **Accepted M4 exact PR head**: `e46f11cc9cccd7763cc8d6e7b3dbcd8907af934b`
- **Accepted M4 merge main SHA**: `d853f8b5fe248ee2e0fd0032f6e0ffccadc5f578`
- **Accepted M5 exact PR head**: `b13438d91ca13ac9a889bad4f31a2b33550533e9`
- **Accepted M5 merge main SHA**: `3f6eb40793991adba82c7d5b60920a5f60c80a04`
- **Accepted M6 exact PR head**: `08c047b35c55b693615d3bdf055a0250d838817a`
- **Accepted M6 merge main SHA**: `cbd8a1ef74ae55b5636b81ecbf757e50adb268da`
- **Accepted M7 exact PR head**: `c4de490bab6d1f3709cf7ce32c4d7b2212131fce`
- **Accepted M7 merge main SHA**: `5ec343a52d58e61b4c2354f7b05a9cf581c4c0d7`
- **Accepted M8 exact PR head**: `5fb86a99a2e98f237c0d516391128ef9a86bd500`
- **Accepted M8 merge main SHA**: `5748d33953c7b46abd945d682618a409c7b9125b`
- **Active Implementation Issue**: none
- **Active Implementation PR**: none
- **Selected Next Milestone**: M9 — Bounded PostgreSQL Restart Recovery
- **Human Review truthfulness item**: Issue #23 CLOSED / COMPLETED; PR #24 MERGED
- **Historical AWS work item**: Issue #15 CLOSED / NOT PLANNED; PR #16 CLOSED / NOT MERGED
- **Updated**: 2026-09-03
- **Final v1.0 Gate**: **PASS — FREEZE APPROVED**
- **Post-v1.0 Gate**: **M1 PASS / M2 PASS / M3 PASS / M4 PASS / M5 PASS / M6 PASS / M7 PASS / M8 PASS — M9 SELECTED**

---

# 1. Product Definition

**Asgard는 운영 로그와 이벤트를 영속적인 비동기 Job으로 처리하고, Kafka 기반 실행 흐름과 Local LLM 분석, 결과 저장, 실패 복구, 감사 및 관측 기능을 제공하는 Local-first AI Operations Platform이다.**

```text
Input / Log
  → Heimdall
  → Persistent Analysis Job
  → Kafka
  → Bifrost
  → Local AI (Ollama)
  → Result Event
  → Persistence
  → Operator / Metrics

Failure
  → FAILED / DLQ
  → Controlled Redrive
  → Audit
  → Retry
  → SUCCEEDED
```

Asgard v1.0의 중심 Proof는 **AI provider 수가 아니라 운영 가능한 AI Job lifecycle**이다.

Post-v1.0의 목적은 이 검증된 lifecycle을 무한 확장하는 것이 아니라, **기술 운영자가 단일 로컬/서버 환경에 재현 가능하게 설치하고, 비동기 Local AI Job을 실행·조회·복구·감사하며 시스템 상태를 이해할 수 있는 usable operational tool로 발전시키는 것**이다.

---

# 2. Frozen v1.0 Boundary

## Core Must Pass — COMPLETE
- Heimdall / Bifrost
- PostgreSQL / Kafka
- Local Ollama provider
- persistent Analysis Job lifecycle
- result persistence / idempotency boundary
- fail-closed local-first routing boundary
- DLQ / Redrive / Audit
- Auth / Rate Limit where used by the bounded workflow
- Prometheus / Grafana operating visibility
- minimal executable frontend boot shell only
- CI / E2E evidence
- buyer-facing truthfulness review at the final Human Review gate

## Explicitly Deferred / Not Required for v1.0
- AWS Bedrock / AWS OIDC / IAM role setup / real cloud-provider execution
- replacing AWS with OpenAI / Gemini / another cloud provider
- multi-provider routing expansion
- RAG as the primary Asgard Proof
- feedback / quality scoring / A-B testing / smart caching expansion
- advanced React admin dashboard
- HP AI Server reference deployment
- Kubernetes production / HA / autoscaling / multi-region
- Keycloak / Vault / enterprise secret-manager work
- full RBAC / multi-tenancy
- production SLA/SLO
- legal GDPR or security certification

Historical cloud code may remain in the repository. **Its existence does not make cloud execution a v1.0 requirement or accepted claim.**

The v1.0 boundary is permanently preserved as a frozen verified baseline. Post-v1.0 progression must not rewrite historical v1.0 PASS claims, accepted evidence, or non-claims merely to make a later milestone look stronger.

---

# 3. Frozen v1.0 Accepted Evidence

| Use case | Accepted evidence | Current |
|---|---|---|
| UC-01 Startup | PR #12; PostgreSQL/Kafka/Redis/Elasticsearch/Prometheus/Grafana/Heimdall/Bifrost/frontend reachability | **PASS** |
| UC-02 Real Local AI | PR #14 merge `ee24e6990d19c0be618baf1698bff275a8b27134`; run `32323663891`; artifact `9390712782` / `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da` | **PASS** |
| UC-03 Local-first Policy | PR #18 merge `a7e079872004c6dcf73cdf36d105aabde37fbb8d`; accepted head `b6fc2c2f15f0d65ba6f314525740a63cc42c24ce`; run `32945550180`; artifact `9598234317` / `sha256:94ce477579261ee28cd9bec30e17d2397628158b5ba85e3a8fa168cd44b32c01` | **PASS** |
| UC-04 Recovery | PR #20 merge `37c29223044100c216372d27169eba0c3c0a0dc0`; accepted head `4b3bf88b31ae7392004121817832b232f4cd8e21`; run `32967543925`; artifact `9606403831` / `sha256:a641015cdb0fa2cabebc49e27da456e93c4ecce5d4b7dff1ccb976604f00e2ec` | **PASS** |
| UC-05 Observability | PR #22 merge `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`; accepted head `e1509b7cefdb47a057c25051c16409b030c11dee`; run `33009550844`; artifact `9622043567` / `sha256:783c37b1bd7079edce01caa61e5ab767826d195cb4a3b800e87ee0cb0c1262a8` | **PASS** |
| Human Review | Issue #23 CLOSED; PR #24 merge `359b26e573e5da04b2d0ec406a56be7ecb508dbd`; CI `33371042786`; CI/CD `33371042762` | **PASS — HUMAN REVIEW PASSED** |

**ASGARD PROOF v1.0 CLOSED / FREEZE — HUMAN REVIEW PASSED.**

### v1.0 claim boundary
Supported: event-driven Java/Python AI operations architecture; persistent async Job lifecycle; Kafka request/result handoff; real local Ollama inference; result persistence; fail-closed Local-first routing; bounded FAILED/DLQ→Redrive→Audit→Retry→SUCCEEDED; duplicate redrive visibility; bounded Prometheus/Grafana lifecycle visibility.

Not verified: production readiness; enterprise-grade operational readiness; legal compliance certification; production SLA/SLO; stable latency/throughput/cost claims; Kubernetes/HA/multi-region; cloud-provider execution; full admin platform; unattended autonomous operations.

---

# 4. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | known non-fatal debt; touch only if a future accepted requirement fails on it |
| R-002 | broad Heimdall Checkstyle/build debt | pre-existing; no mass-fix without a required gate |
| R-003 | startup script / proven CI invocation drift | M1 closed the accepted bounded Linux path; broader convenience only when required |
| R-004 | README / historical docs may overclaim | README closed via Issue #23 / PR #24; historical docs non-authoritative |
| R-005 | hosted CPU Ollama latency variability | bounded generation only; no stable performance claims |
| R-006 | ingestion auto-analysis may create extra job | proof paths isolate target Job where required |
| R-007 | legacy AWS/Bedrock code remains | DEFER; not an automatic progression target |
| R-008 | duplicate routing generations | no refactor without a milestone requirement |
| R-009 | agent self-report | never substitute for executed evidence |
| R-010 | redrive audit pre-state correctness | CLOSED for accepted UC-04 (`FAILED / 0`) |
| R-011 | short-window Grafana delta/rate semantics | do not generalize into production observability claims |
| R-012 | M2 console bounded/read-only by default | recovery only under explicit M3 feature flag |
| R-013 | proof harness queue-order race | bounded harness isolation only; no autonomous-runtime guarantee |
| R-014 | Bifrost restart proof is one bounded single-node replay case | no HA/Kafka-outage/recovery-time generalization |
| R-015 | backup/restore was unverified after M5 | **CLOSED for one bounded M6 PostgreSQL backup/restore case only**; DR/PITR/RPO/RTO remain unverified |
| R-016 | M7 diagnostic snapshot proves one bounded read-only support bundle | no alerting, autonomous remediation, generic monitoring-platform, production monitoring/SLA/SLO claim |
| R-017 | M8 Kafka restart proof is one bounded persisted-request replay case | no multi-broker/HA/autonomous failover/recovery-time/production-durability generalization |

---

# 5. Work Item / PR Lifecycle

1. MASTER first.
2. Current repository / Issue / PR / executed evidence overrides stale checkpoint text and Scheduled Task self-report.
3. One bounded implementation/proof Issue at a time.
4. Active relevant PR before new work.
5. Define executable Acceptance Criteria before implementation.
6. RED → first concrete failure → smallest in-scope correction.
7. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
8. Close Issue only after accepted evidence exists.
9. Reconcile MASTER on `main` after merge.
10. Evaluate Milestone Acceptance before selecting another Issue.
11. Frozen accepted milestone becomes a preserved baseline slice; **FREEZE does not mean project development ends**.
12. After acceptance, return to Progression Review and select the next bounded milestone only when it has clear use/show/delivery value.
13. Do not manufacture work for activity.

---

# 6. Post-v1.0 Progression Contract

## Product Destination

> **A bounded, single-node Local AI Operations Tool that a technical operator can reproducibly deploy, use to submit and inspect asynchronous Local AI analysis jobs, recover supported failures, audit operator actions, and understand system health without requiring a cloud AI provider.**

Priority: reproducibility → reliability/recovery → operator usability/observability → delivery readiness → maintainability/security only when blocking use → new capability only when earlier axes cannot produce useful progress.

Do not automatically select AWS/Bedrock/OIDC/IAM, OpenAI/Gemini cloud expansion, Kubernetes/HA/autoscaling/multi-region, multi-tenancy, full RBAC/SSO, billing, autonomous operations, broad RAG, generic refactors, broad Checkstyle cleanup, or full admin-platform competition.

Disable/queue only for explicit user/product stop, repository archival/supersession, unsafe material product-direction decision, external WIP cap, or no useful bounded milestone remaining.

---

# 7. Accepted Post-v1.0 Milestones

## M1 — Local Reproduction & First Job — ACCEPTED / FROZEN
- Issue #25 CLOSED; PR #30 merged with expected-head guard.
- exact head `0db87a1a1feb54bf677533d88516d72f3bda73ec`; merge `3e90bbd7eedca5f71c341ea91691b0cf2bc121ab`.
- primary CI `33399015985`; M1 `33399015962`; UC-02 `33399016060`; UC-03 `33399016019`; UC-04 `33399015968`: SUCCESS.
- artifact `9760584618` / `sha256:f8011b67f5c49a87ddef93356295d403d37d4dc731b82811bfe087c2399c361`.
- bounded GitHub-hosted Linux path only; no macOS/Windows/stable-performance claim.

## M2 — Operator Console: Read-only Job Lifecycle — ACCEPTED / FROZEN
- Issue #31 CLOSED; PR #32 merged.
- exact head `224e53814bc33e565189acd0b2c45866be32f2a0`; merge `07875ef2c9f6784d54c23c2bb19b326d2ff6ed86`.
- M2 `33405406557`; primary CI `33405406555`; M1 `33405406603`; UC-02/03/04/05 all SUCCESS.
- artifact `9763096595` / `sha256:ff363841b4c4754870ab40a33f630284e39b3820123d503e847096ccc1e19b05`.
- bounded read-only console; not a generic/full admin dashboard.

## M3 — Controlled Recovery Operator Workflow — ACCEPTED / FROZEN
- Issue #33 CLOSED; PR #35 merged; draft PR #34 closed only due connector Draft→Ready failure.
- exact head `b4e79a00dc3677746a244a08c6fd36dfccba620c`; merge `c97dfa2d79f81b7b0172833769a71164934a103e`.
- M3 `33422708481`; primary CI `33422708448`; M1/M2/UC-02/03/04 all SUCCESS.
- artifact `9769683333` / `sha256:2c1bdfe47287dc3e88061259ee2d93f9b8025310721e3a2b66b7ae3fd05d6d78`.
- proves explicit reason/confirmation, redrive to SUCCEEDED, SUCCESS audit, duplicate SKIPPED without attempt inflation.
- no autonomous/background retry guarantee.

## M4 — Runtime Resilience: Bounded Bifrost Restart — ACCEPTED / FROZEN
- Issue #36 CLOSED; PR #38 merged; draft PR #37 closed only after repeated Draft→Ready connector failure.
- exact head `e46f11cc9cccd7763cc8d6e7b3dbcd8907af934b`; merge `d853f8b5fe248ee2e0fd0032f6e0ffccadc5f578`.
- M4 `33444318573`; primary CI `33444318725`: SUCCESS.
- artifact `9777540907` / `sha256:d1a078d52d9fb70a3c9931f6e5065e2fd4220f863fffbf5acc1e1ba07d020ea4`.
- proves one persisted RUNNING Job survives bounded actual Bifrost SIGKILL/restart via same consumer group to SUCCEEDED/resultRef=1.
- no Kafka outage, HA, autonomous recovery, recovery-time, distributed-delivery generalization.

## M5 — Single-node Delivery Handoff — ACCEPTED / FROZEN
- Issue #39 CLOSED; PR #40 merged.
- exact head `b13438d91ca13ac9a889bad4f31a2b33550533e9`; merge `3f6eb40793991adba82c7d5b60920a5f60c80a04`.
- M5 `33652535194`; primary CI `33652535236`; M1 `33652535181`; Real Local AI `33652535237`: SUCCESS.
- artifact `9855507091` / `sha256:f26aa953bcb5a855bc4f628ec1edd56f7e61a750a432ed0d2e4d12a7fbc09683`.
- repository-owned Linux handoff, prerequisites/config ownership, retained-session cleanup metadata/troubleshooting.
- M5 explicitly left backup/restore NOT VERIFIED; M6 later closed one bounded case.

## M6 — Persisted-state Backup/Restore Proof — ACCEPTED / FROZEN

### Accepted Scope
- one bounded single-node PostgreSQL backup/restore case for Asgard-owned Job/result/audit state;
- create real accepted Local-first persisted state;
- stop proof-owned writers before snapshot;
- produce concrete custom-format `pg_dump` backup artifact;
- restore into a newly created proof-owned database rather than source `heimdall` database;
- compare target Job identity/status/result_ref/attempt_count plus referenced result presence and target redrive-audit count before/after restore.

### Actually Changed
- added `scripts/m6-backup-restore-proof.sh`;
- added `.github/workflows/v11-m6-backup-restore.yml`;
- no product runtime, schema, Kafka/Bifrost/Heimdall behavior, cloud provider, HA, or DR infrastructure change.

### Actually Executed / Verified
- Issue #41 — **CLOSED / COMPLETED**;
- PR #42 — **SQUASH MERGED** with expected-head guard;
- accepted exact head `08c047b35c55b693615d3bdf055a0250d838817a`;
- merge main SHA `cbd8a1ef74ae55b5636b81ecbf757e50adb268da`;
- M6 Backup Restore Proof run `33664446061`: **SUCCESS**;
- artifact `9860123355`, digest `sha256:d9e7bb833ed1eaa265baa19bead70b528762c0939160e17c30013385be7c668c`;
- primary CI and Real Local AI regression independently GREEN on the accepted exact head;
- Bifrost build/test and Dependency Security Check GREEN;
- broad CI/CD remained RED first at `Build & Test Heimdall → Build with Gradle`, retained as known pre-existing R-002 debt rather than silently called GREEN.

### Limitations / Non-claims
- one proof-owned single-node PostgreSQL case only;
- no continuous backup, PITR, disaster-recovery certification, HA, Kubernetes volume recovery, RPO/RTO, off-site/cloud durability, production retention/encryption policy, or production-operations claim;
- no AWS/Bedrock/OIDC/cloud AI execution claim.

### Milestone Acceptance
One identifiable persisted Asgard Job/result state was produced through the accepted Local-first path, snapshotted with an explicit PostgreSQL backup artifact, restored into a distinct proof-owned database, and the bounded persisted identity/status/result/audit contract was independently verified on the exact PR head. **M6 PASS / ACCEPTED / FROZEN.**

## M7 — Operator Diagnostic Snapshot — ACCEPTED / FROZEN

### Accepted Scope
- one bounded read-only repository-owned operator diagnostic snapshot for the accepted single-node Local-first proof environment;
- capture supported service health/reachability, one identifiable persisted Job state, bounded lifecycle metrics, proof/session correlation metadata, and sanitized bounded recent Heimdall/Bifrost log evidence;
- emit machine-readable JSON and human-readable Markdown;
- fail closed if known proof credentials or synthetic secrets leak into the evidence;
- no mutation/recovery action in the snapshot path.

### Actually Changed
- added `scripts/operator-diagnostic-snapshot.sh`;
- added `.github/workflows/v11-m7-operator-diagnostic.yml`;
- bounded M7 verification was also wired through the registered M1 proof workflow so exact-head execution did not depend on default-branch registration;
- no product runtime, persistence schema, cloud-provider path, HA, alerting, or autonomous remediation change.

### Actually Executed / Verified
- Issue #43 — **CLOSED / COMPLETED**;
- PR #44 — **SQUASH MERGED** with expected-head guard;
- accepted exact head `c4de490bab6d1f3709cf7ce32c4d7b2212131fce`;
- merge main SHA `5ec343a52d58e61b4c2354f7b05a9cf581c4c0d7`;
- M7 Operator Diagnostic Snapshot run `33693038558`: **SUCCESS**;
- Local-first proof, snapshot capture, M7 evidence-contract verification, artifact upload and cleanup all GREEN;
- artifact `9870849376`, digest `sha256:4961998526b32c5af5cf7b39f8df9159e2cb7c13bdb71743a5116e5bec5ec30b`;
- primary CI `33693038562`, M1 `33693038581`, Real Local AI `33693038595`, M5 handoff `33693038583`: SUCCESS;
- Bifrost build/test and Dependency Security Check GREEN;
- broad CI/CD `33693038579` remained RED first at `Build & Test Heimdall → Build with Gradle`, retained as known pre-existing R-002 debt rather than silently called GREEN.

### Limitations / Non-claims
- one bounded support/handoff diagnostic snapshot only;
- no alerting platform, autonomous remediation, distributed tracing rollout, cloud observability, HA/Kubernetes monitoring, production monitoring certification, stable SLA/SLO, or generic admin/observability-platform claim;
- no AWS/Bedrock/OIDC/cloud AI execution claim.

### Milestone Acceptance
One repository-owned read-only command produced a contract-checked, human- and machine-readable diagnostic snapshot against an actually executed accepted Local-first proof session, including non-empty correlation identifiers and successful artifact publication. **M7 PASS / ACCEPTED / FROZEN.**

## M8 — Bounded Kafka Restart Recovery — ACCEPTED / FROZEN

### Accepted Scope
- one proof-owned single-node Kafka restart case using the accepted Local-first path;
- persist one identifiable target Job and publish its request before Bifrost consumer startup;
- actually stop the proof-owned Kafka broker and independently verify it is unavailable;
- restart the same broker/container with the same bounded storage boundary;
- start Bifrost after broker restart and verify the persisted request reaches SUCCEEDED with exactly one accepted persisted result identity;
- contract-check bounded attempt/audit/result state and publish evidence.

### Actually Changed
- added `.github/workflows/v11-m8-kafka-restart.yml` only;
- no product runtime, schema, Kafka architecture, cloud provider, HA, Kubernetes, or persistence redesign.

### Actually Executed / Verified
- Issue #45 — **CLOSED / COMPLETED**;
- PR #46 — **SQUASH MERGED** with expected-head guard;
- accepted exact head `5fb86a99a2e98f237c0d516391128ef9a86bd500`;
- merge main SHA `5748d33953c7b46abd945d682618a409c7b9125b`;
- M8 Kafka Restart Recovery run `33697888620`: **SUCCESS**;
- actual broker stop/unavailable check, same-broker restart/readiness, Bifrost post-restart processing, M8 evidence contract, artifact upload, and cleanup all GREEN;
- artifact `9872527893`, digest `sha256:0b7827a743fc08e9e583c904c848ca622a02137d487bca4b63d1e6eaef3be486`;
- primary CI `33697887580`: **SUCCESS**;
- CI/CD `33697888516`: Bifrost build/test and Dependency Security Check GREEN; first material RED remained `Build & Test Heimdall → Build with Gradle → :heimdall:checkstyleMain` with 41 files / 111 warnings / 2 info, matching known pre-existing R-002 and unrelated to the one-file M8 workflow diff.

### Limitations / Non-claims
- one bounded single-node Kafka broker restart and persisted-request replay case only;
- no multi-broker Kafka, replication/cluster redesign, HA, autonomous failover, cross-node recovery, Kubernetes, recovery-time guarantee, SLA/SLO, stable performance, or production durability claim;
- no AWS/Bedrock/OIDC/cloud AI execution claim.

### Milestone Acceptance
One identifiable persisted Local-first Job request was published before an actual proof-owned Kafka interruption, the same broker/storage boundary was restarted, and the request then completed through Bifrost to a single persisted accepted result under an independently verified exact-head workflow. **M8 PASS / ACCEPTED / FROZEN.**

---

# 8. M9 — Bounded PostgreSQL Restart Recovery — SELECTED

## Progression Review Decision
M4 and M8 now cover bounded Bifrost-process and Kafka-broker restart behavior, while M6 proves offline backup/restore into a distinct proof-owned database. A remaining direct reliability/handoff gap is the primary persistence service itself: the accepted progression does not yet prove that one already persisted Local-first Job/result remains truthful and queryable after an actual restart of the proof-owned PostgreSQL container using the same data volume.

This is narrower than HA/DR and requires no product-direction decision. It has concrete operator value because a single-node delivery must tolerate a routine bounded database service restart without silently losing accepted state.

## Selected Scope
- one proof-owned single-node PostgreSQL restart case using the existing `postgres-data` persistence boundary;
- create one identifiable accepted Local-first Job/result state before interruption;
- stop the proof-owned PostgreSQL container and independently confirm database unavailability;
- restart the same PostgreSQL service using the same volume, then prove readiness;
- verify the pre-existing target Job identity/status/result_ref/attempt_count and referenced result remain present and consistent after restart;
- verify supported Heimdall read/query health resumes after database recovery;
- make only the smallest same-gap proof/runtime correction if a milestone-caused defect is demonstrated;
- no database architecture redesign.

## Executable Acceptance
1. Exact-head execution establishes one identifiable persisted target Job/result through the accepted Local-first path.
2. The proof actually stops the proof-owned PostgreSQL container and independently confirms the database is unavailable before restart.
3. The same database service and same proof-owned data volume are restarted; no substitute database or restore-from-backup shortcut is used.
4. PostgreSQL readiness returns and the exact pre-interruption Job identity/status/result_ref/attempt_count plus referenced result presence remain consistent.
5. Supported Heimdall health/read behavior resumes against the recovered database.
6. Relevant primary regression/security gates are independently GREEN; broad Heimdall R-002 remains separately classified unless this milestone changes that code.
7. No HA, replication/failover, PITR, DR, RPO/RTO, SLA/SLO, production durability, Kubernetes, or cloud-execution claim is introduced.

## Stop Condition
Stop after one bounded same-volume PostgreSQL restart/recovery case is independently executed and verified. Do not expand into streaming replication, Patroni, managed databases, Kubernetes operators, production DR, performance tuning, or cloud-provider work.

**Current: SELECTED — ISSUE NOT YET OPEN**

---

# 9. Current Post-v1.0 Progression Checkpoint

## Decision
- v1.0 remains **PASS / FREEZE / HUMAN REVIEW PASSED**;
- M1–M8 are **PASS / ACCEPTED / FROZEN**;
- M8 exact head `5fb86a99a2e98f237c0d516391128ef9a86bd500`, PR #46 merge `5748d33953c7b46abd945d682618a409c7b9125b`, Issue #45 CLOSED / COMPLETED;
- M8 run `33697888620`: SUCCESS; artifact `9872527893` / `sha256:0b7827a743fc08e9e583c904c848ca622a02137d487bca4b63d1e6eaef3be486`;
- exact-head primary CI `33697887580` SUCCESS; Bifrost build/test and Dependency Security Check GREEN;
- broad CI/CD `33697888516` remained RED first at Heimdall `:heimdall:checkstyleMain`, demonstrably the accepted pre-existing R-002 debt rather than an M8 workflow regression;
- M8 non-claims remain multi-broker/HA/autonomous failover/cross-node recovery/recovery-time/SLA-SLO/production durability/cloud execution;
- Progression Review selected exactly one next milestone: **M9 — Bounded PostgreSQL Restart Recovery**.

## Exact Next Action
**Open exactly one M9 Issue for a bounded proof-owned same-volume PostgreSQL restart/recovery case. Reuse the accepted Local-first proof path; establish one persisted target Job/result before interruption, actually stop/restart PostgreSQL with the same data volume, and verify persisted identity/result plus supported Heimdall read health after recovery. Keep HA/replication/PITR/DR/RPO-RTO/SLA-SLO/Kubernetes/cloud work out of scope.**