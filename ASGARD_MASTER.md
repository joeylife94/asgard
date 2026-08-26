# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0 Proof. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket / Freelance Proof
- **Target Level**: READY TO SHOW bounded software Proof candidate
- **Product Direction**: **Local-first AI Operations Platform**
- **Current Phase**: Final Proof Acceptance
- **Current Batch**: Human Review
- **Current Status**: **IMPLEMENTATION / PROOF CANDIDATE READY — HUMAN REVIEW REQUIRED**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Accepted implementation main SHA**: `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`
- **Active Issue**: none
- **Active PR**: none
- **Historical AWS work item**: Issue #15 CLOSED / NOT PLANNED; PR #16 CLOSED / NOT MERGED
- **Updated**: 2026-08-27
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
- buyer-facing truthfulness review at the final Human Review gate

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

Historical cloud code may remain in the repository. **Its existence does not make cloud execution a v1.0 requirement or accepted claim.**

---

# 3. Required Use Cases

| UC | Goal | Accepted evidence | Current |
|---|---|---|---|
| UC-01 Startup | executable core stack | required services healthy through PR-visible execution | **PASS** |
| UC-02 Local AI Analysis | real asynchronous AI job | Job → Kafka → real Ollama → result → persistence → `SUCCEEDED` | **PASS** |
| UC-03 Local-first Policy | no implicit external dependency | default/sensitive/cloud-disabled path stays local; no external provider invoked | **PASS** |
| UC-04 Recovery | controlled failure recovery | FAILED / DLQ → Redrive → Audit → Retry → `SUCCEEDED`; duplicate redrive visible | **PASS** |
| UC-05 Observability | operator visibility | requested/succeeded/failed/redriven/health live metrics + existing Grafana path | **PASS** |
| Final | buyer-facing Proof | exact evidence + truthful claims + Human Review | **HUMAN REVIEW REQUIRED** |

---

# 4. Accepted Evidence

## UC-01 — Startup — PASS
- Full core startup/health proof was accepted through PR #12.
- Verified stack included PostgreSQL, Kafka, Redis, Elasticsearch, Prometheus, Grafana, Heimdall, Bifrost, and frontend reachability.
- Frontend accepted scope is a minimal boot shell, not a full operational dashboard.
- Pre-existing Heimdall Checkstyle debt remains known and unresolved by design: recorded baseline **41 files / 109 warnings / 2 info**.

## UC-02 — Real Local AI Golden Path — PASS
- Issue #13 CLOSED / COMPLETED.
- PR #14 MERGED at `ee24e6990d19c0be618baf1698bff275a8b27134`.
- dedicated proof run `32323663891`: SUCCESS.
- primary CI `32323664031`: SUCCESS.
- artifact `9390712782`.
- digest `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da`.
- executed path: deterministic log → Heimdall Analysis Job → Kafka → Bifrost → real Ollama `smollm:135m` → result event → persistence → Job `SUCCEEDED`.
- fallback-only output was not accepted.
- hosted CPU latency is variable and must not be published as stable performance.

## UC-03 — Local-first Policy Boundary — PASS
- Issue #17 CLOSED / COMPLETED.
- PR #18 MERGED at `a7e079872004c6dcf73cdf36d105aabde37fbb8d`.
- accepted exact head `b6fc2c2f15f0d65ba6f314525740a63cc42c24ce`.
- dedicated proof `32945550180`: SUCCESS.
- primary CI `32945550197`: SUCCESS.
- artifact `9598234317`.
- digest `sha256:94ce477579261ee28cd9bec30e17d2397628158b5ba85e3a8fa168cd44b32c01`.
- default, sensitive, and cloud-hint-disabled requests all executed `on_device_rag / ollama` through production `OrchestratorService` dispatch with non-empty real results.
- `ENABLE_CLOUD_LANE=false`; cloud answerer was not initialized; no external provider was invoked.

