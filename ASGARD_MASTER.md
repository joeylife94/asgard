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
- **Status**: PR #12 OPEN — prior exact-head RED; dev gRPC/Prometheus port collision corrected; new exact-head CI RUNNING
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **P0-B3 merge**: `74da74c71625b9bca111b2e1c1bbbb933c82077a`
- **Issue #11**: OPEN — `P0-B4: verify UC-01 full core-service startup and health`
- **PR #12**: OPEN — `test: verify UC-01 full core-service startup and health`
- **Prior tested PR #12 head**: `ae306fad143d5be1f71d6d25354f6af3c7a7d344`
- **Current PR #12 head**: `279261aad0046df8cce59e5f7fabf242921fdb21`
- **Current exact-head CI**: `CI 32315948212` + `CI/CD Pipeline 32315948241` — RUNNING
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
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy | IN PROGRESS — infra proven; current full-stack application health under exact-head execution |
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
Initial PR-visible full-stack execution proved PostgreSQL, Kafka, Redis, Prometheus and Grafana `3001` readiness, then Heimdall failed because enabled Elasticsearch access hit `localhost:9200` with connection refused.

Correction: include the repository's existing Elasticsearch service and prove `_cluster/health` before application startup.

### B. Elasticsearch-corrected runtime — missing gRPC authentication reader
Head `d2d96f47a394e7ce4cc6a798a368b6b83cd28a7a`, `CI` run `32291645192`:
- PostgreSQL: GREEN.
- Kafka: GREEN.
- Redis: GREEN.
- Elasticsearch: GREEN.
- Prometheus: GREEN.
- Grafana `3001`: GREEN.
- Heimdall: RED during application-context startup.

Fatal boundary: `GrpcServerSecurityAutoConfiguration` could not create its security interceptor because no `GrpcAuthenticationReader` bean existed.

The duplicate PostgreSQL `idx_severity` observation was non-fatal in this run and remains HOLD.

### C. Rejected correction — remove gRPC starter
Head `f7abfa7e565711bf7a39539c7865293532905828`, `CI` run `32296242418`:
- removal caused `:heimdall:compileJava` failure because existing `GrpcServerConfig.java` directly requires gRPC starter classes.
- removal was rejected and starter restored.

### D. Explicit gRPC authentication reader — executed RED
Head `ae306fad143d5be1f71d6d25354f6af3c7a7d344`:
- `CI` run `32296456441`: **FAILURE**.
- `CI/CD Pipeline` run `32296456440`: **FAILURE**.
- Phase 0 preflight: GREEN.
- frontend dev-root job: GREEN.
- infrastructure readiness inside full-stack job: GREEN for PostgreSQL, Kafka, Redis, Elasticsearch, Prometheus, Grafana.
- `Start Heimdall, Bifrost, and Frontend`: step completed.
- **first failing step**: `Verify application reachability`.

Downloaded exact-run artifact `p0-b4-core-health-evidence` proves the first acceptance boundary:

```text
Heimdall startup
→ gRPC server start
→ bind 0.0.0.0:9090
→ Address already in use
→ Failed to start bean 'shadedNettyGrpcServerLifecycle'
→ application context aborts
→ Heimdall /actuator/health never becomes reachable
```

Port owner conflict is deterministic in the proof stack: Prometheus is already required and proven reachable on host `9090`, while the Heimdall gRPC server also defaults to `9090`.

Supporting artifact observations, not yet authorized as the active correction:
- Bifrost process log shows its current proof command rejects the supplied `--host 127.0.0.1 --port 8000` arguments.
- Frontend process log shows Vite started and reported local root `http://127.0.0.1:3000/`, but the full-stack verification step exits at Heimdall first; therefore full-stack Frontend acceptance remains unchecked for this exact head.

### E. Current correction — dev gRPC port isolation
Current PR #12 head: `279261aad0046df8cce59e5f7fabf242921fdb21`.

Smallest correction justified by executed evidence:
- `heimdall/src/main/resources/application-dev.yml` now sets `grpc.server.port: ${GRPC_PORT:9091}`.
- this changes the **dev profile only** and preserves an environment override.
- Prometheus remains on required host port `9090`.
- no production profile, web/JWT auth, UI, README, UC-02 behavior, Checkstyle, or unrelated infrastructure changed.

