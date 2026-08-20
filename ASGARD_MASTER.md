# ASGARD MASTER

> **Authoritative v1.0 execution contract**
>
> Single source of truth for Asgard v1.0. Current repository/Issue/PR/executed evidence overrides stale checkpoint fields, README claims, and agent self-report.

## 0. Control

- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 1 — Golden Path
- **Current Batch**: P1-B2 — UC-03 Hybrid Routing
- **Batch Result**: **HOLD / BLOCKED — OIDC role prerequisite**
- **Status**: UC-01 PASS / UC-02 PASS / UC-03 LOCAL VERIFIED, CLOUD BLOCKED
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Active Issue**: #15 — OPEN
- **Active PR**: #16 — DRAFT / HOLD
- **P1-B2 Branch**: `agent/p1-b2-hybrid-routing-proof`
- **P1-B2 PR Exact Head**: `5dc069a1189b4d7cc27cf4a8c4802013e2c57d1b`
- **Primary CI**: `32370250115` — SUCCESS
- **P1-B2 Proof Run**: `32370250218` — FAILURE at OIDC role prerequisite
- **CI/CD Pipeline**: `32370250514` — FAILURE only at pre-existing Heimdall `checkstyleMain`; Bifrost/security GREEN
- **P1-B2 Evidence Artifact**: `9406886841`
- **P1-B2 Evidence Digest**: `sha256:60f8a6085372e3891be6481db894b4d3a8d0e85e903ac4758824be54f5366a69`
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
- Cloud AI Provider proof through the existing Bedrock path
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
| UC-03 Routing | hybrid route | sensitive→LOCAL / general→CLOUD with real providers | **HOLD — LOCAL VERIFIED / CLOUD OIDC role prerequisite** |
| UC-04 Recovery | failure recovery | FAILED → DLQ → Redrive → Audit → SUCCEEDED | PENDING |
| UC-05 Observability | operating visibility | jobs/latency/routes/DLQ/redrive/health | PENDING |

---

# 4. Completed Baseline / Golden Path Evidence

## Phase 0 — PASS
- P0-B1: PR #4 merged; primary Heimdall+Bifrost unit job GREEN; secondary Bifrost install/lint/pytest/coverage GREEN; dependency security GREEN.
- P0-B2: Issue #6 closed; PR #7 merged; minimal four-file frontend boot tree restored; frontend production build GREEN.
- P0-B3: Issue #8 closed; PR #9/#10 merged; frontend dev-server root and root `build-all.ps1 -SkipTests` frontend path GREEN.
- P0-B4: Issue #11 closed; PR #12 merged; full core startup/health GREEN for PostgreSQL, Kafka, Redis, Elasticsearch, Prometheus, Grafana `3001`, Heimdall, Bifrost, Frontend.
- Pre-existing Heimdall Checkstyle debt remains classified out of scope: **41 files / 109 warnings / 2 info**.

## P1-B1 — UC-02 Real Local AI Golden Path — PASS
- Issue #13 CLOSED / COMPLETED.
- PR #14 MERGED at `ee24e6990d19c0be618baf1698bff275a8b27134`.
- proof run `32323663891`: SUCCESS.
- primary CI `32323664031`: SUCCESS.
- deterministic log → Heimdall Job → Kafka request → Bifrost → real Ollama `smollm:135m` → Kafka result → persistence → Job `SUCCEEDED`.
- artifact `9390712782`, digest `sha256:66840ffe978f0a6d011b1440e7960962da530f352cc68da8e23744bf50d212da`.
- hosted CPU latency is variable; do not publish it as a stable performance claim.

---

# 5. P1-B2 — UC-03 Hybrid Routing — HOLD / BLOCKED

## Active Work Item
- **Issue #15**: OPEN — `P1-B2: prove UC-03 Hybrid Routing with real LOCAL and CLOUD execution`.
- **PR #16**: DRAFT / HOLD.
- **Current exact head**: `5dc069a1189b4d7cc27cf4a8c4802013e2c57d1b`.
- **Current proof run**: `32370250218` — FAILURE only because the OIDC role ARN resolved empty.
- **Primary CI**: `32370250115` — SUCCESS.
- **Secondary CI/CD**: `32370250514` — expected pre-existing Heimdall `checkstyleMain` failure; Bifrost and dependency-security jobs GREEN. No new UC-03 blocker.

