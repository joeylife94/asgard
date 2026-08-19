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
- **Status**: PARTIAL EXECUTION VERIFIED; PR #9 STILL RUNNING
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **Issue #8**: OPEN
- **PR #9**: OPEN
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
- bounded Bifrost typing imports and editable-install CI correction merged.

## P0-B2 — PASS / MERGED
- Issue #6 CLOSED; PR #7 merged at `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`.
- frontend boot tree restored with four product files only.
- exact-head production frontend build GREEN.
- secondary Bifrost and dependency security GREEN.
- same pre-existing Heimdall checkstyle debt remained unrelated.
- `npm run dev` root reachability and root `build-all.ps1` frontend-path execution intentionally carried forward as proof debt.

---

# 5. Active Phase 0 Slice — P0-B3

## Issue / PR
- **Issue #8**: `P0-B3: verify UC-01 frontend startup and default build path`
- **PR #9**: `test: verify UC-01 frontend startup proof`
- **Branch**: `agent/p0-b3-uc01-startup-proof`
- **Exact head**: `1f50afc4ff2c4590178bfce14f250866339bd9e6`

## Goal
Close only the two remaining frontend/startup proof debts from P0-B2:
1. execute Vite dev-server root reachability;
2. execute root `build-all.ps1 -SkipTests` without `-SkipFrontend` and determine whether the default path reaches a successful frontend build.

## Authorized Scope
`.github/workflows/ci.yml` only, unless exact-head executed evidence exposes a concrete Issue #8-scoped defect.

## Current Exact-Head Evidence

Primary CI run `32273762721`:
- **UC-01 frontend dev root reachability: GREEN**.
- frontend dependency install: success.
- Vite dev server start: success.
- HTTP GET `http://127.0.0.1:3000/`: success on attempt 2.
- evidence artifact uploaded successfully (`p0-b3-frontend-dev-evidence`).
- Phase 0 preflight frontend install/build: GREEN.
- default Windows build-path job: still IN PROGRESS at last observation.
- unit job: still IN PROGRESS at last observation.

Secondary CI/CD run `32273762445`:
- IN PROGRESS at last observation.

## Acceptance Criteria
- [x] `npm install` succeeds in `bifrost/frontend` under exact-head GitHub execution.
- [x] `npm run dev` starts successfully.
- [x] HTTP GET `/` returns success under exact-head GitHub execution.
- [ ] root `build-all.ps1 -SkipTests` execution result observed.
- [ ] default build path reaches and completes frontend build step.
- [x] no product UI expansion.
- [x] no broad Heimdall cleanup.

## Boundary Rule
If the Windows default build path stops before frontend because of already-known Heimdall `checkstyleMain` debt, record that as executed root-build boundary evidence. Do **not** broaden Issue #8 into mass checkstyle cleanup merely to manufacture green.

## Result
**IN PROGRESS — E-016 is now verified; E-017 remains pending exact-head execution result.**

---

# 6. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 |
| E-002 | P0-B1 bounded repair | VERIFIED / MERGED | PR #4 |
| E-003 | Phase 0 runtime versions | VERIFIED | Java 21 / Python 3.11 / Node 20 / npm 10 / Docker 28 |
| E-004 | Heimdall secondary checkstyle debt | VERIFIED RED / PRE-EXISTING | 41 / 109 / 2 |
| E-005 | P0-B2 frontend repair | VERIFIED / MERGED | PR #7 |
| E-006 | P0-B2 frontend production build | VERIFIED GREEN | PR #7 |
| E-016 | Frontend dev-server root reachability | VERIFIED GREEN | PR #9 run `32273762721`; root reachable attempt 2 |
| E-017 | Root default build path | EXECUTION IN PROGRESS | PR #9 Windows job |
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
| R-001 | PR #9 Windows default-build result still pending | re-fetch exact-head job before any merge |
| R-002 | root build may stop at pre-existing Heimdall checkstyle | classify boundary; no unrelated mass-fix |
| R-003 | broad Heimdall checkstyle debt | separate future work only if MASTER authorizes |
| R-004 | README overclaim / Grafana port drift | proof-hardening later |
| R-005 | fallback-only E2E risk | real-model evidence mandatory |
| R-006 | scope explosion | keep Frozen Scope |
| R-007 | agent self-report without executed proof | never count as PASS |

---

# 8. Work Item / PR Lifecycle

1. Read MASTER first.
2. Active focused PR first.
3. Otherwise find one existing Issue matching the next exact acceptance gap.
4. If none exists, create one bounded Issue before new work.
5. Issue requires Goal / Scope / Acceptance Criteria / Verification / Non-goals / Evidence Required.
6. One active implementation Issue by default.
7. CI/review corrections inside the active gap stay in the same Issue/PR.
8. RED → first concrete failing evidence → smallest in-scope fix only.
9. GREEN bounded acceptance + clean review/security state → merge with expected-head guard.
10. Issue closes after executed acceptance + merge.
11. Reconcile MASTER on `main` before another Issue.
12. Re-evaluate Human Review/FREEZE before another Issue.

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

The frontend dev-server proof debt is now closed with executed evidence. Root default build-path evidence remains active on the same PR.

## What Changed
- Read authoritative MASTER first.
- Confirmed no matching existing open UC-01 Issue; created Issue #8.
- Created branch `agent/p0-b3-uc01-startup-proof`.
- Added bounded GitHub-hosted UC-01 proof jobs only.
- Opened PR #9 linked with `Closes #8`.
- Reconciled MASTER to P0-B3.
- Observed PR #9 exact-head primary CI and captured concrete successful frontend dev-server evidence.

## What Was Executed
- exact-head PR #9 workflow lookup.
- primary workflow job inspection.
- concrete `UC-01 frontend dev root reachability` log inspection.
- `npm install` succeeded.
- Vite dev server launched.
- first curl failed while server initialized; second curl succeeded against `127.0.0.1:3000/`.
- evidence artifact upload succeeded.

## What Was Not Verified
- final Windows default-build result.
- final primary unit-job result.
- final secondary CI/CD result.
- Compose/full-stack startup / UC-01 full service-health closure.
- real Local AI E2E.
- Local vs Cloud routing execution.
- DLQ → Redrive → Success.
- Grafana live evidence.

## Remaining Risks
- root build may stop before frontend at already-classified Heimdall checkstyle debt.
- newly added Windows proof harness may expose an Issue #8-scoped workflow defect.
- UC-01 full service-health closure remains outside this bounded slice.

## NEXT
**Re-fetch current PR #9 exact head and workflow/review state. Inspect the Windows `UC-01 default build path` result first. If RED, inspect the concrete failing step/log and distinguish an Issue #8 proof-harness defect from the pre-existing Heimdall checkstyle boundary. Fix only a concrete Issue #8-scoped defect. If bounded acceptance is satisfied and review/security state is clean, merge with expected-head guard, close Issue #8, and reconcile MASTER before selecting another gap.**
