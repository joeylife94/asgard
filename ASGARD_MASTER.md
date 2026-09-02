# ASGARD MASTER

> **Authoritative execution and progression contract**
>
> Single source of truth for the frozen Asgard v1.0 Proof baseline and bounded post-v1.0 progression. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, Scheduled Task prompt text, and agent self-report.

## 0. Control

- **Frozen Baseline**: Asgard v1.0 — Wishket / Freelance Proof
- **Frozen Baseline Level**: READY TO SHOW bounded software Proof
- **Frozen v1.0 Product Direction**: **Local-first AI Operations Platform**
- **Post-v1.0 Product Destination**: **bounded single-node Local AI Operations Tool for a technical operator**
- **Current Phase**: Post-v1.0 Bounded Progression — M6 SELECTED
- **Current Batch**: M6 — Persisted-state Backup/Restore Proof — SELECTED / ISSUE NOT YET OPEN
- **Current Status**: **v1.0 FROZEN / M1 FROZEN / M2 FROZEN / M3 FROZEN / M4 FROZEN / M5 FROZEN — M6 SELECTED**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Accepted implementation main SHA**: `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`
- **Accepted buyer-facing proof/docs main SHA**: `359b26e573e5da04b2d0ec406a56be7ecb508dbd`
- **Accepted M1 exact PR head**: `0db87a1a1feb54bf677533d88516d72f3bda73ec`
- **Accepted M1 merge main SHA**: `3e90bbd7eedca5f71c341ea91691b0cf2bc121ab`
- **Accepted M2 exact PR head**: `224e53814bc33e565189acd0b2c45866be32f2a0`
- **Accepted M2 merge main SHA**: `07875ef2c9f6784d54c23c2bb19b326d2ff6ed86`
- **Accepted M3 exact PR head**: `b4e79a00dc3677746a244a08c6fd36dfccba620c`
- **Accepted M3 merge main SHA**: `c97dfa2d79f81b7b0172833769a71164934a103e`
- **Accepted M4 exact PR head**: `e46f11cc9cccd7763cc8d6e7b3dbcd8907af934b`
- **Accepted M4 merge main SHA**: `d853f8b5fe248ee2e0fd0032f6e0ffccadc5f578`
- **Accepted M5 exact PR head**: `b13438d91ca13ac9a889bad4f31a2b33550533e9`
- **Accepted M5 merge main SHA**: `3f6eb40793991adba82c7d5b60920a5f60c80a04`
- **Active Implementation Issue**: none
- **Active Implementation PR**: none
- **Selected Next Milestone**: M6 — Persisted-state Backup/Restore Proof
- **Human Review truthfulness item**: Issue #23 CLOSED / COMPLETED; PR #24 MERGED
- **Historical AWS work item**: Issue #15 CLOSED / NOT PLANNED; PR #16 CLOSED / NOT MERGED
- **Updated**: 2026-09-03
- **Final v1.0 Gate**: **PASS — FREEZE APPROVED**
- **Post-v1.0 Gate**: **M1 PASS / M2 PASS / M3 PASS / M4 PASS / M5 PASS — M6 SELECTED**

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

# 3. Required v1.0 Use Cases

| UC | Goal | Accepted evidence | Current |
|---|---|---|---|
| UC-01 Startup | executable core stack | required services healthy through PR-visible execution | **PASS** |
| UC-02 Local AI Analysis | real asynchronous AI job | Job → Kafka → real Ollama → result → persistence → `SUCCEEDED` | **PASS** |
| UC-03 Local-first Policy | no implicit external dependency | default/sensitive/cloud-disabled path stays local; no external provider invoked | **PASS** |
| UC-04 Recovery | controlled failure recovery | FAILED / DLQ → Redrive → Audit → Retry → `SUCCEEDED`; duplicate redrive visible | **PASS** |
| UC-05 Observability | operator visibility | requested/succeeded/failed/redriven/health live metrics + existing Grafana path | **PASS** |
| Final | buyer-facing Proof | exact evidence + truthful claims + Human Review | **PASS — HUMAN REVIEW PASSED** |

---

# 4. Frozen v1.0 Accepted Evidence

## UC-01 — Startup — PASS
- accepted through PR #12;
- PostgreSQL, Kafka, Redis, Elasticsearch, Prometheus, Grafana, Heimdall, Bifrost, and frontend reachability verified;
- frontend v1.0 remained a minimal boot shell;
- broad Heimdall Checkstyle debt remained known: baseline 41 files / 109 warnings / 2 info.