## Frozen Routing Contract

```text
HIGH / MEDIUM sensitivity → local → real Ollama
LOW sensitivity           → cloud → real AWS Bedrock
```

Do not redesign routing policy in this batch.

## OIDC Cloud Execution Path
- GitHub environment: `asgard-proof`
- repository variable: `ASGARD_BEDROCK_ROLE_ARN`
- optional repository variable: `ASGARD_BEDROCK_REGION` (default `us-east-1`)
- optional repository variable: `ASGARD_BEDROCK_MODEL` (default current Bifrost Bedrock model)
- workflow permission: `id-token: write`
- auth action: `aws-actions/configure-aws-credentials@v6.2.3`
- AWS role trust must allow subject `repo:joeylife94/asgard:environment:asgard-proof`
- AWS role permissions must allow required Bedrock invocation, minimally `bedrock:InvokeModel` for the accepted model/resource boundary.

## Deterministic Inputs
- LOCAL/sensitive: `ERROR login failed user email alice@example.com password=SuperSecret123 request=p1-b2-sensitive`
- CLOUD/general: `INFO scheduler completed nightly batch successfully duration_ms=18 job=p1-b2-general`

## Executed Evidence — exact head `5dc069a...`
- Bifrost + boto3 install: GREEN.
- real Ollama container + `smollm:135m` pull: GREEN.
- privacy routing assertions: GREEN.
- sensitive decision: `track=local`, `sensitivity=high`.
- general decision: `track=cloud`, `sensitivity=low`.
- real LOCAL `/analyze`: GREEN with non-empty, non-fallback `smollm:135m` result.
- OIDC credential configuration: SKIPPED because `ASGARD_BEDROCK_ROLE_ARN` resolved empty.
- real STS `AssumeRoleWithWebIdentity`: NOT EXECUTED.
- real Bedrock invocation/result: NOT EXECUTED.
- evidence artifact `9406886841`, digest `sha256:60f8a6085372e3891be6481db894b4d3a8d0e85e903ac4758824be54f5366a69`.

## Acceptance Criteria
- [x] sensitive input classified HIGH/MEDIUM and routed `local`.
- [x] real local Ollama provider executes; mock/fallback-only output rejected.
- [x] general input classified LOW and routed `cloud`.
- [ ] GitHub OIDC successfully assumes the configured AWS role.
- [ ] real existing Bedrock provider executes.
- [x] local route/provider/model/result evidence captured.
- [ ] cloud caller/provider/model/result evidence captured.
- [x] exact-head PR-visible verification executed and evidence preserved.
- [x] bounded diff only; no UC-04/05, UI, README, HP AI Server, duplicate-job or broad Checkstyle work.

## Exact External Prerequisite
Configure repository variable:

`ASGARD_BEDROCK_ROLE_ARN`

with an IAM role whose trust permits:

`repo:joeylife94/asgard:environment:asgard-proof`

and whose permissions allow the required Bedrock call. **No static AWS access key/secret is required or requested.**

If the next execution reaches OIDC and fails at `AssumeRoleWithWebIdentity`, STS caller identity, Bedrock authorization, model entitlement, region, or model configuration, classify only that first concrete AWS prerequisite from executed evidence.

## HOLD Rule
P1-B2 remains **enabled + HOLD/BLOCKED**. Do not close Issue #15 or merge PR #16 as UC-03 PASS until real Bedrock execution is evidenced. Do not start UC-04/05 while this gap remains active.

---

