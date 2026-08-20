# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 1 — Golden Path
- **Current Batch**: P1-B1 — UC-02 Real Local AI Golden Path
- **Batch Result**: IN PROGRESS
- **Status**: Issue #13 OPEN / implementation branch created / executable proof not yet run
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Active Issue**: #13 — `P1-B1: prove UC-02 real Local AI golden path`
- **Active Branch**: `agent/p1-b1-local-ai-golden-path`
- **Active PR**: NONE YET
- **Phase 0 Result**: PASS
- **P0-B4 / PR #12 merge**: `8f79c1aaf7a145abb4721c5f7799059b8c4195aa`
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
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy | **PASS** |
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED | **IN PROGRESS — Issue #13** |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 | PENDING |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED | PENDING |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 | PENDING |

---

# 4. Phase 0 — PASS

## P0-B1 — PASS / MERGED
- PR #4 merged at `fa3f129783387fbeafae537e8a22b4629faf6d42`.
- primary Heimdall + Bifrost unit job GREEN.
- secondary Bifrost install/lint/pytest/coverage GREEN.
- dependency security GREEN.
- Java 21 CI contract aligned.
- broad Heimdall Checkstyle debt classified as pre-existing: **41 files / 109 warnings / 2 info**.

## P0-B2 — PASS / MERGED
- Issue #6 CLOSED.
- PR #7 merged at `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`.
- minimal four-file frontend boot tree restored.
- exact-head production frontend build GREEN.

## P0-B3 — PASS / MERGED
- Issue #8 CLOSED.
- PR #9 proof harness merged at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`.
- PR #10 merged at `74da74c71625b9bca111b2e1c1bbbb933c82077a`.
- frontend dev-server root reachability GREEN.
- root `build-all.ps1 -SkipTests` frontend path GREEN.

## P0-B4 — PASS / MERGED
- Issue #11 CLOSED / COMPLETED.
- PR #12 exact head `1f3459dd5e12bf85b5eccfe41d1eca05bbf6231b`.
- PR #12 merged at `8f79c1aaf7a145abb4721c5f7799059b8c4195aa`.
- primary `CI` run `32320165761`: **SUCCESS**.
- Phase 0 preflight / unit tests / frontend dev-root / default Windows build: GREEN.
- full-core job: GREEN.
- infrastructure: PostgreSQL / Kafka / Redis / Elasticsearch / Prometheus / Grafana `3001` GREEN.
- Heimdall `/actuator/health` → `UP`.
- Bifrost `/health` → `healthy`.
- Frontend root → reachable HTML.
- secondary `CI/CD Pipeline` run `32320165695` RED only at the already-classified pre-existing Heimdall `checkstyleMain` debt; Bifrost/security GREEN.

## Phase 0 Closure
**PASS.** Remaining v1.0 gaps are product-flow proofs, not baseline-startup uncertainty.

---

# 5. Phase 1 — P1-B1 Real Local AI Golden Path

## Work Item
- **Issue #13**: OPEN
- **Branch**: `agent/p1-b1-local-ai-golden-path`
- **PR**: NONE YET

## Goal
Prove the first real Asgard product flow with actual local-model execution.

## Required Flow

```text
Deterministic sample log/input
→ Heimdall
→ real Analysis Job
→ Kafka request
→ Bifrost consumption
→ REAL Local AI model inference
→ result through real integration path
→ persistence
→ Job SUCCEEDED
```

## Acceptance Criteria
- [ ] deterministic sample input/log is fixed and reviewable.
- [ ] Heimdall creates a real Analysis Job.
- [ ] Kafka request publication/consumption is evidenced.
- [ ] Bifrost invokes a **real Local AI model**.
- [ ] mock/fallback-only execution is rejected as PASS evidence.
- [ ] result returns through the real integration path.
- [ ] result is persisted.
- [ ] final Job state is `SUCCEEDED`.
- [ ] route/provider/latency evidence is captured where existing surfaces expose it.
- [ ] flow is repeatable under PR-visible or equivalently reviewable execution.
- [ ] no out-of-scope expansion.

## In Scope
- minimum proof harness/config/code corrections required by executed UC-02 evidence.
- one deterministic input.
- one real local provider/model path.
- only the first concrete failing boundary at a time.

## Out of Scope
- Cloud-vs-Local routing proof / UC-03.
- Cloud provider setup beyond explicitly keeping P1-B1 local-only.
- DLQ/Redrive / UC-04.
- Grafana metric correctness / UC-05.
- UI expansion.
- README/portfolio hardening.
- HP AI Server optimization/reference deployment.
- broad Heimdall Checkstyle cleanup.
- unrelated architecture refactors.

## Verification Rule
Prefer a bounded PR-visible exact-head executable proof. Preserve artifacts/logs proving Job ID/state, Kafka handoff, real model/provider invocation, returned result, persistence, and final `SUCCEEDED`.

