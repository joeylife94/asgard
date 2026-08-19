# ASGARD MASTER

> **Authoritative execution contract**
> Asgard의 현재 상태, v1.0 종료선, Evidence, 다음 작업을 관리한다.
> README보다 본 문서의 상태 판정을 우선한다.

## 0. Control
- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B1 — Focused CI Repair
- **Batch Result**: IN PROGRESS
- **Status**: IN PROGRESS
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Original code baseline**: `bca6567919cbcac3f9039268c09526b25179f370`
- **Phase 0 execution-enabling merge**: `888f2c5694940fe42284466fb57a0b33b2ec73cd` (PR #3)
- **MASTER reconciliation commit**: `4b9ee9a440b34af5c92677e7b6329d840b34f063`
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
- Reproducible build/runtime evidence
- Real-model E2E PASS
- Failure → Recovery PASS
- Relevant CI green for bounded release slices
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

### Proven by PR #3
- [x] GitHub-hosted execution path exists.
- [x] Heimdall primary unit tests passed.
- [x] Frontend install reached Vite build.
- [x] Frontend build failed because `bifrost/frontend/index.html` is absent.
- [x] Bifrost collection exposed missing `Dict` / `Any` imports.
- [x] Secondary Heimdall Build & Test exposed broad pre-existing checkstyle debt.

### Interpretation
- Missing frontend entrypoint = separate frozen Core repair boundary.
- Missing Bifrost typing names = focused Phase 0 repair.
- Broad Heimdall checkstyle debt = pre-existing; **no mass-fix** in focused slices.
- Remaining RED unrelated to a bounded slice does not invalidate a proven bounded acceptance criterion.

---

# 6. Current Focus — PR #4 Bifrost Typing Slice

## Exact head
`422a664961e054102e042f0e96a70aabacf02ba5`

## Intended changes
- `bifrost/bifrost/api.py`: import `Any` and `Dict` used by runtime annotations.
- `.github/workflows/ci-cd.yml`: install Bifrost itself (`pip install -e .`) before secondary lint/pytest.

## Executed exact-head evidence
### Primary `CI` run `32226966755`
- **Unit tests (Heimdall + Bifrost): GREEN**
- **Frontend preflight: RED** at the already-known missing `index.html` boundary

### `CI/CD Pipeline` run `32226965403`
- **Build & Test Bifrost: GREEN**
  - dependency install GREEN
  - flake8 GREEN
  - pytest GREEN
  - coverage upload GREEN
- **Build & Test Heimdall: RED**
  - first failing build step: `./gradlew :heimdall:build`
  - actual failure: `:heimdall:checkstyleMain`
  - **41 files with violations**
  - **109 warnings + 2 info**
  - violations span services/controllers/entities/repositories/security/config/util
  - classification: **broad pre-existing checkstyle debt, unrelated to PR #4 Bifrost slice**
  - action: **DO NOT MASS-FIX**

## PR #4 bounded acceptance
- [x] Prior `Dict` / `Any` collection failure is gone.
- [x] Primary Bifrost/Heimdall unit job GREEN.
- [x] Secondary Bifrost job GREEN.
- [x] Remaining Heimdall RED classified as unrelated pre-existing debt.
- [x] Remaining frontend RED classified as separate frozen Core boundary.
- [ ] Review regression fixed: feedback stats lane docs must remain `on_device_rag, cloud_direct`.
- [ ] Review thread resolved only after source branch actually contains the fix.
- [ ] Merge with `expected_head_sha` after exact-head review state is clean.

## Current blocker
PR #4 currently still changes:

`lane: Filter by routing lane (on_device_rag, cloud_direct)`

into the incorrect:

`lane: Filter by routing lane (on_device/cloud)`

Automated review correctly identifies this as a behavioral documentation regression because feedback lane matching is exact. A prior agent self-report claimed a local correction but **no correction commit is present on the PR branch**, so self-report is not proof.

A new explicit request has been posted to the existing review thread to push only this one-line restoration directly to `agent/p0-bifrost-typing-import`. Until the branch head changes and the diff is clean, PR #4 must not merge.

---

# 7. Frontend Contract — EXECUTED FAILURE, REPAIR FROZEN

PR #3 proved Vite build failure at the missing entrypoint boundary.

Known gap:
- no `bifrost/frontend/index.html`
- no sufficient tracked `bifrost/frontend/src/` boot tree

## Frozen next repair batch — activates after PR #4 resolves
Minimum files only:
- `bifrost/frontend/index.html`
- `bifrost/frontend/src/main.jsx`
- `bifrost/frontend/src/App.jsx`
- `bifrost/frontend/src/index.css`

Allowed scope:
- boot shell only
- no fake metrics/jobs
- no API feature expansion
- no design-system work

Required runtime acceptance:
- [ ] `npm install`
- [ ] `npm run build` exit 0
- [ ] `npm run dev` root reachable
- [ ] default repository build path passes frontend step

---

# 8. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 |
| E-002 | PR #3 merge | VERIFIED | `888f2c5694940fe42284466fb57a0b33b2ec73cd` |
| E-003 | Heimdall primary unit tests | VERIFIED GREEN | PR #3 / PR #4 primary CI |
| E-004 | Frontend Vite build | FAILED EXECUTED | missing `bifrost/frontend/index.html` |
| E-005 | Bifrost typing collection failure | REPAIRED ON PR #4 | exact-head jobs no longer fail on `Dict` / `Any` |
| E-006 | PR #4 primary unit job | VERIFIED GREEN | run `32226966755` |
| E-007 | PR #4 secondary Bifrost | VERIFIED GREEN | run `32226965403` |
| E-008 | PR #4 secondary Heimdall | VERIFIED RED / UNRELATED | `checkstyleMain`: 41 files, 109 warning + 2 info |
| E-009 | PR #4 review correctness | BLOCKED | one-line feedback-lane doc regression still on branch |
| E-010 | Real Local AI E2E | PENDING | |
| E-011 | Local vs Cloud Routing | PENDING | |
| E-012 | DLQ → Redrive → Success | PENDING | |
| E-013 | Grafana live metrics | PENDING | |
| E-014 | Final Demo | PENDING | |
| E-015 | HP AI Server reference run | PENDING | |

---

# 9. Known Debt / Risks

| ID | Risk | Required handling |
|---|---|---|
| R-001 | Frontend entrypoint absent | frozen 4-file repair after PR #4 |
| R-002 | Broad Heimdall checkstyle debt | do not mass-fix in bounded PRs |
| R-003 | README overclaim | publish evidence-backed claims only |
| R-004 | Fallback-only E2E | real-model evidence mandatory |
| R-005 | Scope explosion | keep Frozen Scope |
| R-006 | Missing workflow status | missing ≠ PASS/FAIL; prefer PR-visible execution |
| R-007 | Agent self-report without pushed commit | never treat as proof |

Known later proof-hardening debt:
- README Grafana port drift (`3000` vs Compose `3001`)
- unsupported production/compliance/performance claims

---

# 10. PR Lifecycle Rule

1. Read MASTER first.
2. Inspect current focused PR exact head and PR-visible workflows.
3. RED → inspect first concrete failing job/step/log.
4. Fix only active-slice failures; classify unrelated/pre-existing debt explicitly.
5. Do not mass-fix debt to manufacture green.
6. If bounded acceptance is proven, diff is in scope, and no unresolved review/security/human-decision blocker remains, merge with `expected_head_sha`.
7. Update MASTER on `main` with executed evidence and resulting main SHA.
8. Continue to next smallest acceptance gap.

**Ordinary bounded intermediate PR merges do not require human approval.**

**Human Review remains the FINAL v1.0 gate.**

---

# 11. Required Completion Report

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

# 12. Current Checkpoint

## Result
**IN PROGRESS** — PR #4 Bifrost repair is technically proven by exact-head execution; merge is blocked only by one concrete documentation review regression that is still present on the branch.

## What Changed
- Repaired stale MASTER first and committed it on main.
- Re-read committed MASTER before further action.
- Inspected PR #4 current exact head/diff/reviews.
- Retrieved exact-head workflow jobs and full failing Heimdall job log.
- Classified Heimdall RED as broad pre-existing `checkstyleMain` debt, not a PR #4 regression.
- Re-requested the exact one-line lane-doc restoration directly on the current PR branch.

## What Was Executed
- Main/PR #3 merge verification.
- PR #4 exact-head verification: `422a664961e054102e042f0e96a70aabacf02ba5`.
- PR-visible run lookup for `32226966755` and `32226965403`.
- Job inspection for secondary pipeline.
- Full job log inspection for Heimdall job `95988540570`.
- Review-thread/diff inspection.

## What Was Not Verified
- A pushed commit restoring the feedback lane documentation.
- Exact-head CI after that future one-line correction.
- PR #4 merge result.
- Frontend boot-shell repair runtime acceptance.
- Compose/E2E/real AI/Grafana live evidence.

## Remaining Risks
- PR #4 must not merge until the incorrect lane documentation is actually gone from the branch.
- Frontend remains a separately proven Core failure.
- Broad Heimdall style debt remains intentionally deferred.

## NEXT
**Inspect PR #4 head first. If the requested one-line lane restoration has been pushed, verify the diff/review state and exact-head relevant CI, resolve the review thread, then merge PR #4 with `expected_head_sha`. If it has not been pushed, make no broad change: restore only that line using the safest available branch mutation path, then verify exact-head execution before merge.**
