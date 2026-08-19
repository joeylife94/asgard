# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> This file is the single source of truth for Asgard v1.0 execution. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B4 — UC-01 Full Core-Service Startup / Health Verification
- **Batch Result**: IN PROGRESS
- **Status**: ISSUE #11 OPEN; EXECUTABLE PROOF SLICE NOT YET CREATED
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **P0-B3 merge**: `74da74c71625b9bca111b2e1c1bbbb933c82077a`
- **Issue #11**: OPEN — `P0-B4: verify UC-01 full core-service startup and health`
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

| UC | Goal | PASS 기준 | Current |
|---|---|---|---|
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy | IN PROGRESS — build/frontend slice proven; full service health pending under Issue #11 |
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED | PENDING |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 | PENDING |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED | PENDING |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 | PENDING |

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

## P0-B3 — PASS / MERGED
- Issue #8 CLOSED.
- PR #9 proof harness merged at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`.
- PR #10 exact tested head `dc8cc524bb2f10e8b5674cfcc98247882782a82a` merged at `74da74c71625b9bca111b2e1c1bbbb933c82077a`.
- `CI/CD Pipeline` run `32279712933`: SUCCESS.
- `CI` run `32279712788`: SUCCESS.
- Vite dev server + HTTP root reachability: GREEN.
- root `build-all.ps1 -SkipTests` reaches/completes Frontend: GREEN.
- explicit SkipTests path uses `:heimdall:assemble`; normal full build remains `:heimdall:build`.
- no Checkstyle config suppression or broad cleanup.

---

# 5. Active Phase 0 Slice — P0-B4

## Issue
- **Issue #11**: `P0-B4: verify UC-01 full core-service startup and health`
- State: OPEN

## Goal
Close the remaining UC-01 startup proof gap by executing the actual core stack and collecting concrete service-health/reachability evidence.

## In Scope
- reproducible checkout/configuration for the proof.
- execute the repository-supported core startup path or the minimum CI-equivalent runtime path when the interactive PowerShell launcher is unsuitable for GitHub-hosted execution.
- verify Heimdall reachability/health.
- verify Bifrost reachability/health.
- verify PostgreSQL readiness.
- verify Kafka readiness.
- verify Frontend root reachability as part of the running stack.
- verify Prometheus reachability.
- verify Grafana reachability using Compose host port `3001`.
- verify Redis only if required by the active application/startup contract.
- add only the minimum proof harness required for reviewable execution.

## Current Static Contract Relevant To Execution
- root `docker-compose.yml` contains infrastructure only; application processes are not Compose services.
- Compose includes PostgreSQL, Kafka/Zookeeper, Redis, Elasticsearch, Prometheus, Grafana, Zipkin and support UIs.
- Grafana host mapping is `3001:3000`.
- `start-all.ps1` starts infrastructure with Compose, then starts Heimdall/Bifrost/Frontend as background processes.
- `start-all.ps1` currently prints a completion banner without proving application health; therefore the banner is not UC-01 evidence.
- interactive `Start-Process powershell` behavior may not be directly suitable as a GitHub-hosted proof harness; any CI-equivalent harness must preserve the same service contract rather than invent a different product flow.

## Acceptance Criteria
- [ ] checkout/configuration required by proof is explicit and reproducible.
- [ ] core stack startup command executes under reviewable runtime evidence.
- [ ] Heimdall health/reachability verified.
- [ ] Bifrost health/reachability verified.
- [ ] PostgreSQL readiness verified.
- [ ] Kafka readiness verified.
- [ ] Frontend root reachability verified as part of the stack.
- [ ] Prometheus reachability verified.
- [ ] Grafana reachability verified at host port `3001`.
- [ ] Redis readiness verified if required by active startup contract.
- [ ] no UC-02 product flow, UI expansion, README hardening, or broad Heimdall style cleanup.

