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
- **Status**: PR #12 OPEN — EXPLICIT gRPC AUTH READER CORRECTION PUSHED; EXACT-HEAD CI RUNNING
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **P0-B3 merge**: `74da74c71625b9bca111b2e1c1bbbb933c82077a`
- **Issue #11**: OPEN — `P0-B4: verify UC-01 full core-service startup and health`
- **PR #12**: OPEN — `test: verify UC-01 full core-service startup and health`
- **Initial tested PR #12 head**: `e874550e018e89b889ae9b3a7b6a6eb1542e2e63`
- **Elasticsearch-corrected head**: `d2d96f47a394e7ce4cc6a798a368b6b83cd28a7a`
- **Rejected gRPC dependency-removal head**: `f7abfa7e565711bf7a39539c7865293532905828`
- **Current PR #12 head**: `ae306fad143d5be1f71d6d25354f6af3c7a7d344`
- **Current exact-head CI**: `CI 32296456441` + `CI/CD Pipeline 32296456440` — RUNNING
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
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy | IN PROGRESS — infra including Elasticsearch proven; Heimdall gRPC security startup correction under exact-head execution |
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

## Initial Exact-Head Evidence — `e874550...`

`CI` run `32290803193`, core-health job `96190902370`:
- bootJar/dependency preparation: GREEN.
- PostgreSQL: GREEN, attempt 2.
- Kafka: GREEN, attempt 2.
- Redis: GREEN, attempt 1.
- Prometheus: GREEN, attempt 1.
- Grafana `/api/health` on `3001`: GREEN, attempt 1.
- application launch step: executed.
- Heimdall `/actuator/health`: RED after 60 attempts.

Captured Heimdall log proved Spring/Tomcat/JPA/PostgreSQL initialization proceeded, then application-context startup aborted because the enabled Elasticsearch repository/service attempted `localhost:9200` and received `Connection refused`.

## Elasticsearch Correction / Executed Evidence — `d2d96f47...`

Changed only the Issue #11 proof harness:
- existing Compose `elasticsearch` service added to infrastructure startup.
- explicit readiness loop added for `http://127.0.0.1:9200/_cluster/health` before Heimdall startup.

Exact-head `CI` run `32291645192`: **FAILURE**.
Supporting `CI/CD Pipeline` run `32291645245`: **FAILURE**.

Core-health job evidence after adding Elasticsearch:
- boot/dependency preparation: GREEN.
- PostgreSQL: GREEN.
- Kafka: GREEN.
- Redis: GREEN.
- Elasticsearch `_cluster/health`: GREEN.
- Prometheus: GREEN.
- Grafana `3001`: GREEN.
- Heimdall `/actuator/health`: RED after 60 attempts.

The fatal Heimdall startup error was no longer Elasticsearch. Application startup advanced through PostgreSQL/JPA, then `GrpcServerSecurityAutoConfiguration` failed because no `GrpcAuthenticationReader` bean exists:

```text
BeanCreationException
→ shadedNettyGrpcServerFactory
→ GrpcServerSecurityAutoConfiguration
→ authenticatingServerInterceptor
→ No qualifying bean of type GrpcAuthenticationReader
→ APPLICATION FAILED TO START
```

The duplicate PostgreSQL `idx_severity` DDL observation also appeared, but Hibernate continued past it and the later gRPC failure terminated startup. Therefore `idx_severity` remains HOLD and is not the current blocker.

## Rejected Correction / Executed Evidence — `f7abfa7...`

First attempt removed `net.devh:grpc-spring-boot-starter` after repository search did not surface active gRPC service/client implementations.

Exact-head `CI` run `32296242418` then provided immediate negative evidence:
- Phase 0 frontend preflight: GREEN.
- frontend dev root: GREEN.
- Heimdall unit job: RED at `:heimdall:compileJava`.
- compile error proved `heimdall/src/main/java/com/heimdall/config/GrpcServerConfig.java` directly imports/uses `io.grpc.ServerInterceptor` and `GrpcGlobalServerInterceptor`.

Therefore dependency removal was rejected and the starter was restored. This failed attempt is retained as evidence; it is not the current correction.

## Current Correction — `ae306fad...`

`GrpcServerConfig.java` was inspected directly. It defines a global gRPC logging interceptor but no authentication reader. The grpc-spring implementation requires a `GrpcAuthenticationReader` when its Spring Security integration is active.

Smallest correction now under execution:
- restored the gRPC starter required to compile the existing interceptor configuration.
- added an explicit `GrpcAuthenticationReader` bean using `AnonymousAuthenticationReader("heimdall-grpc-anonymous")`.
- the bean documents that no actual gRPC service is currently implemented and must be replaced together with a real service authentication policy if gRPC product endpoints are introduced.
- no web/JWT security weakening, UI, README, UC-02 behavior or Checkstyle changes.