## UC-02 — Real Local AI Golden Path — PASS
- Issue #13 CLOSED / COMPLETED;
- PR #14 MERGED at `ee24e6990d19c0be618baf1698bff275a8b27134`;
- dedicated proof `32323663891`: SUCCESS;
- primary CI `32323664031`: SUCCESS;
- artifact `9390712782`, digest `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da`;
- deterministic log → Analysis Job → Kafka → Bifrost → real Ollama `smollm:135m` → result → persistence → `SUCCEEDED`;
- fallback-only output was not accepted; hosted CPU latency is not a stable performance claim.

## UC-03 — Local-first Policy Boundary — PASS
- Issue #17 CLOSED / COMPLETED;
- PR #18 MERGED at `a7e079872004c6dcf73cdf36d105aabde37fbb8d`;
- accepted head `b6fc2c2f15f0d65ba6f314525740a63cc42c24ce`;
- dedicated proof `32945550180`: SUCCESS;
- primary CI `32945550197`: SUCCESS;
- artifact `9598234317`, digest `sha256:94ce477579261ee28cd9bec30e17d2397628158b5ba85e3a8fa168cd44b32c01`;
- default, sensitive, and cloud-hint-disabled requests all executed `on_device_rag / ollama`; no external provider was invoked.

## UC-04 — Recovery Golden Path — PASS
- Issue #19 CLOSED / COMPLETED;
- PR #20 MERGED at `37c29223044100c216372d27169eba0c3c0a0dc0`;
- accepted head `4b3bf88b31ae7392004121817832b232f4cd8e21`;
- recovery proof `32967543925`: SUCCESS;
- primary CI `32967543793`: SUCCESS;
- artifact `9606403831`, digest `sha256:a641015cdb0fa2cabebc49e27da456e93c4ecce5d4b7dff1ccb976604f00e2ec`;
- deterministic `FAILED` → listing → authorized redrive → attempt `0→1` → Kafka → Bifrost → real Ollama → `SUCCEEDED` → audit → duplicate redrive `SKIPPED`;
- accepted audit snapshot records true pre-redrive `FAILED / 0`.

## UC-05 — Observability — PASS
- Issue #21 CLOSED / COMPLETED;
- PR #22 squash-merged at `cc5cd10722a4c629da75e90ca0fa4daa05b75a01`;
- accepted head `e1509b7cefdb47a057c25051c16409b030c11dee`;
- dedicated proof `33009550844`: SUCCESS;
- primary CI `33009550928`: SUCCESS;
- artifact `9622043567`, digest `sha256:783c37b1bd7079edce01caa61e5ab767826d195cb4a3b800e87ee0cb0c1262a8`;
- live observed: `ai_job_requested_total=1`, `ai_job_success_total=1`, `ai_job_failed_total=1`, `ai_job_redriven_total=1`, `up{job="heimdall"}=1`;
- Grafana Prometheus datasource/dashboard rendered in browser execution;
- short-window rate/delta values are not production calibration or SLO evidence.

## Final Human Review / Buyer-facing Truthfulness — PASS
- Issue #23 CLOSED / COMPLETED;
- PR #24 MERGED at `359b26e573e5da04b2d0ec406a56be7ecb508dbd`;
- exact head `d37d8e974d1567c473e4e28b10d597dcf402f7b3`;
- `CI` `33371042786`: SUCCESS;
- `CI/CD Pipeline` `33371042762`: SUCCESS;
- README reconciled to accepted Local-first claims; no runtime feature was added for Human Review closure.

## Historical AWS Experiment — DEFERRED / NOT v1.0 ACCEPTANCE
- Issue #15 CLOSED / NOT PLANNED;
- PR #16 CLOSED / NOT MERGED;
- AWS `AssumeRoleWithWebIdentity`, STS caller identity, and real Bedrock invocation/result are **not verified and not required for v1.0**.

---

# 5. Buyer-facing Claim Boundary

