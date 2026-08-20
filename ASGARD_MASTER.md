# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0. Executed evidence overrides README claims and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 1 — Golden Path
- **Current Batch**: P1-B2 — UC-03 Hybrid Routing
- **Batch Result**: **HOLD / BLOCKED — CLOUD prerequisite**
- **Status**: UC-01 PASS / UC-02 PASS / UC-03 LOCAL VERIFIED, CLOUD BLOCKED
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Active Issue**: #15 — OPEN
- **Active PR**: #16 — DRAFT / HOLD
- **P1-B2 Branch**: `agent/p1-b2-hybrid-routing-proof`
- **P1-B2 PR Exact Head**: `8324ae36051c4fedf4937539a3f231bb823c01ff`
- **P1-B2 Proof Run**: `32326966643` — FAILURE at CLOUD prerequisite only
- **P1-B2 Evidence Artifact**: `9391752221`
- **P1-B2 Evidence Digest**: `sha256:ca441898c13407a268fa3891ca9faa53f8b4677971e7c961f7bff4d5437ddc73`
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

| UC | Goal | PASS criterion | Current |
|---|---|---|---|
| UC-01 Startup | third-party executable startup | clone/configure → core services healthy | **PASS** |
| UC-02 Analysis | real AI analysis | Job → Kafka → real AI → result → SUCCEEDED | **PASS — Issue #13 / PR #14** |
| UC-03 Routing | hybrid route | sensitive→LOCAL / general→CLOUD with real providers | **HOLD — LOCAL VERIFIED / CLOUD credential prerequisite** |
| UC-04 Recovery | failure recovery | FAILED → DLQ → Redrive → Audit → SUCCEEDED | PENDING |
| UC-05 Observability | operating visibility | jobs/latency/routes/DLQ/redrive/health | PENDING |

---

# 4. Phase 0 — PASS

## P0-B1 — PASS
- PR #4 merged at `fa3f129783387fbeafae537e8a22b4629faf6d42`.
- primary Heimdall + Bifrost unit job GREEN.
- secondary Bifrost install/lint/pytest/coverage GREEN.
- dependency security GREEN.
- Java 21 CI aligned.
- Heimdall Checkstyle debt classified pre-existing: **41 files / 109 warnings / 2 info**.

## P0-B2 — PASS
- Issue #6 CLOSED.
- PR #7 merged at `b3d7c4bcf20d5376c6fa9d24ba25028f841a2067`.
- minimal four-file frontend boot tree restored.
- exact-head production frontend build GREEN.

## P0-B3 — PASS
- Issue #8 CLOSED.
- PR #9 proof harness merged at `0f12fcfe7b7b9b4944f7d4d6974de456c8695114`.
- PR #10 merged at `74da74c71625b9bca111b2e1c1bbbb933c82077a`.
- frontend dev-server root reachability GREEN.
- root `build-all.ps1 -SkipTests` frontend path GREEN.

## P0-B4 — PASS
- Issue #11 CLOSED / COMPLETED.
- PR #12 merged at `8f79c1aaf7a145abb4721c5f7799059b8c4195aa`.
- primary CI run `32320165761`: SUCCESS.
- full-core startup/health GREEN: PostgreSQL / Kafka / Redis / Elasticsearch / Prometheus / Grafana `3001` / Heimdall / Bifrost / Frontend.
- secondary RED remained only at pre-existing Heimdall `checkstyleMain` debt.

**Phase 0 closure: PASS.** Remaining v1.0 gaps are product-flow proofs, not baseline-startup uncertainty.

---

# 5. Phase 1 — P1-B1 UC-02 Real Local AI Golden Path — PASS

## Work Item / Executed Evidence
- Issue #13: CLOSED / COMPLETED.
- PR #14: MERGED.
- exact head: `eb307ba581609790245f8e6d8fa9a53ce7b12e52`.
- merge SHA: `ee24e6990d19c0be618baf1698bff275a8b27134`.
- exact-head proof run `32323663891`: SUCCESS.
- exact-head primary CI `32323664031`: SUCCESS.
- secondary CI/CD `32323663888`: RED only at pre-existing Heimdall Checkstyle; Bifrost/security GREEN.

## Proven Flow

```text
Deterministic ERROR log
→ Heimdall authenticated ingestion
→ real Analysis Job
→ Kafka analysis.request
→ Bifrost consumer / HeimdallIntegrationService
→ real Ollama smollm:135m inference
→ Kafka analysis.result
→ Heimdall AnalysisResult persistence
→ final Job SUCCEEDED
```

