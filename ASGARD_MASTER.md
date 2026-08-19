# ASGARD MASTER

> **Authoritative execution contract**
> Asgard의 현재 상태, v1.0 종료선, Evidence, 다음 작업을 관리한다.
> README보다 본 문서의 상태 판정을 우선한다.

## 0. Control
- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B1 — Repository Preflight
- **Batch Result**: BLOCKED
- **Status**: IN PROGRESS
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Original code baseline before checkpoint work**: `bca6567919cbcac3f9039268c09526b25179f370`
- **Observed main before this checkpoint update**: `99fc68233f2ab2e48337c2ef036b7a62b33fa2db`
- **Updated**: 2026-08-19
- **Final Gate**: Human Review Required

---

# 1. Product Definition

**기업 로그/운영 데이터를 Local LLM 또는 Cloud LLM으로 선택적으로 분석하고, Kafka 기반 비동기 Job과 장애 복구·관측 기능을 제공하는 Hybrid AI Operations Platform.**

```text
Input → Heimdall → Analysis Job → Kafka → Bifrost
      → Routing ─┬→ Local AI
                 └→ Cloud AI
      → Result / DB → Dashboard / Operator

FAILED → DLQ → Redrive → Audit → Retry → SUCCEEDED
```

---

# 2. v1.0 Target State

> **실제 데이터를 넣어 실제 AI 분석을 수행하고, 장애를 재현·복구할 수 있으며, 제3자가 clone 후 실행·검증할 수 있는 Single-node Production-like Hybrid AI Ops Platform**

## Done Enough To Use
- 실제 Local AI 분석
- 선택적 Cloud AI 분석
- Kafka async Job
- Persistence / Idempotency
- DLQ / Redrive / Audit
- Auth / Rate Limit
- Minimal Dashboard
- Prometheus / Grafana
- 재현 가능한 실행

## Done Enough To Show
- Fresh clone PASS
- Real-model E2E PASS
- Failure → Recovery PASS
- CI green
- Runtime / Grafana screenshots
- README ↔ Evidence 일치
- 2~3분 Demo

## Explicit Non-Goals
- Multi-tenancy 완성
- HA / Multi-region
- Kubernetes production
- Autoscaling
- Full RBAC / Enterprise Secret Manager
- 실제 SLA/SLO 운영
- Security certification
- 법률적 GDPR 인증
- 대형 Admin UI
- 신규 AI 기능 대량 추가

---

# 3. Current State

| Area | Level | Judgment |
|---|---:|---|
| Architecture | 8/10 | Strong |
| Spring Backend | 8/10 | Core operator API surface exists; runtime proof pending |
| Kafka Control Plane | 8/10 | Strong; runtime proof pending |
| AI Routing | 6~7/10 | Runtime proof 필요 |
| DLQ / Redrive | 7~8/10 | API/audit surface verified statically; runtime demo pending |
| Docker Infra | 7/10 | Repro check 필요 |
| Observability | 6~7/10 | Startup Grafana URL corrected; live evidence 필요 |
| Frontend | 3/10 | **BROKEN STATICALLY**: tracked Vite entry/source tree absent |
| CI/CD | 5.5/10 | Java 21 정렬 완료; execution evidence pending |
| E2E Reproducibility | 5~6/10 | Real model run 필요 |
| Documentation Truth | 4.5/10 | Grafana README drift + frontend docs/source drift |
| Wishket Proof | 5~6/10 | NOT READY |

**Current Summary:** Backend/Kafka core depth와 operator API surface는 존재하지만 runtime Evidence가 없고, tracked Frontend는 기본 Vite build/startup contract를 충족하지 못한다.

> **Feature Development → Proof Hardening**

---

# 4. Frozen v1.0 Scope

## CORE — Must Pass
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

## SUPPORTING — Core에서 실제 사용 시 유지
- Circuit Breaker
- Smart Cache
- Quality Metrics
- Redis / Elasticsearch / Tracing

