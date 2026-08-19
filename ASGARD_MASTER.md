# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> This file is the single source of truth for Asgard v1.0 execution. README and agent self-report do not override it.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B1 — Focused CI Repair
- **Batch Result**: BLOCKED
- **Status**: IN PROGRESS
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Original code baseline**: `bca6567919cbcac3f9039268c09526b25179f370`
- **Phase 0 execution-enabling merge**: `888f2c5694940fe42284466fb57a0b33b2ec73cd` (PR #3)
- **MASTER reconciliation**: completed on main
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

# 5. Phase 0 — Authoritative Executed Baseline

## PR #3 — EXECUTED AND MERGED

PR #3 (`ci: retain Phase 0 preflight evidence`) executed on GitHub-hosted Actions and merged to `main` as:

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

## PR
- **PR**: #4 — `fix: restore Bifrost typing imports`
- **Branch**: `agent/p0-bifrost-typing-import`
- **Current exact head**: `422a664961e054102e042f0e96a70aabacf02ba5`
- **State**: OPEN / mergeable

## Intended changes
- `bifrost/bifrost/api.py`: import `Any` and `Dict` used by runtime annotations.
- `.github/workflows/ci-cd.yml`: install Bifrost itself (`pip install -e .`) before secondary lint/pytest.

## Executed exact-head evidence

### Primary `CI` run `32226966755`
- **Unit tests (Heimdall + Bifrost): GREEN**
- **Frontend preflight: RED** at the already-known missing `index.html` boundary

### `CI/CD Pipeline` run `32226965403`
- **Build & Test Bifrost: GREEN**
  - editable package install GREEN
  - flake8 GREEN
  - pytest GREEN
  - coverage upload GREEN
- **Build & Test Heimdall: RED**
  - first failing build step: `./gradlew :heimdall:build`
  - actual failure: `:heimdall:checkstyleMain`
  - 41 files with violations
  - 109 warnings + 2 info
  - classification: broad pre-existing checkstyle debt, unrelated to PR #4 Bifrost slice
  - action: **DO NOT MASS-FIX**

## Bounded acceptance
- [x] Prior `Dict` / `Any` collection failure is gone.
- [x] Primary Bifrost/Heimdall unit job GREEN.
- [x] Secondary Bifrost job GREEN.
- [x] Remaining Heimdall RED classified as unrelated pre-existing debt.
- [x] Remaining frontend RED classified as separate frozen Core boundary.
- [ ] Restore exact feedback lane documentation: `on_device_rag, cloud_direct`.
- [ ] Confirm the restoration exists on the remote PR branch.
- [ ] Resolve the review thread after the remote diff is clean.
- [ ] Re-check exact-head relevant workflows after the correction.
- [ ] Merge using `expected_head_sha` only after review state is clean.

## Current merge blocker — PROVEN

PR #4 still contains this review regression:

```text
lane: Filter by routing lane (on_device/cloud)
```

Required restoration:

```text
lane: Filter by routing lane (on_device_rag, cloud_direct)
```

The unresolved review thread is valid because feedback lane matching is exact.

Two Codex attempts created local-only correction commits (`a84cd2b`, later `b87a1e3`) but neither commit exists on GitHub. The latest Codex report explicitly states that its checkout had **no configured Git remote**, so it could not push to `agent/p0-bifrost-typing-import`. Agent self-report is therefore not proof.

### Current execution-environment mutation blocker

This automation environment currently has no safe partial-line GitHub write path for `bifrost/bifrost/api.py`:

- local `git` cannot reach `github.com` due DNS resolution failure;
- `gh` is unavailable;
- the available GitHub contents writer replaces an entire file rather than applying a one-line patch;
- replacing this large API file wholesale solely to alter one docstring line creates unnecessary corruption risk.

Therefore PR #4 remains **BLOCKED**, and merging it would violate the active bounded acceptance contract.

### Exact external prerequisite

One of the following must become available:

1. a GitHub-capable checkout/remote that can push the one-line correction to `agent/p0-bifrost-typing-import`; or
2. a safe partial-file/patch mutation path for that branch; or
3. a human applies exactly this one-line restoration in the GitHub UI.

No broader code change is authorized as a workaround.

---

# 7. Frontend Contract — EXECUTED FAILURE, REPAIR FROZEN

PR #3 proved Vite build failure at the missing entrypoint boundary.

Known gap:
- no `bifrost/frontend/index.html`
- no sufficient tracked `bifrost/frontend/src/` boot tree

## Frozen next repair batch — activates only after PR #4 resolves

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
| E-008 | PR #4 secondary Heimdall | VERIFIED RED / UNRELATED | `checkstyleMain`: 41 files, 109 warnings + 2 info |
| E-009 | PR #4 review correctness | BLOCKED | exact lane doc regression remains on remote branch |
| E-010 | Codex correction push | NOT VERIFIED / NOT PRESENT | local-only commits; no GitHub object |
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
| R-001 | Frontend entrypoint absent | frozen 4-file repair after PR #4 |
| R-002 | Broad Heimdall checkstyle debt | do not mass-fix in bounded PRs |
| R-003 | README overclaim | publish evidence-backed claims only |
| R-004 | Fallback-only E2E | real-model evidence mandatory |
| R-005 | Scope explosion | keep Frozen Scope |
| R-006 | Missing workflow status | missing ≠ PASS/FAIL; prefer PR-visible execution |
| R-007 | Agent self-report without pushed commit | never treat as proof |
| R-008 | Branch mutation unavailable in current automation environment | require safe patch/push path; do not wholesale-rewrite large source file |

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

**BLOCKED** — PR #4's Bifrost typing/package-install acceptance is technically proven by exact-head execution, but merge remains blocked by one unresolved one-line documentation regression that is still present on the remote branch. The current automation environment cannot safely push that single-line correction without risking a wholesale rewrite of the large API file.

## What Changed
- Re-read the authoritative MASTER before acting.
- Re-confirmed PR #4 remote exact head remains `422a664961e054102e042f0e96a70aabacf02ba5`.
- Re-confirmed the incorrect lane documentation is still present in the actual PR diff.
- Re-confirmed the review thread is unresolved and the previous Codex fixes were local-only, not pushed.
- Re-confirmed exact-head PR-visible workflow runs remain the already-classified executed evidence.
- Recorded the precise branch-mutation prerequisite instead of manufacturing another unrelated implementation step.

## What Was Executed
- PR #4 metadata/head inspection.
- PR #4 file patch inspection.
- PR #4 unresolved review-thread inspection.
- Exact-head workflow-run lookup.
- Git commit/tree history inspection for the typing and package-install commits.
- Local mutation-path check: `gh` unavailable; local GitHub DNS access unavailable.

## What Was Not Verified
- A remote commit restoring the feedback lane documentation.
- Exact-head CI after that future correction.
- PR #4 merge result.
- Frontend boot-shell runtime acceptance.
- Compose/E2E/real AI/Grafana live evidence.

## Remaining Risks
- Merging PR #4 now would knowingly ship misleading API documentation.
- Wholesale replacement of the large `api.py` file for one-line correction would create disproportionate corruption risk.
- Frontend remains the next separately proven Core failure after PR #4 resolves.

## NEXT

**Apply exactly one remote branch correction on `agent/p0-bifrost-typing-import`: restore `lane: Filter by routing lane (on_device_rag, cloud_direct)`. Then inspect the new exact head, resolve the review thread only if the remote diff is clean, verify relevant PR-visible CI, merge with `expected_head_sha`, update this MASTER on `main`, and transition explicitly to the frozen 4-file frontend boot-shell repair batch.**