Current PR-visible execution:
- `CI` run `32315948212`: RUNNING.
- `CI/CD Pipeline` run `32315948241`: RUNNING.
- no PASS is recorded until this exact head completes.

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
- [x] Elasticsearch readiness verified.
- [x] no out-of-scope expansion.

## Result
**IN PROGRESS — the explicit gRPC authentication reader moved Heimdall to the next concrete startup boundary: gRPC port `9090` collided with the already-required Prometheus host port `9090`. Dev gRPC now uses `9091`; exact-head execution is running. P0-B4 is not PASS.**

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
| E-026 | Missing Elasticsearch dependency failure | VERIFIED RED / SUPERSEDED | initial PR #12 run |
| E-027 | Elasticsearch readiness/correction | VERIFIED GREEN | PR #12 |
| E-028 | Missing gRPC authentication reader | VERIFIED RED / SUPERSEDED | run `32291645192` |
| E-029 | gRPC starter removal | VERIFIED RED / REJECTED | compile failure on `f7abfa7...` |
| E-030 | Explicit gRPC authentication reader | VERIFIED PAST PREVIOUS BLOCKER | head `ae306fad...` reached gRPC server start |
| E-031 | Heimdall gRPC/Prometheus port collision | VERIFIED RED | artifact from run `32296456441` |
| E-032 | Dev gRPC port isolation | PUSHED / EXECUTION PENDING | head `279261aad...` |

---

# 7. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | Heimdall dev startup required Elasticsearch | included/proven ready in P0-B4 harness |
| R-002 | duplicate `idx_severity` schema index name observed | HOLD; non-fatal in prior execution; fix only if future run proves blocker |
| R-003 | broad Heimdall checkstyle debt | no mass-fix in P0-B4 |
| R-004 | startup banner is not health proof | endpoint/readiness evidence required |
| R-005 | anonymous gRPC reader could become inappropriate if real gRPC product endpoints are introduced | current scope has no product gRPC service; replace with explicit auth policy when real gRPC endpoints exist |
| R-006 | dev gRPC and Prometheus both previously defaulted to host `9090` | dev gRPC isolated to `9091`; current execution pending |
| R-007 | Bifrost proof command rejected host/port CLI args on prior exact head | HOLD until current run proves it is the next first concrete blocker |
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
- stale RUNNING state for head `ae306fad...` was reconciled to executed FAILURE.
- exact-run evidence artifact was downloaded and inspected.
- first concrete current boundary was proven as Heimdall gRPC bind failure on `9090`, conflicting with required Prometheus host `9090`.
- only the dev-profile gRPC default was moved to `9091`, preserving `GRPC_PORT` override.
- current PR #12 head advanced to `279261aad0046df8cce59e5f7fabf242921fdb21` and new exact-head workflows started.

## What Was Executed
- `CI` run `32296456441`: completed FAILURE on `ae306fad...`.
- `CI/CD Pipeline` run `32296456440`: completed FAILURE on `ae306fad...`.
- core-health artifact from `32296456441` inspected: infra readiness GREEN; first reachability boundary Heimdall RED due gRPC `9090` bind collision.
- branch mutation committed: `279261aad0046df8cce59e5f7fabf242921fdb21`.
- new exact-head workflows: `32315948212`, `32315948241` started.

## What Was Not Verified
- current-head Heimdall health after dev gRPC port isolation.
- current-head Bifrost health in full-stack job.
- current-head Frontend root in full-stack job.
- current-head overall workflow conclusions/review state.
- real Local AI E2E, routing, recovery, live metrics, reference deployment, final demo.

## Remaining Risks
- correction may expose the next real UC-01 startup boundary.
- prior artifact already shows a Bifrost CLI invocation error, but it is not repaired until current execution proves it is the first remaining acceptance blocker.
- duplicate `idx_severity` remains HOLD until executable evidence makes it fatal.

## NEXT
**Inspect PR #12 exact-head `279261aad0046df8cce59e5f7fabf242921fdb21` runs `32315948212` and `32315948241`. If RED, inspect only the first concrete Issue #11-scoped failure and apply the smallest justified correction. If all Issue #11 acceptance is GREEN and review/security state is clean, merge PR #12 with expected-head guard, ensure Issue #11 closes only after acceptance/merge, then reconcile MASTER on main before selecting new work.**
