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
- **Observed main before this checkpoint update**: `5743d1bb0f13a55d6372a467bf9734567aac0512`
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
| Spring Backend | 8/10 | Strong; runtime proof pending |
| Kafka Control Plane | 8/10 | Strong; runtime proof pending |
| AI Routing | 6~7/10 | Runtime proof 필요 |
| DLQ / Redrive | 7~8/10 | Demo proof 필요 |
| Docker Infra | 7/10 | Repro check 필요 |
| Observability | 6~7/10 | Startup Grafana URL corrected; live evidence 필요 |
| Frontend | 3/10 | **BROKEN STATICALLY**: tracked Vite entry/source tree absent |
| CI/CD | 5.5/10 | Java 21 정렬 완료; execution evidence pending |
| E2E Reproducibility | 5~6/10 | Real model run 필요 |
| Documentation Truth | 4.5/10 | Grafana README drift + frontend docs/source drift |
| Wishket Proof | 5~6/10 | NOT READY |

**Current Summary:** Backend/Kafka feature depth는 충분하지만 runtime Evidence가 없고, 현재 tracked Frontend는 기본 Vite build/startup contract를 충족하지 못한다.

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
| E-031 | Minimal frontend repair-slice design | VERIFIED STATICALLY | package/Vite/README contracts compared; minimal repair file set and acceptance criteria frozen below |

---

# 8. Static Baseline Findings

## VERIFIED / CORRECTED
1. Java 21 toolchain; Gradle wrapper 8.5; Python package `>=3.8`.
2. Primary and secondary CI Java setup aligned to JDK 21.
3. Bifrost dependency installation is fail-fast in primary CI.
4. Unified frontend test runner preserves `No tests` / `Skipped` truth.
5. `start-all.ps1` Grafana URL matches Compose: `http://localhost:3001`.
6. README infra ports match Compose except Grafana.
7. CI remains execution-unverified; missing statuses are not PASS evidence.
8. Frontend `package.json` exposes `dev`, `build`, `preview`, `lint`, `format`; no `test` script.
9. Frontend dependencies already include React 18, React DOM, React Router, Axios, Chart.js and React Query.
10. `vite.config.js` uses React plugin, dev port `3000`, `/api` proxy → `http://localhost:8000`, build output `../static/react`.
11. Tracked frontend root has no `index.html`, `src/`, `public/`, or package lock.
12. Frontend README documents a much larger tree and commands/features that are not currently backed by tracked source.
13. Default unified build enters frontend unless explicitly skipped.
14. Startup can announce completion without proving frontend health.

**Important:** static correction/design ≠ runtime/CI PASS.

---

# 9. Frontend Build / Startup Contract — BROKEN STATICALLY

Current tracked frontend cannot satisfy the documented Vite contract as-is:

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
> Activate only after P0-B1 runtime baseline closes or an explicit next batch authorizes repair.

## Goal
Restore the smallest truthful Vite/React application shell required to make the tracked frontend buildable and startable without pretending the full dashboard already exists.

## Minimum File Set

### Must Create
1. `bifrost/frontend/index.html`
   - standard Vite root entry
   - single `#root`
   - imports `/src/main.jsx`

2. `bifrost/frontend/src/main.jsx`
   - `ReactDOM.createRoot`
   - mounts `<App />`
   - imports base stylesheet

3. `bifrost/frontend/src/App.jsx`
   - minimal Asgard shell only
   - identifies project and current UI status
   - no fake metrics, no fake jobs, no fake provider status
   - may expose placeholder navigation labels for planned `Overview / Analyze / Jobs / Operations`, but must clearly mark unavailable sections

4. `bifrost/frontend/src/index.css`
   - minimal readable layout
   - no design-system work

### Must Not Create In This Slice
- mock API data
- fake Grafana/health metrics
- Analysis API integration
- Job tables
- Redrive UI
- Chart.js dashboards
- React Query abstraction
- auth UI
- routing framework unless required for the minimal shell
- tests that assert mocked product behavior
- new dependencies

## Dependency Decision
Current dependencies are more than sufficient for the boot shell. **Add no package dependencies.** The first repair should use React + ReactDOM only. Existing React Router/Axios/Chart.js/React Query remain unused until the later operator-experience slice actually needs them.

## Acceptance Criteria — Repair Batch
- [ ] tracked `index.html` exists and points to `/src/main.jsx`
- [ ] tracked `src/main.jsx`, `src/App.jsx`, `src/index.css` exist
- [ ] no fake operational data or unsupported feature claims in UI
- [ ] no new npm dependency added
- [ ] `npm install` completes — runtime evidence required
- [ ] `npm run build` exits 0 and emits Vite assets to configured output — runtime evidence required
- [ ] `npm run dev` starts and root page returns successfully — runtime evidence required
- [ ] default `build-all.ps1` no longer fails at Frontend build step — runtime evidence required
- [ ] startup script behavior is rechecked; banner alone is not health evidence
- [ ] frontend README is reduced/aligned only after the new tracked tree exists

