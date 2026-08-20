# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 1 — Golden Path
- **Current Batch**: P1-B1 — UC-02 Real Local AI Golden Path
- **Batch Result**: **PASS / MERGED**
- **Status**: UC-01 PASS / UC-02 PASS / closure evaluation before next work item
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Active Issue**: NONE
- **Active PR**: NONE
- **P1-B1 Issue**: #13 — CLOSED / COMPLETED
- **P1-B1 PR**: #14 — MERGED
- **P1-B1 PR Exact Head**: `eb307ba581609790245f8e6d8fa9a53ce7b12e52`
- **P1-B1 Merge SHA**: `ee24e6990d19c0be618baf1698bff275a8b27134`
- **P1-B1 Exact-head Proof Run**: `32323663891` — SUCCESS
- **Phase 0 Result**: PASS
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
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED | **PASS — Issue #13 / PR #14** |
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
- PR #12 merged at `8f79c1aaf7a145abb4721c5f7799059b8c4195aa`.
- primary `CI` run `32320165761`: SUCCESS.
- full-core startup/health GREEN: PostgreSQL / Kafka / Redis / Elasticsearch / Prometheus / Grafana `3001` / Heimdall / Bifrost / Frontend.
- secondary pipeline RED remained only at the already-classified pre-existing Heimdall `checkstyleMain` debt.

## Phase 0 Closure
**PASS.** Remaining v1.0 gaps are product-flow proofs, not baseline-startup uncertainty.

---

# 5. Phase 1 — P1-B1 Real Local AI Golden Path — PASS

## Work Item
- **Issue #13**: CLOSED / COMPLETED
- **PR #14**: MERGED
- **Exact Head**: `eb307ba581609790245f8e6d8fa9a53ce7b12e52`
- **Merge SHA**: `ee24e6990d19c0be618baf1698bff275a8b27134`
- **Exact-head P1-B1 workflow**: run `32323663891` — **SUCCESS**
- **Exact-head primary CI**: run `32323664031` — **SUCCESS**
- **Exact-head secondary CI/CD**: run `32323663888` — RED only at pre-existing Heimdall `checkstyleMain`; Bifrost and dependency security GREEN.

## Proven Flow

```text
Deterministic ERROR log
→ Heimdall authenticated log ingestion
→ real Analysis Job
→ Kafka analysis.request
→ Bifrost consumer / HeimdallIntegrationService
→ real Ollama smollm:135m inference
→ Kafka analysis.result
→ Heimdall AnalysisResult persistence
→ final Job SUCCEEDED
```

## Exact-head Evidence
- deterministic log: `payment-service upstream gateway timeout ... transaction=p1-b1-deterministic`.
- intended manual Job ID: `4aa60d74-cf9f-41aa-b6a6-eb04a4681247`.
- Job final state: `SUCCEEDED`.
- Job `logId`: `1`.
- persisted `analysisId`: `2`.
- persisted model: `smollm:135m`.
- Kafka `analysis.result` for intended Job: `model_used=smollm:135m`, `latency_ms=121045`, status `SUCCEEDED`.
- Bifrost health before execution: Ollama `ok`, Kafka `enabled`, Heimdall integration `enabled`.
- Ollama `/api/tags`: `smollm:135m`, family `llama`, parameter size `134.52M`, quantization `Q4_0`, size `91739413` bytes.
- fallback disabled via `BIFROST_OLLAMA_ALLOW_FALLBACK=false`; persisted result assertion rejects model `fallback`.
- exact-head evidence artifact: `p1-b1-real-local-ai-evidence`, artifact `9390712782`, digest `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da`.
- previous exact-head-equivalent proof run `32323281881` was also GREEN before the trigger-filter-only review correction, demonstrating repeatability.

## Acceptance Criteria
- [x] deterministic sample input/log is fixed and reviewable.
- [x] Heimdall creates a real Analysis Job.
- [x] Kafka request publication/consumption is evidenced.
- [x] Bifrost invokes a **real Local AI model**.
- [x] mock/fallback-only execution is rejected as PASS evidence.
- [x] result returns through the real integration path.
- [x] result is persisted.
- [x] final Job state is `SUCCEEDED`.
- [x] provider/model and latency evidence is captured from the existing Kafka result surface.
- [x] flow repeated successfully under PR-visible execution.
- [x] no out-of-scope product expansion; PR changes only the bounded proof workflow.

## Review / Merge Gate
- automated review found one workflow-trigger correctness gap: root Gradle/wrapper and compose-mounted `scripts/**` inputs were omitted.
- PR #14 corrected only that path filter in the same Issue/PR.
- review thread was resolved only after verifying remote exact head.
- new exact-head P1-B1 run and primary CI were GREEN.
- secondary RED was inspected and remained the same pre-existing 41-file / 109-warning / 2-info Heimdall Checkstyle debt.
- PR #14 merged with expected-head guard; Issue #13 auto-closed as completed.

