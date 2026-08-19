# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> This file is the single source of truth for Asgard v1.0 execution. README and agent self-report do not override executed evidence recorded here.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B2 — Minimal Frontend Boot-Shell Repair
- **Active Issue**: #6 — `P0-B2: restore minimal frontend boot shell`
- **Active PR**: #7 — `fix: restore minimal frontend boot shell`
- **Active PR Branch**: `agent/p0-b2-frontend-boot-shell`
- **Current exact head**: `4c5404642cb68594538396f00d89558fea7c655f`
- **Batch Result**: IN PROGRESS
- **Status**: IN PROGRESS
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Original code baseline**: `bca6567919cbcac3f9039268c09526b25179f370`
- **PR #3 execution merge**: `888f2c5694940fe42284466fb57a0b33b2ec73cd`
- **PR #4 bounded repair merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **Updated**: 2026-08-19
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

Final bounded changes:
- `bifrost/bifrost/api.py`: restore missing `Any` / `Dict` typing imports.
- `.github/workflows/ci-cd.yml`: install Bifrost itself with `pip install -e .` before secondary lint/tests.
- accidental feedback lane documentation regression removed before merge.

Executed exact-head evidence:
- primary CI `32262136812`: Heimdall + Bifrost unit job GREEN.
- secondary CI/CD `32262136715`: Bifrost install/lint/pytest/coverage GREEN.
- dependency security job GREEN.
- frontend preflight RED only at missing `index.html` boundary.
- Heimdall secondary build RED at pre-existing `:heimdall:checkstyleMain`: 41 files, 109 warnings + 2 info. **Do not mass-fix in unrelated slices.**

---

# 6. Active Slice — P0-B2 Frontend Boot Shell

## Issue / PR
- **Issue #6**: OPEN
- **PR #7**: OPEN
- **Exact head**: `4c5404642cb68594538396f00d89558fea7c655f`

## Goal
Restore the minimum tracked Vite/React boot tree required to make the existing frontend build/startup contract executable. No product UI expansion.

## Product repair scope
- `bifrost/frontend/index.html`
- `bifrost/frontend/src/main.jsx`
- `bifrost/frontend/src/App.jsx`
- `bifrost/frontend/src/index.css`

Implemented on PR #7:
- [x] Vite HTML entrypoint
- [x] React root bootstrap
- [x] minimal human-visible Asgard boot shell
- [x] minimal readable styling
- [x] no fake metrics/jobs/API integration/product feature expansion

## Evidence-required CI correction

PR #7 first secondary Frontend job reached `actions/setup-node@v4` and failed before install/build because workflow required nonexistent:

`bifrost/frontend/package-lock.json`

The same job also used `npm ci`, which requires a lockfile. This is executed evidence that the verification contract itself was not executable.

Issue #6 scope was therefore minimally expanded to allow exactly one additional file:
- `.github/workflows/ci-cd.yml`

Correction committed at PR #7 exact head `4c5404642cb68594538396f00d89558fea7c655f`:
- remove npm cache configuration tied to nonexistent lockfile.
- replace `npm ci` with `npm install --no-audit --no-fund`.
- no unrelated workflow refactor.

## Acceptance Criteria
- [ ] `npm install` succeeds on current exact head.
- [ ] `npm run build` exits 0 on current exact head.
- [ ] `npm run dev` serves a reachable root page.
- [ ] default repository build path completes the frontend step.
- [ ] secondary Frontend CI reaches and executes build step.
- [x] no fake operational data introduced.
- [x] product implementation stays inside frozen four-file scope.
- [x] only evidence-required extra file is the bounded secondary-CI correction.

## Current exact-head execution

New PR-visible workflows for `4c5404642cb68594538396f00d89558fea7c655f`:
- primary `CI` run `32262906086`: QUEUED at last observation.
- secondary `CI/CD Pipeline` run `32262906127`: QUEUED at last observation.

Previous PR #7 head `baf957a21b07f2fdccb07f2b97c411a3d92d217d` evidence:
- primary frontend preflight started normal install/build execution.
- secondary Frontend job FAILED at Node setup because `package-lock.json` did not exist; build never ran.
- this failure directly justified the bounded workflow correction above.

## Closure Condition

**Frontend build/startup contract is executable and verified, without adding product features.**

Do not merge PR #7 until current exact-head evidence establishes the applicable acceptance criteria and review/security state is clean. Any remaining unexecutable acceptance item must be recorded explicitly rather than inferred PASS.

---