## Supported by frozen v1.0 bounded evidence
- event-driven Java/Python AI operations architecture;
- persistent asynchronous Analysis Job lifecycle;
- Kafka request/result handoff;
- real local Ollama inference;
- result persistence and final Job state;
- fail-closed Local-first routing under accepted configuration;
- bounded FAILED/DLQ → Redrive → Audit → Retry → `SUCCEEDED` recovery;
- duplicate redrive visibility through `SKIPPED` audit behavior;
- bounded live lifecycle metrics through Prometheus;
- existing Grafana datasource/dashboard path and visible lifecycle panels.

## Prohibited / Not Verified by v1.0
- `production-ready`;
- `enterprise-grade` as an operational-readiness claim;
- legal `GDPR-compliant` certification;
- production SLA/SLO;
- stable latency / throughput / cost-saving percentages;
- production Kubernetes / HA / multi-region readiness;
- cloud-provider execution;
- full operational/admin dashboard product;
- unattended autonomous operations;
- stable Grafana calibration from the short synthetic UC-05 run.

Post-v1.0 milestone acceptance may add new supported claims only when the claim has its own executable acceptance evidence. It does not retroactively broaden v1.0.

---

# 6. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | known non-fatal debt; touch only if a future accepted requirement fails on it |
| R-002 | broad Heimdall Checkstyle debt | pre-existing; no mass-fix without a required gate |
| R-003 | startup script / proven CI invocation drift | M1 CLOSED for accepted bounded Linux reproduction path; broader convenience remains out of scope until required |
| R-004 | README / historical docs may overclaim | README CLOSED via Issue #23 / PR #24; historical docs remain non-authoritative context |
| R-005 | hosted CPU Ollama latency variability | M1/UC-03 proof harnesses use bounded generation; no stable performance claims |
| R-006 | ingestion auto-analysis may create extra job | accepted proof paths isolate target Job where required; default behavior not claimed changed |
| R-007 | legacy AWS/Bedrock code remains | DEFER; not an automatic progression target |
| R-008 | duplicate routing generations | no refactor without a milestone requirement |
| R-009 | agent self-report | never substitute for executed evidence |
| R-010 | redrive audit pre-state correctness | CLOSED for accepted UC-04 bounded path (`FAILED / 0` proven) |
| R-011 | short-window Grafana delta/rate semantics | do not generalize bounded screenshot values into production observability claims |
| R-012 | M2 operator console is bounded/read-only by default | accepted for recent persisted Job list/detail and success/failure inspection; M3 recovery appears only under its explicit recovery feature flag |
| R-013 | proof harness ordering can race queued analysis requests | M3 exact-head proof explicitly consumed the seed request before starting Bifrost; do not generalize this harness isolation into autonomous runtime guarantees |
| R-014 | Bifrost restart proof is one bounded single-node replay case | accepted M4 proves one SIGKILL/restart path only; do not generalize to Kafka outage, HA, recovery time, or autonomous retry |
| R-015 | backup/restore remains unverified after delivery handoff | M5 states this explicitly; M6 may verify one bounded persisted-state backup/restore path without implying DR/HA |

Known risks do not reopen or weaken frozen accepted milestones. A risk becomes active work only when it blocks the selected bounded milestone or creates regression against an accepted path.

---

# 7. Work Item / PR Lifecycle

1. MASTER first.
2. Current repository / Issue / PR / executed evidence overrides stale checkpoint text and Scheduled Task self-report.
3. One bounded implementation/proof Issue at a time.
4. Active relevant PR before new work.
5. Define executable Acceptance Criteria before implementation.
6. RED → first concrete failure → smallest in-scope correction.
7. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
8. Close Issue only after accepted evidence exists.
9. Reconcile MASTER on `main` after merge.
10. Evaluate Milestone Acceptance before selecting another Issue.
11. Frozen accepted milestone becomes a preserved baseline slice; **FREEZE does not mean project development ends**.
12. After acceptance, return to Progression Review and select the next bounded milestone only when it has clear use/show/delivery value.
13. Do not manufacture work for activity. Existing asset reuse and small gap closure precede new implementation.

---

# 8. Frozen v1.0 Checkpoint

## Result
**UC-01 PASS / UC-02 PASS / UC-03 PASS / UC-04 PASS / UC-05 PASS / HUMAN REVIEW PASS / AWS-CLOUD DEFERRED.**

**ASGARD PROOF v1.0 CLOSED / FREEZE — HUMAN REVIEW PASSED.**

