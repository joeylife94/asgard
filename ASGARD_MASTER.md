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
- **Status**: PR #12 OPEN — ELASTICSEARCH CORRECTION PUSHED; EXACT-HEAD CI RUNNING
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **P0-B3 merge**: `74da74c71625b9bca111b2e1c1bbbb933c82077a`
- **Issue #11**: OPEN — `P0-B4: verify UC-01 full core-service startup and health`
- **PR #12**: OPEN — `test: verify UC-01 full core-service startup and health`
- **Initial tested PR #12 head**: `e874550e018e89b889ae9b3a7b6a6eb1542e2e63`
- **Current PR #12 head**: `d2d96f47a394e7ce4cc6a798a368b6b83cd28a7a`
- **Current exact-head CI**: `CI 32291645192` + `CI/CD Pipeline 32291645245` — RUNNING
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
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy | IN PROGRESS — infra readiness proven; Elasticsearch correction under exact-head execution |
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
- only minimum proof-harness corrections justified by executed evidence.

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

```text
elasticsearchService
→ logSearchRepository
→ SimpleElasticsearchRepository
→ DataAccessResourceFailureException
→ Connection refused (localhost:9200)
```

Automated review independently identified the same missing Elasticsearch startup dependency.

## Correction — Current Head `d2d96f47...`

Changed only the Issue #11 proof harness:
- existing Compose `elasticsearch` service added to infrastructure startup.
- explicit readiness loop added for `http://127.0.0.1:9200/_cluster/health` before Heimdall startup.
- no product behavior, UI, Checkstyle or README changes.

Current PR-visible exact-head execution:
- `CI` run `32291645192`: RUNNING.
- `CI/CD Pipeline` run `32291645245`: RUNNING.
- no PASS is recorded until current exact-head runtime completes.

### Separate Observation — HOLD
Initial Heimdall logs also exposed a duplicate PostgreSQL index-name warning/error for `idx_severity`. It is recorded but is not authorized for proactive repair. Address only if it becomes the next concrete P0-B4 startup blocker.

## Acceptance Criteria
- [x] reviewable checkout/configuration/proof command.
- [x] actual PR-visible core-stack execution exists.
- [ ] current exact-head Heimdall health verified.
- [ ] current exact-head Bifrost health verified in full-stack job.
- [x] PostgreSQL readiness verified on initial run.
- [x] Kafka readiness verified on initial run.
- [ ] current exact-head Frontend root verified in full-stack job.
- [x] Prometheus reachability verified on initial run.
- [x] Grafana `3001` reachability verified on initial run.
- [x] Redis readiness verified on initial run.
- [ ] Elasticsearch readiness verified by current exact-head run.
- [x] no out-of-scope expansion.

## Result
**IN PROGRESS — bounded Elasticsearch correction is pushed; current exact-head execution is running. P0-B4 is not PASS.**

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
| E-025 | P0-B4 infra readiness | VERIFIED GREEN | Postgres/Kafka/Redis/Prometheus/Grafana initial run |
| E-026 | Missing Elasticsearch dependency failure | VERIFIED RED | initial PR #12 run |
| E-027 | Elasticsearch proof-harness correction | PUSHED / EXECUTION PENDING | head `d2d96f47...` |

---

# 7. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | Current Heimdall dev startup requires Elasticsearch | correction under exact-head execution |
| R-002 | duplicate `idx_severity` schema index name observed | HOLD; fix only if next concrete startup blocker |
| R-003 | broad Heimdall checkstyle debt | no mass-fix in P0-B4 |
| R-004 | startup banner is not health proof | endpoint/readiness evidence required |
| R-005 | README overclaim / Grafana port drift | proof-hardening later |
| R-006 | fallback-only E2E risk | real-model proof required later |
| R-007 | agent self-report | never PASS without executed evidence |

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
- MASTER reconciled with initial PR #12 executed failure evidence.
- repository Compose Elasticsearch contract confirmed: service `elasticsearch`, host `9200`, `_cluster/health` healthcheck.
- PR #12 proof harness corrected to start Elasticsearch and wait for readiness.
- exact-head advanced from `e874550...` to `d2d96f47...`.
- new PR-visible CI runs triggered.

## What Was Executed
- initial exact-head core-stack proof and failing Heimdall health probe.
- concrete infrastructure readiness for PostgreSQL/Kafka/Redis/Prometheus/Grafana.
- captured Heimdall Elasticsearch connection-refused root cause.
- current-head workflow dispatch via PR push; runs are active.

## What Was Not Verified
- current-head Elasticsearch readiness result.
- current-head Heimdall/Bifrost/full-stack Frontend health.
- current-head overall relevant workflow conclusions.
- real Local AI E2E, routing, recovery, live metrics, reference deployment, final demo.

## Remaining Risks
- Elasticsearch correction may reveal the next real startup boundary.
- duplicate `idx_severity` remains a recorded HOLD, not a proactive cleanup target.

## NEXT
**Inspect PR #12 exact-head `d2d96f47a394e7ce4cc6a798a368b6b83cd28a7a` runs `32291645192` and `32291645245`. If RED, inspect only the first concrete Issue #11-scoped failure and apply the smallest justified correction. If bounded acceptance is GREEN and review/security state is clean, resolve the now-outdated Elasticsearch review thread, merge PR #12 with expected-head guard, close Issue #11 only after merge/acceptance, and reconcile MASTER before selecting new work.**