## Key Evidence
- intended manual Job `4aa60d74-cf9f-41aa-b6a6-eb04a4681247` → `SUCCEEDED`.
- `logId=1`, persisted `analysisId=2`, model `smollm:135m`.
- exact-head Kafka result: `model_used=smollm:135m`, `latency_ms=121045`.
- fallback disabled; persisted result assertion rejects model `fallback`.
- artifact `9390712782`, digest `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da`.
- prior equivalent proof `32323281881` also GREEN.

## Residual Observation
Log ingestion automatically creates another analysis request beside the explicit proof Job. This did not invalidate UC-02. HOLD unless a future acceptance gap makes it a blocker.

---

# 6. Phase 1 — P1-B2 UC-03 Hybrid Routing — HOLD / BLOCKED

## Closure Evaluation
Closure evaluation after UC-02 found real v1.0 work remaining: Hybrid Routing, Recovery, Observability and final proof packaging are still Core/PENDING. The project is **not** at Human Review / FREEZE.

## Work Item
- **Issue #15**: OPEN — `P1-B2: prove UC-03 Hybrid Routing with real LOCAL and CLOUD execution`.
- **PR #16**: DRAFT / HOLD.
- **Branch**: `agent/p1-b2-hybrid-routing-proof`.
- **Exact Head**: `8324ae36051c4fedf4937539a3f231bb823c01ff`.
- **Exact-head P1-B2 run**: `32326966643` — FAILURE at `Verify real CLOUD prerequisite`.
- **Evidence artifact**: `9391752221`, digest `sha256:ca441898c13407a268fa3891ca9faa53f8b4677971e7c961f7bff4d5437ddc73`.

## Frozen Routing Contract
The current product-facing automatic privacy route is the existing Bifrost `/analyze` path using `PrivacyRouter`:

```text
HIGH / MEDIUM sensitivity → local → real Ollama
LOW sensitivity           → cloud → real AWS Bedrock
```

Do not redesign routing policy in this batch.

## Deterministic Inputs
- LOCAL/sensitive: `ERROR login failed user email alice@example.com password=SuperSecret123 request=p1-b2-sensitive`.
- CLOUD/general: `INFO scheduler completed nightly batch successfully duration_ms=18 job=p1-b2-general`.

## Executed Evidence — exact head `8324ae3...`
- Bifrost + boto3 install: GREEN.
- real Ollama container + `smollm:135m` pull: GREEN.
- deterministic privacy-route assertions: GREEN.
- Bifrost API startup: GREEN.
- sensitive route decision: `track=local`, `sensitivity=high`; email and password patterns detected.
- general route decision: `track=cloud`, `sensitivity=low`; no sensitive pattern detected.
- real LOCAL `/analyze`: GREEN.
- LOCAL persisted response: `id=1`, `model=smollm:135m`, `cached=false`, non-empty real model output.
- LOCAL proof duration observed ~122 s on hosted CPU. **Do not publish as a stable performance claim.**
- CLOUD prerequisite step: **RED**.
- CLOUD Bedrock invocation step: SKIPPED because prerequisite failed.

## Concrete Blocker
Artifact `p1-b2-cloud-prerequisite.txt` records:

```text
UC-03 CLOUD BLOCKED: GitHub Actions AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY secrets are not available to this PR run.
Required prerequisite: repository Actions credentials with bedrock:InvokeModel permission for the configured model/region.
```

This is an external credential/capability prerequisite, not a code failure. Mocks or fabricated credentials are prohibited.

## Acceptance Criteria
- [x] sensitive input classified HIGH/MEDIUM and routed `local`.
- [x] real local Ollama provider executes; fallback/mock is not PASS.
- [x] general input classified LOW and routed `cloud`.
- [ ] real existing Bedrock provider executes with actually available credentials/capability.
- [x] route decision and local provider/model evidence captured.
- [ ] cloud provider/model result evidence captured.
- [x] exact-head PR-visible verification executed and evidence preserved.
- [x] bounded diff only; no UC-04/05, UI, README, HP AI Server, duplicate-job or broad Checkstyle work.

## HOLD Rule
P1-B2 remains enabled and on HOLD/BLOCKED. Do not close Issue #15 or merge PR #16 as UC-03 PASS until real Bedrock execution is evidenced. Do not start UC-04/05 while this active acceptance gap remains.

---

