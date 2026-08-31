# ASGARD MASTER

> **Authoritative execution and progression contract**
>
> Single source of truth for the frozen Asgard v1.0 Proof baseline and bounded post-v1.0 progression. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, Scheduled Task prompt text, and agent self-report.

## 0. Control

- **Frozen Baseline**: Asgard v1.0 — Wishket / Freelance Proof
- **Frozen Baseline Level**: READY TO SHOW bounded software Proof
- **Frozen v1.0 Product Direction**: **Local-first AI Operations Platform**
- **Post-v1.0 Product Destination**: **bounded single-node Local AI Operations Tool for a technical operator**
- **Current Phase**: Post-v1.0 Bounded Progression — M1 ACCEPTED / FROZEN
- **Current Batch**: M1 — Local Reproduction & First Job — CLOSED
- **Current Status**: **v1.0 FROZEN / VERIFIED BASELINE PRESERVED — M1 PASS / ACCEPTED / FROZEN — RETURN TO PROGRESSION REVIEW**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Accepted implementation main SHA**: `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`
- **Accepted buyer-facing proof/docs main SHA**: `359b26e573e5da04b2d0ec406a56be7ecb508dbd`
- **Accepted M1 exact PR head**: `0db87a1a1feb54bf677533d88516d72f3bda73ec`
- **Accepted M1 merge main SHA**: `3e90bbd7eedca5f71c341ea91691b0cf2bc121ab`
- **Active Implementation Issue**: none
- **Active Implementation PR**: none
- **Selected Next Milestone**: none — Progression Review required before selecting the next bounded milestone
- **Human Review truthfulness item**: Issue #23 CLOSED / COMPLETED; PR #24 MERGED
- **Historical AWS work item**: Issue #15 CLOSED / NOT PLANNED; PR #16 CLOSED / NOT MERGED
- **Updated**: 2026-08-31
- **Final v1.0 Gate**: **PASS — FREEZE APPROVED**
- **Post-v1.0 Gate**: **M1 PASS / ACCEPTED / FROZEN — NEXT: PROGRESSION REVIEW**

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

Post-v1.0의 목적은 이 검증된 lifecycle을 무한 확장하는 것이 아니라, **기술 운영자가 단일 로컬/서버 환경에 재현 가능하게 설치하고, 비동기 Local AI Job을 실행·조회·복구·감사하며 시스템 상태를 이해할 수 있는 usable operational tool로 발전시키는 것**이다.

---

# 2. Frozen v1.0 Boundary

## Core Must Pass — COMPLETE
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

The v1.0 boundary is permanently preserved as a frozen verified baseline. Post-v1.0 progression must not rewrite historical v1.0 PASS claims, accepted evidence, or non-claims merely to make a later milestone look stronger.

---

# 3. Required Use Cases

| UC | Goal | Accepted evidence | Current |
|---|---|---|---|
| UC-01 Startup | executable core stack | required services healthy through PR-visible execution | **PASS** |
| UC-02 Local AI Analysis | real asynchronous AI job | Job → Kafka → real Ollama → result → persistence → `SUCCEEDED` | **PASS** |
| UC-03 Local-first Policy | no implicit external dependency | default/sensitive/cloud-disabled path stays local; no external provider invoked | **PASS** |
| UC-04 Recovery | controlled failure recovery | FAILED / DLQ → Redrive → Audit → Retry → `SUCCEEDED`; duplicate redrive visible | **PASS** |
| UC-05 Observability | operator visibility | requested/succeeded/failed/redriven/health live metrics + existing Grafana path | **PASS** |
| Final | buyer-facing Proof | exact evidence + truthful claims + Human Review | **PASS — HUMAN REVIEW PASSED** |

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
- dashboard `increase(...)` / rate-style window panels can show `0` for this very short single-event synthetic window even when the current Prometheus counter values are `1`. Therefore UC-05 proves the existing metrics/Grafana path and visible supported panels, **not production dashboard calibration or SLO maturity**.
- `ai_job_duplicate_result_total` remains source/config-only in UC-05 and is not claimed as live-observed.