# 6. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | GitHub-hosted baseline execution | VERIFIED | Phase 0 |
| E-004 | Heimdall Checkstyle debt | VERIFIED RED / PRE-EXISTING | 41 / 109 / 2 |
| E-005 | Frontend boot repair/build | VERIFIED / MERGED | PR #7 |
| E-024 | UC-01 full core-stack health | VERIFIED GREEN / MERGED | PR #12 |
| E-018 | Real Local AI E2E | VERIFIED GREEN / MERGED | Issue #13 / PR #14 |
| E-040 | Real local model identity | VERIFIED | `smollm:135m`; fallback disabled |
| E-042 | UC-02 persistence + final state | VERIFIED | Job SUCCEEDED |
| E-019 | Local vs Cloud Routing | **PARTIAL VERIFIED / CLOUD BLOCKED** | Issue #15 / PR #16 / run `32370250218` |
| E-043 | UC-03 LOCAL privacy route + real provider | **VERIFIED GREEN** | high→local / `smollm:135m` |
| E-044 | UC-03 CLOUD real provider execution | **BLOCKED** | OIDC role ARN variable empty; Bedrock not executed |
| E-045 | UC-03 OIDC workflow wiring | **VERIFIED STATIC + EXECUTED SKIP** | `asgard-proof`, `id-token: write`, configure-aws-credentials v6.2.3 |
| E-020 | DLQ → Redrive → Success | PENDING | UC-04 |
| E-021 | Grafana live metrics | PENDING | UC-05 |
| E-022 | Final Demo | PENDING | final proof packaging |
| E-023 | HP AI Server reference run | PENDING | reference deployment |

---

# 7. Known Risks / Holds

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
| R-011 | `ASGARD_BEDROCK_ROLE_ARN` absent/empty | ACTIVE BLOCKER; configure trusted GitHub OIDC role; do not mock |

---

# 8. Work Item / PR Lifecycle

1. MASTER first.
2. Current repository/Issue/PR state overrides stale checkpoint fields.
3. Active focused PR first.
4. One active implementation Issue by default.
5. Same-gap CI/review corrections remain in the same Issue/PR.
6. RED → first concrete failure → smallest in-scope fix.
7. Exact-head GREEN + bounded diff + clean review/security → merge with expected-head guard.
8. Issue closes only after acceptance + merge.
9. Reconcile MASTER on `main` before another Issue.
10. Human Review remains the final v1.0 gate.

---

# 9. Current Checkpoint

## Result
**PHASE 0 PASS / UC-01 PASS / UC-02 PASS / UC-03 HOLD — LOCAL VERIFIED, CLOUD OIDC ROLE BLOCKED.**

## What Changed
- re-fetched current Issue #15 / PR #16 / exact head and PR-visible workflows.
- reconciled stale MASTER state from static AWS key prerequisite to the current GitHub OIDC path.
- updated exact head, workflow run IDs, artifact, digest, and current external prerequisite.
- inspected secondary CI/CD failure and confirmed it remains only the known pre-existing Heimdall Checkstyle debt; Bifrost/security are GREEN.
- no product-code mutation performed.

## What Was Executed
- current exact-head primary CI `32370250115`: SUCCESS.
- current exact-head P1-B2 proof `32370250218`: executed; LOCAL and route assertions GREEN; OIDC role step skipped because `ASGARD_BEDROCK_ROLE_ARN` was empty; proof concluded FAILURE at cloud prerequisite.
- current exact-head CI/CD `32370250514`: Heimdall failed at `:heimdall:checkstyleMain` with 41 files / 109 warnings / 2 info; Bifrost and dependency-security jobs GREEN.

## What Was Not Verified
- successful GitHub OIDC `AssumeRoleWithWebIdentity`.
- STS caller identity.
- real Bedrock invocation/result.
- AWS trust policy, Bedrock permission, model entitlement, region/model validity after role ARN becomes available.
- UC-04 / UC-05 / final proof package / HP AI Server reference run.

## Remaining Risks
- UC-03 cannot PASS without real Bedrock execution.
- no product-code correction is justified by the current failure; the immediate blocker is external AWS/OIDC configuration.
- stable performance claims remain prohibited.
- pre-existing Checkstyle and duplicate-job holds remain out of scope.

## Exact Next Action
**Keep Issue #15 and draft PR #16 open. Configure repository variable `ASGARD_BEDROCK_ROLE_ARN` to a trusted IAM role for GitHub environment `asgard-proof`, with the required Bedrock invocation permission. Then re-run the current exact-head `P1-B2 Hybrid Routing Proof`. If OIDC/STS/Bedrock reaches a new concrete failure, fix or record only that first Issue #15-scoped prerequisite. If real CLOUD execution succeeds and review/security are clean, mark PR ready, merge with expected-head guard, close Issue #15 only after acceptance, reconcile this MASTER, then perform closure evaluation before UC-04.**