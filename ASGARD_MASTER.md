# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0 Proof. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket / Freelance Proof
- **Target Level**: READY TO SHOW bounded software Proof
- **Product Direction**: **Local-first AI Operations Platform**
- **Current Phase**: Phase 1 — Operational Visibility / Proof Closure
- **Current Batch**: P1-B4 — UC-05 Observability live proof
- **Current Status**: **UC-01 PASS / UC-02 PASS / UC-03 PASS / UC-04 PASS / UC-05 IN PROGRESS**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Active Issue**: #21 — `P1-B4: prove UC-05 observability through existing Prometheus/Grafana path`
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
| UC-04 Recovery | controlled failure recovery | FAILED / DLQ → Redrive → Audit → Retry → `SUCCEEDED`; duplicate redrive visible | **PASS** |
| UC-05 Observability | operator visibility | requested/succeeded/failed/redriven/health evidence visible through existing metrics/Grafana path | **IN PROGRESS — Issue #21** |
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
- secondary CI/CD run `32945550181`: Bifrost GREEN and Dependency Security GREEN; Heimdall RED remained the known pre-existing Checkstyle debt.
- artifact `9598234317`
- digest `sha256:94ce477579261ee28cd9bec30e17d2397628158b5ba85e3a8fa168cd44b32c01`
- executed proof used real Ollama `smollm:135m` through production `OrchestratorService` dispatch.
- `ENABLE_CLOUD_LANE=false` proof showed default, sensitive and cloud-hint-disabled requests all executed `on_device_rag / ollama` with non-empty real results.
- cloud answerer was not initialized and no external provider was invoked.

## UC-04 — Recovery Golden Path — PASS
- Issue #19 CLOSED / COMPLETED after merge.
- PR #20 squash-merged at `37c29223044100c216372d27169eba0c3c0a0dc0`.
- accepted exact head: `4b3bf88b31ae7392004121817832b232f4cd8e21`.
- dedicated recovery proof run `32967543925`: **SUCCESS**.
- primary CI run `32967543793`: **SUCCESS**.
- secondary CI/CD run `32967543989`:
  - Bifrost build/test GREEN.
  - Dependency Security GREEN.
  - Heimdall RED remained the already-known pre-existing Checkstyle gate and was not expanded into this bounded slice.
- durable evidence artifact `9606403831`.
- artifact digest `sha256:a641015cdb0fa2cabebc49e27da456e93c4ecce5d4b7dff1ccb976604f00e2ec`.

Executed lifecycle proven:

```text
Analysis Job
→ deterministic existing DLQ failure path
→ persisted FAILED + attributable error/trace
→ failed-job listing
→ authorized POST /redrive
→ attemptCount 0 → 1
→ Kafka retry handoff
→ Bifrost
→ real Ollama
→ persisted SUCCEEDED
→ SUCCESS audit
→ duplicate redrive
→ SKIPPED audit + attemptCount remains 1
```

Accepted audit evidence includes:
- operator `admin`
- outcome `SUCCESS`
- redrive trace and reason
- true pre-redrive snapshot `previousStatus=FAILED`
- true pre-redrive snapshot `previousAttemptCount=0`
- duplicate redrive outcome `SKIPPED`
- duplicate trace/reason captured
- final job remains `SUCCEEDED`, attempt count unchanged at `1`

The proof exposed and corrected one real product bug: redrive audit previously sampled the already-mutated managed job and could record `RUNNING / 1` instead of the true pre-redrive `FAILED / 0`. The accepted correction snapshots scalar values before mutation and passes them into SUCCESS/SKIPPED audit creation.

The proof also raised the local Ollama client timeout from 120s to 300s after hosted-CPU execution exceeded the prior window. This is **not** a stable latency claim; hosted CPU remains variable.

## Historical UC-03 AWS Experiment — DEFERRED, NOT ACCEPTED AS v1.0 REQUIREMENT
- Issue #15: CLOSED / NOT PLANNED on 2026-08-26.
- PR #16: CLOSED / NOT MERGED.
- Historical LOCAL/routing diagnostics remain historical evidence only.
- **NOT VERIFIED and not required for v1.0**: AWS `AssumeRoleWithWebIdentity`, STS caller identity, real Bedrock invocation/result.

---

# 5. UC-03 — Local-first Policy Boundary

## Result
**PASS — Issue #17 completed through merged PR #18.**

No further UC-03 implementation is authorized unless later executable evidence regresses this accepted contract.

---

# 6. UC-04 — Recovery

## Result
**PASS — Issue #19 completed through merged PR #20.**