## UC-04 — Recovery Golden Path — PASS
- Issue #19 CLOSED / COMPLETED.
- PR #20 MERGED at `37c29223044100c216372d27169eba0c3c0a0dc0`.
- accepted exact head `4b3bf88b31ae7392004121817832b232f4cd8e21`.
- dedicated recovery proof `32967543925`: SUCCESS.
- primary CI `32967543793`: SUCCESS.
- artifact `9606403831`.
- digest `sha256:a641015cdb0fa2cabebc49e27da456e93c4ecce5d4b7dff1ccb976604f00e2ec`.
- executed path: Analysis Job → deterministic failure → persisted `FAILED` → failed listing → authorized redrive → attempt `0 → 1` → Kafka retry → Bifrost → real Ollama → persisted `SUCCEEDED` → SUCCESS audit → duplicate redrive → `SKIPPED` audit with attempt unchanged.
- accepted audit snapshot records the real pre-redrive state `FAILED / 0`.
- one real bug was corrected: audit previously sampled already-mutated managed state instead of a true pre-redrive snapshot.
- local Ollama timeout was raised from 120s to 300s only as hosted-CPU tolerance, **not** as a performance claim.

## UC-05 — Observability — PASS
- Issue #21 CLOSED / COMPLETED after merge.
- PR #22 squash-merged at `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`.
- accepted exact head `e1509b7cefdb47a057c25051c16409b030c11dee`.
- dedicated proof run `33009550844`: **SUCCESS**.
- primary CI run `33009550928`: **SUCCESS**.
- supporting CI/CD run `33009550808`:
  - Bifrost build/test GREEN.
  - Dependency Security GREEN.
  - Heimdall build RED remained the known pre-existing broad Checkstyle gate and was not expanded into UC-05.
- evidence artifact `9622043567`.
- digest `sha256:783c37b1bd7079edce01caa61e5ab767826d195cb4a3b800e87ee0cb0c1262a8`.

### Actually observed live through Prometheus
- `ai_job_requested_total = 1`
- `ai_job_success_total = 1`
- `ai_job_failed_total = 1`
- `ai_job_redriven_total = 1`
- `up{job="heimdall"} = 1`

### Grafana evidence
- existing datasource was provisioned as Prometheus at `http://prometheus:9090`.
- existing Asgard dashboard was provisioned and rendered the lifecycle panels Jobs Requested / Succeeded / Failed / Redriven.
- Playwright screenshot execution was GREEN after pinning browser locale to `en-US`; diagnostic execution proved prior browser boot failure came from CI locale `en-US@posix`, not failed JS/CSS asset delivery.
- final artifact screenshot/text was inspected as synthetic-safe and contained no PII/secrets.
- final durable artifact excludes the Heimdall debug process log; the archive was inspected for credential/token patterns.
- dashboard `increase(...)` / rate-style window panels can show `0` for this very short single-event synthetic window even though the current Prometheus counter values are `1`. Therefore UC-05 proves the existing metrics/Grafana path and visible supported panels, **not production dashboard calibration or SLO maturity**.
- `ai_job_duplicate_result_total` remains source/config-only in UC-05 and is not claimed as live-observed.

## Historical AWS Experiment — DEFERRED / NOT v1.0 ACCEPTANCE
- Issue #15 CLOSED / NOT PLANNED.
- PR #16 CLOSED / NOT MERGED.
- AWS `AssumeRoleWithWebIdentity`, STS caller identity, and real Bedrock invocation/result are **not verified and not required for v1.0**.

---

# 5. Buyer-facing Claim Boundary

## Supported by accepted bounded evidence
- event-driven Java/Python AI operations architecture
- persistent asynchronous Analysis Job lifecycle
- Kafka request/result handoff
- real local Ollama inference
- result persistence and final Job state
- fail-closed Local-first routing under the accepted configuration
- bounded FAILED/DLQ → Redrive → Audit → Retry → `SUCCEEDED` recovery
- duplicate redrive visibility through `SKIPPED` audit behavior
- bounded live lifecycle metrics through Prometheus
- existing Grafana datasource/dashboard path and visible lifecycle panels

