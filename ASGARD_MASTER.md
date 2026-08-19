# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> This file is the single source of truth for Asgard v1.0 execution. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B3 — UC-01 Frontend Startup / Default Build Verification
- **Batch Result**: IN PROGRESS
- **Status**: FRONTEND DEV VERIFIED; ROOT BUILD BLOCKER VERIFIED; BOUNDED BUILD-CONTRACT REPAIR AUTHORIZED
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **PR #9 merge**: `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`
- **Issue #8**: OPEN
- **PR #9**: MERGED as proof harness; Issue #8 intentionally remains OPEN because the default build-path acceptance criterion is not yet satisfied
- **PR #9 exact head**: `1f50afc4ff2c4590178bfce14f250866339bd9e6`
- **Primary CI run**: `32273762721`
- **Secondary CI/CD run**: `32273762445`
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

| UC | Goal | PASS 기준 |
|---|---|---|
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy |
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 |

---

# 4. Closed Phase 0 Evidence

## P0-B1 — PASS / MERGED
- PR #4 merged at `fa3f129783387fbeafae537e8a22b4629faf6d42`.
- primary Heimdall + Bifrost unit job GREEN.
- secondary Bifrost install/lint/pytest/coverage GREEN.
- dependency security GREEN.
- secondary Heimdall RED classified as pre-existing `:heimdall:checkstyleMain`: 41 files / 109 warnings / 2 info.

## P0-B2 — PASS / MERGED
- Issue #6 CLOSED; PR #7 merged at `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`.
- minimal four-file frontend boot tree restored.
- exact-head production frontend build GREEN.
- secondary Bifrost and dependency security GREEN.

---

# 5. Active Phase 0 Slice — P0-B3

## Issue / PR
- **Issue #8**: `P0-B3: verify UC-01 frontend startup and default build path`
- **PR #9**: proof harness merged at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`
- **Issue state**: OPEN

## Goal
Close the two remaining frontend/startup proof debts from P0-B2:
1. Vite dev-server root reachability;
2. root `build-all.ps1 -SkipTests` without `-SkipFrontend`, including a successful frontend build step.

## Executed Evidence

Primary CI run `32273762721`, exact head `1f50afc4ff2c4590178bfce14f250866339bd9e6`:
- **UC-01 frontend dev root reachability: GREEN**.
- frontend dependency install: success.
- Vite dev server start: success.
- HTTP GET `http://127.0.0.1:3000/`: success on attempt 2.
- Phase 0 frontend install/build preflight: GREEN.
- primary Heimdall + Bifrost unit job: GREEN.
- Windows default build path: EXECUTED RED.
- root `build-all.ps1 -SkipTests` stopped in Heimdall at `:heimdall:checkstyleMain` before reaching Frontend.
- exact failure is the already-classified broad debt: **41 files / 109 warnings / 2 info**.
- default-build evidence artifact uploaded successfully.

Secondary CI/CD run `32273762445`:
- Bifrost: GREEN.
- dependency security: GREEN.
- Heimdall: RED at the same pre-existing build/checkstyle boundary.
- Frontend job skipped because only workflow files changed.

## Acceptance Criteria
- [x] `npm install` succeeds in `bifrost/frontend` under exact-head GitHub execution.
- [x] `npm run dev` starts successfully.
- [x] HTTP GET `/` returns success under exact-head GitHub execution.
- [x] root `build-all.ps1 -SkipTests` execution result observed.
- [ ] default build path reaches and completes frontend build step.
- [x] no product UI expansion.
- [x] no broad Heimdall cleanup.

## Root-Build Contract Decision
The blocker is now executable and falsifiable. `build-all.ps1 -SkipTests` currently calls:

```text
:heimdall:clean :heimdall:build -x test
```

Gradle `build` still runs `checkstyleMain`, so `-SkipTests` does not produce a usable artifact path in the presence of the already-known style debt and prevents the unified build from reaching Bifrost/Frontend.

**Authorized bounded repair inside Issue #8:**
- when `-SkipTests` is supplied, change only the Heimdall artifact-build task from `build -x test` to an artifact-producing task that does not execute verification gates, preferably `:heimdall:assemble` after `:heimdall:clean`;
- when `-SkipTests` is NOT supplied, preserve the existing full `:heimdall:build` behavior;
- do not disable checkstyle globally;
- do not modify Checkstyle rules;
- do not mass-fix Heimdall style debt;
- do not expand product UI or other services.

## Repair Acceptance
- [ ] PR-visible Windows execution of `build-all.ps1 -SkipTests` reaches Frontend.
- [ ] Frontend build completes successfully in the unified default path.
- [ ] existing primary Heimdall+Bifrost unit job remains GREEN.
- [ ] no global checkstyle suppression and no broad style cleanup.

