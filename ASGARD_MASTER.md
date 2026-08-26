# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0 Proof. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket / Freelance Proof
- **Target Level**: READY TO SHOW bounded software Proof
- **Product Direction**: **Local-first AI Operations Platform**
- **Current Phase**: Phase 1 — Recovery Proof
- **Current Batch**: P1-B3 / UC-04 Recovery — bounded executable proof
- **Current Status**: **UC-01 PASS / UC-02 PASS / UC-03 PASS / UC-04 IN PROGRESS / UC-05 PENDING**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Active Issue**: Issue #19 — `P1-B3: prove UC-04 recovery redrive golden path`
- **Active PR**: none yet
- **Historical AWS work item**: Issue #15 CLOSED / NOT PLANNED; PR #16 CLOSED / NOT MERGED
- **Updated**: 2026-08-26
- **Final v1.0 Gate**: Human Review Required

---

# 1. Product Definition

**Asgard는 운영 로그와 이벤트를 영속적인 비동기 Job으로 처리하고, Kafka 기반 실행 흐름과 Local LLM 분석, 결과 저장, 실패 복구, 감사 및 관측 기능을 제공하는 Local-first AI Operations Platform이다.**

```text
Input / Log
  → Heimdall
  → Persistent Analysis Job
  → Kafka
  → Bifrost
  → Local AI (Ollama)
  → Result Event
  → Persistence
  → Operator / Metrics

Failure
  → FAILED / DLQ
  → Controlled Redrive
  → Audit
  → Retry
  → SUCCEEDED
```

Asgard v1.0의 중심 Proof는 **AI provider 수가 아니라 운영 가능한 AI Job lifecycle**이다.

---

# 2. Frozen v1.0 Boundary

## Core Must Pass
- Heimdall / Bifrost
- PostgreSQL / Kafka
- Local Ollama provider
- persistent Analysis Job lifecycle
- result persistence / idempotency boundary
- fail-closed local-first routing boundary
- DLQ / Redrive / Audit
- Auth / Rate Limit where used by the bounded workflow
- Prometheus / Grafana operating visibility
- minimal executable frontend boot shell only
- CI / E2E evidence
- final buyer-facing truthfulness reconciliation

## Explicitly Deferred / Not Required for v1.0
- AWS Bedrock
- AWS OIDC / IAM role setup
- real cloud-provider execution
- replacing AWS with OpenAI / Gemini / another cloud provider
- multi-provider routing expansion
- RAG as the primary Asgard Proof
- feedback / quality scoring / A-B testing / smart caching expansion
- advanced React admin dashboard
- HP AI Server reference deployment
- Kubernetes production / HA / autoscaling / multi-region
- Keycloak / Vault / enterprise secret-manager work
- full RBAC / multi-tenancy
- production SLA/SLO
- legal GDPR or security certification

Historical code may still contain Bedrock/cloud lanes. **Existence does not make them current v1.0 requirements.** Do not delete or modernize them unless a bounded accepted Proof gap requires it.

---

# 3. Required Use Cases

| UC | Goal | PASS criterion | Current |
|---|---|---|---|
| UC-01 Startup | executable core stack | clone/configure → required core services healthy | **PASS** |
| UC-02 Local AI Analysis | real asynchronous AI job | Job → Kafka → real Ollama → result → persistence → `SUCCEEDED` | **PASS** |
| UC-03 Local-first Policy | no implicit external dependency | default/sensitive/cloud-disabled path remains local; no AWS requirement | **PASS** |
| UC-04 Recovery | controlled failure recovery | FAILED / DLQ → Redrive → Audit → Retry → `SUCCEEDED` | **IN PROGRESS — Issue #19** |
| UC-05 Observability | operator visibility | requested/succeeded/failed/redriven/health evidence visible through existing metrics/Grafana path | **PENDING** |
| Final | buyer-facing Proof | exact evidence + truthful README/Proof package + Human Review | **PENDING** |

