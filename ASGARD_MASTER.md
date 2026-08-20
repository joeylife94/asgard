# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B4 — UC-01 Full Core-Service Startup / Health Verification
- **Batch Result**: IN PROGRESS
- **Status**: PR #12 OPEN — Redis auth boundary corrected and verified past; Bifrost launch correction under exact-head execution
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **P0-B3 merge**: `74da74c71625b9bca111b2e1c1bbbb933c82077a`
- **Issue #11**: OPEN — `P0-B4: verify UC-01 full core-service startup and health`
- **PR #12**: OPEN — `test: verify UC-01 full core-service startup and health`
- **Last executed RED head**: `abce79e183894f117fe0cc6fb590298a58813ee8`
- **Current PR #12 head**: `1f3459dd5e12bf85b5eccfe41d1eca05bbf6231b`
- **Current exact-head CI**: `CI 32320165761` IN PROGRESS; `CI/CD Pipeline 32320165695` QUEUED at reconciliation time
- **Updated**: 2026-08-20
- **Final v1.0 Gate**: **Human Review Required**

---

# 1. Product Definition

**Asgard는 기업 로그/운영 데이터를 Local LLM 또는 Cloud LLM으로 선택적으로 분석하고, Kafka 기반 비동기 Job과 장애 복구·관측 기능을 제공하는 Hybrid AI Operations Platform이다.**

```text
Input → Heimdall → Analysis Job → Kafka → Bifrost
      → Routing ─┬→ Local AI
                 └→ Cloud AI
      → Result / DB → Dashboard / Operator

FAILED → DLQ → Redrive → Audit → Retry → SUCCEEDED
```

---

# 2. Frozen v1.0 Boundary

## Core Must Pass
- Heimdall / Bifrost
- PostgreSQL / Kafka
- Local AI Provider
- Optional Cloud AI Provider
- Hybrid Routing
- Analysis Job / Persistence / Idempotency
- DLQ / Redrive / Audit
- Auth / Rate Limit
- Prometheus / Grafana
- Minimal React Dashboard
- CI / E2E Demo

## Explicit Non-Goals
- Multi-tenancy completion
- HA / multi-region
- Kubernetes production
- autoscaling
- full RBAC / enterprise secret manager
- production SLA/SLO
- security certification / legal GDPR certification
- large admin UI
- experimental feature expansion before Core completion

---

# 3. Required Use Cases

| UC | Goal | PASS 기준 | Current |
|---|---|---|---|
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy | IN PROGRESS — infra + Heimdall proven on latest executed head; Bifrost next boundary under correction |
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED | PENDING |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 | PENDING |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED | PENDING |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 | PENDING |

---

# 4. Closed Phase 0 Evidence

## P0-B1 — PASS / MERGED
- PR #4 merged at `fa3f129783387fbeafae537e8a22b4629faf6d42`.
- primary Heimdall + Bifrost unit job GREEN.
- secondary Bifrost install/lint/pytest/coverage GREEN.
- dependency security GREEN.
- Heimdall `checkstyleMain` debt classified pre-existing: **41 files / 109 warnings / 2 info**.

## P0-B2 — PASS / MERGED
- Issue #6 CLOSED; PR #7 merged at `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`.
- minimal four-file frontend boot tree restored.
- exact-head production frontend build GREEN.

## P0-B3 — PASS / MERGED
- Issue #8 CLOSED.
- PR #9 proof harness merged at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`.
- PR #10 merged at `74da74c71625b9bca111b2e1c1bbbb933c82077a`.
- `CI/CD Pipeline` run `32279712933`: SUCCESS.
- `CI` run `32279712788`: SUCCESS.
- Vite dev-server/root reachability: GREEN.
- root `build-all.ps1 -SkipTests` reaches/completes Frontend: GREEN.
- `-SkipTests` uses `:heimdall:assemble`; normal build remains `:heimdall:build`.

---

# 5. Active Phase 0 Slice — P0-B4

## Work Item
- **Issue #11**: OPEN
- **PR #12**: OPEN
- **Branch**: `agent/p0-b4-uc01-core-health-proof`

## Goal
Execute the actual core stack and collect concrete service readiness/reachability evidence for UC-01.