Current PR-visible exact-head execution:
- `CI` run `32296456441`: RUNNING.
- `CI/CD Pipeline` run `32296456440`: RUNNING.
- no PASS is recorded until current exact-head runtime completes.

### Separate Observation — HOLD
Duplicate PostgreSQL index-name error/warning for `idx_severity` remains recorded but not authorized for proactive repair. Address only if a future exact-head run proves it is the next concrete P0-B4 blocker.

## Acceptance Criteria
- [x] reviewable checkout/configuration/proof command.
- [x] actual PR-visible core-stack execution exists.
- [ ] current exact-head Heimdall health verified.
- [ ] current exact-head Bifrost health verified in full-stack job.
- [x] PostgreSQL readiness verified.
- [x] Kafka readiness verified.
- [ ] current exact-head Frontend root verified in full-stack job.
- [x] Prometheus reachability verified.
- [x] Grafana `3001` reachability verified.
- [x] Redis readiness verified.
- [x] Elasticsearch readiness verified on `d2d96f47...`.
- [x] no out-of-scope expansion.

## Result
**IN PROGRESS — post-Elasticsearch runtime exposed missing gRPC authentication-reader configuration. An over-broad dependency-removal attempt was rejected by compile evidence; the starter is restored and the narrow explicit-reader correction is now executing. P0-B4 is not PASS.**

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
| E-025 | P0-B4 infra readiness | VERIFIED GREEN | Postgres/Kafka/Redis/Prometheus/Grafana |
| E-026 | Missing Elasticsearch dependency failure | VERIFIED RED / SUPERSEDED | initial PR #12 run |
| E-027 | Elasticsearch readiness/correction | VERIFIED GREEN | head `d2d96f47...` |
| E-028 | Heimdall gRPC security startup failure | VERIFIED RED | run `32291645192` |
| E-029 | gRPC starter removal | VERIFIED RED / REJECTED | compile failure on `f7abfa7...` |
| E-030 | Explicit gRPC authentication reader | PUSHED / EXECUTION PENDING | head `ae306fad...` |

---

# 7. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | Heimdall dev startup required Elasticsearch | Elasticsearch now included/proven ready in P0-B4 harness |
| R-002 | duplicate `idx_severity` schema index name observed | HOLD; non-fatal on `d2d96f47...`; fix only if future run proves blocker |
| R-003 | broad Heimdall checkstyle debt | no mass-fix in P0-B4 |
| R-004 | startup banner is not health proof | endpoint/readiness evidence required |
| R-005 | gRPC security auto-config lacked an authentication reader | explicit reader under exact-head execution; anonymous policy is temporary until real gRPC services exist |
| R-006 | README overclaim / Grafana port drift | proof-hardening later |
| R-007 | fallback-only E2E risk | real-model proof required later |
| R-008 | agent self-report | never PASS without executed evidence |

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
- `d2d96f47...` runtime failure reconciled: Elasticsearch GREEN; fatal blocker moved to gRPC security authentication-reader creation.
- duplicate `idx_severity` confirmed non-fatal in that execution and kept on HOLD.
- first gRPC-starter removal attempt was executed and rejected because `GrpcServerConfig.java` requires starter classes to compile.
- starter restored and explicit `GrpcAuthenticationReader` added on current PR #12 head `ae306fad...`.
- new exact-head workflows triggered.

## What Was Executed
- `CI` run `32291645192`: completed FAILURE on `d2d96f47...`; infra including Elasticsearch GREEN; Heimdall failed at gRPC security bean creation.
- `CI` run `32296242418` on `f7abfa7...`: Heimdall compile failure proved dependency removal invalid.
- current-head workflow execution started: `32296456441`, `32296456440`.

## What Was Not Verified
- current-head compile/unit outcome after starter restoration + reader bean.
- current-head Heimdall health.
- current-head Bifrost health in full-stack job.
- current-head Frontend root in full-stack job.
- current-head overall workflow conclusions/review state.
- real Local AI E2E, routing, recovery, live metrics, reference deployment, final demo.

## Remaining Risks
- explicit anonymous gRPC reader is only appropriate while no real gRPC product service exists; it must not silently become the production auth policy for future gRPC endpoints.
- correction may reveal another real UC-01 startup boundary.
- duplicate `idx_severity` remains HOLD until executable evidence makes it fatal.

## NEXT
**Inspect PR #12 exact-head `ae306fad143d5be1f71d6d25354f6af3c7a7d344` runs `32296456441` and `32296456440`. If RED, inspect only the first concrete Issue #11-scoped failure and apply the smallest justified correction. If all Issue #11 acceptance is GREEN and review/security state is clean, merge PR #12 with expected-head guard, ensure Issue #11 closes only after acceptance/merge, then reconcile MASTER on main before selecting new work.**