---

# 4. Accepted Evidence

## Phase 0 / UC-01 — PASS
- PR #12 merged after full core startup/health proof.
- Verified stack included PostgreSQL, Kafka, Redis, Elasticsearch, Prometheus, Grafana, Heimdall, Bifrost, and frontend reachability.
- Frontend accepted scope is a minimal boot shell, not a full operational dashboard.
- Pre-existing Heimdall Checkstyle debt remains known and is not silently treated as resolved: **41 files / 109 warnings / 2 info** at the recorded checkpoint.

## UC-02 — Real Local AI Golden Path — PASS
- Issue #13 CLOSED / COMPLETED.
- PR #14 MERGED at `ee24e6990d19c0be618baf1698bff275a8b27134`.
- proof run `32323663891`: SUCCESS.
- primary CI `32323664031`: SUCCESS.
- deterministic path executed:

```text
Log
→ Heimdall Analysis Job
→ Kafka request
→ Bifrost
→ real Ollama `smollm:135m`
→ Kafka result
→ Heimdall persistence
→ Job `SUCCEEDED`
```

- artifact `9390712782`
- digest `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da`
- fallback-only output was not accepted.
- hosted CPU latency is variable and must not be published as a stable performance claim.

## UC-03 — Local-first Policy Boundary — PASS
- Issue #17 CLOSED / COMPLETED.
- PR #18 squash-merged at `a7e079872004c6dcf73cdf36d105aabde37fbb8d`.
- accepted exact head: `b6fc2c2f15f0d65ba6f314525740a63cc42c24ce`.
- dedicated proof run `32945550180`: SUCCESS.
- primary CI run `32945550197`: SUCCESS.
- secondary CI/CD run `32945550181`: Bifrost GREEN and Dependency Security GREEN; Heimdall RED remains the already-known pre-existing Checkstyle debt and was not expanded into this bounded UC-03 work item.
- evidence artifact `9598234317`.
- artifact digest `sha256:94ce477579261ee28cd9bec30e17d2397628158b5ba85e3a8fa168cd44b32c01`.
- executed proof used real Ollama `smollm:135m` through the production `OrchestratorService` dispatch boundary.
- captured evidence:

```text
cloud_lane_enabled = false

default:
  lane = on_device_rag
  decision_provider = ollama
  executed_provider = ollama
  result_non_empty = true

sensitive:
  lane = on_device_rag
  decision_provider = ollama
  executed_provider = ollama
  result_non_empty = true

cloud_hint_disabled:
  lane = on_device_rag
  decision_provider = ollama
  executed_provider = ollama
  result_non_empty = true

cloud_answerer_initialized = false
external_provider_invoked = false
```

- The initial review defect—proofing the router decision without production dispatch—was corrected before acceptance. The exact-head run exercised `OrchestratorService._sync_answer()` and the outdated review thread was resolved only after that executable correction.
- No AWS credential, Bedrock/OIDC, replacement cloud provider, RAG expansion, frontend expansion, or unrelated product refactor was introduced.

## Historical UC-03 AWS Experiment — DEFERRED, NOT ACCEPTED AS v1.0 REQUIREMENT
- Issue #15: CLOSED / NOT PLANNED on 2026-08-26.
- PR #16: CLOSED / NOT MERGED.
- Historical LOCAL/routing diagnostics remain historical evidence only.
- **NOT VERIFIED and not required for v1.0**: AWS `AssumeRoleWithWebIdentity`, STS caller identity, real Bedrock invocation/result.

---

# 5. UC-03 — Local-first Policy Boundary

## Result
**PASS — Issue #17 completed through merged PR #18.**

## Acceptance Criteria
- [x] default request resolves to local/on-device under default configuration.
- [x] sensitive request remains local.
- [x] explicit cloud hint with `ENABLE_CLOUD_LANE=false` resolves local/fail-closed and does not initialize/invoke the cloud answerer.
- [x] accepted provider execution uses real Ollama, not mock/fallback-only output.
- [x] exact route/lane/provider/result evidence captured in PR-visible execution artifact.
- [x] exact-head dedicated proof and primary CI GREEN.
- [x] diff bounded to the proof workflow and no deferred cloud/provider scope introduced.