## In Scope
- reproducible PR-visible proof runtime.
- Heimdall / Bifrost health.
- PostgreSQL / Kafka readiness.
- Frontend root reachability in the full-stack job.
- Prometheus / Grafana host `3001` reachability.
- Redis readiness because current startup contract configures Redis.
- Elasticsearch readiness because current Heimdall dev startup contract enables Elasticsearch.
- only minimum product/config/proof corrections justified by executed startup evidence.

## Out of Scope
- UC-02/03/04/05 behavior.
- UI expansion.
- README hardening.
- broad Heimdall Checkstyle cleanup.
- unrelated infrastructure.

## Executed Failure Sequence

### A. Initial runtime — missing Elasticsearch
- PostgreSQL, Kafka, Redis, Prometheus and Grafana `3001` readiness proved.
- Heimdall failed because enabled Elasticsearch access hit `localhost:9200` with connection refused.
- correction: start repository Elasticsearch and prove `_cluster/health`.

### B. Elasticsearch-corrected runtime — missing gRPC authentication reader
Head `d2d96f47a394e7ce4cc6a798a368b6b83cd28a7a`, `CI` run `32291645192`:
- infrastructure GREEN.
- Heimdall RED during context startup because no `GrpcAuthenticationReader` bean existed.
- duplicate PostgreSQL `idx_severity` was non-fatal and remains HOLD.

### C. Rejected correction — remove gRPC starter
Head `f7abfa7e565711bf7a39539c7865293532905828`, `CI` run `32296242418`:
- `:heimdall:compileJava` failed because `GrpcServerConfig.java` directly requires starter classes.
- removal rejected; starter restored.

### D. Explicit gRPC authentication reader — executed RED
Head `ae306fad143d5be1f71d6d25354f6af3c7a7d344`, `CI` run `32296456441`:
- infrastructure GREEN.
- first application boundary was Heimdall gRPC bind failure: Prometheus host `9090` already occupied the port.
- correction: dev-profile gRPC isolated to `${GRPC_PORT:9091}`.

### E. Dev gRPC isolation — executed RED on Redis health
Head `279261aad0046df8cce59e5f7fabf242921fdb21`:
- `CI` run `32315948212`: **FAILURE**.
- `CI/CD Pipeline` run `32315948241`: **FAILURE**.
- Phase 0 preflight: GREEN.
- frontend dev-root job: GREEN.
- unit tests: GREEN.
- default Windows build path: GREEN.
- infrastructure proof: PostgreSQL/Kafka/Redis/Elasticsearch/Prometheus/Grafana GREEN.
- Heimdall application successfully started Tomcat on `8080` and gRPC on `9091`, but `/actuator/health` repeatedly returned `503` because Spring Boot's actual `RedisConnectionFactory` had no password.
- artifact error: `RedisCommandExecutionException: NOAUTH HELLO ...`.

Correction justified by execution:
- existing env contract already supplies `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`.
- `application.yml` exposed those only under `heimdall.data.redis`, while Spring Boot auto-configured Redis uses `spring.data.redis.*`.
- dev profile now binds `spring.data.redis.host/port/password` to the existing `REDIS_*` environment contract.

### F. Redis binding correction — executed RED; Heimdall now GREEN
Head `abce79e183894f117fe0cc6fb590298a58813ee8`, `CI` run `32319692632`:
- Phase 0 preflight: GREEN.
- frontend dev-root: GREEN.
- unit tests Heimdall + Bifrost: GREEN.
- default Windows build path: GREEN.
- infrastructure readiness: GREEN.
- artifact proves Heimdall:
  - Tomcat started on `8080`.
  - gRPC started on `9091`.
  - `/actuator/health` produced `{"status":"UP","groups":["liveness","readiness"]}`.
- **first remaining Issue #11 blocker promoted from HOLD**: Bifrost did not start.
- exact Bifrost process output:

```text
Usage: python -m bifrost.main serve [OPTIONS]
Error: Got unexpected extra arguments (127.0.0.1 8000)
```

The verifier checks Heimdall first, then Bifrost, so this run proves Bifrost is now the first concrete remaining acceptance boundary. Frontend full-stack verification remains after Bifrost.

