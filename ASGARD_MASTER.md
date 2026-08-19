# ASGARD MASTER

> **Authoritative execution contract**
> Asgard의 현재 상태, v1.0 종료선, Evidence, 다음 작업을 관리한다.
> README보다 본 문서의 상태 판정을 우선한다.

## 0. Control
- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B1 — Repository Preflight / Focused CI Repair
- **Batch Result**: IN PROGRESS
- **Status**: IN PROGRESS
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Original code baseline**: `bca6567919cbcac3f9039268c09526b25179f370`
- **Phase 0 execution-enabling merge**: `888f2c5694940fe42284466fb57a0b33b2ec73cd` (PR #3)
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

# 2. v1.0 Target State

> **실제 데이터를 넣어 실제 AI 분석을 수행하고, 장애를 재현·복구할 수 있으며, 제3자가 clone 후 실행·검증할 수 있는 Single-node Production-like Hybrid AI Ops Platform**

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
- Fresh clone / CI-equivalent reproducible build evidence
- Real-model E2E PASS
- Failure → Recovery PASS
- Relevant CI green for bounded release slice
- Runtime / Grafana screenshots
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
- Feedback
- A/B Testing
- Advanced Routing
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

# 5. Phase 0 — Authoritative Executed Baseline

## PR #3 — EXECUTED AND MERGED

PR #3 (`ci: retain Phase 0 preflight evidence`) was executed on GitHub-hosted Actions and merged to `main` as:

`888f2c5694940fe42284466fb57a0b33b2ec73cd`

This closes the previous false assumption that Phase 0 had no GitHub-hosted execution evidence.

### Proven by PR #3 execution
- [x] GitHub-hosted execution path exists and runs repository workflows.
- [x] Heimdall unit tests passed in the PR-visible primary CI unit job.
- [x] Frontend dependency installation reached the Vite build boundary.
- [x] Frontend build failed because `bifrost/frontend/index.html` is absent.
- [x] Bifrost test collection exposed missing `Dict` / `Any` typing imports as a concrete scope-relevant failure.
- [x] Secondary Heimdall Build & Test exposed broad pre-existing checkstyle debt.

### Interpretation rules
- The missing frontend entrypoint is a **separate frozen Core repair boundary**. Do not hide it by disabling the build.
- The Bifrost `Dict` / `Any` collection failure is a **focused Phase 0 repair candidate** because it blocks executable unit evidence.
- Broad Heimdall checkstyle debt is **pre-existing** and must not be mass-fixed merely to manufacture a green pipeline.
- A RED workflow is not automatically a blocker for a bounded PR if the intended acceptance is green and the remaining RED is demonstrably unrelated/pre-existing or belongs to another frozen repair boundary.

---

# 6. Current Focus — PR #4 Bifrost Typing Slice

## Supervisor-observed exact head
`422a664961e054102e042f0e96a70aabacf02ba5`

## Executed evidence already observed
- Primary `CI` run `32226966755`
  - **Heimdall/Bifrost unit job: GREEN**
  - **Frontend preflight: RED** at the expected missing-entrypoint boundary
- `CI/CD Pipeline` run `32226965403`
  - **Bifrost: GREEN**
  - **Heimdall Build & Test: RED**

## Required decision for this slice
1. Inspect the first concrete failing Heimdall build step/log from PR #4 exact head.
2. Classify it as either:
   - **pre-existing broad checkstyle debt**, or
   - **new scope-relevant regression introduced by PR #4**.
3. If pre-existing/unrelated and PR #4's Bifrost typing acceptance is proven, do **not** mass-fix Heimdall style debt.
4. Resolve only remaining scope-safe review/diff issues.
5. Merge PR #4 with an **expected-head guard** when bounded acceptance is satisfied and no unresolved review/security/human-decision blocker remains.
6. Update this MASTER on `main` with the resulting main SHA and evidence.

---

# 7. Frontend Contract — EXECUTED FAILURE, REPAIR FROZEN

PR #3 proved the frontend installation reaches Vite build and fails because the tracked frontend lacks `index.html`.

Known tracked-tree gap:
- no `bifrost/frontend/index.html`
- no tracked `bifrost/frontend/src/` boot tree sufficient for Vite startup

## Frozen next repair batch — not active until Bifrost slice is resolved
Minimum file set only:
- `bifrost/frontend/index.html`
- `bifrost/frontend/src/main.jsx`
- `bifrost/frontend/src/App.jsx`
- `bifrost/frontend/src/index.css`

### Allowed scope
- boot shell only
- no fake metrics
- no fake jobs
- no API feature expansion
- no design-system work

### Required runtime acceptance
- [ ] `npm install`
- [ ] `npm run build` exit 0
- [ ] `npm run dev` root reachable
- [ ] default repository build path passes frontend step

---

# 8. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 executed Actions successfully enough to expose concrete failures |
| E-002 | PR #3 merge | VERIFIED | main merge SHA `888f2c5694940fe42284466fb57a0b33b2ec73cd` |
| E-003 | Heimdall primary unit tests | VERIFIED ON PR #3 | passed |
| E-004 | Frontend Vite build | FAILED EXECUTED | missing `bifrost/frontend/index.html` |
| E-005 | Bifrost collection | FAILED EXECUTED ON PR #3 | missing `Dict` / `Any` imports |
| E-006 | Heimdall secondary build/checkstyle | FAILED EXECUTED | broad pre-existing checkstyle debt; no mass-fix authorization |
| E-007 | PR #4 primary unit job | VERIFIED GREEN | run `32226966755` |
| E-008 | PR #4 frontend preflight | VERIFIED RED | expected frozen frontend boundary |
| E-009 | PR #4 secondary Bifrost | VERIFIED GREEN | run `32226965403` |
| E-010 | PR #4 secondary Heimdall | RED — CLASSIFICATION REQUIRED | inspect first concrete failing step/log |
| E-011 | Real Local AI E2E | PENDING | |
| E-012 | Local vs Cloud Routing | PENDING | |
| E-013 | DLQ → Redrive → Success | PENDING | |
| E-014 | Grafana live metrics | PENDING | |
| E-015 | Final Demo | PENDING | |
| E-016 | HP AI Server reference run | PENDING | |

---

# 9. Known Debt / Risks

| ID | Risk | Required handling |
|---|---|---|
| R-001 | Frontend entrypoint absent | repair only in frozen 4-file boot-shell batch |
| R-002 | Broad Heimdall checkstyle debt | classify as pre-existing; do not mass-fix in focused slices |
| R-003 | README overclaim | publish evidence-backed claims only |
| R-004 | Fallback-only E2E risk | real-model evidence mandatory |
| R-005 | Scope explosion | keep Frozen Scope |
| R-006 | Missing workflow status | missing ≠ PASS/FAIL; prefer PR-visible exact-head execution |
| R-007 | Docs/config drift | repair only when it changes execution truth |

Known README debt retained for later proof-hardening:
- Grafana host-facing port drift (`3000` vs Compose `3001`)
- unsupported production/compliance/performance claims

---

# 10. PR Lifecycle Rule

For every focused PR:
1. Read this MASTER first.
2. Inspect active Phase/Batch and PR exact head.
3. Prefer pull_request-visible workflows/checks.
4. If RED, inspect the first concrete failing job/step/log.
5. Fix only failures caused by or blocking the active bounded slice.
6. Do not mass-fix unrelated/pre-existing debt to manufacture green.
7. If intended acceptance is GREEN, diff is in scope, and no unresolved review/security/human-decision blocker remains, merge with `expected_head_sha`.
8. Update MASTER on `main` with executed evidence and resulting main SHA.
9. Continue to the next smallest acceptance gap.

**Ordinary bounded intermediate PR merges do not require human approval.**

**Human Review remains the FINAL v1.0 gate.**

---

# 11. Work Rules

Required completion report every iteration:
- **What Changed**
- **What Was Executed**
- **What Was Not Verified**
- **Remaining Risks**
- **Result**: PASS / FAIL / BLOCKED / IN PROGRESS
- **Next**: one exact task

Rules:
- Agent self-report ≠ proof
- Executed evidence beats static inference
- Missing CI status ≠ PASS
- Same blocker loop prohibited
- Experimental scope prohibited before Core completion
- MASTER must be synchronized before new product change

---

# 12. Current Checkpoint

## Result
**IN PROGRESS** — Phase 0 execution is no longer globally blocked. PR #3 proved GitHub-hosted execution. The active bounded decision is PR #4 Bifrost typing slice classification/merge readiness.

## What Changed
- Reconciled stale MASTER with already-executed PR #3 evidence.
- Recorded PR #3 merge SHA `888f2c5694940fe42284466fb57a0b33b2ec73cd`.
- Recorded executed frontend failure at missing `index.html` boundary.
- Recorded executed Bifrost `Dict` / `Any` collection failure.
- Recorded Heimdall broad checkstyle debt as pre-existing and out of scope for mass cleanup.
- Recorded supervisor-observed PR #4 exact-head workflow evidence.

## What Was Executed
- Root MASTER first-read on main.
- Main branch/merge SHA verification.
- PR #3 merged-state verification.
- PR #3 pull_request workflow-run verification.

## What Was Not Verified Yet
- PR #4 first failing Heimdall secondary build step/log classification in this synchronized ledger state.
- PR #4 current exact head/review-thread state after any later branch changes.
- Final PR #4 merge readiness.
- Frontend repair runtime acceptance.
- Compose/E2E/real AI/Grafana live evidence.

## Remaining Risks
- PR #4 may have moved from the supervisor-observed SHA.
- PR #4 may contain an unresolved review/diff issue unrelated to Bifrost typing acceptance.
- Frontend remains an executed failure and must be repaired in its own frozen batch.

## NEXT
**Re-read this committed MASTER, then inspect PR #4 current exact head, reviews, diff, and exact-head workflow evidence. Classify the first concrete failing Heimdall Build & Test step. If remaining RED is pre-existing/unrelated and the Bifrost slice is proven, resolve only scope-safe review issues and merge PR #4 with an expected-head guard.**