## Result
**IN PROGRESS — Issue #11 is the only active implementation/proof work item. No runtime PASS has been claimed yet.**

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
| E-017 | Root default SkipTests build path reaches/completes Frontend | VERIFIED GREEN / MERGED | PR #10; runs 32279712933 + 32279712788 |
| E-018 | Real Local AI E2E | PENDING | |
| E-019 | Local vs Cloud Routing | PENDING | |
| E-020 | DLQ → Redrive → Success | PENDING | |
| E-021 | Grafana live metrics | PENDING | |
| E-022 | Final Demo | PENDING | |
| E-023 | HP AI Server reference run | PENDING | |
| E-024 | UC-01 full core-stack service health | IN PROGRESS | Issue #11 |

---

# 7. Known Debt / Risks

| ID | Risk | Required handling |
|---|---|---|
| R-001 | full-stack startup may expose environment/configuration failures | inspect first concrete RED; fix only Issue #11 scope |
| R-002 | broad Heimdall checkstyle debt | keep visible; do not mass-fix unless a later authorized quality batch requires it |
| R-003 | interactive Windows startup script is not itself a health proof | use executable health checks; do not count banner text as PASS |
| R-004 | README overclaim / Grafana port drift | proof-hardening later |
| R-005 | fallback-only E2E risk | real-model evidence mandatory |
| R-006 | scope explosion | keep Frozen Scope |
| R-007 | agent self-report without executed proof | never count as PASS |

---

# 8. Work Item / PR Lifecycle

1. Read MASTER first.
2. Active focused PR first.
3. One active implementation/proof Issue at a time by default.
4. Corrections inside the active acceptance gap stay in the same Issue/PR.
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
**P0-B1 PASS / P0-B2 PASS / P0-B3 PASS / P0-B4 IN PROGRESS.**

P0-B3 closed with exact-head GREEN workflows, a guarded merge of PR #10, and completed Issue #8. The remaining UC-01 gap is now isolated under Issue #11: prove the actual core services start and are reachable/healthy together.

## What Changed
- read authoritative MASTER first.
- re-fetched PR #10 exact head, diff, workflow state, and review state.
- confirmed exact head `dc8cc524bb2f10e8b5674cfcc98247882782a82a` remained current.
- confirmed both PR-visible workflows GREEN.
- confirmed no review submissions or unresolved inline review threads.
- merged PR #10 with expected-head guard; resulting main SHA `74da74c71625b9bca111b2e1c1bbbb933c82077a`.
- closed Issue #8 as completed after acceptance and merge.
- reconciled MASTER on main.
- searched for an existing open Issue matching the remaining UC-01 full-stack health gap; none existed.
- created exactly one bounded Issue #11 for P0-B4.
- inspected current Compose/startup contract only enough to define the next executable proof slice.

## What Was Executed
- PR #10 exact-head workflow lookup.
- PR review/review-thread inspection.
- expected-head squash merge.
- Issue #8 closure.
- open-Issue search for the next exact acceptance gap.
- Issue #11 creation.
- Compose/startup contract inspection.

## What Was Not Verified
- P0-B4 core-stack runtime execution.
- Heimdall/Bifrost health in the full running stack.
- PostgreSQL/Kafka/Prometheus/Grafana readiness in one reviewable startup proof.
- real Local AI E2E.
- Local vs Cloud routing execution.
- DLQ → Redrive → Success.
- Grafana live metric correctness.
- HP AI Server reference deployment.
- final demo.

## Remaining Risks
- application configuration may prevent Heimdall or Bifrost from reaching healthy state after infrastructure starts.
- GitHub-hosted execution may require a bounded non-interactive equivalent of the interactive `start-all.ps1` process launcher.
- normal Heimdall full build still exposes known Checkstyle debt.

## NEXT
**Under Issue #11, create the smallest PR-visible executable proof harness for UC-01 full-stack startup/health. Prefer the existing startup/service contracts; do not invent product behavior. The first execution must capture infrastructure readiness plus Heimdall, Bifrost, Frontend, Prometheus and Grafana reachability. If RED, inspect only the first concrete failing boundary and fix only Issue #11 scope.**