## EXPERIMENTAL — v1.0 Gate에 영향 없음
- Feedback
- A/B Testing
- Advanced Routing
- Additional Providers
- Interview-specific features

**Rule:** Experimental 개선은 Core PASS 이후에만 허용.

---

# 5. Required Use Cases

| UC | Goal | PASS 기준 |
|---|---|---|
| UC-01 Startup | 제3자 실행 | clone → config → core services healthy |
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 |

---

# 6. Phase 0 — Baseline Truth

## Acceptance Criteria
- [ ] Local working tree / local branch / local↔remote sync — **BLOCKED**
- [x] Remote HEAD / branch state
- [x] Secret-risk static check
- [x] Large-file static check
- [ ] Installed runtime prerequisites — **PARTIAL**: declarations known, installed versions unverified
- [ ] Clean build — **BROKEN STATICALLY at Frontend step; runtime confirmation pending**
- [ ] Heimdall tests — **BLOCKED**
- [ ] Bifrost tests — **BLOCKED**
- [ ] Frontend build — **BROKEN STATICALLY; runtime confirmation pending**
- [ ] Compose startup — **BLOCKED**
- [ ] Current E2E smoke — **BLOCKED**
- [ ] Local / Cloud AI runtime path — **BLOCKED**
- [x] CI static audit
- [x] README/config static audit
- [x] Unified test status truth static correction
- [x] Startup script Grafana host-port correction
- [x] Frontend tracked-tree audit
- [x] Unified build/startup frontend failure-boundary audit
- [x] Frontend repair-slice design — **DESIGN ONLY; no implementation in Phase 0**
- [x] Analysis / Job / Redrive operator API inventory — **STATIC CONTRACT ONLY**

**Gate 0:** 거짓말 없는 Baseline 확보.

---

# 7. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | Clean Build | **BROKEN STATICALLY** | default build reaches frontend Vite build; runtime confirmation pending |
| E-002 | Heimdall Tests | PENDING | runtime blocked |
| E-003 | Bifrost Tests | PENDING | runtime blocked |
| E-004 | Frontend Build | **BROKEN STATICALLY** | no tracked `index.html` / `src/`; runtime confirmation pending |
| E-005 | Real Local AI E2E | PENDING | runtime blocked |
| E-006 | Local vs Cloud Routing | PENDING | runtime blocked |
| E-007 | DLQ → Redrive → Success | PENDING | runtime blocked |
| E-008 | Grafana Metrics | PENDING | runtime blocked |
| E-009 | GitHub Actions Green | PENDING | no green run/status evidence |
| E-010 | Actual Benchmark | PENDING | published numbers unsupported until rerun |
| E-011 | Final Demo | PENDING | |
| E-012 | HP AI Server Run | PENDING | |
| E-013 | Remote branch state | VERIFIED | `main` inspected; branch unprotected, no required status checks |
| E-014 | Runtime declarations | VERIFIED | Java 21 toolchain, Gradle 8.5, Python >=3.8 |
| E-015 | Primary CI correction | VERIFIED STATICALLY | primary CI JDK 21; Bifrost dependency install fail-fast |
| E-016 | Frontend test contract | VERIFIED | build script exists; test script absent |
| E-017 | README claim risk | VERIFIED | build/coverage/production/GDPR claims lack current runtime evidence |
| E-018 | README ↔ Compose Grafana drift | VERIFIED | Compose `3001:3000`; README still exposes host 3000 in three places |
| E-019 | gRPC caveat | VERIFIED | starter exists; protobuf generation config commented out |
| E-020 | Secondary CI correction | VERIFIED STATICALLY | secondary CI Java setup uses JDK 21 |
| E-021 | Unified frontend test truth correction | VERIFIED STATICALLY | no false all-pass summary |
| E-022 | README Grafana exact-location audit | VERIFIED STATICALLY | three host-facing corrections required |
| E-023 | Startup Grafana correction | VERIFIED STATICALLY | startup script prints `localhost:3001` |
| E-024 | README infra port audit | VERIFIED STATICALLY | Grafana is the remaining infra port drift |
| E-025 | Current commit combined status lookup | VERIFIED | no statuses attached; absence of evidence, not green CI |
| E-026 | Fresh clone blocker reproduction | VERIFIED | execution environment cannot resolve `github.com` |
| E-027 | README mutation safety check | VERIFIED | connector only supports whole-file replacement |
| E-028 | Commit workflow-run lookup limitation | VERIFIED | available lookup cannot prove push-CI success |
| E-029 | Frontend tracked-tree contract | VERIFIED STATICALLY | only `README.md`, `package.json`, `vite.config.js`; no entry/source tree |
| E-030 | Unified build/startup frontend failure boundary | VERIFIED STATICALLY | default build reaches Vite build; startup checks package.json only |
| E-031 | Minimal frontend repair-slice design | VERIFIED STATICALLY | 4-file boot shell frozen; no implementation in Phase 0 |
| E-032 | Core operator API inventory | VERIFIED STATICALLY | Analysis request/result, Job read/failed list, Redrive, per-job/recent audit endpoints exist; runtime behavior pending |