## Final Human Review / Buyer-facing Truthfulness — PASS
- Human Review identified one concrete buyer-facing defect: the public README retained stale Hybrid/Cloud, production-readiness, compliance, performance, and infrastructure claims broader than the accepted v1.0 evidence.
- Issue #23 — `Proof review: reconcile buyer-facing README to accepted v1.0 evidence` — **CLOSED / COMPLETED**.
- PR #24 — `docs: reconcile buyer-facing v1.0 proof claims` — **MERGED**.
- final PR #24 exact head: `d37d8e974d1567c473e4e28b10d597dcf402f7b3`.
- exact-head `CI` run `33371042786`: **SUCCESS**.
  - Windows default build path: SUCCESS.
  - Phase 0 preflight/frontend build: SUCCESS.
  - frontend root reachability: SUCCESS.
  - full core-service startup/health: SUCCESS.
  - Heimdall + Bifrost unit tests: SUCCESS.
  - optional/manual integration job: skipped by workflow design.
- exact-head `CI/CD Pipeline` run `33371042762`: **SUCCESS**.
- final diff was README-only.
- automated review raised one valid P2 reproduction-path concern; the same PR was corrected to link the accepted executable CI / UC-02 / UC-03 / UC-04 / UC-05 workflow paths directly.
- PR #24 was squash-merged with expected-head guard at `359b26e573e5da04b2d0ec406a56be7ecb508dbd`.
- Issue #23 auto-closed as completed.
- no product/runtime feature was added for Human Review closure.

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

The public README has been reconciled to this boundary. ROADMAP, `PROJECT_COMPLETION.md`, old Bifrost docs, and historical portfolio text remain non-authoritative when they conflict with this Master or current accepted evidence.

Post-v1.0 milestone acceptance may add new supported claims only when the new claim has its own executable acceptance evidence. It does not retroactively broaden v1.0.

---

# 6. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | known non-fatal debt; touch only if a future accepted requirement fails on it |
| R-002 | broad Heimdall Checkstyle debt | pre-existing; no mass-fix without a required gate |
| R-003 | startup script / proven CI invocation drift | **M1 CLOSED for the accepted bounded Linux reproduction path**; broader convenience remains out of scope until another accepted requirement needs it |
| R-004 | README / historical docs may overclaim | **README CLOSED via Issue #23 / PR #24; historical docs remain non-authoritative context** |
| R-005 | hosted CPU Ollama latency variability | M1/UC-03 proof harnesses use an explicit bounded generation option; no stable performance claims |
| R-006 | ingestion auto-analysis may create extra job | M1/UC-02 proof processes isolate the explicit target Job; product-default behavior is not claimed changed |
| R-007 | legacy AWS/Bedrock code remains | DEFER; not a v1.0 blocker or automatic post-v1.0 progression target |
| R-008 | duplicate routing generations | accepted `PolicyRouter` local-first path is proven; no refactor without a milestone requirement |
| R-009 | agent self-report | never substitute for executed evidence |
| R-010 | redrive audit pre-state correctness | CLOSED for accepted UC-04 bounded path (`FAILED / 0` proven) |
| R-011 | short-window Grafana delta/rate panel semantics | UC-05 live counters are proven; do not generalize screenshot values into production observability claims |

Known risks do not reopen or weaken the frozen v1.0 baseline. A risk may become active post-v1.0 work only when it blocks the currently selected bounded milestone or creates a reproducibility/reliability regression against an accepted path.

---

# 7. Work Item / PR Lifecycle

1. MASTER first.
2. Current repository / Issue / PR / executed evidence overrides stale checkpoint text and Scheduled Task self-report.
3. One bounded implementation/proof Issue at a time.
4. Active relevant PR first.
5. Define executable Acceptance Criteria before implementation.
6. RED → first concrete failure → smallest in-scope correction.
7. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
8. Close the Issue only after accepted evidence exists.
9. Reconcile this Master on `main` after merge.
10. Evaluate Milestone Acceptance before selecting another Issue.
11. A frozen accepted milestone becomes a new preserved baseline slice; **FREEZE does not mean project development ends**.
12. After each accepted milestone, return to Progression Review and select the next bounded milestone only when it has clear usability, reproducibility, reliability/recovery, observability/auditability, demonstrability, or delivery value.
13. Do not manufacture work for activity. Existing asset reuse and small gap closure precede new implementation.

---

# 8. Frozen v1.0 Checkpoint

