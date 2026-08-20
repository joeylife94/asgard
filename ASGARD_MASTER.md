# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 1 — Golden Path
- **Current Batch**: P1-B1 — UC-02 Real Local AI Golden Path
- **Batch Result**: IN PROGRESS
- **Status**: Issue #13 OPEN / PR #14 OPEN / exact-head real-model proof running
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Active Issue**: #13 — `P1-B1: prove UC-02 real Local AI golden path`
- **Active Branch**: `agent/p1-b1-local-ai-golden-path`
- **Active PR**: #14 — `test: prove UC-02 real Local AI golden path`
- **Active PR Head**: `f4354d8a5f29c3f0d9f4a6a1711297514ade0fdc`
- **Active P1-B1 Run**: `32323281881` — IN PROGRESS
- **Phase 0 Result**: PASS
- **P0-B4 / PR #12 merge**: `8f79c1aaf7a145abb4721c5f7799059b8c4195aa`
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
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED | **IN PROGRESS — Issue #13 / PR #14** |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 | PENDING |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED | PENDING |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 | PENDING |

---

# 4. Phase 0 — PASS

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
- root `build-all.ps1 -SkipTests` frontend path GREEN.

## P0-B4 — PASS / MERGED
- Issue #11 CLOSED / COMPLETED.
- PR #12 exact head `1f3459dd5e12bf85b5eccfe41d1eca05bbf6231b`.
- PR #12 merged at `8f79c1aaf7a145abb4721c5f7799059b8c4195aa`.
- primary `CI` run `32320165761`: **SUCCESS**.
- Phase 0 preflight / unit tests / frontend dev-root / default Windows build: GREEN.
- full-core job: GREEN.
- infrastructure: PostgreSQL / Kafka / Redis / Elasticsearch / Prometheus / Grafana `3001` GREEN.
- Heimdall `/actuator/health` → `UP`.
- Bifrost `/health` → `healthy`.
- Frontend root → reachable HTML.
- secondary `CI/CD Pipeline` run `32320165695` RED only at the already-classified pre-existing Heimdall `checkstyleMain` debt; Bifrost/security GREEN.

## Phase 0 Closure
**PASS.** Remaining v1.0 gaps are product-flow proofs, not baseline-startup uncertainty.

---

# 5. Phase 1 — P1-B1 Real Local AI Golden Path

## Work Item
- **Issue #13**: OPEN
- **Branch**: `agent/p1-b1-local-ai-golden-path`
- **PR #14**: OPEN
- **Exact Head**: `f4354d8a5f29c3f0d9f4a6a1711297514ade0fdc`
- **Exact-head P1-B1 workflow**: run `32323281881` — IN PROGRESS

## Goal
Prove the first real Asgard product flow with actual local-model execution.

## Required Flow

```text
Deterministic sample log/input
→ Heimdall
→ real Analysis Job
→ Kafka request
→ Bifrost consumption
→ REAL Local AI model inference
→ result through real integration path
→ persistence
→ Job SUCCEEDED
```

## Current Executable Proof Slice
PR #14 adds one bounded GitHub-hosted workflow only. It:
- builds Heimdall and installs Bifrost from the PR head;
- starts PostgreSQL / Kafka / Redis / Elasticsearch using the existing repository Compose contract;
- starts a real Ollama runtime in Docker;
- pulls the official real model `smollm:135m`;
- starts Bifrost with `KAFKA_ENABLED=true`, `HEIMDALL_ENABLED=true`, `BIFROST_OLLAMA_MODEL=smollm:135m`, and `BIFROST_OLLAMA_ALLOW_FALLBACK=false`;
- authenticates to Heimdall and ingests one deterministic ERROR log;
- creates a real Heimdall Analysis Job;
- polls the real Job endpoint until `SUCCEEDED` or first concrete failure;
- queries the persisted Heimdall analysis result and requires its model to contain `smollm` and not equal `fallback`;
- captures Kafka request/result topics, Job ID/state, persisted result, Ollama model evidence, and service logs as an artifact.

The selected CI model is intentionally small to keep hosted execution bounded. Official Ollama registry evidence identifies `smollm:135m` as a real 135M model (~92 MB), not a mock or deterministic substitute.

## Acceptance Criteria
- [x] deterministic sample input/log is fixed and reviewable in PR #14.
- [ ] Heimdall creates a real Analysis Job — runtime proof pending.
- [ ] Kafka request publication/consumption is evidenced — runtime proof pending.
- [ ] Bifrost invokes a **real Local AI model** — runtime proof pending.
- [x] mock/fallback-only execution is explicitly rejected by the proof harness (`BIFROST_OLLAMA_ALLOW_FALLBACK=false` + persisted model assertion).
- [ ] result returns through the real integration path — runtime proof pending.
- [ ] result is persisted — runtime proof pending.
- [ ] final Job state is `SUCCEEDED` — runtime proof pending.
- [ ] route/provider/latency evidence is captured where existing surfaces expose it.
- [ ] flow is repeatable under PR-visible or equivalently reviewable execution.
- [x] no out-of-scope expansion in current diff (one proof workflow file).

## In Scope
- minimum proof harness/config/code corrections required by executed UC-02 evidence.
- one deterministic input.
- one real local provider/model path.
- only the first concrete failing boundary at a time.

## Out of Scope
- Cloud-vs-Local routing proof / UC-03.
- Cloud provider setup beyond explicitly keeping P1-B1 local-only.
- DLQ/Redrive / UC-04.
- Grafana metric correctness / UC-05.
- UI expansion.
- README/portfolio hardening.
- HP AI Server optimization/reference deployment.
- broad Heimdall Checkstyle cleanup.
- unrelated architecture refactors.