## Result
**IN PROGRESS — E-016 PASS; E-017 VERIFIED RED at pre-existing Heimdall quality-gate boundary; minimal build-contract repair authorized.**

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
| E-016 | Frontend dev-server root reachability | VERIFIED GREEN | PR #9 run `32273762721` |
| E-017 | Root default build path | VERIFIED RED / BLOCKED | Windows runner reaches Heimdall then stops at pre-existing `checkstyleMain` before Frontend |
| E-018 | Real Local AI E2E | PENDING | |
| E-019 | Local vs Cloud Routing | PENDING | |
| E-020 | DLQ → Redrive → Success | PENDING | |
| E-021 | Grafana live metrics | PENDING | |
| E-022 | Final Demo | PENDING | |
| E-023 | HP AI Server reference run | PENDING | |

---

# 7. Known Debt / Risks

| ID | Risk | Required handling |
|---|---|---|
| R-001 | root build stops before Frontend at Heimdall checkstyle | use only the bounded SkipTests build-contract repair authorized above |
| R-002 | broad Heimdall checkstyle debt | keep visible; do not mass-fix in P0-B3 |
| R-003 | changing build semantics could accidentally hide quality gates | preserve normal full `build`; only SkipTests artifact path may use `assemble` |
| R-004 | README overclaim / Grafana port drift | proof-hardening later |
| R-005 | fallback-only E2E risk | real-model evidence mandatory |
| R-006 | scope explosion | keep Frozen Scope |
| R-007 | agent self-report without executed proof | never count as PASS |

---

# 8. Work Item / PR Lifecycle

1. Read MASTER first.
2. Active focused PR first.
3. Otherwise use the existing open Issue matching the current acceptance gap.
4. Do not create another Issue while Issue #8 remains active.
5. Corrections inside this gap stay under Issue #8.
6. RED → first concrete failing evidence → smallest in-scope fix only.
7. GREEN bounded acceptance + clean review/security state → merge with expected-head guard.
8. Issue closes only after executed acceptance + merge.
9. Reconcile MASTER on `main` before another Issue.
10. Re-evaluate Human Review/FREEZE before another Issue.

**Ordinary bounded intermediate PR merges do not require human approval. Human Review remains the FINAL v1.0 gate.**

---

# 9. Required Completion Report

Every iteration records:
- What Changed
- What Was Executed
- What Was Not Verified
- Remaining Risks
- Result
- Next

Rules:
- Agent self-report ≠ proof
- Executed evidence beats static inference
- Missing CI status ≠ PASS
- Same blocker loop prohibited
- Experimental scope prohibited before Core completion
- MASTER synchronized before product changes

---

# 10. Current Checkpoint

## Result
**P0-B1 PASS / P0-B2 PASS / P0-B3 IN PROGRESS.**

Frontend dev-server reachability is verified. The unified root build is also now executed and its blocker is proven: pre-existing Heimdall `checkstyleMain` prevents the build from reaching Frontend. PR #9 was merged as durable proof infrastructure without auto-closing Issue #8.

## What Changed
- Read authoritative MASTER first.
- Re-fetched current PR #9 exact head and completed workflows.
- Inspected the concrete Windows default-build failure log.
- Confirmed the failure is the exact previously classified 41-file / 109-warning / 2-info Heimdall checkstyle debt.
- Updated PR #9 body from `Closes #8` to `Refs #8` because Issue acceptance is not complete.
- Merged PR #9 with expected-head guard.
- Reconciled MASTER on `main`.
- Authorized one bounded build-contract repair under the still-open Issue #8.

## What Was Executed
- PR #9 workflow lookup.
- primary and secondary workflow job inspection.
- Windows job log inspection.
- exact-head primary unit job confirmed GREEN.
- dev-server root reachability confirmed GREEN.
- `build-all.ps1 -SkipTests` confirmed RED before Frontend at `:heimdall:checkstyleMain`.

## What Was Not Verified
- unified root build reaching Frontend successfully.
- Compose/full-stack startup / UC-01 full service-health closure.
- real Local AI E2E.
- Local vs Cloud routing execution.
- DLQ → Redrive → Success.
- Grafana live evidence.

## Remaining Risks
- a SkipTests build-contract change must not suppress normal full-build quality gates.
- broad checkstyle debt remains visible and unresolved.
- UC-01 full service-health closure remains outside this bounded slice.

## NEXT
**Under existing Issue #8, create the smallest focused branch/PR that changes only the Heimdall `-SkipTests` path in `build-all.ps1` from `:heimdall:build -x test` to an artifact-producing path such as `:heimdall:assemble`, while preserving normal full `:heimdall:build`. Execute the existing PR-visible Windows proof. If the unified build reaches and completes Frontend and primary unit checks remain GREEN, merge with expected-head guard, close Issue #8, and reconcile MASTER before selecting another gap.**