No further UC-03 implementation is authorized unless later executable evidence regresses this accepted contract.

---

# 6. UC-04 — Recovery

Existing code already contains failed-job listing, controlled redrive, per-user redrive rate limiting, redrive audit records, actor/source/trace/reason capture, retry preparation, Kafka re-publication, and `ai_job_redriven_total` metric hooks.

**Active bounded work item: Issue #19.** The proof must exercise the existing subsystem rather than replace it.

## Acceptance Criteria
- [ ] create or induce one deterministic failed job through a bounded supported path.
- [ ] failure state is persisted and attributable.
- [ ] redrive is authorized through the existing endpoint/path.
- [ ] redrive audit records operator/outcome and relevant trace/reason evidence.
- [ ] retry republishes work and reaches a final accepted state, preferably `SUCCEEDED`.
- [ ] duplicate or unsafe redrive behavior is not hidden.
- [ ] exact-head executable evidence is captured in PR-visible CI/artifact output.

## Current Verified Static Contract
- `GET /api/v1/analysis/jobs/failed` lists persisted FAILED jobs.
- `POST /api/v1/analysis/jobs/{jobId}/redrive` applies per-user rate limiting, invokes `redriveJob`, and records SUCCESS/SKIPPED/FAILED audit outcomes.
- `prepareRetry` only transitions retriable FAILED jobs to PENDING and increments attempt count.
- `redriveJob` rebuilds and republishes an `AnalysisRequestEvent`, marks the job RUNNING, and increments `ai_job_redriven_total`.
- per-job audit endpoint exposes operator/outcome/trace/reason fields.

These are code-path observations only; **UC-04 remains IN PROGRESS until exact-head runtime evidence proves the complete lifecycle.**

Do not invent a new recovery subsystem if the existing one can be proven.

---

# 7. UC-05 — Observability

Existing Prometheus/Grafana assets already reference operational metrics including job requested, succeeded, failed, redriven, and duplicate-result counters.

This is **NOT VERIFIED as a live buyer-facing Proof yet**.

## Acceptance Criteria
- [ ] run one bounded job/recovery scenario that emits current metrics.
- [ ] Prometheus can query the relevant metric series.
- [ ] existing Grafana dashboard loads against the configured datasource and visibly reflects supported job lifecycle metrics.
- [ ] screenshot/log evidence is synthetic-safe and contains no secrets/PII.
- [ ] no claim of production observability/SLO maturity is made.

---

# 8. Buyer-facing Claim Boundary

## Allowed after current evidence remains valid
- event-driven Java/Python AI operations architecture
- persistent asynchronous Analysis Job lifecycle
- Kafka request/result handoff
- real local Ollama inference
- result persistence and final Job state
- fail-closed Local-first routing boundary under accepted configuration
- bounded recovery/redrive/audit only after UC-04 execution
- bounded operational metrics/Grafana visibility only after UC-05 execution

## Prohibited / Not Verified
- `production-ready`
- `enterprise-grade` as an operational-readiness claim
- legal `GDPR-compliant` certification
- stable latency / throughput / cost-saving percentages
- `80%+ coverage` unless re-verified at the accepted head and needed for Proof
- production Kubernetes / HA / multi-region readiness
- cloud-provider execution
- full operational dashboard product
- unattended autonomous operations

README, ROADMAP, `PROJECT_COMPLETION.md`, old Bifrost docs, and historical portfolio text are **not authoritative** when they conflict with this Master or current evidence.

---

