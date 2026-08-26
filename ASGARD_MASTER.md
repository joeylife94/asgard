# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0 Proof. Current repository / Issue / PR / executable evidence overrides README claims, historical roadmap text, old portfolio positioning, and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket / Freelance Proof
- **Target Level**: READY TO SHOW bounded software Proof
- **Product Direction**: **Local-first AI Operations Platform**
- **Current Phase**: Phase 1 — UC-03 Local-first Policy
- **Current Batch**: P1-B2R — UC-03 Local-first Policy verification
- **Current Status**: **UC-01 PASS / UC-02 PASS / UC-03 IN PROGRESS / UC-04 PENDING / UC-05 PENDING**
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Active Issue**: #17 — `P1-B2R: prove UC-03 Local-first Policy boundary`
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
- feedback system expansion
- quality scoring expansion
- A/B testing expansion
- smart caching expansion
- advanced React admin dashboard
- HP AI Server reference deployment
- Kubernetes production / HA / autoscaling / multi-region
- Keycloak / Vault / enterprise secret-manager work
- full RBAC / multi-tenancy
- production SLA/SLO
- legal GDPR certification or security certification

Historical code may still contain Bedrock/cloud lanes. **Existence does not make them current v1.0 requirements.** Do not delete or modernize them unless a bounded accepted Proof gap requires it.

---

# 3. Required Use Cases

| UC | Goal | PASS criterion | Current |
|---|---|---|---|
| UC-01 Startup | executable core stack | clone/configure → required core services healthy | **PASS** |
| UC-02 Local AI Analysis | real asynchronous AI job | Job → Kafka → real Ollama → result → persistence → `SUCCEEDED` | **PASS** |
| UC-03 Local-first Policy | no implicit external dependency | default/sensitive/cloud-disabled path remains local; no AWS requirement | **IN PROGRESS — Issue #17** |
| UC-04 Recovery | controlled failure recovery | FAILED / DLQ → Redrive → Audit → Retry → `SUCCEEDED` | **PENDING** |
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

## Historical UC-03 AWS Experiment — DEFERRED, NOT ACCEPTED AS v1.0 REQUIREMENT
- Issue #15: CLOSED / NOT PLANNED on 2026-08-26.
- PR #16: CLOSED / NOT MERGED.
- Historical run evidence proved:
  - HIGH/MEDIUM sensitive input → LOCAL decision
  - real Ollama LOCAL execution
  - legacy LOW input → CLOUD decision in `PrivacyRouter`
  - GitHub OIDC claim issuance diagnostics
- **NOT VERIFIED**:
  - AWS `AssumeRoleWithWebIdentity`
  - STS caller identity
  - real Bedrock invocation/result
- These unverified AWS items are no longer closure debt. They remain historical non-claims.

---

# 5. UC-03 — Local-first Policy Boundary

## Active Work Item
- **Issue #17** — `P1-B2R: prove UC-03 Local-first Policy boundary`
- No active PR is accepted until one is created from Issue #17 after current-state inspection.
- Historical PR #16 is not reusable as the acceptance surface.

## Current Intended Contract

```text
Default request        → LOCAL
Sensitive request      → LOCAL
Cloud requested but disabled → LOCAL / fail closed
No implicit external egress requirement
```

Current newer `PolicyRouter` already defaults `ENABLE_CLOUD_LANE=false` and keeps cloud-requested work on-device when cloud is disabled. This code existence alone is **NOT** PASS; current bounded executable evidence is still required.

## Acceptance Criteria
- [ ] default request resolves to the local/on-device lane under default configuration.
- [ ] sensitive request remains local.
- [ ] explicit cloud hint with cloud lane disabled does not invoke an external provider and resolves local/fail-closed according to current product contract.
- [ ] real local provider execution uses Ollama, not mock/fallback-only output.
- [ ] exact route/provider/result evidence is captured in a PR-visible run.
- [ ] exact-head relevant CI/proof is GREEN.
- [ ] no AWS credential, Bedrock, replacement cloud-provider, RAG expansion, UI expansion, or unrelated refactor is introduced.

## Smallest Useful Deliverable
One Issue #17-linked branch and one PR containing only the bounded executable proof harness or smallest correction required by executed evidence. Prefer reuse of existing `PolicyRouter`, current provider abstraction, and the already-proven Ollama path.

---

# 6. UC-04 — Recovery

Existing code already contains failed-job listing, controlled redrive, per-user redrive rate limiting, redrive audit records, actor/source/trace/reason capture, retry preparation, Kafka re-publication, and `ai_job_redriven_total` metric hooks.

This is **NOT VERIFIED as a complete v1.0 Golden Path yet**.

## Acceptance Criteria
- [ ] create or induce one deterministic failed job through a bounded supported path.
- [ ] failure state is persisted and attributable.
- [ ] redrive is authorized through the existing endpoint/path.
- [ ] redrive audit records operator/outcome and relevant trace/reason evidence.
- [ ] retry republishes work and reaches a final accepted state, preferably `SUCCEEDED`.
- [ ] duplicate or unsafe redrive behavior is not hidden.

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
| R-008 | duplicate routing generations (`PrivacyRouter` vs newer `PolicyRouter`) | prove current intended local-first path; refactor only if necessary for acceptance |
| R-009 | agent self-report | never PASS without executed evidence |

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
**SCOPE RESET ACCEPTED — UC-01 PASS / UC-02 PASS / AWS/CLOUD DEFERRED / ISSUE #17 ACTIVE FOR UC-03 LOCAL-FIRST PROOF.**

## Changed
- product direction narrowed from hybrid local+cloud to **Local-first AI Operations Platform**.
- AWS Bedrock / AWS OIDC removed from v1.0 required Proof boundary.
- historical Issue #15 closed `not_planned` and PR #16 closed without merge.
- Issue #17 created as the sole active UC-03 work item.
- Recovery and Observability retained because they strengthen the actual event-driven operations Proof.
- broad roadmap features and cloud/provider expansion explicitly removed from current execution authority.

## Executed / Verified
- UC-01 startup/health remains accepted from prior merged evidence.
- UC-02 real Local AI asynchronous Job lifecycle remains accepted from prior merged evidence.
- existing recovery and observability code/assets were inspected as candidate reusable assets, but complete UC-04/05 Golden Paths are still NOT VERIFIED.

## Not Verified
- Issue #17 UC-03 current local-first policy executable proof.
- UC-04 complete failure → redrive → audit → retry → accepted final state.
- UC-05 live Prometheus/Grafana buyer-facing evidence.
- final README/Proof package truthfulness reconciliation.

## Exact Next Action
**Process Issue #17 only. Create/use one linked branch and one PR. Prove default/sensitive/cloud-disabled behavior through the current `PolicyRouter` and real Ollama path with no external cloud dependency. Merge only after exact-head evidence is GREEN, close Issue #17 after acceptance, reconcile this Master, then evaluate whether UC-04 is the next smallest remaining Proof gap.**