---

# 6. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted baseline execution | VERIFIED | Phase 0 |
| E-004 | Heimdall Checkstyle debt | VERIFIED RED / PRE-EXISTING | 41 / 109 / 2 |
| E-005 | Frontend boot repair/build | VERIFIED / MERGED | PR #7 |
| E-016 | Frontend dev-server root | VERIFIED GREEN | Phase 0 |
| E-017 | Root SkipTests build path | VERIFIED GREEN | Phase 0 |
| E-024 | UC-01 full core-stack health | VERIFIED GREEN / MERGED | PR #12 / CI `32320165761` |
| E-025 | Infra readiness | VERIFIED GREEN | Postgres/Kafka/Redis/Elasticsearch/Prometheus/Grafana |
| E-035 | Heimdall full-stack health | VERIFIED GREEN | `/actuator/health` = UP |
| E-038 | Bifrost full-stack health | VERIFIED GREEN | `/health` = healthy |
| E-039 | Full-stack Frontend root | VERIFIED GREEN | root HTML captured |
| E-018 | Real Local AI E2E | **IN PROGRESS** | Issue #13 |
| E-019 | Local vs Cloud Routing | PENDING | UC-03 |
| E-020 | DLQ → Redrive → Success | PENDING | UC-04 |
| E-021 | Grafana live metrics | PENDING | UC-05 |
| E-022 | Final Demo | PENDING | final proof packaging |
| E-023 | HP AI Server reference run | PENDING | reference deployment |

---

# 7. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | HOLD; repeatedly non-fatal; fix only if future executable evidence makes it a blocker |
| R-002 | broad Heimdall Checkstyle debt | VERIFIED PRE-EXISTING; no mass-fix without separate authorization |
| R-003 | anonymous gRPC reader may be inappropriate for future real gRPC endpoints | replace with explicit policy only if actual product gRPC endpoint is introduced |
| R-004 | root startup banner is not health evidence | use endpoint/readiness evidence |
| R-005 | root `start-all.ps1` Bifrost launch differs from proven CI `serve` invocation | evaluate only if P1-B1 executable path uses it and it becomes a direct blocker |
| R-006 | README overclaim / Grafana port drift | proof-hardening later |
| R-007 | fallback-only AI E2E risk | P1-B1 requires concrete real-model invocation evidence |
| R-008 | GitHub-hosted runner may need a bounded local-model runtime/model strategy | do not weaken real-model acceptance; record exact prerequisite if no safe reviewable execution is possible |
| R-009 | agent self-report | never PASS without executed evidence |

---

# 8. Work Item / PR Lifecycle

1. MASTER first.
2. Active focused PR first.
3. One active implementation Issue by default.
4. Same-gap CI/review corrections remain in the same Issue/PR.
5. RED → first concrete failure → smallest in-scope fix.
6. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
7. Issue closes only after acceptance + merge.
8. Reconcile MASTER on `main` before another Issue.
9. Human Review remains the final v1.0 gate.

---

# 9. Current Checkpoint

## Result
**PHASE 0 PASS / UC-01 PASS / P1-B1 IN PROGRESS.**

## What Changed
- PR #12 exact-head primary CI completed SUCCESS and Issue #11 closed after merge.
- Phase 0 and UC-01 were closed PASS from executed evidence.
- no matching open Issue existed for the next authorized Phase 1 gap.
- Issue #13 was created as the sole active implementation work item.
- branch `agent/p1-b1-local-ai-golden-path` was created from synchronized `main`.

## What Was Executed
- `CI` run `32320165761`: SUCCESS.
- full-core artifact proved Heimdall `UP`, Bifrost `healthy`, Frontend root reachable.
- `CI/CD Pipeline` run `32320165695`: pre-existing Heimdall Checkstyle RED; Bifrost/security GREEN.
- PR #12 merge and Issue #11 completed closure verified.
- Issue #13 creation and Phase 1 branch creation completed.

## What Was Not Verified
- real Local AI inference E2E.
- Analysis Job → Kafka → Bifrost → real model → persisted result → `SUCCEEDED`.
- Local vs Cloud routing.
- DLQ/Redrive recovery.
- live Grafana metric correctness.
- HP AI Server reference run.
- final demo/portfolio package.

## Remaining Risks
- P1-B1 may expose integration/configuration defects not visible in health checks.
- Local AI proof must not silently pass via mock or fallback.
- current execution environment for a real model must remain reviewable and bounded.

## NEXT
**Under Issue #13 only, inspect the existing real Heimdall Analysis Job → Kafka → Bifrost → local-provider integration far enough to create the smallest executable P1-B1 proof slice. Do not create another Issue. The first PR should prove or falsify the real Local AI Golden Path; any RED must be handled one concrete boundary at a time.**