# 9. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | known non-fatal debt; touch only if a current proof fails on it |
| R-002 | broad Heimdall Checkstyle debt | pre-existing; no mass-fix without a required gate |
| R-003 | startup script / proven CI invocation drift | evaluate only if a required current proof depends on it |
| R-004 | README / old docs overclaim | final truthfulness reconciliation required |
| R-005 | hosted CPU Ollama latency variability | no stable performance claims |
| R-006 | ingestion auto-analysis may create extra job | keep visible in evidence; do not hide |
| R-007 | legacy AWS/Bedrock code remains | DEFER; not a v1.0 blocker |
| R-008 | duplicate routing generations (`PrivacyRouter` vs newer `PolicyRouter`) | current intended `PolicyRouter` local-first path is now proven; refactor only if a later accepted gap requires it |
| R-009 | agent self-report | never PASS without executed evidence |
| R-010 | redrive audit's recorded previous status/attempt values may depend on when the mutable job is sampled | do not assume correctness; current UC-04 execution must verify attributable audit semantics and expose any mismatch |

---

# 10. Work Item / PR Lifecycle

1. MASTER first.
2. Current repository / Issue / PR / executed evidence overrides stale checkpoint text.
3. One bounded implementation/proof Issue at a time.
4. Active relevant PR first.
5. Same-gap CI/review corrections stay in the same Issue/PR.
6. RED → first concrete failure → smallest in-scope correction.
7. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
8. Issue closes only after acceptance + merge; `not_planned` is allowed only for explicit scope removal such as historical Issue #15.
9. Reconcile this Master on `main` before selecting the next gap.
10. Re-evaluate closure before creating another Issue.
11. Final v1.0 gate is Human Review; do not auto-declare public Proof complete.

---

# 11. Current Checkpoint

## Result
**UC-01 PASS / UC-02 PASS / UC-03 PASS / AWS-CLOUD DEFERRED / UC-04 IN PROGRESS — ISSUE #19 ACTIVE.**

## Changed
- created Issue #19 as the sole bounded UC-04 Recovery work item.
- reconciled authoritative state from `UC-04 PENDING` to `UC-04 IN PROGRESS` before implementation.
- inspected existing recovery/redrive/audit code sufficiently to confirm the intended proof should use current paths, not a new subsystem.

## Actually Executed / Verified
- current `main` MASTER was read before work selection.
- open PRs were checked: none existed for UC-04.
- open Issues were checked: only unrelated/stale Issue #1 existed before Issue #19; no exact UC-04 work item existed.
- static recovery contract verified in current source: failed-job listing, controlled redrive endpoint, retry preparation, Kafka re-publication, per-user rate limiting, and audit outcome/actor/trace/reason capture paths exist.

## Not Verified
- deterministic persisted FAILED job under current exact head.
- runtime failed-job listing for that job.
- authorized redrive request and audit persistence.
- actual retry Kafka re-publication/consumption.
- final accepted retry state (`SUCCEEDED` preferred).
- duplicate/unsafe redrive runtime behavior.
- UC-05 live Prometheus/Grafana buyer-facing evidence.
- final README/Proof package truthfulness reconciliation.

## Remaining Risks
- UC-04 code existence may not match runtime semantics; only exact-head execution can close the gap.
- audit `previousStatus` / `previousAttemptCount` may reflect post-`prepareRetry` mutable state rather than the true pre-redrive state; do not claim correctness until runtime evidence verifies it.
- pre-existing Heimdall Checkstyle debt remains outside UC-04 unless it directly blocks proof execution.
- no stable latency, throughput, production-readiness, cloud execution, or certification claim is authorized.

## Exact Next Action
**Under Issue #19, create one Issue-linked branch and the smallest PR-visible proof harness that deterministically drives an existing Analysis Job to persisted FAILED, invokes the existing redrive endpoint with operator/trace/reason evidence, verifies audit + retry attempt/republication, waits for an accepted final state (prefer `SUCCEEDED`), and explicitly probes duplicate/unsafe redrive behavior. First executable RED determines the only authorized correction. Do not start UC-05 concurrently.**