### G. Current correction — use Bifrost serve defaults
Current PR #12 head: `1f3459dd5e12bf85b5eccfe41d1eca05bbf6231b`.

Smallest correction justified by executed evidence:
- proof harness changed only Bifrost launch from `python -m bifrost.main serve --host 127.0.0.1 --port 8000` to `python -m bifrost.main serve`.
- repository CLI already defines `serve` defaults as host `0.0.0.0`, port `8000`; no product/UI/UC-02 expansion.
- no claim that Bifrost is healthy until exact-head execution completes.

Current PR-visible execution at reconciliation time:
- `CI` run `32320165761`: IN PROGRESS.
- `CI/CD Pipeline` run `32320165695`: QUEUED.

## Acceptance Criteria
- [x] reviewable checkout/configuration/proof command.
- [x] actual PR-visible core-stack execution exists.
- [x] Heimdall health verified on exact executed head `abce79e...`.
- [ ] current exact-head Bifrost health verified in full-stack job.
- [x] PostgreSQL readiness verified.
- [x] Kafka readiness verified.
- [ ] current exact-head Frontend root verified in full-stack job.
- [x] Prometheus reachability verified.
- [x] Grafana `3001` reachability verified.
- [x] Redis readiness verified.
- [x] Elasticsearch readiness verified.
- [x] no out-of-scope expansion.

## Result
**IN PROGRESS — Redis authentication is now correctly bound in dev and executed evidence proves Heimdall `UP`. The next first concrete boundary is Bifrost launch; the minimal serve-default correction is under exact-head execution. P0-B4 is not PASS.**

---

# 6. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 |
| E-002 | P0-B1 bounded repair | VERIFIED / MERGED | PR #4 |
| E-003 | Phase 0 runtime versions | VERIFIED | Java 21 / Python 3.11 / Node 20 / npm 10 / Docker 28 |
| E-004 | Heimdall checkstyle debt | VERIFIED RED / PRE-EXISTING | 41 / 109 / 2 |
| E-005 | P0-B2 frontend repair | VERIFIED / MERGED | PR #7 |
| E-006 | P0-B2 frontend production build | VERIFIED GREEN | PR #7 |
| E-016 | Frontend dev-server root reachability | VERIFIED GREEN | PR #9 |
| E-017 | Root default SkipTests build path | VERIFIED GREEN / MERGED | PR #10 |
| E-018 | Real Local AI E2E | PENDING | |
| E-019 | Local vs Cloud Routing | PENDING | |
| E-020 | DLQ → Redrive → Success | PENDING | |
| E-021 | Grafana live metrics | PENDING | |
| E-022 | Final Demo | PENDING | |
| E-023 | HP AI Server reference run | PENDING | |
| E-024 | UC-01 full core-stack health | IN PROGRESS | PR #12 |
| E-025 | P0-B4 infra readiness | VERIFIED GREEN | Postgres/Kafka/Redis/Elasticsearch/Prometheus/Grafana |
| E-026 | Missing Elasticsearch dependency | VERIFIED RED / SUPERSEDED | initial PR #12 |
| E-028 | Missing gRPC authentication reader | VERIFIED RED / SUPERSEDED | `32291645192` |
| E-029 | gRPC starter removal | VERIFIED RED / REJECTED | compile failure |
| E-030 | Explicit gRPC authentication reader | VERIFIED PAST BLOCKER | reached gRPC server start |
| E-031 | gRPC/Prometheus `9090` collision | VERIFIED RED / SUPERSEDED | artifact `32296456441` |
| E-032 | Dev gRPC port isolation | VERIFIED PAST BLOCKER | gRPC starts on `9091` |
| E-033 | Redis auth/config mismatch | VERIFIED RED / SUPERSEDED | run `32315948212` |
| E-034 | Dev Spring Redis binding | VERIFIED PAST BLOCKER | head `abce79e...` Heimdall health UP |
| E-035 | Heimdall full-stack health | VERIFIED GREEN | artifact `32319692632` |
| E-036 | Bifrost proof launch args | VERIFIED RED | artifact `32319692632` |
| E-037 | Bifrost serve-default correction | PUSHED / EXECUTION PENDING | head `1f3459d...` |