## Not Verified / Explicit Non-Claims
- production readiness;
- production SLA/SLO, stable latency/throughput/cost savings;
- legal GDPR/security compliance certification;
- production Kubernetes/HA/multi-region posture;
- accepted cloud-provider execution;
- full operational/admin dashboard product;
- unattended autonomous operations;
- production observability calibration beyond bounded proof conditions.

## Exact Next Action
**Preserve v1.0 as a frozen verified baseline. Do not reopen v1.0 scope. Continue only through the bounded post-v1.0 progression contract below.**

---

# 9. Post-v1.0 Progression Contract

## 9.1 Product Destination

> **A bounded, single-node Local AI Operations Tool that a technical operator can reproducibly deploy, use to submit and inspect asynchronous Local AI analysis jobs, recover supported failures, audit operator actions, and understand system health without requiring a cloud AI provider.**

### Intended user
- one technical operator or a small technical team using the same bounded environment;
- developer / backend engineer / AI engineer / internal operator;
- user understands service health, jobs, failures, retries, and logs at a technical level.

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

1. **Usability**
2. **Reproducibility**
3. **Reliability / Recovery**
4. **Observability / Auditability**
5. **Buyer-facing Demonstrability**
6. **Delivery Readiness**
7. **Maintainability / Security only when it blocks actual use or delivery**
8. **New Capability only when earlier axes cannot close the accepted gap**

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
- one active bounded implementation Issue per repository;
- active relevant PR before new work;
- milestone scope and executable acceptance fixed before implementation;
- accepted evidence records Changed / Executed / Verified / Not Verified / Known Limitations;
- agent self-report is never Final Acceptance;
- later milestones preserve accepted v1.0 behavior unless user approves product-direction change;
- technical HOLD / RED is correction state, not stop reason;
- no-op MASTER churn is prohibited.

## 9.4 Automatic Scope Guardrails

Do not automatically select:
- AWS Bedrock / OIDC / IAM;
- OpenAI / Gemini / other cloud-provider expansion;
- multi-provider routing as product goal;
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

## 9.5 Builder Stop / Disable Conditions

A frozen version, READY TO SHOW state, Human Review PASS, or accepted milestone **does not disable progression**.

Disable / queue only when:
- explicit user/product stop;
- repository archived or superseded;
- unsafe or material human product-direction decision is required before a bounded milestone can be selected;
- external WIP cap requires `QUEUED — WIP CAP` rotation;
- no useful bounded milestone remains and further work would be feature creep.

---

# 10. Post-v1.0 Milestone Map

Only the selected milestone becomes active work. Later milestones must be re-reviewed against actual `main` after every acceptance.

## M1 — Local Reproduction & First Job

### Accepted Scope
Clean supported Linux path with prerequisites/preflight, required services, Local Ollama/model, one deterministic persistent Job, Kafka → Bifrost → real Ollama result, final `SUCCEEDED`, operator-visible IDs/result, and bounded cleanup.

### Accepted Evidence
- Issue #25 CLOSED / COMPLETED;
- PR #30 SQUASH MERGED with expected-head guard;
- accepted head `0db87a1a1feb54bf677533d88516d72f3bda73ec`;
- merge main SHA `3e90bbd7eedca5f71c341ea91691b0cf2bc121ab`;
- primary CI `33399015985`: SUCCESS;
- M1 runner `33399015962`: SUCCESS;
- UC-02 `33399016060`: SUCCESS;
- UC-03 `33399016019`: SUCCESS;
- UC-04 `33399015968`: SUCCESS;
- artifact `9760584618`, digest `sha256:f8011b67f5c49a87ddef93356295d403d37d4dc731b82811bfe087c2399c361`;
- artifact: `status=PASS`, `provider=ollama`, `model=smollm:135m`, persistent IDs, `synthetic=true`, `cloudExecution=false`;
- CI/CD remained RED only on pre-existing Heimdall Checkstyle debt.

### Limitations
- accepted executable environment is GitHub-hosted Linux; macOS not independently executed;
- Windows scripts were not replaced;
- no latency/throughput/cost/SLA/SLO claim.

**Current: ACCEPTED / FROZEN — PASS**

---

## M2 — Operator Console: Read-only Job Lifecycle

### Accepted Scope
- authenticated recent Job list backed by persisted data;
- Job detail with persisted status, timestamps, attempt count, trace/result references;
- successful real Local Ollama result inspection;
- deterministic failed/error state inspection;
- bounded React operator surface;
- default surface strictly read-only.