---

# 8. Static Baseline Findings

1. Java 21 toolchain; Gradle wrapper 8.5; Python package `>=3.8`.
2. Primary and secondary CI Java setup aligned to JDK 21.
3. Bifrost dependency installation is fail-fast in primary CI.
4. Unified frontend test runner preserves `No tests` / `Skipped` truth.
5. `start-all.ps1` Grafana URL matches Compose: `http://localhost:3001`.
6. README infra ports match Compose except Grafana.
7. CI remains execution-unverified; missing statuses are not PASS evidence.
8. Frontend `package.json` has Vite build but no test script.
9. Frontend dependencies already include React/ReactDOM/Router/Axios/Chart.js/React Query.
10. `vite.config.js`: dev 3000, `/api` proxy → Heimdall 8000, build output `../static/react`.
11. Tracked frontend root has no `index.html`, `src/`, `public/`, or package lock.
12. Frontend README describes a larger tree and commands not backed by tracked source.
13. Default unified build enters frontend unless skipped.
14. Startup can announce completion without proving frontend health.
15. Heimdall exposes the Core operator API needed for a later minimal operator UI; no new backend endpoint is currently required merely to design Analyze / Jobs / Operations screens.

**Important:** static correction/design ≠ runtime/CI PASS.

---

# 9. Frontend Build / Startup Contract — BROKEN STATICALLY

- `package.json`: `dev = vite`, `build = vite build`
- `vite.config.js`: no custom Rollup input
- no tracked root `index.html`
- no tracked `src/`
- build script invokes frontend by default
- startup script checks only `package.json` before launching dev server
- README describes non-existent files and `npm test`, but no test script exists

**Classification:** Frontend and default unified clean-build contract are `BROKEN STATICALLY`; runtime command output still pending.

Implementation is not authorized while P0-B1 remains active.

---

# 10. Planned Core Repair Slice — FRONTEND BOOT SHELL

> **Status: DESIGN FROZEN, NOT ACTIVE, NOT IMPLEMENTED**

## Minimum File Set
- `bifrost/frontend/index.html`
- `bifrost/frontend/src/main.jsx`
- `bifrost/frontend/src/App.jsx`
- `bifrost/frontend/src/index.css`

## Rules
- React + ReactDOM only for first repair
- no new dependencies
- no fake metrics/jobs/provider state
- no API integration in this repair slice
- no dashboard/Redrive/auth expansion

## Runtime Acceptance
- [ ] `npm install`
- [ ] `npm run build` exit 0
- [ ] `npm run dev` root reachable
- [ ] default `build-all.ps1` passes Frontend step

