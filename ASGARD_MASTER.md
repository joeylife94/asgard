# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 1 — Golden Path
- **Current Batch**: NOT STARTED — next bounded work item must be created from the Phase 1 acceptance gap
- **Phase 0 Result**: PASS
- **Status**: UC-01 VERIFIED / Issue #11 CLOSED / PR #12 MERGED
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **P0-B1 merge**: `fa3f129783387fbeafae537e8a22b4629faf6d42`
- **P0-B2 merge**: `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`
- **P0-B3 merge**: `74da74c71625b9bca111b2e1c1bbbb933c82077a`
- **P0-B4 / PR #12 merge**: `8f79c1aaf7a145abb4721c5f7799059b8c4195aa`
- **Issue #11**: CLOSED / COMPLETED
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
| UC-01 Startup | 제3자 실행 | clone/configure → core services healthy | **PASS** |
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED | PENDING |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 | PENDING |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED | PENDING |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 | PENDING |

---

# 4. Phase 0 — PASS

## Goal
Establish a truthful, executable baseline and prove the repository can build and start its required core stack under reviewable execution.

## P0-B1 — PASS / MERGED
- PR #4 merged at `fa3f129783387fbeafae537e8a22b4629faf6d42`.
- primary Heimdall + Bifrost unit job GREEN.
- secondary Bifrost install/lint/pytest/coverage GREEN.
- dependency security GREEN.
- Java 21 CI contract aligned.
- broad Heimdall Checkstyle debt classified as pre-existing: **41 files / 109 warnings / 2 info**.

## P0-B2 — PASS / MERGED
- Issue #6 CLOSED.
- PR #7 merged at `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`.
- minimal four-file frontend boot tree restored.
- exact-head production frontend build GREEN.

## P0-B3 — PASS / MERGED
- Issue #8 CLOSED.
- PR #9 proof harness merged at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`.
- PR #10 merged at `74da74c71625b9bca111b2e1c1bbbb933c82077a`.
- frontend dev-server root reachability GREEN.
- root `build-all.ps1 -SkipTests` reaches/completes Frontend GREEN.
- `-SkipTests` uses `:heimdall:assemble`; normal build remains `:heimdall:build`.

## P0-B4 — PASS / MERGED
- Issue #11 CLOSED / COMPLETED.
- PR #12 exact head: `1f3459dd5e12bf85b5eccfe41d1eca05bbf6231b`.
- PR #12 merged at `8f79c1aaf7a145abb4721c5f7799059b8c4195aa` using expected-head guard.
- primary `CI` run `32320165761`: **SUCCESS**.
- exact-head full-core job: **SUCCESS**.
- Phase 0 preflight: GREEN.
- unit tests Heimdall + Bifrost: GREEN.
- frontend dev root: GREEN.
- default Windows build path: GREEN.
- infrastructure readiness: PostgreSQL / Kafka / Redis / Elasticsearch / Prometheus / Grafana `3001` GREEN.
- application evidence artifact:
  - Heimdall `/actuator/health` → `UP`.
  - Bifrost `/health` → `healthy`.
  - Frontend root → reachable HTML.
- stale Elasticsearch review thread resolved after exact-head evidence confirmed the correction.

### Secondary CI classification
- `CI/CD Pipeline` run `32320165695`: overall FAILURE.
- Bifrost build/lint/pytest/coverage: GREEN.
- dependency security: GREEN.
- Heimdall `Build with Gradle` failed at the already-classified `:heimdall:checkstyleMain` boundary.
- exact log again reports **41 files / 109 warnings / 2 info**.
- this is the same pre-existing broad style debt and is **not** treated as a PR #12 / UC-01 regression.
- no mass Checkstyle cleanup is authorized by Phase 0 closure.

## Phase 0 Closure
**PASS.** The repository now has executable evidence for buildability, frontend boot, default build path, unit tests, and full core-stack startup/health. Remaining v1.0 gaps are product-flow proofs, not baseline-startup uncertainty.

---

# 5. Phase 1 — GOLDEN PATH

## Goal
Close the first real product-flow proof with actual AI execution.

## Required Flow

```text
Input / Log
→ Heimdall
→ Analysis Job
→ Kafka request
→ Bifrost consumption
→ Real Local AI inference
→ Result
→ Persistence
→ Job SUCCEEDED
```

## Phase 1 Acceptance Boundary
- [ ] one deterministic sample input/log is fixed.
- [ ] an Analysis Job is created through the real Heimdall flow.
- [ ] the request crosses Kafka to Bifrost.
- [ ] **real Local AI** is invoked; fallback/mock-only execution is not PASS.
- [ ] result returns through the real integration path.
- [ ] result is persisted.
- [ ] final Job state is `SUCCEEDED`.
- [ ] route/provider/latency evidence is captured where available.
- [ ] the flow is repeatable under reviewable execution.
- [ ] no Cloud-routing, DLQ/Redrive, dashboard expansion, README hardening, or unrelated cleanup is pulled into this batch unless executed evidence proves it is a direct blocker.

## Phase 1 Non-Goals
- Cloud-vs-Local routing proof / UC-03.
- failure recovery / UC-04.
- Grafana metric correctness / UC-05.
- final portfolio packaging.
- HP AI Server optimization.
- broad Checkstyle cleanup.

## Phase 1 Rule
A Local AI adapter, configuration, or code path existing in source is not enough. **Real model inference + end-to-end job/result evidence is required.**

---