## Result
**UC-01 PASS / UC-02 PASS / UC-03 PASS / UC-04 PASS / UC-05 PASS / HUMAN REVIEW PASS / AWS-CLOUD DEFERRED.**

**ASGARD PROOF v1.0 CLOSED / FREEZE — HUMAN REVIEW PASSED.**

## Changed
- completed UC-01 through UC-05 within the frozen Local-first v1.0 boundary;
- closed the final buyer-facing README truthfulness defect through Issue #23 / PR #24;
- replaced stale Hybrid/Cloud and production/compliance wording with claims bounded to accepted evidence;
- restored direct links to accepted executable proof workflows after review feedback;
- no AWS/Bedrock/OIDC work, replacement cloud provider, new observability platform, UI expansion, RAG expansion, or broad Checkstyle cleanup was introduced.

## Actually Executed / Verified
- all required v1.0 UC-01 through UC-05 have bounded executable PASS evidence;
- UC-05 exact-head run `33009550844` and primary CI `33009550928` are GREEN;
- UC-05 artifact `9622043567` / `sha256:783c37b1bd7079edce01caa61e5ab767826d195cb4a3b800e87ee0cb0c1262a8` was inspected for synthetic safety and absence of secrets/PII;
- live Prometheus observed requested/succeeded/failed/redriven counters and Heimdall health at `1` in the accepted proof;
- existing Grafana dashboard/datasource path rendered successfully in the accepted screenshot execution;
- final Human Review README head `d37d8e974d1567c473e4e28b10d597dcf402f7b3` passed CI `33371042786` and CI/CD `33371042762`;
- PR #24 merged at `359b26e573e5da04b2d0ec406a56be7ecb508dbd` and Issue #23 closed completed.

## Not Verified / Explicit Non-Claims
- production readiness;
- production SLA/SLO, stable latency/throughput/cost savings;
- legal GDPR/security compliance certification;
- production Kubernetes/HA/multi-region posture;
- accepted cloud-provider execution;
- full operational/admin dashboard product;
- unattended autonomous operations;
- production observability calibration beyond the bounded proof conditions.

## Closure Evaluation
The frozen v1.0 implementation, executable Proof, buyer-facing truthfulness, and Human Review criteria are complete. No mandatory v1.0 gap remains.

## Exact Next Action
**Preserve v1.0 as a frozen verified baseline. Do not reopen v1.0 scope. Continue only through the bounded post-v1.0 progression contract below.**

---

# 9. Post-v1.0 Progression Contract

## 9.1 Product Destination

Post-v1.0 Asgard targets:

> **A bounded, single-node Local AI Operations Tool that a technical operator can reproducibly deploy, use to submit and inspect asynchronous Local AI analysis jobs, recover supported failures, audit operator actions, and understand system health without requiring a cloud AI provider.**

This destination is intentionally narrower than an enterprise AI platform.

### Intended user
- one technical operator or a small technical team using the same bounded environment;
- developer / backend engineer / AI engineer / internal operator;
- user can understand service health, jobs, failures, retries, and logs at a technical level.

### Intended use
- start the supported local stack;
- submit or trigger an analysis job;
- inspect job lifecycle and result;
- identify supported failures;
- perform controlled redrive where allowed;
- inspect audit and trace information;
- understand bounded system health;
- hand the supported single-node setup to another technical operator with explicit constraints.

## 9.2 Progression Axes — Priority Order

Default priority:

1. **Usability**
2. **Reproducibility**
3. **Reliability / Recovery**
4. **Observability / Auditability**
5. **Buyer-facing Demonstrability**
6. **Delivery Readiness**
7. **Maintainability / Security only when it blocks actual use or delivery**
8. **New Capability only when the earlier axes cannot close the accepted gap**

M1 intentionally starts with reproducibility because every later operator-facing milestone depends on a trustworthy clean start / first-job verification path. This is an enabling exception, not a reversal of the long-term priority order.

## 9.3 Progression Loop

```text
Frozen Verified Baseline
→ Progression Review
→ Select one bounded milestone
→ Create one implementation Issue
→ Branch
→ Implementation
→ PR
→ Exact-head Verification
→ Merge
→ Issue Close
→ MASTER Reconciliation
→ Milestone Acceptance / Freeze
→ Progression Review
```