## Prohibited / Not Verified
- `production-ready`
- `enterprise-grade` as an operational-readiness claim
- legal `GDPR-compliant` certification
- production SLA/SLO
- stable latency / throughput / cost-saving percentages
- production Kubernetes / HA / multi-region readiness
- cloud-provider execution
- full operational/admin dashboard product
- unattended autonomous operations
- stable Grafana dashboard calibration from the short synthetic UC-05 run

README, ROADMAP, `PROJECT_COMPLETION.md`, old Bifrost docs, and historical portfolio text are **not authoritative** when they conflict with this Master or current accepted evidence.

---

# 6. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | known non-fatal debt; touch only if a future accepted requirement fails on it |
| R-002 | broad Heimdall Checkstyle debt | pre-existing; no mass-fix without a required gate |
| R-003 | startup script / proven CI invocation drift | evaluate only if a future required proof depends on it |
| R-004 | README / historical docs may overclaim | **Human Review gate** decides final buyer-facing reconciliation |
| R-005 | hosted CPU Ollama latency variability | no stable performance claims |
| R-006 | ingestion auto-analysis may create extra job | remain explicit in evidence; do not hide |
| R-007 | legacy AWS/Bedrock code remains | DEFER; not a v1.0 blocker or accepted execution claim |
| R-008 | duplicate routing generations | accepted `PolicyRouter` local-first path is proven; no refactor without new requirement |
| R-009 | agent self-report | never substitute for executed evidence |
| R-010 | redrive audit pre-state correctness | CLOSED for accepted UC-04 bounded path (`FAILED / 0` proven) |
| R-011 | short-window Grafana delta/rate panel semantics | UC-05 live counters are proven; do not generalize screenshot values into production observability claims |

---

# 7. Work Item / PR Lifecycle

1. MASTER first.
2. Current repository / Issue / PR / executed evidence overrides stale checkpoint text.
3. One bounded implementation/proof Issue at a time.
4. Active relevant PR first.
5. RED → first concrete failure → smallest in-scope correction.
6. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
7. Reconcile this Master on `main` after merge.
8. Final v1.0 gate is Human Review; do not create another implementation Issue merely to manufacture activity.

---

# 8. Current Checkpoint

## Result
**UC-01 PASS / UC-02 PASS / UC-03 PASS / UC-04 PASS / UC-05 PASS / AWS-CLOUD DEFERRED.**

**IMPLEMENTATION / PROOF CANDIDATE READY — HUMAN REVIEW REQUIRED.**

## Changed
- completed UC-05 under Issue #21 / PR #22 using the existing Prometheus/Grafana subsystem.
- accepted only the smallest scrape/security, datasource/dashboard provisioning, proof-harness, browser-locale, and artifact-safety corrections needed for executable evidence.
- no AWS/Bedrock/OIDC work, replacement cloud provider, new observability platform, UI expansion, RAG expansion, or broad Checkstyle cleanup was introduced.

## Actually Executed / Verified
- all required v1.0 UC-01 through UC-05 have bounded executable PASS evidence.
- UC-05 exact-head run `33009550844` and primary CI `33009550928` are GREEN.
- UC-05 artifact `9622043567` / `sha256:783c37b1bd7079edce01caa61e5ab767826d195cb4a3b800e87ee0cb0c1262a8` was inspected for synthetic safety and absence of secrets/PII.
- live Prometheus observed requested/succeeded/failed/redriven counters and Heimdall health at `1` in the accepted proof.
- existing Grafana dashboard/datasource path rendered successfully in the accepted screenshot execution.

## Not Automatically Accepted
- final public/Wishket wording, README/Proof-package truthfulness, and screenshot selection remain Human Review decisions.
- production readiness, SLO/SLA, stable performance, legal compliance, HA, cloud execution, and full admin UI are not proven.

## Closure Evaluation
The frozen v1.0 implementation/proof criteria are complete. There is no remaining mandatory automatic implementation gap. The project is therefore at its intended **Human Review boundary**.

## Exact Next Action
**Human Review:** inspect the accepted evidence and buyer-facing claim boundary, then decide the final README / Wishket / Proof-package wording and whether the candidate is accepted for external presentation. Do not create another automatic implementation Issue unless Human Review identifies one concrete bounded defect or the user creates a new explicit Sales/Proof requirement.