# 6. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted Phase 0 execution | VERIFIED | PR #3 onward |
| E-002 | P0-B1 bounded repair | VERIFIED / MERGED | PR #4 |
| E-003 | Phase 0 runtime versions | VERIFIED | Java 21 / Python 3.11 / Node 20 / npm 10 / Docker 28 |
| E-004 | Heimdall Checkstyle debt | VERIFIED RED / PRE-EXISTING | 41 / 109 / 2 |
| E-005 | P0-B2 frontend repair | VERIFIED / MERGED | PR #7 |
| E-006 | Frontend production build | VERIFIED GREEN | PR #7 |
| E-016 | Frontend dev-server root | VERIFIED GREEN | PR #9 / current CI |
| E-017 | Root default SkipTests build path | VERIFIED GREEN | PR #10 / current CI |
| E-024 | UC-01 full core-stack health | **VERIFIED GREEN / MERGED** | PR #12 / CI `32320165761` |
| E-025 | P0-B4 infra readiness | VERIFIED GREEN | Postgres/Kafka/Redis/Elasticsearch/Prometheus/Grafana |
| E-035 | Heimdall full-stack health | VERIFIED GREEN | `/actuator/health` = UP |
| E-038 | Bifrost full-stack health | VERIFIED GREEN | `/health` = healthy |
| E-039 | Full-stack Frontend root | VERIFIED GREEN | root HTML captured |
| E-018 | Real Local AI E2E | **NEXT GAP** | Phase 1 |
| E-019 | Local vs Cloud Routing | PENDING | Phase 2/UC-03 |
| E-020 | DLQ → Redrive → Success | PENDING | later / UC-04 |
| E-021 | Grafana live metrics | PENDING | later / UC-05 |
| E-022 | Final Demo | PENDING | final proof packaging |
| E-023 | HP AI Server reference run | PENDING | reference deployment |

---

# 7. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | HOLD; repeatedly non-fatal; fix only if future executable evidence makes it a blocker |
| R-002 | broad Heimdall Checkstyle debt | VERIFIED PRE-EXISTING; no mass-fix without separate authorization |
| R-003 | anonymous gRPC reader may be inappropriate for future real gRPC product endpoints | current product flow has no real gRPC endpoint; replace with explicit policy if one is introduced |
| R-004 | root `start-all.ps1` banner is not health evidence | proof uses endpoint/readiness evidence instead |
| R-005 | root `start-all.ps1` Bifrost launch may not represent the proven CI `serve` invocation | evaluate only if next executable flow uses this script and it becomes a direct blocker |
| R-006 | README overclaim / Grafana port drift | proof-hardening later |
| R-007 | fallback-only AI E2E risk | Phase 1 explicitly requires real Local AI inference |
| R-008 | agent self-report | never PASS without executed evidence |

---

# 8. Work Item / PR Lifecycle

1. MASTER first.
2. Active focused PR first.
3. Search for an existing open Issue matching the next authorized acceptance gap.
4. If none exists and real work remains, create exactly one bounded Issue before implementation.
5. One active implementation Issue by default.
6. Same-gap CI/review corrections remain in the same Issue/PR.
7. RED → first concrete failure → smallest in-scope fix.
8. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
9. Issue closes only after acceptance + merge.
10. Reconcile MASTER on `main` before another Issue.
11. Human Review remains the final v1.0 gate.

---

# 9. Current Checkpoint

## Result
**PHASE 0 PASS / UC-01 PASS / PHASE 1 READY.**

## What Changed
- PR #12 exact-head primary CI completed SUCCESS.
- full core-stack application reachability completed SUCCESS.
- exact artifact proves Heimdall `UP`, Bifrost `healthy`, and Frontend root reachable.
- secondary Heimdall RED was re-confirmed as the identical pre-existing broad Checkstyle debt.
- outdated Elasticsearch review thread resolved.
- PR #12 merged with expected-head guard at `8f79c1aaf7a145abb4721c5f7799059b8c4195aa`.
- Issue #11 closed automatically as completed.
- Phase 0 closed PASS and execution contract advanced to Phase 1.

## What Was Executed
- exact-head `CI` run `32320165761`: SUCCESS.
- exact-head `CI/CD Pipeline` run `32320165695`: FAILURE only because Heimdall `checkstyleMain` remains pre-existing debt; Bifrost/security GREEN.
- full-core evidence artifact `9389538671` inspected:
  - Heimdall health = `UP`.
  - Bifrost health = `healthy`.
  - Frontend root HTML captured.
- PR #12 merged and Issue #11 closure verified.

## What Was Not Verified
- real Local AI inference E2E.
- Analysis Job → Kafka → Bifrost → real model → persisted result → SUCCEEDED flow.
- Local vs Cloud routing behavior.
- DLQ/Redrive recovery.
- live Grafana metric correctness.
- HP AI Server reference run.
- final demo/portfolio package.

## Remaining Risks
- Phase 1 may expose configuration or integration defects that startup health alone cannot reveal.
- Local AI evidence must not silently fall back to mock/fallback behavior.
- pre-existing Checkstyle debt remains visible but out of the current product-proof critical path.

## NEXT
**Re-read this synchronized MASTER, search open Issues for an exact match to the Phase 1 Real Local AI Golden Path gap, and if none exists create exactly one bounded Issue covering only: deterministic sample input → real Heimdall Analysis Job → Kafka → Bifrost → real Local AI inference → persisted result → `SUCCEEDED`. Do not include Cloud routing, recovery, observability hardening, UI expansion, README cleanup, or broad style work.**