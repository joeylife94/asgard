# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> This file is the single source of truth for Asgard v1.0 execution. README and agent self-report do not override executed evidence recorded here.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B2 — Minimal Frontend Boot-Shell Repair
- **Batch Result**: NOT STARTED — Issue-first activation required
- **Status**: IN PROGRESS
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Original code baseline**: `bca6567919cbcac3f9039268c09526b25179f370`
- **Phase 0 execution-enabling merge**: `888f2c5694940fe42284466fb57a0b33b2ec73cd` (PR #3)
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

# 5. Phase 0 Executed Baseline

## PR #3 — EXECUTED AND MERGED

Merged to `main` as `888f2c5694940fe42284466fb57a0b33b2ec73cd`.

Proven:
- [x] GitHub-hosted execution path exists.
- [x] Heimdall primary unit tests can pass independently of integration tests.
- [x] Frontend install reaches Vite build.
- [x] Frontend build fails because `bifrost/frontend/index.html` is absent.
- [x] Bifrost collection exposed missing `Dict` / `Any` imports.
- [x] Secondary Heimdall build exposes broad pre-existing checkstyle debt.

Interpretation:
- Missing frontend entrypoint = separate Core repair boundary.
- Bifrost typing/package-install defects = bounded Phase 0 repair, now closed by PR #4.
- Broad Heimdall checkstyle debt = pre-existing; **do not mass-fix inside unrelated bounded work**.

---

# 6. P0-B1 — Bifrost Typing / CI Package Repair — PASS

## PR #4

- **PR**: #4 — `fix: restore Bifrost typing imports`
- **Final exact head**: `1d301377a5951962cb3afd4e653a1975b8a2267a`
- **Merged to main**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **Result**: PASS for bounded slice

## Final bounded diff

`bifrost/bifrost/api.py`
- add `Any` and `Dict` to typing imports.

`.github/workflows/ci-cd.yml`
- add `pip install -e .` before secondary Bifrost lint/tests.

The accidental feedback-lane documentation regression was remotely corrected before merge. Final PR diff no longer contained that line change.

## Executed exact-head evidence

### Primary `CI` run `32262136812`
- **Unit tests (Heimdall + Bifrost): GREEN**
  - Heimdall unit tests GREEN
  - Bifrost dependency install GREEN
  - Bifrost unit tests GREEN
- **Phase 0 frontend preflight: RED / unrelated boundary**
  - `npm install`: GREEN; 351 packages installed
  - `npm run build`: RED
  - exact failure: `Could not resolve entry module "index.html".`
  - runtime captured: Java 21.0.12, Python 3.11.16, Node 20.20.2, npm 10.8.2, Docker 28.0.4

### `CI/CD Pipeline` run `32262136715`
- **Build & Test Bifrost: GREEN**
  - package install GREEN
  - flake8 GREEN
  - pytest GREEN
  - coverage upload GREEN
- **Dependency Security Check: GREEN**
- **Build & Test Heimdall: RED / unrelated pre-existing debt**
  - failing task: `:heimdall:checkstyleMain`
  - 41 files with violations
  - 109 warnings + 2 info
  - no mass-fix authorized

## Review state
- [x] Remote lane documentation restored to `on_device_rag, cloud_direct`.
- [x] Remote PR diff verified bounded after correction.
- [x] Review thread resolved only after remote proof.
- [x] Exact-head relevant CI re-executed.
- [x] Merge used `expected_head_sha` guard.

---

# 7. P0-B2 — Minimal Frontend Boot-Shell Repair

## Activation rule

This is a **new work item**. Before any branch/commit/implementation/proof test:
1. search for one open Issue exactly matching this acceptance gap;
2. if none exists, create exactly one bounded Issue;
3. then create one focused Issue-linked branch/PR.

## Goal

Restore only the minimum tracked Vite/React boot tree required to make the existing frontend contract executable. No product UI expansion.

## Frozen file scope

Only these files may be added/changed for the repair unless executed evidence proves another file is strictly required:
- `bifrost/frontend/index.html`
- `bifrost/frontend/src/main.jsx`
- `bifrost/frontend/src/App.jsx`
- `bifrost/frontend/src/index.css`

## Allowed
- React/Vite boot shell
- human-visible product title/context
- minimal CSS needed for a readable boot screen

## Non-goals
- fake metrics or fake jobs
- API integration
- routing controls
- job table
- redrive UI
- charts
- auth UI
- design-system expansion
- dependency upgrade

## Acceptance Criteria
- [ ] `npm install` succeeds.
- [ ] `npm run build` exits 0.
- [ ] `npm run dev` serves a reachable root page.
- [ ] default repository build path completes the frontend step.
- [ ] no fake operational data is introduced.
- [ ] PR diff remains inside frozen scope unless a new executed contradiction is documented first.

## Closure Condition

**Frontend build/startup contract is executable and verified, without adding product features.**

---

# 8. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 |
| E-002 | PR #3 merge | VERIFIED | `888f2c5694940fe42284466fb57a0b33b2ec73cd` |
| E-003 | Bifrost typing repair | VERIFIED / MERGED | PR #4 → `fa3f129783387fbeafae537e8a22b4629faf6d42` |
| E-004 | PR #4 primary unit tests | VERIFIED GREEN | run `32262136812` |
| E-005 | PR #4 secondary Bifrost | VERIFIED GREEN | run `32262136715` |
| E-006 | Dependency security check | VERIFIED GREEN | run `32262136715` |
| E-007 | Frontend npm install | VERIFIED GREEN | run `32262136812` |
| E-008 | Frontend Vite build | FAILED EXECUTED | `Could not resolve entry module "index.html".` |
| E-009 | Phase 0 runtime versions | VERIFIED | Java 21.0.12 / Python 3.11.16 / Node 20.20.2 / npm 10.8.2 / Docker 28.0.4 |
| E-010 | Heimdall secondary build | VERIFIED RED / PRE-EXISTING | `checkstyleMain`: 41 files, 109 warnings + 2 info |
| E-011 | PR #4 review correction | VERIFIED | remote correction + resolved thread |
| E-012 | Real Local AI E2E | PENDING | |
| E-013 | Local vs Cloud Routing | PENDING | |
| E-014 | DLQ → Redrive → Success | PENDING | |
| E-015 | Grafana live metrics | PENDING | |
| E-016 | Final Demo | PENDING | |
| E-017 | HP AI Server reference run | PENDING | |

---

# 9. Known Debt / Risks

| ID | Risk | Required handling |
|---|---|---|
| R-001 | Frontend entrypoint absent | P0-B2 frozen minimal repair |
| R-002 | Broad Heimdall checkstyle debt | classify separately; no unrelated mass-fix |
| R-003 | README overclaim | publish evidence-backed claims only |
| R-004 | Fallback-only E2E | real-model evidence mandatory |
| R-005 | Scope explosion | keep Frozen Scope |
| R-006 | Missing workflow status | missing ≠ PASS/FAIL; prefer PR-visible execution |
| R-007 | Agent self-report without remote/executed proof | never treat as proof |

Resolved:
- ~~R-008 Branch mutation unavailable~~ — GitHub `fetch_blob` + SHA-guarded `update_file` proved a safe branch mutation path on PR #4.

Known later proof-hardening debt:
- README Grafana port drift (`3000` vs Compose `3001`)
- unsupported production/compliance/performance claims

---

# 10. Work Item / PR Lifecycle

After grandfathered PR #4, all new acceptance gaps use Issue-first execution:

1. Read MASTER first.
2. Active focused PR first.
3. Otherwise search for one existing open Issue matching the exact next MASTER-authorized gap.
4. If none exists, create exactly one bounded Issue before new implementation/proof work.
5. Issue body must include Goal / Scope / Acceptance Criteria / Verification / Non-goals / Evidence Required.
6. Default one active implementation Issue at a time.
7. CI/review corrections inside that gap stay in the same Issue/PR.
8. PR links the Issue and records Changed / Actually Executed / Verified / Not Verified / Risks.
9. RED → inspect the first concrete failing job/step/log and make only the smallest scope-safe correction.
10. GREEN bounded acceptance + clean review/security state → merge with expected-head guard rather than idle.
11. Issue closes only after required verification + merged acceptance.
12. Reconcile this MASTER on `main` before selecting another gap.
13. Re-evaluate Human Review/FREEZE before creating another Issue.

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

**P0-B1 PASS / P0-B2 NOT STARTED.** PR #4 is merged with exact-head evidence proving the Bifrost typing/package-install repair. The next proven Core defect is the missing frontend Vite entry/source boot tree.

## What Changed
- Restored the feedback lane documentation on PR #4 directly on the remote branch using the exact fetched blob SHA.
- Verified the corrected PR diff contains only the intended Bifrost typing import and CI editable-install changes.
- Resolved the review thread after remote proof.
- Re-ran exact-head PR-visible workflows.
- Merged PR #4 with `expected_head_sha=1d301377a5951962cb3afd4e653a1975b8a2267a`.
- Updated the authoritative MASTER to the resulting main merge `fa3f129783387fbeafae537e8a22b4629faf6d42`.

## What Was Executed
- PR metadata/diff/review inspection.
- SHA-guarded GitHub branch file update.
- Exact-head primary CI `32262136812`.
- Exact-head secondary CI/CD `32262136715`.
- Frontend `npm install` and `npm run build` on GitHub-hosted Ubuntu runner.
- Heimdall and Bifrost primary unit tests.
- Secondary Bifrost install/lint/pytest/coverage.
- Dependency security check.
- Expected-head guarded PR #4 squash merge.

## What Was Not Verified
- Frontend successful build after repair.
- Frontend dev-server reachability.
- Default full repository build after frontend repair.
- Compose/E2E/real AI/Grafana live evidence.

## Remaining Risks
- Frontend currently cannot build because its Vite entrypoint/source boot tree is absent.
- Secondary Heimdall build remains red on broad pre-existing checkstyle debt.
- Real-model, recovery, observability, and final proof evidence remain pending.

## NEXT

**Issue-first activation of P0-B2: search for an existing open Issue matching the frozen minimal frontend boot-shell repair. If none exists, create exactly one bounded Issue with the frozen four-file scope and acceptance criteria before any implementation.**
