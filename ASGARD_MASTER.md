# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> This file is the single source of truth for Asgard v1.0 execution. README and agent self-report do not override executed evidence recorded here.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B2 — Minimal Frontend Boot-Shell Repair
- **Batch Result**: PASS / MERGED
- **Status**: READY FOR NEXT BOUNDED GAP
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Original code baseline**: `bca6567919cbcac3f9039268c09526b25179f370`
- **PR #3 execution merge**: `888f2c5694940fe42284466fb57a0b33b2ec73cd`
- **PR #4 bounded repair merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **PR #7 frontend boot-shell merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
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

## SUPPORTING — Core에서 실제 사용 시 유지
- Circuit Breaker
- Smart Cache
- Quality Metrics
- Redis / Elasticsearch / Tracing

## EXPERIMENTAL — v1.0 Gate에 영향 없음
- Feedback feature expansion
- A/B Testing expansion
- Advanced Routing expansion
- Additional Providers
- Interview-specific features

**Rule:** Experimental 개선은 Core PASS 이후에만 허용.

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

# 5. Closed Phase 0 Slice — P0-B1 PASS

## PR #4
- final exact head: `1d301377a5951962cb3afd4e653a1975b8a2267a`
- merged main SHA: `fa3f129783387fbeafae537e8a22b4629faf6d42`

Bounded changes:
- restored missing `Any` / `Dict` typing imports in Bifrost.
- secondary CI installs Bifrost with `pip install -e .` before lint/tests.
- accidental feedback-lane documentation regression removed before merge.

Executed evidence:
- primary CI `32262136812`: Heimdall + Bifrost unit job GREEN.
- secondary CI/CD `32262136715`: Bifrost install/lint/pytest/coverage GREEN.
- dependency security GREEN.
- Heimdall secondary build RED at pre-existing `:heimdall:checkstyleMain`: 41 files, 109 warnings + 2 info. **Do not mass-fix in unrelated slices.**

---

# 6. Closed Phase 0 Slice — P0-B2 PASS

