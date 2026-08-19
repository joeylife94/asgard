# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> This file is the single source of truth for Asgard v1.0 execution. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B4 — UC-01 Full Core-Service Startup / Health Verification
- **Batch Result**: IN PROGRESS
- **Status**: PR #12 OPEN — INITIAL EXACT-HEAD EXECUTION RED AT HEIMDALL ELASTICSEARCH DEPENDENCY
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **P0-B3 merge**: `74da74c71625b9bca111b2e1c1bbbb933c82077a`
- **Issue #11**: OPEN — `P0-B4: verify UC-01 full core-service startup and health`
- **PR #12**: OPEN — `test: verify UC-01 full core-service startup and health`
- **Current tested PR #12 head**: `e874550e018e89b889ae9b3a7b6a6eb1542e2e63`
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
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy | IN PROGRESS — infrastructure readiness proven; Heimdall blocked by missing Elasticsearch dependency in PR #12 harness |
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
- Heimdall broad `checkstyleMain` debt classified as pre-existing: **41 files / 109 warnings / 2 info**.

## P0-B2 — PASS / MERGED
- Issue #6 CLOSED; PR #7 merged at `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`.
- minimal four-file frontend boot tree restored.
- exact-head production frontend build GREEN.

## P0-B3 — PASS / MERGED
- Issue #8 CLOSED.
- PR #9 proof harness merged at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`.
- PR #10 tested head `dc8cc524bb2f10e8b5674cfcc98247882782a82a` merged at `74da74c71625b9bca111b2e1c1bbbb933c82077a`.
- `CI/CD Pipeline` run `32279712933`: SUCCESS.
- `CI` run `32279712788`: SUCCESS.
- Vite dev server + HTTP root reachability: GREEN.
- root `build-all.ps1 -SkipTests` reaches/completes Frontend: GREEN.
- explicit SkipTests path uses `:heimdall:assemble`; normal full build remains `:heimdall:build`.
- no Checkstyle config suppression or broad cleanup.

---

# 5. Active Phase 0 Slice — P0-B4

## Work Item
- **Issue #11**: OPEN
- **PR #12**: OPEN
- **PR branch**: `agent/p0-b4-uc01-core-health-proof`
- **Initial tested head**: `e874550e018e89b889ae9b3a7b6a6eb1542e2e63`

## Goal
Close the remaining UC-01 startup proof gap by executing the actual core stack and collecting concrete service-health/reachability evidence.

## In Scope
- reproducible checkout/configuration for proof.
- repository-supported core startup path or minimum CI-equivalent runtime path.
- Heimdall / Bifrost health.
- PostgreSQL / Kafka readiness.
- Frontend root reachability in the running stack.
- Prometheus / Grafana reachability; Grafana host port `3001`.
- Redis readiness because current Heimdall/startup contract configures Redis.
- Elasticsearch readiness when required by the active Heimdall startup contract.
- only the minimum proof-harness correction required by executed evidence.

## Out of Scope
- UC-02/03/04/05 product behavior.
- UI expansion.
- README hardening.
- broad Heimdall Checkstyle cleanup.
- unrelated production infrastructure.

## Initial PR #12 Executed Evidence

### Workflow
- `CI` run `32290803193`: overall FAILURE because P0-B4 core-health job failed.
- `UC-01 full core-service startup and health` job `96190902370`: FAILURE at **Verify application reachability**.
- Primary Heimdall+Bifrost unit tests: GREEN.
- Phase 0 preflight/frontend build: GREEN.
- UC-01 frontend dev root proof: GREEN.
- UC-01 default Windows build path: GREEN.

### Proven Infrastructure Readiness
- PostgreSQL: GREEN — ready on attempt 2.
- Kafka: GREEN — ready on attempt 2.
- Redis: GREEN — ready on attempt 1.
- Prometheus: GREEN — reachable on attempt 1.
- Grafana: GREEN — `/api/health` reachable on host port `3001` on attempt 1.

### First Concrete Failure Boundary
Heimdall never became reachable at `http://127.0.0.1:8080/actuator/health`.

The captured Heimdall log proves the application reached Spring/Tomcat/JPA initialization and connected to PostgreSQL, then aborted application-context startup because the enabled Elasticsearch repository/service attempted `localhost:9200` and received `Connection refused`.

Root chain:

```text
elasticsearchService
→ logSearchRepository
→ SimpleElasticsearchRepository
→ DataAccessResourceFailureException
→ Connection refused (localhost:9200)
```

The PR harness starts `postgres zookeeper kafka redis prometheus grafana` but not the repository Compose `elasticsearch` service. The repository Compose contract exposes Elasticsearch at `9200:9200` and defines a `_cluster/health` healthcheck. Automated review independently identified the same omission.

### Separate Observation — Do Not Expand This Batch
Heimdall logs also expose a duplicate PostgreSQL index name warning/error for `idx_severity`. This is real evidence but is **not the first blocking boundary** for P0-B4; do not repair it unless it becomes the next concrete startup blocker after Elasticsearch is corrected.

