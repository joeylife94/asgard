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
- **Status**: EXECUTION PENDING ON PR #9
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Original code baseline**: `bca6567919cbcac3f9039268c09526b25179f370`
- **PR #3 execution merge**: `888f2c5694940fe42284466fb57a0b33b2ec73cd`
- **PR #4 bounded repair merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **PR #7 frontend boot-shell merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **Issue #8**: OPEN — P0-B3 UC-01 executable verification
- **PR #9**: OPEN — `test: verify UC-01 frontend startup proof`
- **PR #9 exact head at creation**: `1f50afc4ff2c4590178bfce14f250866339bd9e6`
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

# 2. v1.0 Boundary

## Done Enough To Use
- 실제 Local AI 분석
- 선택적 Cloud AI 분석
- Kafka async Job
- Persistence / Idempotency
- DLQ / Redrive / Audit
- Auth / Rate Limit
- Minimal Dashboard
- Prometheus / Grafana
- 재현 가능한 실행

## Done Enough To Show
- reproducible build/runtime evidence
- Real-model E2E PASS
- Failure → Recovery PASS
- relevant CI green for bounded slices
- runtime / Grafana screenshots
- README ↔ Evidence 일치
- 2~3분 Demo

## Explicit Non-Goals
- Multi-tenancy 완성
- HA / Multi-region
- Kubernetes production
- Autoscaling
- Full RBAC / Enterprise Secret Manager
- 실제 SLA/SLO 운영
- Security certification
- 법률적 GDPR 인증
- 대형 Admin UI
- 신규 AI 기능 대량 추가

---

# 3. Frozen v1.0 Scope

## CORE — Must Pass
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

## SUPPORTING — Keep only when used by Core
- Circuit Breaker
- Smart Cache
- Quality Metrics
- Redis / Elasticsearch / Tracing

## EXPERIMENTAL — Does not block v1.0
- Feedback expansion
- A/B Testing expansion
- Advanced Routing expansion
- Additional Providers
- Interview-specific features

**Rule:** Experimental expansion is prohibited before Core completion.

---

# 4. Required Use Cases

| UC | Goal | PASS 기준 |
|---|---|---|
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy |
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 |

---

# 5. Closed Phase 0 Slices

## P0-B1 — PASS / MERGED

PR #4:
- final exact head: `1d301377a5951962cb3afd4e653a1975b8a2267a`
- merged main SHA: `fa3f129783387fbeafae537e8a22b4629faf6d42`

Executed evidence:
- primary CI `32262136812`: Heimdall + Bifrost unit job GREEN.
- secondary CI/CD `32262136715`: Bifrost install/lint/pytest/coverage GREEN.
- dependency security GREEN.
- secondary Heimdall RED is pre-existing `:heimdall:checkstyleMain`: 41 files / 109 warnings / 2 info.

Bounded fixes:
- restored missing `Any` / `Dict` Bifrost imports.
- secondary CI installs Bifrost with `pip install -e .`.
- accidental feedback-lane documentation regression removed before merge.

## P0-B2 — PASS / MERGED