# 7. Evidence Registry

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
| E-018 | Real Local AI E2E | VERIFIED GREEN / MERGED | Issue #13 / PR #14 |
| E-040 | Real local model identity | VERIFIED | `smollm:135m`; fallback disabled |
| E-041 | UC-02 Kafka handoff + latency | VERIFIED | intended Job request/result |
| E-042 | UC-02 persistence + final state | VERIFIED | Job SUCCEEDED |
| E-019 | Local vs Cloud Routing | **PARTIAL VERIFIED / CLOUD BLOCKED** | Issue #15 / PR #16 / run `32326966643` |
| E-043 | UC-03 LOCAL privacy route + real provider | **VERIFIED GREEN** | high→local / `smollm:135m` / artifact `9391752221` |
| E-044 | UC-03 CLOUD real provider execution | **BLOCKED** | Actions AWS credentials absent in PR run |
| E-020 | DLQ → Redrive → Success | PENDING | UC-04 |
| E-021 | Grafana live metrics | PENDING | UC-05 |
| E-022 | Final Demo | PENDING | final proof packaging |
| E-023 | HP AI Server reference run | PENDING | reference deployment |

---

# 8. Known Risks / Holds

| ID | Risk | Handling |
|---|---|---|
| R-001 | duplicate `idx_severity` schema index name | HOLD; repeatedly non-fatal |
| R-002 | broad Heimdall Checkstyle debt | VERIFIED PRE-EXISTING; no mass-fix |
| R-003 | anonymous gRPC reader inappropriate for future real gRPC endpoint | replace only when actual endpoint exists |
| R-004 | startup banner is not health evidence | endpoint/readiness evidence only |
| R-005 | root `start-all.ps1` Bifrost launch differs from proven CI invocation | evaluate only if future gap needs it |
| R-006 | README overclaim / Grafana port drift | proof-hardening later |
| R-007 | fallback-only AI risk | CLOSED for UC-02; forbidden as UC-03 PASS evidence |
| R-008 | hosted CPU inference latency varies materially | no stable performance claims |
| R-009 | ingestion auto-analysis creates extra job | HOLD |
| R-010 | agent self-report | never PASS without executed evidence |
| R-011 | AWS/Bedrock credentials unavailable to PR Actions | ACTIVE BLOCKER; require safe Actions credentials with `bedrock:InvokeModel`; do not mock |

---

# 9. Work Item / PR Lifecycle

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

# 10. Current Checkpoint

## Result
**PHASE 0 PASS / UC-01 PASS / UC-02 PASS / UC-03 HOLD — LOCAL VERIFIED, CLOUD BLOCKED.**

## What Changed
- re-read synchronized MASTER and current open work state.
- performed closure evaluation and confirmed real v1.0 work remains.
- created exactly one bounded Issue #15 before UC-03 implementation.
- created branch `agent/p1-b2-hybrid-routing-proof` from synchronized `main`.
- added one proof-only workflow and opened draft PR #16.
- aligned the Issue to the actual existing privacy-routing integration (`PrivacyRouter` + `/analyze`).
- updated PR #16 with executed evidence and the exact cloud prerequisite.

## What Was Executed
- exact-head run `32326966643` completed.
- routing assertions: sensitive high→local, general low→cloud — GREEN.
- real Ollama `smollm:135m` startup/pull — GREEN.
- real LOCAL `/analyze` — GREEN; persisted id `1`, real non-empty result, model `smollm:135m`.
- CLOUD prerequisite check — RED because AWS credential secrets are unavailable to the PR run.
- evidence artifact `9391752221` inspected directly.

## What Was Not Verified
- real Bedrock invocation/result.
- whether credentials exist in another environment but are withheld from pull-request Actions.
- Bedrock IAM/model entitlement once credentials are made available.
- UC-04 / UC-05 / final proof package / HP AI Server reference run.

## Remaining Risks
- UC-03 cannot PASS without a real cloud execution.
- no source-code correction is justified by the current failure; it is an external credential prerequisite.
- local hosted CPU duration is variable and must not become a published performance claim.
- pre-existing Checkstyle and duplicate-job holds remain out of scope.

## Exact Next Action
**Keep Issue #15 and PR #16 open. Provide GitHub Actions-accessible AWS credentials with `bedrock:InvokeModel` permission for an allowed Bedrock model/region, then re-run PR #16 exact-head workflow `P1-B2 Hybrid Routing Proof`. If the cloud step reaches Bedrock and fails, inspect only that first concrete Issue #15 failure (region/model/IAM/config). If real CLOUD returns successfully and review/security is clean, mark PR ready, merge with expected-head guard, close Issue #15 only after merge, reconcile this MASTER, then perform closure evaluation before any further Issue.**