## Residual Observation
Log ingestion also creates an automatic analysis request for the same log. In both proof executions this produced an additional real-model job alongside the explicitly idempotent manual proof Job. This did **not** invalidate UC-02 because the intended manual Job independently traversed request → model → result → persistence → `SUCCEEDED`, but the duplicate/automatic behavior should be considered when later evaluating product semantics or routing. Do not fix it unless a future active acceptance gap makes it a blocker.

---

# 6. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted baseline execution | VERIFIED | Phase 0 |
| E-004 | Heimdall Checkstyle debt | VERIFIED RED / PRE-EXISTING | 41 / 109 / 2 |
| E-005 | Frontend boot repair/build | VERIFIED / MERGED | PR #7 |
| E-016 | Frontend dev-server root | VERIFIED GREEN | Phase 0 |
| E-017 | Root SkipTests build path | VERIFIED GREEN | Phase 0 |
| E-024 | UC-01 full core-stack health | VERIFIED GREEN / MERGED | PR #12 |
| E-035 | Heimdall full-stack health | VERIFIED GREEN | `/actuator/health` = UP |
| E-038 | Bifrost full-stack health | VERIFIED GREEN | `/health` = healthy |
| E-039 | Full-stack Frontend root | VERIFIED GREEN | root HTML captured |
| E-018 | Real Local AI E2E | **VERIFIED GREEN / MERGED** | Issue #13 / PR #14 / run `32323663891` |
| E-040 | Real local model identity | **VERIFIED** | `smollm:135m`; fallback disabled; artifact `9390712782` |
| E-041 | UC-02 Kafka handoff + latency | **VERIFIED** | intended Job request/result; 121045 ms exact-head run |
| E-042 | UC-02 persistence + final state | **VERIFIED** | analysisId 2 / Job SUCCEEDED |
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
| R-003 | anonymous gRPC reader may be inappropriate for future real gRPC endpoints | replace only if actual product gRPC endpoint is introduced |
| R-004 | root startup banner is not health evidence | use endpoint/readiness evidence |
| R-005 | root `start-all.ps1` Bifrost launch differs from proven CI `serve` invocation | evaluate only if a future active gap uses it and it becomes a blocker |
| R-006 | README overclaim / Grafana port drift | proof-hardening later |
| R-007 | fallback-only AI E2E risk | CLOSED for UC-02 by real model identity + fallback-disabled exact-head proof |
| R-008 | hosted CPU local inference latency can vary materially | observed ~0.7 s in first proof and ~121 s in exact-head repeat; do not claim stable performance from these proof runs |
| R-009 | log ingestion auto-analysis creates an additional job beside explicit manual analysis | HOLD; record semantics before future product-facing claims |
| R-010 | agent self-report | never PASS without executed evidence |

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
**PHASE 0 PASS / UC-01 PASS / UC-02 PASS / P1-B1 CLOSED.**

## What Changed
- fast-forwarded the existing Issue #13 branch to current `main` before implementation.
- added one bounded PR-visible UC-02 proof workflow.
- opened PR #14 and executed a real Ollama model through the existing Heimdall/Kafka/Bifrost integration.
- fixed one automated-review workflow trigger gap without product-code expansion.
- merged PR #14 with expected-head guard at `ee24e6990d19c0be618baf1698bff275a8b27134`.
- Issue #13 closed as completed.

## What Was Executed
- initial real-model proof run `32323281881`: GREEN.
- final exact-head proof run `32323663891`: GREEN.
- exact-head primary CI run `32323664031`: GREEN.
- exact-head secondary Bifrost build/test and dependency security: GREEN.
- exact-head secondary Heimdall build: RED only at existing `:heimdall:checkstyleMain` debt (41 files / 109 warnings / 2 info).
- final exact-head proof artifact inspected directly: real `smollm:135m`, Kafka handoff, persisted analysis, Job `SUCCEEDED`.

## What Was Not Verified
- UC-03 Local-vs-Cloud routing.
- UC-04 DLQ/Redrive recovery.
- UC-05 live Grafana metric correctness.
- HP AI Server reference run.
- final demo/portfolio package.
- performance consistency of hosted CPU local inference.

## Remaining Risks
- do not publish stable latency/performance claims from P1-B1; two valid real-model proofs showed materially different latency.
- auto-analysis on ingestion creates an extra analysis job in addition to the explicit manual request.
- pre-existing Heimdall Checkstyle debt remains unrelated and intentionally unmodified.

## NEXT
**Closure evaluation before any new Issue. The next frozen v1.0 use case is UC-03 Hybrid Routing, but do not create or implement it until the next run re-reads this synchronized MASTER, confirms no active PR/Issue remains, and creates exactly one bounded Issue for the smallest routing proof gap.**