Rules:
- only one active bounded implementation Issue per repository;
- active relevant PR is always handled before new work;
- milestone scope and executable acceptance are fixed before implementation;
- accepted milestone evidence must record Changed / Executed / Verified / Not Verified / Known Limitations;
- agent self-report is never Final Acceptance;
- a later milestone must preserve already accepted v1.0 behavior unless the user explicitly approves a product-direction change;
- technical HOLD / RED is a correction state, not a reason to stop progression;
- no-op MASTER churn is prohibited.

## 9.4 Automatic Scope Guardrails

The Builder must not automatically select these as progression work:
- AWS Bedrock / OIDC / IAM;
- OpenAI / Gemini / other cloud-provider expansion;
- multi-provider routing as a product goal;
- Kubernetes / HA / autoscaling / multi-region;
- multi-tenancy;
- full RBAC / SSO / enterprise identity;
- billing;
- unattended autonomous operations;
- broad RAG expansion;
- feedback / experiment / MLflow / cache subsystems merely because historical code exists;
- broad Checkstyle cleanup;
- generic refactors without a current Acceptance blocker;
- full admin-platform feature competition.

Historical or unused assets may be reused only after proving that reuse is the smallest gap closure for the selected milestone. Existing code is not accepted functionality until executed and verified under that milestone.

## 9.5 Builder Stop / Disable Conditions

The existence of a frozen version, READY TO SHOW state, Human Review PASS, or accepted milestone **does not disable the progression Builder**.

Builder disable / queue is allowed only when:
- explicit user/product stop;
- repository archived or superseded;
- unsafe or material human product-direction decision is required before any bounded milestone can be selected;
- external WIP cap requires `QUEUED — WIP CAP` rotation;
- no useful bounded milestone remains within the defined destination and further work would be feature creep.

---

# 10. Post-v1.0 Milestone Map

The map is directional. Only the selected milestone becomes active work. Later milestones must be re-reviewed against actual main state after every acceptance.

## M1 — Local Reproduction & First Job

### Why
CI proves the stack can execute, but CI execution is not yet equivalent to a low-friction technical-operator reproduction path. A trustworthy clean-start contract reduces setup ambiguity and becomes reusable verification infrastructure for every later milestone.

### Scope
- clean-checkout supported environment contract;
- explicit prerequisites and configuration preflight;
- Local Ollama/model availability check;
- smallest supported start path for required services;
- health confirmation;
- one deterministic sample input / analysis request;
- real Local Ollama execution through the accepted Job lifecycle;
- result / final Job state confirmation;
- bounded teardown / reset guidance;
- reuse existing scripts/workflows where possible before creating new machinery.

### Executable Acceptance
From a clean supported environment with declared prerequisites:
1. preflight clearly PASSes or fail-fast identifies a missing prerequisite/configuration;
2. required bounded services become healthy through the documented start path;
3. a deterministic sample request creates a persistent Analysis Job;
4. the request traverses Kafka → Bifrost → real Ollama;
5. a non-fallback result is persisted and the Job reaches `SUCCEEDED`;
6. operator-visible commands/output identify the Job and result;
7. teardown leaves the documented bounded state;
8. primary regression CI remains GREEN on the exact PR head.

### Evidence
- exact commands / environment preconditions;
- preflight output;
- health output;
- Job ID / lifecycle output;
- real Ollama/model evidence without secrets;
- final result/state evidence;
- exact-head CI/run links and artifact where durable evidence is useful;
- Known Limitations and What Was Not Verified.

### Stop Condition
Stop when one clean supported reproduction path and first real Local AI Job are independently executable and exact-head verified. Do not add UI, cloud providers, HA, deployment orchestration, or unrelated cleanup in M1.

**Current: ACCEPTED / FROZEN — PASS**

---

## M2 — Operator Console: Read-only Job Lifecycle

### Why
The backend has meaningful Job lifecycle APIs, while the current React surface is only a boot shell. The next usability gap is to let a technical operator understand current jobs without assembling API calls manually.

### Scope
- minimal recent Job list/read surface;
- Job detail;
- status / timestamps / attempt count;
- result summary/payload or bounded error state;
- failed-job visibility;
- trace/result references that already exist in the backend;
- smallest backend read API gap only if the current API cannot support the view.