## Issue / PR
- **Issue #6**: CLOSED
- **PR #7**: MERGED
- **Final exact head**: `4c5404642cb68594538396f00d89558fea7c655f`
- **Merged main SHA**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`

## Goal
Restore the minimum tracked Vite/React boot tree required to make the existing frontend build contract executable without product UI expansion.

## Merged Scope
- `bifrost/frontend/index.html`
- `bifrost/frontend/src/main.jsx`
- `bifrost/frontend/src/App.jsx`
- `bifrost/frontend/src/index.css`
- `.github/workflows/ci-cd.yml` only for the evidence-required frontend install correction (`npm ci` without lockfile → bounded `npm install`).

## Executed Exact-Head Evidence

PR-visible primary `CI` run `32262906086` on exact head `4c540464...`:
- **SUCCESS**.

PR-visible secondary `CI/CD Pipeline` run `32262906127` on the same exact head:
- `Build & Test Frontend`: **SUCCESS**.
  - Node setup: success
  - dependency install: success
  - lint step: success
  - production bundle build: success
  - artifact upload: success
- `Build & Test Bifrost`: **SUCCESS**.
- `Dependency Security Check`: **SUCCESS**.
- `Build & Test Heimdall`: **FAILURE**, confirmed unrelated/pre-existing at `:heimdall:checkstyleMain` with **41 files / 109 warnings / 2 info**. This is the same classified debt from P0-B1 and is not a PR #7 regression.

Review state before merge:
- no inline review threads.
- no submitted reviews blocking merge.

## Acceptance Classification
- [x] `npm install` succeeds under exact-head PR execution.
- [x] `npm run build` / production bundle build succeeds under exact-head PR execution.
- [x] secondary Frontend CI reaches and executes build successfully.
- [x] no fake operational data introduced.
- [x] product implementation stayed inside frozen four-file scope.
- [x] only extra file was the evidence-required CI correction.
- [ ] `npm run dev` root reachability — **NOT VERIFIED** by current CI.
- [ ] default root `build-all.ps1` frontend-step execution — **NOT VERIFIED** directly; frontend production build itself is verified.

## Result

**PASS / MERGED** for the bounded P0-B2 repair. The two unexecuted acceptance items remain explicit proof debt and must not be represented as verified.

---

# 7. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 |
| E-002 | PR #3 merge | VERIFIED | `888f2c5694940fe42284466fb57a0b33b2ec73cd` |
| E-003 | P0-B1 bounded repair | VERIFIED / MERGED | PR #4 → `fa3f129...` |
| E-004 | PR #4 primary unit tests | VERIFIED GREEN | run `32262136812` |
| E-005 | PR #4 secondary Bifrost | VERIFIED GREEN | run `32262136715` |
| E-006 | Phase 0 runtime versions | VERIFIED | Java 21.0.12 / Python 3.11.16 / Node 20.20.2 / npm 10.8.2 / Docker 28.0.4 |
| E-007 | Frontend pre-repair build | FAILED EXECUTED | missing `index.html` |
| E-008 | Heimdall secondary build | VERIFIED RED / PRE-EXISTING | checkstyle debt |
| E-009 | Issue #6 lifecycle | VERIFIED / CLOSED | issue-first lifecycle |
| E-010 | PR #7 bounded frontend diff | VERIFIED / MERGED | four boot files + bounded CI correction |
| E-011 | PR #7 primary CI | VERIFIED GREEN | run `32262906086` |
| E-012 | PR #7 secondary Frontend | VERIFIED GREEN | run `32262906127` |
| E-013 | PR #7 secondary Bifrost | VERIFIED GREEN | run `32262906127` |
| E-014 | PR #7 dependency security | VERIFIED GREEN | run `32262906127` |
| E-015 | PR #7 Heimdall failure classification | VERIFIED RED / PRE-EXISTING | checkstyleMain 41 / 109 / 2 |
| E-016 | Frontend dev-server root reachability | PENDING | not executed |
| E-017 | Root default build path | PENDING | not executed directly |
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
| R-001 | Frontend dev-server reachability not yet executed | preserve as proof debt; verify in later startup slice |
| R-002 | Root default build path not directly executed | verify before UC-01 closure |
| R-003 | Broad Heimdall checkstyle debt | classify separately; no unrelated mass-fix |
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
6. Default one active implementation Issue at a time.
7. CI/review corrections inside that gap stay in the same Issue/PR.
8. PR links the Issue and records Changed / Actually Executed / Verified / Not Verified / Risks.
9. RED → inspect first concrete failing job/step/log; fix only smallest active-slice defect.
10. GREEN bounded acceptance + clean review/security state → merge with expected-head guard rather than idle.
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

**P0-B1 PASS / P0-B2 PASS.** Issue #6 is closed and PR #7 is merged. The missing frontend Vite entry/source defect is repaired and the exact-head production frontend build is executed GREEN. The secondary Heimdall RED remains the same pre-existing broad checkstyle debt and was deliberately not expanded into Issue #6.

## What Changed
- Inspected current PR #7 exact head and both PR-visible workflows.
- Confirmed primary CI success.
- Inspected secondary workflow jobs and concrete Heimdall failure log.
- Confirmed Frontend install/build/artifact job success.
- Confirmed Heimdall failure is the already-classified `checkstyleMain` debt, not a PR #7 regression.
- Confirmed no review threads/reviews blocked the bounded merge.
- Merged PR #7 with expected-head guard.
- Confirmed Issue #6 auto-closed.
- Reconciled this MASTER on `main`.

## What Was Executed
- PR #7 exact-head workflow lookup.
- Secondary workflow job inspection.
- Concrete Heimdall job-log inspection.
- Review-thread/review inspection.
- Expected-head squash merge.
- Issue #6 closure verification.

## What Was Not Verified
- `npm run dev` root reachability.
- direct execution of root `build-all.ps1` frontend step.
- Compose startup / UC-01 closure.
- real Local AI E2E.
- Local vs Cloud routing execution.
- DLQ → Redrive → Success execution.
- Grafana live evidence.

## Remaining Risks
- UC-01 still needs startup/runtime proof, including frontend root reachability.
- Real-model, routing, recovery, observability, and final proof evidence remain pending.
- Broad Heimdall checkstyle debt remains pre-existing and should be handled only when a MASTER-authorized gap requires it.

## NEXT

**Re-read this merged checkpoint, search for an existing open Issue matching the smallest remaining Phase 0 acceptance gap. If none exists, create exactly one bounded Issue for executable UC-01 startup verification (including frontend dev-server root reachability and the default repository frontend build path) before any new implementation. Do not broaden into product UI or Heimdall checkstyle cleanup.**