# 7. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 |
| E-002 | PR #3 merge | VERIFIED | `888f2c5694940fe42284466fb57a0b33b2ec73cd` |
| E-003 | P0-B1 bounded repair | VERIFIED / MERGED | PR #4 → `fa3f129783387fbeafae537e8a22b4629faf6d42` |
| E-004 | PR #4 primary unit tests | VERIFIED GREEN | run `32262136812` |
| E-005 | PR #4 secondary Bifrost | VERIFIED GREEN | run `32262136715` |
| E-006 | Phase 0 runtime versions | VERIFIED | Java 21.0.12 / Python 3.11.16 / Node 20.20.2 / npm 10.8.2 / Docker 28.0.4 |
| E-007 | Frontend pre-repair npm install | VERIFIED GREEN | exact executed preflight |
| E-008 | Frontend pre-repair build | FAILED EXECUTED | missing `index.html` |
| E-009 | Heimdall secondary build | VERIFIED RED / PRE-EXISTING | checkstyle debt |
| E-010 | Issue #6 lifecycle | VERIFIED | created before P0-B2 implementation |
| E-011 | PR #7 initial bounded product diff | VERIFIED STATIC | four frontend files only |
| E-012 | PR #7 secondary Frontend CI | FAILED EXECUTED / CONTRACT | nonexistent lockfile blocks setup |
| E-013 | PR #7 CI contract repair | IMPLEMENTED / RE-EXECUTION PENDING | current head `4c540464...` |
| E-014 | Real Local AI E2E | PENDING | |
| E-015 | Local vs Cloud Routing | PENDING | |
| E-016 | DLQ → Redrive → Success | PENDING | |
| E-017 | Grafana live metrics | PENDING | |
| E-018 | Final Demo | PENDING | |
| E-019 | HP AI Server reference run | PENDING | |

---

# 8. Known Debt / Risks

| ID | Risk | Required handling |
|---|---|---|
| R-001 | Frontend acceptance not yet re-executed after CI fix | inspect current PR #7 exact-head workflows first |
| R-002 | Broad Heimdall checkstyle debt | classify separately; no unrelated mass-fix |
| R-003 | README overclaim | publish evidence-backed claims only |
| R-004 | Fallback-only E2E | real-model evidence mandatory |
| R-005 | Scope explosion | keep Frozen Scope |
| R-006 | Missing workflow status | missing ≠ PASS/FAIL; prefer PR-visible execution |
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

**P0-B1 PASS / P0-B2 IN PROGRESS.** PR #4 is merged. Issue #6 and PR #7 now own the next proven Core defect: the missing frontend boot tree. The four-file boot shell is implemented. Exact execution exposed and then corrected one CI verification-contract defect; the corrected exact-head workflows are now pending execution.

## What Changed
- Completed PR #4 remote review correction, exact-head verification, expected-head merge, and MASTER reconciliation.
- Created Issue #6 before new frontend implementation.
- Created PR #7 with exactly the frozen four frontend boot-shell files.
- Inspected first PR #7 secondary Frontend failure.
- Proved it failed before frontend execution because CI referenced nonexistent `package-lock.json` and used `npm ci` without a lockfile.
- Updated Issue #6 with the evidence-required CI correction boundary.
- Corrected only the secondary Frontend CI install contract on the same PR.

## What Was Executed
- PR #4 branch mutation, review resolution, exact-head CI inspection, and merge.
- Issue search and Issue #6 creation.
- PR #7 branch/file creation and PR creation.
- PR #7 exact-head workflow lookup.
- Secondary Frontend CI job/log inspection on initial PR #7 head.
- CI correction commit triggering new exact-head workflows.

## What Was Not Verified
- `npm install` success on current PR #7 exact head.
- `npm run build` success on current PR #7 exact head.
- `npm run dev` root reachability.
- default repository build path frontend-step success.
- current exact-head PR #7 review/security state after CI settles.
- Compose/E2E/real AI/Grafana live evidence.

## Remaining Risks
- PR #7 may expose another concrete frontend build/startup defect when the new exact-head jobs run.
- Secondary Heimdall checkstyle debt remains pre-existing and unrelated.
- Real-model, recovery, observability, and final proof evidence remain pending.

## NEXT

**Inspect PR #7 exact-head `4c5404642cb68594538396f00d89558fea7c655f` PR-visible workflows `32262906086` and `32262906127`. If RED, inspect the first concrete active-slice failure and make only the smallest Issue #6-scoped correction. If bounded acceptance is proven and review/security state is clean, merge with `expected_head_sha`, confirm Issue #6 closure, then reconcile this MASTER before selecting another gap.**