### Actually Changed
- authenticated read-only recent-job paging endpoint ordered by persisted `createdAt DESC`;
- frontend boot shell upgraded into bounded read-only operator console;
- exact-head real-stack Playwright proof for one real `SUCCEEDED` Job and one deterministic `FAILED` Job;
- no cloud providers, RAG, generic admin tooling, or broad cleanup.

### Actually Executed / Verified
- Issue #31 CLOSED / COMPLETED;
- PR #32 SQUASH MERGED with expected-head guard;
- exact head `224e53814bc33e565189acd0b2c45866be32f2a0`;
- merge main SHA `07875ef2c9f6784d54c23c2bb19b326d2ff6ed86`;
- M2 run `33405406557`: SUCCESS;
- primary CI `33405406555`: SUCCESS;
- M1 `33405406603`: SUCCESS;
- UC-02 `33405406515`: SUCCESS;
- UC-03 `33405406542`: SUCCESS;
- UC-04 `33405406571`: SUCCESS;
- UC-05 `33405406432`: SUCCESS;
- artifact `9763096595`, digest `sha256:ff363841b4c4754870ab40a33f630284e39b3820123d503e847096ccc1e19b05`;
- browser proof records success visible, failure visible, mutation controls absent, `synthetic=true`;
- review threads none; submitted reviews none;
- supporting CI/CD RED remained known Heimdall build/Checkstyle debt while Bifrost/frontend/dependency security were GREEN.

### Limitations
- M2 does not independently prove browser recovery/redrive;
- M2 is not a generic/full admin dashboard;
- no production readiness, HA, SLA/SLO, stable performance, or cloud-execution claim;
- bounded proof uses synthetic credentials/inputs in CI.

**Current: ACCEPTED / FROZEN — PASS**

---

## M3 — Controlled Recovery Operator Workflow

### Accepted Scope
- select persisted `FAILED` Job from M2 surface;
- require explicit redrive reason and visible confirmation boundary;
- invoke only existing authorized redrive endpoint;
- show persisted status/attempt transition;
- show bounded per-job redrive audit history;
- make duplicate redrive visible as `SKIPPED` with attempt unchanged;
- preserve M2 default read-only behavior unless `VITE_ENABLE_RECOVERY=true`;
- reuse existing UC-04 recovery semantics rather than inventing new recovery machinery.

### Actually Changed
- bounded recovery panel gated by `VITE_ENABLE_RECOVERY=true`;
- mandatory operator reason + confirmation before mutation;
- existing `/api/v1/analysis/jobs/{jobId}/redrive` only;
- per-job audit visibility and duplicate `SKIPPED` visibility;
- exact-head real-stack Playwright M3 workflow;
- proof harness corrected to consume the initial seeded `analysis.request` before starting Bifrost, eliminating interference from the pre-redrive request;
- no AWS/Bedrock/OIDC/cloud, autonomous retry, generic admin mutations, or unrelated backend recovery semantics.

### Actually Executed / Verified
- Issue #33 — **CLOSED / COMPLETED**;
- Draft PR #34 — CLOSED / NOT MERGED only because connector Draft→Ready GraphQL transition failed on `Repository.fullDatabaseId`; implementation head preserved;
- replacement PR #35 — **SQUASH MERGED** with expected-head guard;
- accepted exact head `b4e79a00dc3677746a244a08c6fd36dfccba620c`;
- merge main SHA `c97dfa2d79f81b7b0172833769a71164934a103e`;
- M3 Recovery Console run `33422708481`: **SUCCESS**;
- primary CI `33422708448`: **SUCCESS**;
- M1 Local Proof `33422708431`: **SUCCESS**;
- M2 Operator Console `33422708497`: **SUCCESS**;
- UC-02 `33422708460`: **SUCCESS**;
- UC-03 `33422708512`: **SUCCESS**;
- UC-04 `33422708432`: **SUCCESS**;
- artifact `9769683333`, digest `sha256:2c1bdfe47287dc3e88061259ee2d93f9b8025310721e3a2b66b7ae3fd05d6d78`;
- persisted final Job evidence: `SUCCEEDED`, `attemptCount=1`;
- SUCCESS audit records `previousStatus=FAILED`, `previousAttemptCount=0`, operator reason, outcome `SUCCESS`;
- duplicate audit records `previousStatus=SUCCEEDED`, `previousAttemptCount=1`, outcome `SKIPPED`, and attempt remains unchanged;
- browser evidence records `status=PASS`, `initialStatus=FAILED`, `initialAttempt=0`, `recoveredStatus=SUCCEEDED`, `recoveredAttempt=1`, `successAuditVisible=true`, `duplicateOutcomeVisible=SKIPPED`, `duplicateAttemptUnchanged=true`, `synthetic=true`, `cloudExecution=false`;
- M3 job steps all GREEN: deterministic FAILED seed, browser proof, persisted API capture, synthetic-safe verification, artifact upload;
- review threads none; submitted reviews none;
- Dependency Security Check GREEN;
- supporting CI/CD remained RED only at known pre-existing Heimdall broad Checkstyle/build boundary; frontend and Bifrost jobs were GREEN.

