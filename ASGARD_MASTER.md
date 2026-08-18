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
- **Observed main before this checkpoint update**: `e9047928d063d1239e63596980b73b83b7299a61`
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

**Current Summary:** Backend/Kafka feature depth는 충분하지만, runtime Evidence와 실제 Frontend build contract가 닫히지 않았다.

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
- [ ] Clean build — **BLOCKED**
- [ ] Heimdall tests — **BLOCKED**
- [ ] Bifrost tests — **BLOCKED**
- [ ] Frontend build — **BROKEN STATICALLY; runtime confirmation pending**
- [ ] Compose startup — **BLOCKED**
- [ ] Current E2E smoke — **BLOCKED**
- [ ] Local / Cloud AI runtime path — **BLOCKED**
- [x] CI static audit
- [x] README/config static audit
- [x] Unified test status truth static correction
- [x] README Grafana port drift exact-location audit
- [x] Startup script Grafana host-port correction
- [x] README infrastructure host-port contract audit
- [x] Current commit status-check lookup — **no statuses attached; NOT CI PASS evidence**
- [x] README mutation tool-safety check — **whole-file replacement only; no partial patch available**
- [x] Current commit workflow-run lookup limitation recorded — **PR-triggered runs only; empty result is not push-CI evidence**
- [x] Frontend tracked-tree audit — **no `index.html`, `src/`, `public/`, or package lock under `bifrost/frontend/`**

**Gate 0:** 거짓말 없는 Baseline 확보.

---

# 7. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | Clean Build | PENDING | runtime blocked |
| E-002 | Heimdall Tests | PENDING | runtime blocked |
| E-003 | Bifrost Tests | PENDING | runtime blocked |
| E-004 | Frontend Build | **BROKEN STATICALLY** | `npm run build` points to Vite, but tracked frontend root has no standard entrypoint/source tree; runtime confirmation pending |
| E-005 | Real Local AI E2E | PENDING | runtime blocked |
| E-006 | Local vs Cloud Routing | PENDING | runtime blocked |
| E-007 | DLQ → Redrive → Success | PENDING | runtime blocked |
| E-008 | Grafana Metrics | PENDING | runtime blocked |
| E-009 | GitHub Actions Green | PENDING | no green run/status evidence obtained |
| E-010 | Actual Benchmark | PENDING | published numbers unsupported until rerun |
| E-011 | Final Demo | PENDING | |
| E-012 | HP AI Server Run | PENDING | |
| E-013 | Remote branch state | VERIFIED | `main` inspected; branch unprotected, no required status checks |
| E-014 | Runtime declarations | VERIFIED | Java 21 toolchain, Gradle 8.5, Python >=3.8 |
| E-015 | Primary CI correction | VERIFIED STATICALLY | `.github/workflows/ci.yml`: JDK 21; Bifrost dependency install fail-fast |
| E-016 | Frontend test contract | VERIFIED | build script exists; test script absent |
| E-017 | README claim risk | VERIFIED | build/coverage/production/GDPR claims lack current runtime evidence |
| E-018 | README ↔ Compose Grafana drift | VERIFIED | Compose `3001:3000`; README exposes host 3000 |
| E-019 | gRPC caveat | VERIFIED | starter exists; protobuf generation config commented out |
| E-020 | Secondary CI correction | VERIFIED STATICALLY | `.github/workflows/ci-cd.yml`: Java setup steps use JDK 21 |
| E-021 | Unified frontend test truth correction | VERIFIED STATICALLY | `No tests`/`Skipped` preserved; no false all-pass summary |
| E-022 | README Grafana exact-location audit | VERIFIED STATICALLY | exactly three README host-facing corrections required |
| E-023 | Startup Grafana correction | VERIFIED STATICALLY | `start-all.ps1` prints `localhost:3001`, matching Compose |
| E-024 | README infra port audit | VERIFIED STATICALLY | Kafka UI 8090, Redis Commander 8081, Prometheus 9090, Zipkin 9411 match Compose; Grafana only mismatch |
| E-025 | Current commit combined status lookup | VERIFIED | no attached combined statuses; absence of evidence, not green CI |
| E-026 | Fresh clone blocker reproduction | VERIFIED | `git clone` / `git ls-remote` failed with `Could not resolve host: github.com` in execution environment |
| E-027 | README mutation safety check | VERIFIED | available repository editor replaces whole file only; prior run did not risk partial edit |
| E-028 | Commit workflow-run lookup limitation | VERIFIED | connector returns PR-triggered runs only; empty result does not prove push CI absence or success |
| E-029 | Frontend tracked-tree contract | VERIFIED STATICALLY | `bifrost/frontend/` contains only `README.md`, `package.json`, `vite.config.js`; code search found no React `createRoot`/`ReactDOM` entry |