Issue #6: CLOSED. PR #7: MERGED.
- final exact head: `4c5404642cb68594538396f00d89558fea7c655f`
- merged main SHA: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`

Merged scope:
- `bifrost/frontend/index.html`
- `bifrost/frontend/src/main.jsx`
- `bifrost/frontend/src/App.jsx`
- `bifrost/frontend/src/index.css`
- bounded `.github/workflows/ci-cd.yml` install correction

Executed evidence:
- primary CI `32262906086`: SUCCESS.
- secondary Frontend: install/build/artifact SUCCESS.
- secondary Bifrost: SUCCESS.
- dependency security: SUCCESS.
- secondary Heimdall: same pre-existing checkstyle debt, not a PR #7 regression.

Acceptance:
- [x] frontend install executable
- [x] frontend production build executable
- [x] no fake operational data
- [x] four-file product repair scope preserved
- [ ] frontend `npm run dev` root reachability — carried to P0-B3
- [ ] root default `build-all.ps1` frontend path — carried to P0-B3

---

# 6. Active Phase 0 Slice — P0-B3

## Issue / PR
- **Issue #8**: OPEN
- **PR #9**: OPEN
- **Branch**: `agent/p0-b3-uc01-startup-proof`
- **Exact head at creation**: `1f50afc4ff2c4590178bfce14f250866339bd9e6`

## Goal
Close the smallest remaining UC-01 proof debt without product expansion:
1. execute frontend dev-server `/` reachability;
2. execute the repository default root build path without `-SkipFrontend` and prove whether it reaches a successful frontend build.

## Authorized Scope
Only the minimum CI/proof harness required to execute those two checks.

Current PR #9 change:
- `.github/workflows/ci.yml` only.
- Ubuntu job: install frontend deps → start Vite dev server → HTTP GET `/` → upload evidence.
- Windows job: JDK 21 / Python 3.11 / Node 20 → execute `build-all.ps1 -SkipTests` without `-SkipFrontend` → require successful frontend build marker → upload evidence.

## Acceptance Criteria
- [ ] `npm install` succeeds in `bifrost/frontend` under exact-head GitHub execution.
- [ ] `npm run dev` starts and HTTP GET `/` succeeds.
- [ ] root `build-all.ps1 -SkipTests` executes without `-SkipFrontend`.
- [ ] default build path reaches and completes frontend build step.
- [x] no product UI expansion introduced by the proof harness.
- [x] no Heimdall broad checkstyle cleanup added.

## Important Boundary
If the Windows default build path stops before frontend because of the already-known Heimdall `checkstyleMain` debt, record that as executed default-path boundary evidence. **Do not broaden Issue #8 into mass checkstyle cleanup merely to manufacture green.**

## Current Result

**IN PROGRESS — exact-head PR execution not yet observed.**

---

# 7. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 |
| E-002 | PR #3 merge | VERIFIED | `888f2c...` |
| E-003 | P0-B1 bounded repair | VERIFIED / MERGED | PR #4 |
| E-004 | PR #4 primary unit tests | VERIFIED GREEN | run `32262136812` |
| E-005 | PR #4 secondary Bifrost | VERIFIED GREEN | run `32262136715` |
| E-006 | Phase 0 runtime versions | VERIFIED | Java 21.0.12 / Python 3.11.16 / Node 20.20.2 / npm 10.8.2 / Docker 28.0.4 |
| E-007 | Frontend pre-repair build | FAILED EXECUTED | missing `index.html` |
| E-008 | Heimdall secondary build | VERIFIED RED / PRE-EXISTING | checkstyle debt |
| E-009 | Issue #6 lifecycle | VERIFIED / CLOSED | issue-first lifecycle |
| E-010 | PR #7 frontend repair | VERIFIED / MERGED | bounded boot shell |
| E-011 | PR #7 primary CI | VERIFIED GREEN | run `32262906086` |
| E-012 | PR #7 secondary Frontend | VERIFIED GREEN | run `32262906127` |
| E-013 | PR #7 secondary Bifrost | VERIFIED GREEN | run `32262906127` |
| E-014 | PR #7 dependency security | VERIFIED GREEN | run `32262906127` |
| E-015 | PR #7 Heimdall failure classification | VERIFIED RED / PRE-EXISTING | 41 / 109 / 2 |
| E-016 | Frontend dev-server root reachability | EXECUTION PENDING | Issue #8 / PR #9 |
| E-017 | Root default build path | EXECUTION PENDING | Issue #8 / PR #9 |
| E-018 | Real Local AI E2E | PENDING | |
| E-019 | Local vs Cloud Routing | PENDING | |
| E-020 | DLQ → Redrive → Success | PENDING | |
| E-021 | Grafana live metrics | PENDING | |
| E-022 | Final Demo | PENDING | |
| E-023 | HP AI Server reference run | PENDING | |

---

# 8. Known Debt / Risks

| ID | Risk | Required handling |
|---|---|---|
| R-001 | P0-B3 exact-head execution pending | inspect PR-visible workflows before any merge |
| R-002 | Root default build may stop at pre-existing Heimdall checkstyle | classify boundary; do not mass-fix outside a separately authorized gap |
| R-003 | Broad Heimdall checkstyle debt | no unrelated mass-fix |
| R-004 | README overclaim | publish evidence-backed claims only |
| R-005 | Fallback-only E2E | real-model evidence mandatory |
| R-006 | Scope explosion | keep Frozen Scope |
| R-007 | Agent self-report without remote/executed proof | never treat as proof |

Known later proof-hardening debt:
- README Grafana port drift (`3000` vs Compose `3001`)
- unsupported production/compliance/performance claims

---

# 9. Work Item / PR Lifecycle

1. Read MASTER first.
2. Active focused PR first.
3. Otherwise search for one existing open Issue matching the exact next MASTER-authorized gap.
4. If none exists, create exactly one bounded Issue before new implementation/proof work.
5. Issue body: Goal / Scope / Acceptance Criteria / Verification / Non-goals / Evidence Required.
6. One active implementation Issue by default.
7. CI/review corrections inside the active gap stay in the same Issue/PR.
8. PR links Issue and records Changed / Actually Executed / Verified / Not Verified / Risks.
9. RED → inspect first concrete failing evidence; fix only smallest active-slice defect.
10. GREEN bounded acceptance + clean review/security state → merge with expected-head guard.
11. Issue closes only after required verification + merged acceptance.
12. Reconcile MASTER on `main` before selecting another gap.
13. Re-evaluate Human Review/FREEZE before another Issue.

**Ordinary bounded intermediate PR merges do not require human approval.**

**Human Review remains the FINAL v1.0 gate.**

---

# 10. Required Completion Report

Every iteration records:
- **What Changed**
- **What Was Executed**
- **What Was Not Verified**
- **Remaining Risks**
- **Result**
- **Next**

Rules:
- Agent self-report ≠ proof
- Executed evidence beats static inference
- Missing CI status ≠ PASS
- Same blocker loop prohibited
- Experimental scope prohibited before Core completion
- MASTER synchronized before product changes

---

# 11. Current Checkpoint

## Result

**P0-B1 PASS / P0-B2 PASS / P0-B3 IN PROGRESS.**

Issue #8 and PR #9 now exist for the exact two proof debts intentionally left open after P0-B2. No product implementation was added in this slice; only executable verification was added.

## What Changed
- Re-read current merged MASTER and confirmed P0-B2 PASS.
- Searched current open Issues; no exact UC-01 proof Issue existed.
- Created Issue #8 before new work.
- Created branch `agent/p0-b3-uc01-startup-proof`.
- Added bounded PR-visible CI proof for frontend dev root reachability and Windows root build path.
- Opened PR #9 linked with `Closes #8`.
- Reconciled MASTER on `main` to P0-B3 IN PROGRESS.