### Limitations / Non-claims
- recovery UI is bounded, not a generic admin platform;
- no autonomous/background retry policy is proven;
- no production readiness, SLA/SLO, stable performance, HA/Kubernetes, cloud-provider execution, enterprise identity, or legal compliance claim;
- M3 harness ordering proves the bounded scenario, not all possible queue/restart race behavior.

### Milestone Acceptance
A technical operator can start from a persisted deterministic `FAILED` Job, explicitly confirm and explain a redrive, recover through the existing authorized path and real Local Ollama to `SUCCEEDED`, inspect the SUCCESS audit, and observe a duplicate redrive as `SKIPPED` without attempt inflation. Exact-head regressions remained GREEN. **M3 PASS / ACCEPTED / FROZEN.**

**Current: ACCEPTED / FROZEN — PASS**

---

## M4 — Runtime Resilience: Bounded Bifrost Restart Around Persisted Job

### Accepted Scope
One bounded single-node failure mode: **Bifrost process interruption/restart while a target Analysis Job is already persisted and actively processing**.

### Actually Changed
- one dedicated exact-head M4 workflow only;
- real persisted target Job + Kafka + Bifrost + real Local Ollama;
- first Bifrost started without the development reloader so the workflow controlled the actual server PID;
- workflow waits for real target processing, SIGKILLs the first Bifrost process, verifies the process/health endpoint are down, restarts Bifrost with the same consumer group, and waits for final persisted success;
- synthetic-safe artifact captures pre-interruption Job, process lifecycle, replay observation, final Job/result, and explicit limitations;
- no product runtime retry subsystem, AWS/Bedrock/OIDC/cloud, Kafka-outage, HA, Kubernetes, multi-node, or broad cleanup.

### Actually Executed / Verified
- Issue #36 — **CLOSED / COMPLETED**;
- Draft PR #37 — CLOSED / NOT MERGED only after repeated Draft→Ready connector GraphQL failure; exact implementation head preserved;
- replacement PR #38 — **SQUASH MERGED** with expected-head guard;
- accepted exact head `e46f11cc9cccd7763cc8d6e7b3dbcd8907af934b`;
- merge main SHA `d853f8b5fe248ee2e0fd0032f6e0ffccadc5f578`;
- M4 Bifrost Restart Proof run `33444318573`: **SUCCESS**;
- primary CI run `33444318725`: **SUCCESS**;
- artifact `9777540907`, digest `sha256:d1a078d52d9fb70a3c9931f6e5065e2fd4220f863fffbf5acc1e1ba07d020ea4`;
- pre-interruption persisted Job: `RUNNING`, `attemptCount=0`, `resultRef=null`;
- first process observed processing target Job, killed with `SIGKILL`, and confirmed down before restart;
- second Bifrost process restarted with `bifrost-consumer-group` and replayed the target request;
- final persisted Job: `SUCCEEDED`, `attemptCount=0`, `resultRef=1`;
- evidence records `firstProcessObserved=true`, `firstProcessKilledBeforeSuccessLog=true`, `firstProcessConfirmedDown=true`, `replayedAfterRestart=true`, `finalPersistedResultVisible=true`, `synthetic=true`, `cloudExecution=false`;
- Bifrost build/test GREEN and Dependency Security Check GREEN on the exact head;
- broad CI/CD remained RED at `Build & Test Heimdall → Build with Gradle`, classified as pre-existing R-002 debt because the PR changed only the M4 workflow and the accepted contract does not require this broad debt gate to be GREEN.