---

# 8. Static Baseline Findings

## VERIFIED / CORRECTED
1. Project declares Java 21 toolchain; Gradle wrapper 8.5; Python package `>=3.8`.
2. Primary CI uses JDK 21 and Bifrost dependency install is fail-fast.
3. Secondary CI Java setup steps use JDK 21.
4. Unified frontend test runner no longer converts `No tests` / `Skipped` into `Passed`.
5. `start-all.ps1` Grafana URL matches Compose: `http://localhost:3001`.
6. README infra ports match Compose except Grafana.
7. Current commit combined-status lookup returned no statuses; CI remains unverified.
8. Commit workflow-run lookup is PR-only in the available connector and cannot prove push-run success/absence.
9. README mutation requires whole-file replacement through the current connector; edit only when reconstruction is safe.
10. Frontend `package.json` exposes `build: vite build` but no `test` script.
11. `bifrost/frontend/` tracked directory currently contains only `README.md`, `package.json`, `vite.config.js`.
12. `vite.config.js` does not define a custom build input; standard Vite root entry (`index.html`) is absent.
13. Frontend README claims `public/`, `src/`, components and `npm test`, but those tracked paths/scripts are absent.

**Important:** static correction ≠ runtime/CI PASS.

## FRONTEND BUILD CONTRACT — BROKEN STATICALLY
Evidence indicates the current tracked frontend cannot satisfy the documented Vite build contract as-is:

- `package.json`: `build = vite build`
- `vite.config.js`: no custom `build.rollupOptions.input`
- tracked frontend root: no `index.html`
- tracked frontend root: no `src/` or `public/`
- frontend README documents those missing paths and `npm test`, but package.json has no `test` script

**Classification:** `BROKEN STATICALLY`, with actual command failure still requiring runtime confirmation.

This is a Core-scope issue, but **implementation is deferred until Phase 0 baseline is closed or the next active batch explicitly authorizes the fix**.

## README ↔ COMPOSE GRAFANA DRIFT
`docker-compose.yml` publishes Grafana as `3001:3000`; host-facing docs must use `3001`.

README has three known drifted entries:
1. `Infrastructure Services` → `Grafana: http://localhost:3000 (admin/admin)`
2. `Monitoring Stack` table → Grafana port `3000`
3. `Access URLs` → `Grafana: http://localhost:3000`

Expected host-facing value: `3001`.

## STARTUP CONTRACT CAVEAT
`start-all.ps1` prints `ASGARD STARTUP COMPLETE` after launching background processes but does not prove Heimdall/Bifrost/Frontend health. UC-01 remains runtime-unverified.

## STILL BROKEN / INCONSISTENT
1. Frontend tracked source/entry tree absent.
2. Frontend actual test suite absent.
3. Frontend README describes files/scripts that are not tracked.
4. README Grafana 3-entry mutation pending.
5. README build/coverage badges are static claims, not live Evidence.
6. Startup completion banner is not health-check proof.

## UNVERIFIED CLAIMS
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

# 9. Claim Policy

**Evidence 없는 숫자/품질 주장은 공개 문서에 넣지 않는다.**

검증 전 사용 금지:
- Production Ready
- GDPR Compliant / Article 32 Compliant
- 10,000+ req/s / 50K+ msg/s
- 80%+ coverage
- 60% cost reduction
- 70% MTTR reduction
- 80% local workload
- CI/CD time `40-60% reduction`