## What Was Executed
- Current repository MASTER read.
- Open-Issue search.
- Issue #8 creation.
- Branch creation.
- CI proof-harness commit `1f50afc4ff2c4590178bfce14f250866339bd9e6`.
- PR #9 creation.
- PR metadata re-fetch confirming exact head `1f50afc4...` and mergeable state.

## What Was Not Verified
- PR #9 exact-head workflow result.
- `npm run dev` root reachability.
- default root `build-all.ps1` reaching frontend.
- Compose startup / full UC-01 closure.
- real Local AI E2E.
- Local vs Cloud routing execution.
- DLQ → Redrive → Success execution.
- Grafana live evidence.

## Remaining Risks
- The Windows default build path may fail before frontend at already-known Heimdall checkstyle debt.
- A workflow defect may appear in the newly added proof jobs; only concrete active-slice defects may be fixed.
- UC-01 full service-health closure remains outside this small proof slice.

## NEXT

**Fetch current PR #9 exact head and PR-visible workflow/review state. If RED, inspect the first concrete failing P0-B3 step and fix only the smallest Issue #8-scoped defect. If frontend dev reachability is GREEN and the default build path stops only at already-classified unrelated Heimdall checkstyle debt, record that distinction and evaluate whether P0-B3 can close as partial executed proof or whether the root build contract itself requires a separately authorized repair. Do not broaden Issue #8 into product UI or broad checkstyle cleanup.**