### Limitations / Non-claims
- one bounded single-node SIGKILL/restart scenario only;
- no Kafka outage, multi-node failover, HA/autoscaling/Kubernetes, recovery-time guarantee, SLA/SLO, autonomous recovery, or cloud-provider execution claim;
- replay proof validates the accepted scenario and does not establish all crash windows or distributed delivery semantics.

### Milestone Acceptance
A persisted target Job observed `RUNNING` during real Bifrost processing was not silently lost when that actual Bifrost server process was SIGKILLed. Restarting Bifrost in the same bounded single-node environment and consumer group replayed the request and produced one visible persisted final result with `SUCCEEDED / resultRef=1`. Exact-head primary CI, Bifrost regression, and dependency security gates were GREEN; the broad Heimdall RED remained demonstrably pre-existing debt. **M4 PASS / ACCEPTED / FROZEN.**

**Current: ACCEPTED / FROZEN — PASS**

---

## M5 — Single-node Delivery Handoff

### Accepted Scope
- one technical-operator handoff for the accepted single-node Linux Local-first path;
- prerequisites and configuration ownership aligned to executable dependencies;
- reuse of `scripts/local-proof.sh` rather than a second deployment path;
- retained-session metadata and explicit cleanup commands for `ASGARD_PROOF_KEEP=1`;
- bounded reference to accepted M4 restart semantics without falsely claiming an independent local replay proof;
- explicit `Backup/restore: NOT VERIFIED` boundary;
- exact-head handoff contract validation plus real Local-first proof execution.

### Actually Changed
- added `docs/SINGLE_NODE_HANDOFF.md`;
- added `.github/workflows/v11-m5-handoff.yml`;
- aligned `scripts/local-proof.sh` Python preflight to Python 3.9+;
- added `retained-session.env` metadata for retained proof cleanup;
- documented proof-owned process/container/Compose cleanup;
- preserved AWS/cloud, HA/Kubernetes, enterprise identity, SLA/SLO, production-readiness and legal-certification non-claims.

### Actually Executed / Verified
- Issue #39 — **CLOSED / COMPLETED**;
- PR #40 — **SQUASH MERGED** with expected-head guard;
- accepted exact head `b13438d91ca13ac9a889bad4f31a2b33550533e9`;
- merge main SHA `3f6eb40793991adba82c7d5b60920a5f60c80a04`;
- M5 Delivery Handoff run `33652535194`: **SUCCESS**;
- primary CI `33652535236`: **SUCCESS**;
- M1 Local Proof `33652535181`: **SUCCESS**;
- P1-B1 Real Local AI Golden Path `33652535237`: **SUCCESS**;
- artifact `9855507091`, digest `sha256:f26aa953bcb5a855bc4f628ec1edd56f7e61a750a432ed0d2e4d12a7fbc09683`;
- Bifrost build/test and Dependency Security Check GREEN on exact head;
- three earlier Codex review threads were corrected on the same PR and resolved as outdated;
- broad CI/CD remained RED first at `Build & Test Heimdall → Build with Gradle`, consistent with pre-existing R-002 debt rather than the bounded M5 diff.

### Limitations / Non-claims
- backup/restore is explicitly NOT VERIFIED by M5;
- the handoff is bounded to the supported Linux Local-first proof path, not a production deployment guide;
- M4 restart semantics remain the executable restart/replay acceptance reference; M5 does not independently broaden that claim;
- no HA/Kubernetes/multi-node, production support, SLA/SLO, autonomous operations, cloud execution, enterprise identity, or legal compliance claim.

### Milestone Acceptance
A technical operator now has one repository-owned handoff for the accepted single-node Linux Local-first path, with executable prerequisites, configuration ownership, real Local-first proof command, retained-session cleanup metadata, troubleshooting boundaries and explicit non-claims. Exact-head M5, primary CI, M1 and real Local AI regression gates were GREEN, with security/Bifrost gates GREEN and broad Heimdall RED retained as pre-existing debt. **M5 PASS / ACCEPTED / FROZEN.**

**Current: ACCEPTED / FROZEN — PASS**

---

## M6 — Persisted-state Backup/Restore Proof