### Executable Acceptance
- browser-visible Job list from real persisted data;
- Job detail accurately matches backend persisted state;
- successful Job result is inspectable;
- failed Job state/error is inspectable;
- no mutation/redrive control is introduced in M2;
- Playwright or equivalent browser path verifies the bounded workflow;
- existing v1.0 regression paths remain GREEN.

### Evidence
- browser screenshots/video where useful;
- browser E2E log;
- API/integration tests for any new read contract;
- exact-head CI.

### Stop Condition
Stop when an operator can inspect the supported lifecycle without curl/manual DB inspection. Do not build a generic admin dashboard.

**Current: FUTURE CANDIDATE / NOT STARTED**

---

## M3 — Controlled Recovery Operator Workflow

### Why
Backend redrive/audit is already strong proof, but real operator usability requires a controlled, understandable recovery workflow rather than hidden API-only mutation.

### Scope
- failed Job selection;
- explicit redrive reason;
- confirmation boundary;
- supported rate-limit/error feedback;
- attempt transition visibility;
- duplicate-redrive behavior visibility;
- redrive audit history in the bounded operator surface.

### Executable Acceptance
A deterministic failure can be observed in the operator surface, redriven through the authorized production endpoint, reach `SUCCEEDED`, and display the resulting audit record. Duplicate redrive must remain visible as bounded non-creation / `SKIPPED` behavior without silently mutating attempt state.

### Evidence
- browser E2E covering failure → redrive → success → audit;
- API/integration regression evidence;
- screenshot/video of the bounded operator path;
- exact-head CI.

### Stop Condition
Stop when the already-accepted recovery semantics are safely usable through the minimal operator workflow. Do not add arbitrary write tools or autonomous retry control.

**Current: FUTURE CANDIDATE / NOT STARTED**

---

## M4 — Runtime Resilience & Traceability

### Why
A single deterministic redrive proof does not establish behavior across process interruption or temporary service failure. Before stronger delivery claims, a small number of realistic lifecycle failure cases should be proven end to end.

### Scope
At milestone start, select only one or two concrete failure modes from current evidence, for example:
- temporary Bifrost unavailability;
- Heimdall/Bifrost restart around a persisted Job;
- duplicate result/idempotency boundary;
- Kafka interruption/recovery where the existing architecture supports a bounded deterministic proof.

Do not attempt a comprehensive chaos/HA program.

### Executable Acceptance
Each selected failure mode must have a deterministic reproduction, explicit expected persisted state, recovery procedure or bounded fail-closed outcome, exact actual result, and no regression to accepted v1.0 lifecycle semantics.

### Evidence
- deterministic failure-injection steps;
- Job/attempt/trace state before and after;
- recovery/audit output;
- exact-head integration proof;
- known unsupported failure classes.

### Stop Condition
Stop after the selected bounded failure cases are accepted. Do not generalize into SLA/HA claims.

**Current: FUTURE CANDIDATE / NOT STARTED**

---

## M5 — Single-node Delivery Handoff

### Why
A usable technical tool becomes delivery-relevant only when another technical operator can receive the supported deployment boundary and reproduce normal operation without private tribal knowledge.

### Scope
- supported single-node environment boundary;
- prerequisites / configuration ownership;
- start / stop / restart;
- persistence expectations;
- supported update/redeploy path if already practical;
- bounded troubleshooting/runbook path;
- explicit backup/restore boundary: either verified supported procedure or explicit NOT VERIFIED statement;
- proof/reproduction command reference.

### Executable Acceptance
A clean independent handoff exercise can follow the documented supported path to start the system, run a real Local AI Job, inspect result/health, restart within the supported boundary, and identify known limitations without undocumented private steps.

### Evidence
- handoff checklist;
- clean-environment execution log;
- exact commands/config contract;
- restart/persistence evidence for whatever is claimed;
- unresolved risks and non-claims.

### Stop Condition
Stop when the defined single-node handoff is reproducible. Do not extend into production HA, Kubernetes, enterprise identity, or legal compliance unless a separate approved delivery requirement requires it.

**Current: FUTURE CANDIDATE / NOT STARTED**

---

# 11. Current Post-v1.0 Progression Checkpoint

## Decision
- v1.0 remains **PASS / FREEZE / HUMAN REVIEW PASSED**.
- Post-v1.0 destination remains **Local AI Operations Tool**.
- M1 — Local Reproduction & First Job is **PASS / ACCEPTED / FROZEN**.
- no next milestone is automatically active; return to Progression Review against current `main` before selecting another bounded Issue.