**Closure:** static files alone do not promote Frontend to PASS; runtime evidence required.

---

# 11. Core Operator API Contract — STATIC INVENTORY

> **Purpose:** Phase 2 UI 설계를 위한 최소 backend contract를 고정한다. 구현/동작 PASS가 아니라 source-level inventory다.

## Analyze

### Request analysis
`POST /api/v1/logs/{logId}/analysis`

Optional inputs:
- Header: `Idempotency-Key`
- Body: `{ "idempotencyKey": string <= 200, "modelPolicy": object }`

Accepted response:
- `jobId`
- `status`
- `created`

### Latest analysis result
`GET /api/v1/logs/{logId}/analysis`

Response includes:
- `analysisId`, `logId`, `bifrostAnalysisId`
- `summary`, `rootCause`, `recommendation`
- `severity`, `confidence`, `model`, `analyzedAt`

## Jobs

### Job detail
`GET /api/v1/analysis/jobs/{jobId}`

Response includes:
- `jobId`, `idempotencyKey`, `status`, `attemptCount`
- `createdAt`, `startedAt`, `finishedAt`
- `traceId`, `logId`
- `resultRef`, `resultSummary`, `resultPayload`
- `errorCode`, `errorMessage`

### Failed jobs
`GET /api/v1/analysis/jobs/failed?page=0&size=20`

Returns paginated `AnalysisJobResponse`.

## Operations / Redrive

### Redrive job
`POST /api/v1/analysis/jobs/{jobId}/redrive`

Optional body:
```json
{ "reason": "operator reason" }
```

Behavior visible from source:
- user-based rate limit: max 10 redrives / 60 minutes
- returns `202 Accepted` with job response on accepted path
- records SUCCESS / SKIPPED / FAILURE audit outcome
- optional `X-Trace-Id`

### Per-job audit
`GET /api/v1/analysis/jobs/{jobId}/redrive/audit`

### Recent audit
`GET /api/v1/analysis/jobs/redrive/audit?page=0&size=20`

## UI Mapping Decision
- **Analyze screen** → POST analysis + poll/read Job + GET result
- **Jobs screen** → Job detail; failed list is available, but a general all-jobs list was **not verified in this inventory**
- **Operations screen** → failed list + redrive + audit endpoints
- **Overview screen** → should use metrics/health contracts later; do not synthesize fake dashboard totals from these endpoints

## Important Gaps / Non-Claims
- General paginated `GET /analysis/jobs` endpoint was not verified.
- Runtime auth requirements were not executed.
- Endpoint success/error payloads were not exercised.
- No claim that Redrive actually reaches Kafka/Bifrost is allowed until E2E evidence exists.
- No frontend implementation is authorized by this inventory alone.

---

# 12. README / Claim Debt

## Known Drift
`docker-compose.yml` publishes Grafana as `3001:3000`; README still has three host-facing `3000` entries.

## Unverified Claims — Do Not Publish As Fact
- `production-ready`
- `GDPR-compliant`
- `80%+ test coverage`
- `10,000+ req/s`
- `50K+ Kafka msg/s`
- `70% MTTR reduction`
- `60% cost reduction`
- `40-60% CI/CD reduction`
- Real Local/Cloud routing behavior
- Runtime gRPC flow

---

# 13. Known Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-001 | README overclaim | Claim audit + evidence |
| R-002 | CI runtime truth unverified | execute workflow/build when runner available |
| R-003 | Frontend source/entrypoint absent | frozen boot-shell repair only after authorization |
| R-004 | Fallback-only E2E | Real-model mandatory |
| R-005 | Scope explosion | Frozen Scope |
| R-006 | Infra overbuild | Single-node PoC 종료 |
| R-007 | Docs/config drift | Evidence-backed docs |
| R-008 | Runtime environment unavailable | GitHub-accessible execution runner required |
| R-009 | Connector whole-file replacement only | only safe complete reconstructions |
| R-010 | Startup banner can overstate readiness | require health evidence |
| R-011 | No status checks attached | missing status ≠ PASS |
| R-012 | Workflow lookup limitation | do not infer push-CI outcome |
| R-013 | Frontend README describes absent tree | align after implementation |
| R-014 | Default build reaches broken frontend | repair before clean-build PASS |
| R-015 | Repair slice scope expansion | frozen 4-file shell |
| R-016 | Jobs UI may need all-jobs listing | verify existing search/list surface before adding endpoint |