## Verification Rule
Prefer a bounded PR-visible exact-head executable proof. Preserve artifacts/logs proving Job ID/state, Kafka handoff, real model/provider invocation, returned result, persistence, and final `SUCCEEDED`.

---

# 6. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted baseline execution | VERIFIED | Phase 0 |
| E-004 | Heimdall Checkstyle debt | VERIFIED RED / PRE-EXISTING | 41 / 109 / 2 |
| E-005 | Frontend boot repair/build | VERIFIED / MERGED | PR #7 |
| E-016 | Frontend dev-server root | VERIFIED GREEN | Phase 0 |
| E-017 | Root SkipTests build path | VERIFIED GREEN | Phase 0 |
| E-024 | UC-01 full core-stack health | VERIFIED GREEN / MERGED | PR #12 / CI `32320165761` |
| E-025 | Infra readiness | VERIFIED GREEN | Postgres/Kafka/Redis/Elasticsearch/Prometheus/Grafana |
| E-035 | Heimdall full-stack health | VERIFIED GREEN | `/actuator/health` = UP |
| E-038 | Bifrost full-stack health | VERIFIED GREEN | `/health` = healthy |
| E-039 | Full-stack Frontend root | VERIFIED GREEN | root HTML captured |
| E-018 | Real Local AI E2E | **IN PROGRESS** | Issue #13 / PR #14 / run `32323281881` |
| E-040 | Real local model proof contract | EXECUTION PENDING | `smollm:135m`; fallback disabled; PR #14 |
| E-019 | Local vs Cloud Routing | PENDING | UC-03 |
| E-020 | DLQ → Redrive → Success | PENDING | UC-04 |
| E-021 | Grafana live metrics | PENDING | UC-05 |
| E-022 | Final Demo | PENDING | final proof packaging |
| E-023 | HP AI Server reference run | PENDING | reference deployment |

---

# 7. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | HOLD; repeatedly non-fatal; fix only if future executable evidence makes it a blocker |
| R-002 | broad Heimdall Checkstyle debt | VERIFIED PRE-EXISTING; no mass-fix without separate authorization |
| R-003 | anonymous gRPC reader may be inappropriate for future real gRPC endpoints | replace with explicit policy only if actual product gRPC endpoint is introduced |
| R-004 | root startup banner is not health evidence | use endpoint/readiness evidence |
| R-005 | root `start-all.ps1` Bifrost launch differs from proven CI `serve` invocation | evaluate only if P1-B1 executable path uses it and it becomes a direct blocker |
| R-006 | README overclaim / Grafana port drift | proof-hardening later |
| R-007 | fallback-only AI E2E risk | current PR explicitly disables fallback and asserts persisted model identity |
| R-008 | GitHub-hosted CPU/Ollama execution may expose runtime/network constraints | run `32323281881`; RED must identify first concrete blocker; do not substitute mock |
| R-009 | agent self-report | never PASS without executed evidence |

---

# 8. Work Item / PR Lifecycle

1. MASTER first.
2. Active focused PR first.
3. One active implementation Issue by default.
4. Same-gap CI/review corrections remain in the same Issue/PR.
5. RED → first concrete failure → smallest in-scope fix.
6. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
7. Issue closes only after acceptance + merge.
8. Reconcile MASTER on `main` before another Issue.
9. Human Review remains the final v1.0 gate.

---

# 9. Current Checkpoint

## Result
**PHASE 0 PASS / UC-01 PASS / P1-B1 IN PROGRESS / PR #14 EXECUTING.**

## What Changed
- confirmed Issue #13 remains the sole active implementation work item.
- confirmed there was no active PR for Issue #13.
- fast-forwarded `agent/p1-b1-local-ai-golden-path` to current `main` before implementation.
- inspected the real integration path: Heimdall AnalysisOrchestrator publishes `analysis.request`; Bifrost Kafka consumer calls `HeimdallIntegrationService`; local mode invokes `OllamaClient`; Bifrost publishes `analysis.result`; Heimdall exposes Job and persisted AnalysisResult endpoints.
- added one bounded PR-visible proof workflow only.
- opened PR #14 at exact head `f4354d8a5f29c3f0d9f4a6a1711297514ade0fdc`.

## What Was Executed
- PR #14 creation triggered exact-head workflows.
- `P1-B1 Real Local AI Golden Path` run `32323281881` started successfully.
- checkout, JDK setup, and Python setup are GREEN; `Prepare Heimdall and Bifrost` is currently executing.
- primary `CI` run `32323281862` is also IN PROGRESS; secondary `CI/CD Pipeline` run `32323281844` was queued at checkpoint time.

## What Was Not Verified
- real Ollama model pull/inference completion.
- real Analysis Job creation.
- Kafka request/result handoff during UC-02.
- persisted real-model result.
- final Job `SUCCEEDED`.
- route/provider/latency evidence beyond the proof contract.

## Remaining Risks
- the first exact-head runtime may expose a configuration/network/serialization defect not visible statically.
- hosted CPU inference may be slower than prior health-only jobs; workflow timeout is bounded at 30 minutes.
- no fallback/mock substitution is allowed if real Ollama execution fails.

## NEXT
**Inspect PR #14 exact-head workflow run `32323281881` first. If RED, inspect the first concrete failing step/log and fix only that Issue #13 boundary in the same PR. If the UC-02 job is GREEN, verify the uploaded artifact proves Job ID/state, Kafka handoff, real `smollm:135m` model identity, persisted result, and final `SUCCEEDED`; then inspect review/security state before merge.**