## Acceptance Criteria
- [x] deterministic persisted FAILED job through an existing bounded path.
- [x] failure state attributable by error/trace evidence.
- [x] failed-job listing exposes the target job.
- [x] existing authorized redrive endpoint invoked.
- [x] retry attempt increments and work is republished/consumed.
- [x] retry reaches `SUCCEEDED` through real local Ollama.
- [x] audit records operator/outcome/trace/reason and true pre-redrive status/attempt snapshot.
- [x] duplicate redrive is explicitly surfaced as `SKIPPED` and does not increment attempt count.
- [x] exact-head PR-visible CI and durable artifact evidence captured.

No new recovery subsystem was introduced.

---

# 7. UC-05 — Observability

Existing Prometheus/Grafana assets already reference operational metrics including job requested, succeeded, failed, redriven, and duplicate-result counters.

This is **NOT VERIFIED as a live buyer-facing Proof yet**.

## Active Work Item
- Issue #21 — `P1-B4: prove UC-05 observability through existing Prometheus/Grafana path`
- Scope is proof-first: use existing metrics/Prometheus/Grafana paths and one bounded synthetic-safe lifecycle scenario; do not invent a replacement observability subsystem.

## Acceptance Criteria
- [ ] run one bounded job/recovery scenario that emits current metrics.
- [ ] Prometheus can query the relevant metric series.
- [ ] existing Grafana dashboard loads against the configured datasource and visibly reflects supported job lifecycle metrics.
- [ ] screenshot/log evidence is synthetic-safe and contains no secrets/PII.
- [ ] distinguish metrics actually observed from counters merely present in source/config.
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
- bounded FAILED/DLQ → Redrive → Audit → Retry → `SUCCEEDED` recovery behavior
- duplicate redrive visibility through recorded `SKIPPED` audit behavior
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
| R-005 | hosted CPU Ollama latency variability | no stable performance claims; 300s client timeout is tolerance, not a performance assertion |
| R-006 | ingestion auto-analysis may create extra job | keep visible in evidence; do not hide |
| R-007 | legacy AWS/Bedrock code remains | DEFER; not a v1.0 blocker |
| R-008 | duplicate routing generations (`PrivacyRouter` vs newer `PolicyRouter`) | current intended `PolicyRouter` local-first path is proven; refactor only if a later accepted gap requires it |
| R-009 | agent self-report | never PASS without executed evidence |
| R-010 | redrive audit pre-state correctness | **CLOSED for accepted UC-04 path**: exact-head runtime proof verified `FAILED / 0`; do not generalize beyond bounded evidence |
| R-011 | historical UC-02 hosted-CPU workflow can time out under variable inference duration | supporting regression signal only; do not claim stable inference timing; investigate only if a required current acceptance gate regresses |

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
**UC-01 PASS / UC-02 PASS / UC-03 PASS / UC-04 PASS / AWS-CLOUD DEFERRED / UC-05 IN PROGRESS — Issue #21.**

## Changed
- created Issue #21 as the sole bounded UC-05 Observability work item after confirming no relevant active PR or matching Issue existed.
- no UC-05 product/proof implementation has been accepted yet.

## Actually Executed / Verified
- prior accepted UC-01 through UC-04 evidence remains unchanged.
- current main/MASTER and open Issue/PR state were re-fetched before Issue #21 creation.

## Not Verified
- UC-05 bounded scenario metric emission.
- UC-05 live Prometheus metric query evidence.
- UC-05 live Grafana dashboard evidence against configured datasource.
- buyer-facing synthetic-safe screenshot/log package for observability.
- final README / Proof-package truthfulness reconciliation.
- Human Review acceptance.

## Remaining Risks
- pre-existing Heimdall Checkstyle debt remains outside current proof unless it directly blocks a required gate.
- hosted CPU Ollama latency remains variable; no stable latency or throughput claims.
- legacy cloud-provider code remains deferred and unproven.
- no production-readiness, SLO, HA, cloud execution, or certification claim is authorized.

## Closure Evaluation
The v1.0 implementation/proof candidate is **not yet at Human Review** because `Prometheus / Grafana operating visibility` remains inside the frozen Core Must Pass boundary and UC-05 is now the active bounded work item under Issue #21.

## Exact Next Action
**Re-read this synchronized MASTER on `main`, inspect existing metrics/Prometheus/Grafana implementation, then create one Issue #21-linked branch/PR containing only the smallest executable UC-05 proof harness/correction needed to produce exact-head live Prometheus queries plus Grafana datasource/dashboard evidence. Do not touch deferred AWS/cloud scope or create another Issue.**