---

# 10. Known Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-001 | README overclaim | Claim audit + evidence |
| R-002 | CI runtime truth unverified | execute workflow/build when runner available |
| R-003 | Frontend source/entrypoint absent | classify truthfully now; repair in an explicitly authorized Core batch |
| R-004 | Fallback-only E2E | Real-model mandatory |
| R-005 | Scope explosion | Frozen Scope |
| R-006 | Infra overbuild | Single-node PoC 종료 |
| R-007 | Docs/config drift | Evidence-backed docs |
| R-008 | Runtime environment unavailable | GitHub-accessible execution runner required |
| R-009 | Connector whole-file replacement only | mutate large files only after complete safe reconstruction |
| R-010 | Startup banner can overstate readiness | require actual health evidence before UC-01 PASS |
| R-011 | No status checks attached to current commit | never interpret missing statuses as successful CI |
| R-012 | Commit workflow lookup is PR-only | do not use empty PR-run result as push-CI evidence |
| R-013 | Frontend README describes non-existent tracked tree | align docs only after source direction is decided |

---

# 11. Work Rules

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

# 12. Current Checkpoint — P0-B1

## Result
**BLOCKED** — fresh-clone/runtime evidence가 없어 Gate 0 종료 불가. 다만 Frontend는 더 이상 단순 runtime-unverified가 아니라 **tracked repository contract 기준 BROKEN STATICALLY**로 분류한다.

## What Changed
- `ASGARD_MASTER.md`
  - observed `main`을 `e9047928d063d1239e63596980b73b83b7299a61`로 최신화
  - Frontend 상태를 `BROKEN STATICALLY`로 재분류
  - E-029 Frontend tracked-tree evidence 추가
  - Phase 0 Frontend build criterion / risks / static findings 최신화
- Application / experimental code 변경 없음
- Frontend 구현은 Phase 0 범위를 넘으므로 생성하지 않음

## What Was Executed
- MASTER first-read
- remote `main` inspection → `e9047928d063d1239e63596980b73b83b7299a61`
- `bifrost/frontend/` GitHub contents inspection
  - tracked entries: `README.md`, `package.json`, `vite.config.js` only
- `bifrost/frontend/package.json` inspection
  - `build: vite build`
  - `test` script absent
- `bifrost/frontend/vite.config.js` inspection
  - no custom build input
- repository code search
  - `ReactDOM` → no result
  - `createRoot` → no result
- frontend README inspection
  - documents `public/`, `src/`, components, `npm test`, which do not match tracked tree/package scripts
- repeated local DNS clone attempt intentionally skipped under blocker-loop rule

## What Was Not Verified
- actual `npm run build` failure output
- Fresh clone / local working tree / local↔remote sync
- actual Java/Python/Node/Docker versions
- Clean build / Heimdall tests / Bifrost tests
- Compose/E2E
- GitHub Actions green result
- Real AI calls / Grafana live metrics
- README Grafana 3-entry mutation

## Remaining Risks
- GitHub-accessible runtime runner 없이는 P0-B1 PASS 불가.
- Frontend source/entrypoint가 tracked tree에 없어 UC-01/Frontend build가 현재 blocker다.
- README는 존재하지 않는 frontend tree/scripts를 문서화한다.
- README Grafana drift 3곳이 남아 있다.
- README performance/compliance claims는 unsupported.

## Next — single task
**P0-B1 Runtime Preflight remains first priority:** GitHub-accessible checkout runner가 확보되면 fresh clone → HEAD/sync → Java/Python/Node/Docker versions → clean build readiness를 실행하고, `npm run build`로 Frontend static-broken 판정을 runtime-confirm한다.

**If the environmental blocker still persists:** 다음 non-redundant GitHub-side step은 `build-all.ps1` / startup scripts가 현재 누락된 Frontend tree를 어떻게 취급하는지 정적 추적하여, P0-B1 clean-build/startup contract의 실제 failure boundary를 확정한다.

**Concrete external prerequisite:** `github.com` DNS/HTTPS가 가능한 checkout runner.