## Changed by M1
- added `scripts/local-proof.sh` as one supported bounded Local-first reproduction command for Unix-like environments;
- added `.github/workflows/v11-m1-local-proof.yml` with exact-head execution, PASS artifact, and failure diagnostics;
- protected caller-owned work directories from recursive cleanup and reject non-empty caller-owned directories before mutation;
- removed tracked `gradlew` executable-bit mutation from the runner by invoking it through `bash`;
- added opt-in `BIFROST_OLLAMA_NUM_PREDICT` generation bounds without changing default product inference behavior;
- bounded M1 and UC-03 hosted proof generation to remove stochastic runaway output;
- isolated the UC-02 proof target Job from ingestion auto-analysis only inside the proof process and kept its hosted polling window bounded;
- did not add UI, cloud execution, Kubernetes/HA, RAG expansion, production claims, or broad Checkstyle cleanup.

## Actually Executed / Verified for M1
- Issue #25 — **CLOSED / COMPLETED**.
- PR #30 — **SQUASH MERGED** with expected-head guard.
- accepted exact PR head: `0db87a1a1feb54bf677533d88516d72f3bda73ec`.
- merge main SHA: `3e90bbd7eedca5f71c341ea91691b0cf2bc121ab`.
- primary `CI` run `33399015985` (#132): **SUCCESS**.
- M1 Local Proof Runner run `33399015962` (#11): **SUCCESS**.
- UC-02 real Local AI run `33399016060` (#30): **SUCCESS**.
- UC-03 Local-first Policy run `33399016019` (#9): **SUCCESS**.
- UC-04 Recovery run `33399015968` (#21): **SUCCESS**.
- M1 artifact `9760584618`, digest `sha256:f8011b67f5c49a87ddef93356295d403d37d4dc731b82811bfe087c2399c361`, was directly inspected and records `status=PASS`, `provider=ollama`, `model=smollm:135m`, persistent Job/Log/Analysis IDs, `synthetic=true`, and `cloudExecution=false` without credential material in the summary.
- supporting UC-02 artifact `9760764140`, digest `sha256:fc38cec2e4b364b335d699dbbd280b6c848a121d9aeae1865eb3d663095bd12f`.
- supporting UC-03 artifact `9760508364`, digest `sha256:487b928ffe89e880e2f39acd98ed03c0797ccc32c4d06e3e27fcca665ee6aa5e`.
- automated review findings for caller-owned work-dir deletion and tracked `gradlew` mode mutation were corrected, replied to, and both review threads are resolved.
- `CI/CD Pipeline` run `33399016089` (#149) remains **RED only on the pre-existing broad Heimdall Checkstyle gate**: `checkstyleMain` reported 41 files / 111 warnings / 2 info. The same run has Bifrost build/test, Dependency Security, Code Quality, and CI/CD Summary GREEN. M1 changes no Java source and does not claim this debt resolved.

## Not Verified / Known Limitations
- macOS was not independently executed; accepted M1 executable evidence is GitHub-hosted Linux;
- existing Windows scripts were not replaced;
- hosted CPU Ollama latency remains variable and no latency/throughput/cost/SLA/SLO claim is added;
- production readiness, production HA/Kubernetes, cloud-provider execution, enterprise identity, and full admin-console behavior remain outside the accepted boundary;
- M2 operator-console usability, M3 operator recovery UI, M4 broader runtime resilience, and M5 independent delivery handoff remain NOT VERIFIED.

## Closure Evaluation
M1 satisfies its bounded executable acceptance: a supported clean-path runner performs preflight, service readiness, one persistent Job, Kafka → Bifrost → real Ollama execution, persisted non-fallback result, operator-visible identifiers, and bounded cleanup with exact-head regression evidence. **M1 is therefore accepted and frozen as a new post-v1.0 baseline slice.** This FREEZE does not terminate Asgard progression.

## Exact Next Action
**Return to Progression Review. Re-read current `main`, preserve v1.0 + M1 accepted evidence, and select exactly one next bounded milestone only if it closes a concrete usability/reliability/observability/delivery gap. M2 is the current directional candidate because operator usability is the highest remaining product gap, but it must not be treated as active work until the Progression Review confirms it.**