---

# 7. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | Heimdall dev startup required Elasticsearch | included/proven ready in P0-B4 harness |
| R-002 | duplicate `idx_severity` schema index name | HOLD; non-fatal in executed runs; fix only if future evidence makes it blocker |
| R-003 | broad Heimdall checkstyle debt | no mass-fix in P0-B4 |
| R-004 | startup banner is not health proof | endpoint/readiness evidence required |
| R-005 | anonymous gRPC reader may be inappropriate for future real gRPC product endpoints | replace with explicit policy when actual gRPC endpoints exist |
| R-006 | gRPC/Prometheus dev port collision | SUPERSEDED; gRPC proven on `9091` |
| R-007 | Bifrost explicit host/port CLI invocation rejected | ACTIVE correction uses repository `serve` defaults; execution pending |
| R-008 | README overclaim / Grafana port drift | proof-hardening later |
| R-009 | fallback-only E2E risk | real-model proof required later |
| R-010 | agent self-report | never PASS without executed evidence |

---

# 8. Work Item / PR Lifecycle

1. MASTER first.
2. Active focused PR first.
3. One active Issue by default.
4. Same-gap corrections remain in same Issue/PR.
5. RED → first concrete failure → smallest in-scope fix.
6. Exact-head GREEN + bounded diff + clean review/security → merge expected-head.
7. Issue closes only after acceptance + merge.
8. Reconcile MASTER on main before new Issue.
9. Human Review remains final v1.0 gate only.

---

# 9. Current Checkpoint

## Result
**P0-B1 PASS / P0-B2 PASS / P0-B3 PASS / P0-B4 IN PROGRESS.**

## What Changed
- reconciled stale `279261aad...` RUNNING state to executed FAILURE.
- downloaded/inspected run `32315948212` core-health artifact and proved Redis authentication was the first blocker after gRPC port isolation.
- bound Spring Boot dev Redis properties to the existing `REDIS_*` environment contract.
- executed head `abce79e...` proved Heimdall health GREEN and promoted the prior Bifrost CLI observation from HOLD to the first concrete blocker.
- changed only the proof launch to `python -m bifrost.main serve` so the CLI's existing default host/port are used.
- current PR #12 head is `1f3459dd5e12bf85b5eccfe41d1eca05bbf6231b` with exact-head workflows started.

## What Was Executed
- `CI` `32315948212`: FAILURE on head `279261aad...`; infrastructure GREEN, Heimdall RED with Redis `NOAUTH` health failure.
- `CI/CD Pipeline` `32315948241`: FAILURE on head `279261aad...`.
- `CI` `32319692632`: FAILURE on head `abce79e...`; preflight/frontend-dev/unit/default-build GREEN, infra GREEN, Heimdall health GREEN, Bifrost launch RED.
- core-health artifact `9389420201` inspected: `p0-b4-heimdall-health.json` = UP; `p0-b4-bifrost.log` = unexpected explicit host/port arguments.
- branch corrections committed: `abce79e183894f117fe0cc6fb590298a58813ee8`, then `1f3459dd5e12bf85b5eccfe41d1eca05bbf6231b`.

## What Was Not Verified
- current-head Bifrost health after serve-default correction.
- current-head Frontend root in the full-stack job.
- current-head final workflow conclusions/review/security state.
- real Local AI E2E, routing, recovery, live metrics, reference deployment, final demo.

## Remaining Risks
- Bifrost may expose another bounded startup/configuration defect after the invocation correction.
- duplicate `idx_severity` remains HOLD because it has stayed non-fatal.
- root startup script behavior is not treated as health evidence; P0-B4 requires endpoint proof.

## NEXT
**Inspect PR #12 exact-head `1f3459dd5e12bf85b5eccfe41d1eca05bbf6231b` runs `32320165761` and `32320165695`. RED → inspect only the first concrete Issue #11-scoped failure and apply the smallest justified correction. Fully GREEN Issue #11 acceptance + bounded diff + clean review/security → merge PR #12 with expected-head guard, ensure Issue #11 closes only after acceptance/merge, then reconcile MASTER on `main` and re-evaluate UC-01/Phase 0 closure before any new Issue.**