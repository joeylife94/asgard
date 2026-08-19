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
- **Original code baseline**: `bca6567919cbcac3f9039268c09526b25179f370`
- **Observed main before this checkpoint update**: `52af70296dcce14ee51aa3a5a446306e817865de`
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
| CI/CD | 6/10 | Java 21 aligned; Phase 0 executable preflight added; run result pending |
| E2E Reproducibility | 5~6/10 | Real model run 필요 |
| Documentation Truth | 4.5/10 | Grafana README drift + frontend docs/source drift |
| Wishket Proof | 5~6/10 | NOT READY |

**Current Summary:** static inventory is sufficient. Phase 0 now prioritizes GitHub-visible execution evidence. Frontend/default build remains BROKEN STATICALLY until runtime confirms or repairs it in an authorized later batch.

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
- [ ] Local working tree / local branch / local↔remote sync — **BLOCKED in current external environment**
- [x] Remote HEAD / branch state
- [x] Secret-risk static check
- [x] Large-file static check
- [ ] Installed runtime prerequisites — **EXECUTABLE VIA CI PREFLIGHT; result pending**
- [ ] Clean build — **BROKEN STATICALLY at Frontend step; runtime confirmation pending**
- [ ] Heimdall tests — **CI configured; run result pending**
- [ ] Bifrost tests — **CI configured; run result pending**
- [ ] Frontend build — **CI PREFLIGHT CONFIGURED; expected failure must be proven by run evidence**
- [ ] Compose startup — **BLOCKED**
- [ ] Current E2E smoke — **BLOCKED**
- [ ] Local / Cloud AI runtime path — **BLOCKED**
- [x] CI static audit
- [x] CI Java 21 alignment / dependency fail-fast correction
- [x] Unified test false-pass correction
- [x] Startup Grafana host-port correction
- [x] Frontend tracked-tree/failure-boundary audit
- [x] Frontend repair slice frozen — **DESIGN ONLY; implementation not authorized in Phase 0**
- [x] Phase 0 repo-native executable preflight added to primary CI

**Gate 0:** 거짓말 없는 Baseline 확보. Missing status / unavailable lookup is never PASS.

---

# 7. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | Clean Build | **BROKEN STATICALLY** | default build reaches frontend; runtime confirmation pending |
| E-002 | Heimdall Tests | PENDING | CI configured; execution result pending |
| E-003 | Bifrost Tests | PENDING | CI configured; execution result pending |
| E-004 | Frontend Build | **BROKEN STATICALLY** | no tracked `index.html` / `src/`; CI preflight now executes install/build |
| E-005 | Real Local AI E2E | PENDING | runtime blocked |
| E-006 | Local vs Cloud Routing | PENDING | runtime blocked |
| E-007 | DLQ → Redrive → Success | PENDING | runtime blocked |
| E-008 | Grafana Metrics | PENDING | runtime blocked |
| E-009 | GitHub Actions Green | PENDING | no green run/check evidence |
| E-010 | Actual Benchmark | PENDING | published numbers unsupported until rerun |
| E-011 | Final Demo | PENDING | |
| E-012 | HP AI Server Run | PENDING | |
| E-013 | Remote branch state | VERIFIED | `main` inspected; branch unprotected, no required status checks |
| E-014 | Runtime declarations | VERIFIED | Java 21 toolchain, Gradle 8.5, Python >=3.8 |
| E-015 | Primary CI correction | VERIFIED STATICALLY | primary CI JDK 21; Bifrost install fail-fast |
| E-016 | Frontend test contract | VERIFIED | build script exists; test script absent |
| E-017 | README claim risk | VERIFIED | unsupported production/compliance/performance claims identified |
| E-018 | README ↔ Compose Grafana drift | VERIFIED | Compose `3001:3000`; README still has three host-facing `3000` values |
| E-019 | gRPC caveat | VERIFIED | starter exists; protobuf generation config commented out |
| E-020 | Secondary CI correction | VERIFIED STATICALLY | secondary CI Java setup JDK 21 |
| E-021 | Unified frontend test truth correction | VERIFIED STATICALLY | no false all-pass summary |
| E-022 | README Grafana exact-location audit | VERIFIED STATICALLY | three corrections required |
| E-023 | Startup Grafana correction | VERIFIED STATICALLY | startup script prints `localhost:3001` |
| E-024 | README infra port audit | VERIFIED STATICALLY | Grafana is remaining infra port drift |
| E-025 | Commit combined status lookup | VERIFIED | empty status list = absence of evidence, not green |
| E-026 | Fresh clone blocker reproduction | VERIFIED | external execution environment could not resolve `github.com` |
| E-027 | README mutation safety | VERIFIED | connector existing-file mutation is whole-file replacement |
| E-028 | Workflow lookup limitation | VERIFIED | available commit workflow lookup cannot prove push-CI success |
| E-029 | Frontend tracked-tree contract | VERIFIED STATICALLY | no tracked Vite entry/source tree |
| E-030 | Unified build/startup failure boundary | VERIFIED STATICALLY | default build reaches frontend; startup banner lacks health proof |
| E-031 | Minimal frontend repair slice | VERIFIED STATICALLY | frozen 4-file boot shell; not active |
| E-032 | Core operator API inventory | VERIFIED STATICALLY | source-level only; runtime behavior pending |
| E-033 | Phase 0 executable CI preflight | VERIFIED STATICALLY | commit `52af702...` adds checkout + JDK21/Python3.11/Node20/runtime capture + frontend `npm install`/`npm run build` |
| E-034 | Preflight-trigger commit status lookup | UNVERIFIED EXECUTION | combined statuses empty; no GitHub Actions run/check result available through current lookup |

---