## Closure Condition
**Frontend transitions from `BROKEN STATICALLY` to `BUILDABLE VERIFIED` only when runtime build/start evidence exists. Static file creation alone is insufficient.**

## Why This Slice Is Small
The v1.0 product requires a Minimal React Dashboard, but Phase 2 owns operator screens. The immediate repair must only restore the executable frontend contract so Phase 1/2 work can proceed without carrying a broken default build.

---

# 11. README / Claim Debt

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

# 12. Known Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-001 | README overclaim | Claim audit + evidence |
| R-002 | CI runtime truth unverified | execute workflow/build when runner available |
| R-003 | Frontend source/entrypoint absent | execute frozen minimal repair slice only after authorization |
| R-004 | Fallback-only E2E | Real-model mandatory |
| R-005 | Scope explosion | Frozen Scope |
| R-006 | Infra overbuild | Single-node PoC 종료 |
| R-007 | Docs/config drift | Evidence-backed docs |
| R-008 | Runtime environment unavailable | GitHub-accessible execution runner required |
| R-009 | Connector whole-file replacement only | large-file mutations only with complete safe reconstruction |
| R-010 | Startup banner can overstate readiness | require health evidence before UC-01 PASS |
| R-011 | No status checks attached | never interpret missing statuses as CI PASS |
| R-012 | Workflow lookup limitation | do not infer push-CI outcome from unsupported lookup |
| R-013 | Frontend README describes absent tree | align after source direction is implemented |
| R-014 | Default build reaches broken frontend | repair frontend contract before clean-build PASS |
| R-015 | Repair slice could expand into UI rebuild | frozen 4-file boot shell; no API/features/new deps |

---

# 13. Work Rules

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

# 14. Current Checkpoint — P0-B1

## Result
**BLOCKED** — fresh-clone/runtime evidence가 없어 Gate 0 종료 불가. Frontend/default unified build는 tracked contract 기준 **BROKEN STATICALLY**.

## What Changed
- `ASGARD_MASTER.md`
  - observed main을 `5743d1bb0f13a55d6372a467bf9734567aac0512`로 최신화
  - E-031 Minimal frontend repair-slice design 추가
  - planned Core repair를 4-file boot shell로 동결
  - repair acceptance / closure criteria 명시
- Application / experimental code 변경 없음
- Frontend 구현 없음

## What Was Executed
- MASTER first-read
- remote `main` inspection
- runtime DNS check 1회 → `github.com` resolution failure persists
- `bifrost/frontend/package.json` inspection
- `bifrost/frontend/README.md` inspection
- `bifrost/frontend/vite.config.js` inspection
- dependency / command / tracked-tree contract comparison
- repeated clone retries intentionally skipped under blocker-loop rule

## What Was Not Verified
- Fresh clone / local working tree / local↔remote sync
- actual Java/Python/Node/Docker versions
- `npm install`, `npm run build`, `npm run dev`
- Heimdall/Bifrost tests
- default `build-all.ps1` runtime failure
- Compose/E2E
- GitHub Actions green result
- Real AI calls / Grafana live metrics
- README Grafana 3-entry mutation

## Remaining Risks
- GitHub-accessible runtime runner 없이는 P0-B1 PASS 불가.
- Frontend/default build는 runtime confirmation 전까지 BROKEN STATICALLY 상태다.
- Startup banner는 실제 readiness보다 성공적으로 보일 수 있다.
- README frontend 문서는 tracked source보다 앞서 있다.
- README Grafana drift와 unsupported performance/compliance claims가 남아 있다.

## Next — single task
**P0-B1 Runtime Preflight remains first priority:** `github.com` DNS/HTTPS가 가능한 checkout runner에서 fresh clone → HEAD/sync → Java/Python/Node/Docker versions → `npm install` / `npm run build` → default build readiness를 실행해 static diagnosis를 runtime-confirm한다.

**If the same environmental blocker persists again:** repair 구현으로 넘어가지 말고, Backend/Frontend integration을 위해 실제로 존재하는 Analysis/Job/Redrive API surface를 GitHub에서 정적으로 inventory하여 Phase 2 operator UI가 사용할 최소 API contract만 설계한다.

**Concrete external prerequisite:** `github.com` DNS/HTTPS가 가능한 checkout runner.