---

# 14. Work Rules

Every iteration:
1. `ASGARD_MASTER.md` first-read
2. Current Phase / Batch 확인
3. Repo state inspection
4. Next smallest safe step
5. 실제 가능한 실행/검증
6. Evidence 수집
7. PASS / FAIL / BLOCKED
8. MASTER 갱신
9. Next 하나 지정

Required completion report:
- **What Changed**
- **What Was Executed**
- **What Was Not Verified**
- **Remaining Risks**

Rules:
- Agent self-report ≠ final evidence
- Evidence 없는 완료 금지
- 한 Batch = 한 목표
- README보다 MASTER 우선
- 같은 environmental blocker만 반복하지 않는다
- Human Review가 최종 Gate

---

# 15. Current Checkpoint — P0-B1

## Result
**BLOCKED** — fresh-clone/runtime evidence가 없어 Gate 0 종료 불가. Frontend/default unified build는 tracked contract 기준 **BROKEN STATICALLY**.

## What Changed
- `ASGARD_MASTER.md`
  - observed main을 `99fc68233f2ab2e48337c2ef036b7a62b33fa2db`로 최신화
  - E-032 Core operator API inventory 추가
  - Analysis / Job / Redrive 최소 API contract와 UI mapping을 고정
  - general all-jobs list가 미확인임을 명시
- Application / experimental code 변경 없음
- Frontend 구현 없음

## What Was Executed
- MASTER first-read
- remote `main` commit inspection
- `AnalysisController.java` inspection
- `AnalysisJobController.java` inspection
- `RequestLogAnalysis.java` inspection
- `AnalysisJobAcceptedResponse.java` inspection
- `AnalysisJobResponse.java` inspection
- `RedriveRequest.java` inspection
- actual endpoint / DTO source contract comparison
- same DNS/clone blocker command was intentionally not repeated

## What Was Not Verified
- Fresh clone / local working tree / local↔remote sync
- actual Java/Python/Node/Docker versions
- `npm install`, `npm run build`, `npm run dev`
- Heimdall/Bifrost tests
- default `build-all.ps1` runtime failure
- Compose/E2E
- GitHub Actions green result
- Runtime auth and API responses
- Real AI calls / Grafana live metrics
- Redrive runtime Kafka/Bifrost path
- README Grafana 3-entry mutation

## Remaining Risks
- GitHub-accessible runtime runner 없이는 P0-B1 PASS 불가.
- Frontend/default build는 runtime confirmation 전까지 BROKEN STATICALLY.
- Startup banner는 실제 readiness보다 성공적으로 보일 수 있음.
- General all-jobs API가 없으면 Phase 2 Jobs 화면에서 backend gap이 발생할 수 있음.
- README Grafana drift와 unsupported claims가 남아 있음.

## Next — single task
**P0-B1 Runtime Preflight remains first priority:** GitHub-accessible checkout runner에서 fresh clone → HEAD/sync → Java/Python/Node/Docker versions → `npm install` / `npm run build` → default build readiness를 실행한다.

**If the same environmental blocker persists again:** `LogController` / log ingestion-search API surface를 정적으로 inventory하여 UC-02의 실제 시작점인 "log 생성/선택 → analysis request" 계약을 닫고, 새 backend 구현 없이 Golden Path를 구성할 수 있는지 판정한다.

**Concrete external prerequisite:** `github.com` DNS/HTTPS가 가능한 checkout runner.
