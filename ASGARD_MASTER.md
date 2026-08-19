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
- **Status**: BUILD-CONTRACT REPAIR PR #10 OPEN; EXACT-HEAD EXECUTION PENDING
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **PR #9 proof-harness merge**: `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`
- **Issue #8**: OPEN
- **PR #10**: OPEN — `fix: make SkipTests use Heimdall assemble path`
- **PR #10 exact head**: `dc8cc524bb2f10e8b5674cfcc98247882782a82a`
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
- Heimdall broad `checkstyleMain` debt classified as pre-existing: **41 files / 109 warnings / 2 info**.

## P0-B2 — PASS / MERGED
- Issue #6 CLOSED; PR #7 merged at `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`.
- minimal four-file frontend boot tree restored.
- exact-head production frontend build GREEN.

---

# 5. Active Phase 0 Slice — P0-B3

## Issue / PR
- **Issue #8**: `P0-B3: verify UC-01 frontend startup and default build path`
- **PR #9**: proof harness merged at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`
- **PR #10**: bounded build-contract repair, OPEN
- **PR #10 exact head**: `dc8cc524bb2f10e8b5674cfcc98247882782a82a`

## Goal
Close the two frontend/startup proof debts from P0-B2:
1. Vite dev-server root reachability;
2. root `build-all.ps1 -SkipTests` without `-SkipFrontend`, including a successful frontend build step.

## Executed Evidence Before PR #10

PR #9 exact head `1f50afc4ff2c4590178bfce14f250866339bd9e6`, primary run `32273762721`:
- frontend dependency install: GREEN.
- Vite dev server: GREEN.
- HTTP GET `http://127.0.0.1:3000/`: GREEN on attempt 2.
- Phase 0 frontend install/build preflight: GREEN.
- primary Heimdall + Bifrost unit job: GREEN.
- Windows `build-all.ps1 -SkipTests`: EXECUTED RED before Frontend.
- failure boundary: `:heimdall:checkstyleMain`, exactly the known **41 files / 109 warnings / 2 info** debt.
- evidence artifact uploaded.

## Acceptance Criteria
- [x] `npm install` succeeds in `bifrost/frontend` under GitHub-hosted execution.
- [x] `npm run dev` starts successfully.
- [x] HTTP GET `/` returns success.
- [x] root `build-all.ps1 -SkipTests` execution result observed.
- [ ] default build path reaches and completes frontend build step.
- [x] no product UI expansion.
- [x] no broad Heimdall cleanup.

## Root-Build Contract Decision
The original `-SkipTests` path used:

```text
:heimdall:clean :heimdall:build -x test
```

Gradle `build` still executes `checkstyleMain`, so the explicit SkipTests artifact path could not progress through the unified build despite the style debt already being classified separately.

### PR #10 Authorized Repair
Only `build-all.ps1` changes:
- `-SkipTests` → `:heimdall:clean :heimdall:assemble`.
- normal build without `-SkipTests` → unchanged full `:heimdall:build`.
- no Checkstyle rule/config change.
- no global quality-gate suppression.
- no Heimdall style cleanup.
- no product/frontend change.

### PR #10 Acceptance
- [ ] exact-head Windows `build-all.ps1 -SkipTests` reaches Frontend.
- [ ] Frontend build succeeds in the unified path.
- [ ] primary Heimdall+Bifrost unit job remains GREEN.
- [ ] no global checkstyle suppression / broad cleanup.

## Result
**IN PROGRESS — E-016 PASS; E-017 has executed RED evidence; PR #10 is the smallest authorized repair and awaits exact-head execution.**

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
| E-017 | Root default build path | REPAIR IN PROGRESS | PR #9 proved pre-Frontend checkstyle block; PR #10 tests bounded SkipTests artifact-path correction |
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
| R-001 | PR #10 may expose a new unified-build failure after Heimdall | inspect first concrete RED; fix only Issue #8 scope |
| R-002 | broad Heimdall checkstyle debt | keep visible; do not mass-fix in P0-B3 |
| R-003 | assemble could accidentally weaken normal quality gates | normal full `build` must remain unchanged |
| R-004 | README overclaim / Grafana port drift | proof-hardening later |
| R-005 | fallback-only E2E risk | real-model evidence mandatory |
| R-006 | scope explosion | keep Frozen Scope |
| R-007 | agent self-report without executed proof | never count as PASS |

---

# 8. Work Item / PR Lifecycle

1. Read MASTER first.
2. Active focused PR first.
3. Do not create another Issue while Issue #8 remains active.
4. Corrections inside this gap stay under Issue #8 / PR #10 where possible.
5. RED → first concrete failing evidence → smallest in-scope fix only.
6. GREEN bounded acceptance + clean review/security state → merge with expected-head guard.
7. Issue closes only after executed acceptance + merge.
8. Reconcile MASTER on `main` before another Issue.
9. Re-evaluate Human Review/FREEZE before another Issue.

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

The dev-server portion is proven GREEN. PR #9 proved the unified build currently stops in Heimdall checkstyle before Frontend. That proof harness is merged and Issue #8 remains open. PR #10 now contains the single bounded build-contract correction authorized by this MASTER.

## What Changed
- Read authoritative MASTER first.
- Re-fetched PR #9 exact-head completed runs/review state.
- Inspected the Windows failure log and confirmed the exact known checkstyle boundary.
- Removed `Closes #8` from PR #9 because acceptance was incomplete.
- Merged PR #9 with expected-head guard at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`.
- Reconciled MASTER before new product change.
- Under existing Issue #8, created branch `agent/p0-b3-skiptests-build-contract`.
- Changed only the Heimdall SkipTests path in `build-all.ps1` to use `assemble`; normal full build remains unchanged.
- Opened PR #10 at exact head `dc8cc524bb2f10e8b5674cfcc98247882782a82a`.

## What Was Executed
- PR #9 primary/secondary job inspection.
- Windows job full log inspection.
- exact-head unit job GREEN verification.
- dev-server root GREEN verification.
- PR #9 expected-head squash merge.
- PR #10 workflow lookup immediately after opening; no PR-visible run had appeared yet at that observation.

## What Was Not Verified
- PR #10 exact-head Windows unified build result.
- PR #10 exact-head primary unit result.
- Compose/full-stack startup / UC-01 full service-health closure.
- real Local AI E2E.
- Local vs Cloud routing execution.
- DLQ → Redrive → Success.
- Grafana live evidence.

## Remaining Risks
- unified build may expose another concrete failure after Heimdall assembly.
- broad checkstyle debt remains visible in normal full-build/secondary CI paths.
- UC-01 full service-health closure remains outside this bounded slice.

## NEXT
**Re-fetch current PR #10 exact head and PR-visible workflows/review. Inspect the Windows `UC-01 default build path` job first. If RED, inspect the first concrete failing step/log and fix only an Issue #8-scoped defect. If Windows unified build reaches/completes Frontend, primary unit checks remain GREEN, and review/security state is clean, merge PR #10 with expected-head guard, close Issue #8, and reconcile MASTER before selecting another gap.**