### Selected Scope
- one bounded single-node PostgreSQL backup/restore path for Asgard-owned persisted Job/result/audit state;
- create accepted persisted state using the existing Local-first path;
- take an explicit database backup using current repository infrastructure;
- restore into a clean proof-owned database/volume boundary;
- verify the target Job/result/audit records are queryable after restore;
- document operator commands and failure limitations;
- no claim of continuous backup, PITR, disaster recovery, HA, RPO/RTO, encrypted off-site storage, or production retention policy.

### Executable Acceptance
1. Exact-head proof creates one identifiable persisted Asgard Job/result state using the accepted Local-first path.
2. A concrete PostgreSQL backup artifact is produced by an operator-executable command.
3. The original proof database/volume is not reused as evidence for restore success; restore occurs into a clean proof-owned persistence boundary.
4. Restored state contains the expected target Job identity, terminal status/result reference, and bounded related audit/result data that was present before backup.
5. Evidence records backup command/path, restore command/path, before/after identifiers, and synthetic-safe limitations.
6. Relevant primary regression/security gates remain independently GREEN; pre-existing broad Heimdall debt is not silently called GREEN.
7. No HA/DR/RPO/RTO/cloud-storage/production-retention claim is introduced.

### Stop Condition
Stop after one reproducible single-node persisted-state backup/restore case is independently executed and verified. Do not expand into continuous backup infrastructure, cloud object storage, cross-region DR, Kubernetes volume recovery, or production policy.

**Current: SELECTED — ISSUE NOT YET OPEN**

---

# 11. Current Post-v1.0 Progression Checkpoint

## Decision
- v1.0 remains **PASS / FREEZE / HUMAN REVIEW PASSED**;
- M1 is **PASS / ACCEPTED / FROZEN**;
- M2 is **PASS / ACCEPTED / FROZEN**;
- M3 is **PASS / ACCEPTED / FROZEN**;
- M4 is **PASS / ACCEPTED / FROZEN**;
- M5 is **PASS / ACCEPTED / FROZEN**;
- M5 accepted exact head `b13438d91ca13ac9a889bad4f31a2b33550533e9`, merged via PR #40 at `3f6eb40793991adba82c7d5b60920a5f60c80a04`;
- Issue #39 CLOSED / COMPLETED;
- Progression Review selected exactly one next milestone: **M6 — Persisted-state Backup/Restore Proof**.

## Changed by M5
- added one bounded technical-operator delivery handoff;
- aligned Python support boundary to actual Bifrost dependency requirements;
- added retained-session metadata and executable cleanup ownership;
- added exact-head contract validation and re-executed the accepted real Local-first proof;
- no cloud execution, HA/multi-node, generic admin platform, or production-readiness feature expansion.

## Actually Executed / Verified for M5
- M5 Delivery Handoff run `33652535194`: SUCCESS;
- primary CI `33652535236`: SUCCESS;
- M1 Local Proof `33652535181`: SUCCESS;
- P1-B1 Real Local AI Golden Path `33652535237`: SUCCESS;
- artifact `9855507091`, digest `sha256:f26aa953bcb5a855bc4f628ec1edd56f7e61a750a432ed0d2e4d12a7fbc09683`;
- Bifrost build/test and Dependency Security Check GREEN;
- broad CI/CD first failure remained `Build & Test Heimdall → Build with Gradle`, consistent with accepted R-002 pre-existing debt;
- three stale Codex review threads were corrected and resolved before merge.

## Not Verified / Known Limitations
- backup/restore remains unverified until M6 executes it;
- no continuous backup, PITR, DR, HA, RPO/RTO, cloud-storage durability, production retention, or production operations readiness claim;
- full admin-platform behavior remains outside scope;
- v1.0/M1–M5 accepted evidence and non-claims remain frozen.

## M6 Milestone Gate
M6 has concrete delivery/reliability value because M5 now provides a truthful single-node handoff but explicitly leaves persisted-state backup/restore unverified. A single proof-owned PostgreSQL backup/restore case is executable, bounded to one Issue/PR, and does not require a product-direction decision or cloud/HA expansion.

## Exact Next Action
**Open exactly one M6 Issue for a bounded persisted-state backup/restore proof. Reuse the accepted Local-first stack and current PostgreSQL infrastructure, create one identifiable persisted Job/result state, back it up, restore into a clean proof-owned persistence boundary, and verify the restored records. Keep DR/HA/RPO/RTO/cloud storage and production retention explicitly out of scope.**