# 8. Execution-First Baseline Decisions

1. No additional endpoint inventories, frontend redesign notes, or repeated README audits unless a new contradiction changes execution decisions.
2. `.github/workflows/ci.yml` now has a `preflight` job that makes two Phase 0 criteria falsifiable on GitHub-hosted Ubuntu:
   - runtime versions: Git/Java/Python/Node/npm/Docker
   - frontend dependency install and Vite build
3. Primary unit job independently executes Heimdall and Bifrost tests; preflight failure does not suppress the unit job.
4. Frontend repair remains unauthorized while P0-B1 is active.
5. Missing commit status is not CI evidence. Actual workflow/job/check result is required before promotion.
6. If CI result cannot be observed with available tooling, do not manufacture more static work; record the exact observation prerequisite and stop that loop.

---

# 9. Frontend Contract — BROKEN STATICALLY

- `package.json`: `dev = vite`, `build = vite build`
- no tracked root `index.html`
- no tracked `src/`
- default unified build reaches frontend
- startup checks package existence, not frontend health

## Frozen Later Repair — NOT ACTIVE
Minimum file set:
- `bifrost/frontend/index.html`
- `bifrost/frontend/src/main.jsx`
- `bifrost/frontend/src/App.jsx`
- `bifrost/frontend/src/index.css`

Runtime acceptance after authorization:
- [ ] `npm install`
- [ ] `npm run build` exit 0
- [ ] `npm run dev` root reachable
- [ ] default `build-all.ps1` passes frontend step

---

# 10. README / Claim Debt

Known drift: Compose publishes Grafana as `3001:3000`; README still has three host-facing `3000` entries.

Do not publish as fact until measured/verified:
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

# 11. Known Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-001 | README overclaim | publish evidence-backed claims only |
| R-002 | CI runtime truth not observable yet | obtain actual Actions run/job/check evidence |
| R-003 | Frontend source/entrypoint absent | frozen repair only after Phase 0 authorization changes |
| R-004 | Fallback-only E2E | Real-model mandatory |
| R-005 | Scope explosion | Frozen Scope |
| R-006 | Infra overbuild | Single-node PoC 종료 |
| R-007 | Docs/config drift | Evidence-backed docs |
| R-008 | External checkout DNS/runtime unavailable | use GitHub-hosted CI where observable; otherwise require accessible runner |
| R-009 | Connector whole-file replacement | avoid unsafe partial-document mutations |
| R-010 | Startup banner can overstate readiness | require health evidence |
| R-011 | Missing status/check | missing ≠ PASS |
| R-012 | Workflow lookup limitation | do not infer push-CI outcome |
| R-013 | Default build reaches broken frontend | runtime-confirm then repair in authorized batch |

---

# 12. Work Rules

Every iteration:
1. `ASGARD_MASTER.md` first-read
2. Current Phase / Batch 확인
3. Repo / CI state inspection
4. Next smallest non-redundant executable step
5. Actual verification when available
6. Evidence
7. PASS / FAIL / BLOCKED
8. MASTER update only when authoritative state materially changes
9. One exact Next task

Required completion report:
- **What Changed**
- **What Was Executed**
- **What Was Not Verified**
- **Remaining Risks**

Rules:
- Agent self-report ≠ final evidence
- Evidence 없는 완료 금지
- Missing CI status ≠ PASS
- 동일 blocker 반복 금지
- Phase 0 implementation prohibition 유지
- Experimental scope 금지
- Human Review가 최종 Gate

---

# 13. Current Checkpoint — P0-B1

## Result
**BLOCKED** — Gate 0를 닫을 actual execution evidence가 아직 부족하다. Frontend/default build는 **BROKEN STATICALLY**, CI preflight execution result는 **UNVERIFIED**.

## What Changed
- `.github/workflows/ci.yml`
  - `Phase 0 preflight (runtime + frontend build)` job 추가
  - JDK 21 / Python 3.11 / Node 20 setup
  - Git/Java/Python/Node/npm/Docker version capture
  - `bifrost/frontend`에서 `npm install --no-audit --no-fund` + `npm run build`
- `ASGARD_MASTER.md`
  - static-loop fallback 제거
  - Phase 0를 execution-first 상태로 갱신
  - E-033/E-034 추가
- Application / frontend source / experimental code 변경 없음

## What Was Actually Executed
- MASTER first-read
- primary CI workflow inspection
- repository update: CI preflight commit `52af70296dcce14ee51aa3a5a446306e817865de`
- commit metadata/patch verification
- combined commit status lookup: empty status list
- direct generic Actions listing attempts were unsupported by the available GitHub fetch surface; no run result inferred

## What Was Not Verified
- Actual GitHub Actions preflight run/job/check conclusion
- Captured runtime version output
- `npm install` / `npm run build` runtime result
- Heimdall/Bifrost unit test runtime result
- Fresh local clone / local↔remote sync
- Compose/E2E / real AI / Grafana live metrics
- Frontend dev-server reachability

## Remaining Risks
- CI configuration can be correct while the workflow still fails before reaching the intended step.
- The expected frontend failure remains static until an actual CI/local command proves it.
- Current connector status lookup does not expose a push Actions run/check result; empty statuses cannot be treated as execution evidence.

## Next — single task
**Obtain the actual GitHub Actions workflow/job result for commit `52af70296dcce14ee51aa3a5a446306e817865de`; if the preflight failed, capture the failing step/log and promote the corresponding Phase 0 criterion from static suspicion to runtime evidence.**

**Concrete prerequisite if unavailable:** a GitHub Actions run/check lookup or GitHub-accessible execution runner that exposes command output. Until that exists, do not add more static inventory or implementation in P0-B1.