## Acceptance Criteria
- [x] checkout/configuration required by proof explicit and reproducible via PR-visible CI.
- [x] core-stack proof command executes under reviewable runtime evidence.
- [ ] Heimdall health/reachability verified.
- [ ] Bifrost health/reachability verified in the full-stack job.
- [x] PostgreSQL readiness verified.
- [x] Kafka readiness verified.
- [ ] Frontend root reachability verified in the full-stack job.
- [x] Prometheus reachability verified.
- [x] Grafana reachability verified at host port `3001`.
- [x] Redis readiness verified.
- [ ] Elasticsearch readiness verified as required Heimdall dependency.
- [x] no UC-02 product flow, UI expansion, README hardening, or broad Heimdall style cleanup in initial slice.

## Result
**IN PROGRESS — initial runtime execution is valid evidence; next correction is bounded to starting/awaiting Elasticsearch before Heimdall. No P0-B4 PASS yet.**

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
| E-017 | Root default SkipTests build path reaches/completes Frontend | VERIFIED GREEN / MERGED | PR #10 |
| E-018 | Real Local AI E2E | PENDING | |
| E-019 | Local vs Cloud Routing | PENDING | |
| E-020 | DLQ → Redrive → Success | PENDING | |
| E-021 | Grafana live metrics | PENDING | |
| E-022 | Final Demo | PENDING | |
| E-023 | HP AI Server reference run | PENDING | |
| E-024 | UC-01 full core-stack service health | IN PROGRESS / INITIAL RED | PR #12, run 32290803193 |
| E-025 | P0-B4 infrastructure readiness | VERIFIED GREEN | Postgres/Kafka/Redis/Prometheus/Grafana in PR #12 initial run |
| E-026 | Heimdall Elasticsearch startup dependency | VERIFIED RED | PR #12 job 96190902370; localhost:9200 connection refused |

---

# 7. Known Debt / Risks

| ID | Risk | Required handling |
|---|---|---|
| R-001 | Heimdall requires Elasticsearch in current dev startup contract | start + await existing Compose Elasticsearch in PR #12 harness; do not invent product behavior |
| R-002 | duplicate `idx_severity` schema index name observed | record only; address only if it becomes next concrete startup blocker |
| R-003 | broad Heimdall checkstyle debt | keep visible; no mass-fix in P0-B4 |
| R-004 | interactive Windows startup banner is not health proof | continue executable endpoint/readiness checks |
| R-005 | README overclaim / Grafana port drift | proof-hardening later |
| R-006 | fallback-only E2E risk | real-model evidence mandatory later |
| R-007 | agent self-report without executed proof | never count as PASS |

---

# 8. Work Item / PR Lifecycle

1. Read MASTER first.
2. Active focused PR first.
3. One active implementation/proof Issue at a time by default.
4. Corrections inside the active acceptance gap stay in the same Issue/PR.
5. RED → first concrete failing evidence → smallest in-scope fix only.
6. GREEN bounded acceptance + clean review/security state → merge with expected-head guard.
7. Issue closes only after executed acceptance + merge.
8. Reconcile MASTER on `main` before another Issue.
9. Re-evaluate Human Review/FREEZE before another Issue.

**Ordinary bounded intermediate PR merges do not require human approval. Human Review remains the FINAL v1.0 gate.**

---

# 9. Current Checkpoint

## Result
**P0-B1 PASS / P0-B2 PASS / P0-B3 PASS / P0-B4 IN PROGRESS.**

## What Changed
- authoritative MASTER re-read first.
- current Issue #11 confirmed OPEN.
- active PR #12 discovered and inspected before new work.
- initial exact-head PR #12 workflows, job steps and failing logs inspected.
- executed infrastructure readiness classified as GREEN where directly proven.
- first concrete P0-B4 blocker isolated to missing Elasticsearch startup in the proof harness.
- automated review feedback independently corroborates the same dependency omission.

## What Was Executed
- PR #12 exact-head `e874550e018e89b889ae9b3a7b6a6eb1542e2e63` workflow execution.
- `CI` run `32290803193`.
- core-health job `96190902370`.
- Heimdall bootJar build.
- Bifrost/frontend dependency preparation.
- Compose startup/readiness for PostgreSQL, Kafka, Redis, Prometheus and Grafana.
- application launch attempt for Heimdall, Bifrost and Frontend.
- 60-attempt Heimdall health probe and captured startup failure log.

## What Was Not Verified
- Elasticsearch readiness in the PR harness.
- Heimdall healthy startup after Elasticsearch correction.
- Bifrost/full-stack health after Heimdall passes.
- Frontend/full-stack root after Heimdall passes.
- real Local AI E2E.
- routing/recovery/live metrics/reference deployment/final demo.

## Remaining Risks
- adding Elasticsearch may expose the next concrete Heimdall startup defect; handle only the first new Issue #11-scoped boundary.
- duplicate `idx_severity` schema name may become a later blocker but is not authorized for proactive cleanup.

## NEXT
**Within existing PR #12 only, add the repository's existing `elasticsearch` Compose service to the P0-B4 infrastructure startup and wait for `http://127.0.0.1:9200/_cluster/health` before Heimdall starts. Re-run exact-head PR-visible CI. If RED, inspect only the first new concrete Issue #11 failure. If the bounded acceptance becomes GREEN and review state is clean, merge with expected-head guard, close Issue #11, and reconcile MASTER before selecting any new work.**
