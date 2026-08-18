# ASGARD MASTER

> **Authoritative checkpoint**
> Asgard의 현재 상태, v1.0 종료선, Evidence, 다음 작업을 관리하는 단일 실행 계약.
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
- **Observed Remote HEAD before this checkpoint update**: `f5fbe44d1598a7009ac3c389a28f97a24d5f78d7`
- **Original code baseline before MASTER-only commits**: `bca6567919cbcac3f9039268c09526b25179f370`
- **Updated**: 2026-08-18
- **Final Gate**: Human Review Required

---

# 1. Product Definition

**Asgard는 기업 로그/운영 데이터를 Local LLM 또는 Cloud LLM으로 선택적으로 분석하고, Kafka 기반 비동기 Job과 장애 복구·관측 기능을 제공하는 Hybrid AI Operations Platform이다.**

```text
Input → Heimdall → Analysis Job → Kafka → Bifrost
      → Routing ─┬→ Local AI
                 └→ Cloud AI
      → Result / DB → Dashboard / Operator
```

Failure path:

```text
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
| Spring Backend | 8/10 | Strong |
| Kafka Control Plane | 8/10 | Strong |
| AI Routing | 6~7/10 | Runtime proof 필요 |
| DLQ / Redrive | 7~8/10 | Demo proof 필요 |
| Docker Infra | 7/10 | Repro check 필요 |
| Observability | 6~7/10 | Real evidence 필요 |
| Frontend | 4~5/10 | Golden Path 부족 |
| CI/CD | 4/10 | Fix 필요 |
| E2E Reproducibility | 5~6/10 | Real model run 필요 |
| Documentation Truth | 4/10 | Cleanup 필요 |
| Wishket Proof | 5~6/10 | NOT READY |

**Current Summary:** 기능과 설계는 충분하지만 실제 사용 흐름과 Evidence가 닫히지 않았다.

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

## Required Evidence
- UC-01: terminal, compose status, health endpoints, screenshot
- UC-02: request, Job ID, Kafka event, AI result, DB/result state, route/provider/latency
- UC-03: Local/Cloud inputs and outputs, route/provider evidence, Local-only survival
- UC-04: FAILED state, DLQ, Redrive, Audit, final SUCCEEDED, duplicate safety
- UC-05: Jobs Requested/Succeeded/Failed, success rate, latency, Local/Cloud requests, DLQ/Redrive count, service health

---

# 6. Minimal Frontend

| Screen | Required |
|---|---|
| Overview | Health, total jobs, success/failed, local/cloud count |
| Analyze | input, question, AUTO/LOCAL/CLOUD, Analyze |
| Jobs | ID, status, route, provider, latency, result |
| Operations | failed jobs, DLQ, redrive, audit |

**Not Now:** Experiment UI, Feedback Admin, Model Registry, complex user admin, design-system polishing.

---

# 7. Phase Plan

## Phase 0 — BASELINE TRUTH
**Goal:** 현재 실제 상태 확정.

- [ ] git status / local branch / local↔remote sync
- [x] remote HEAD / branch state
- [x] secret-risk / large-file static scan
- [ ] installed runtime prerequisites
- [ ] clean build
- [ ] Heimdall tests
- [ ] Bifrost tests
- [ ] Frontend build
- [ ] Compose startup
- [ ] current E2E smoke
- [ ] Local / Cloud AI runtime path
- [x] CI static audit
- [x] README/config claim static audit — partial baseline completed

**Output:** `VERIFIED / BROKEN / UNVERIFIED / REMOVE`

**Gate 0:** 거짓말 없는 Baseline 확보.

## Phase 1 — GOLDEN PATH
**Goal:** `Input → Heimdall → Job → Kafka → Bifrost → Real Local AI → Result → DB → SUCCEEDED`

- [ ] sample scenario 고정
- [ ] real local provider 고정
- [ ] cloud provider optional
- [ ] state transition / persistence
- [ ] repeatable E2E

**Gate 1:** Real-model E2E 반복 성공.

## Phase 2 — OPERATOR EXPERIENCE
- [ ] Overview
- [ ] Analyze
- [ ] Jobs
- [ ] Operations
- [ ] real backend wiring
- [ ] error/loading states

**Gate 2:** 브라우저 Golden Path PASS.

## Phase 3 — RELIABILITY
- [ ] provider down
- [ ] processing failure
- [ ] duplicate request/result
- [ ] DLQ
- [ ] Redrive
- [ ] Circuit Breaker
- [ ] Audit

**Gate 3:** Failure → Detection → Recovery PASS.

## Phase 4 — PROOF HARDENING
- [ ] Java 21 CI
- [ ] Python CI fail-fast
- [ ] frontend false-pass 제거
- [ ] CI green
- [ ] E2E automation
- [ ] coverage 실측
- [ ] benchmark 실측
- [ ] unsupported claims 제거
- [ ] README 재작성
- [ ] architecture diagram
- [ ] screenshots / demo

**Gate 4:** README 주요 claim마다 Evidence 존재.

## Phase 5 — WISHKET PACKAGE
- [ ] Final README
- [ ] Architecture diagram
- [ ] 2~3분 Demo
- [ ] 4~6 screenshots
- [ ] Problem → Solution → Result
- [ ] 핵심 기술적 의사결정
- [ ] 담당 범위
- [ ] 검증/미검증 범위
- [ ] Wishket portfolio copy

**Gate 5:** 비개발 발주자가 1분 내 가치 이해.

---

# 8. Definition of Done

## Functional
- [ ] UC-01 PASS
- [ ] UC-02 PASS
- [ ] UC-03 PASS
- [ ] UC-04 PASS
- [ ] UC-05 PASS

## Reproducibility
- [ ] Fresh clone PASS
- [ ] Repeat run PASS
- [ ] Hidden manual setup 없음

## Reliability
- [ ] Failure scenario PASS
- [ ] DLQ / Redrive PASS
- [ ] Duplicate handling PASS

## Quality
- [ ] CI green
- [ ] Unit tests PASS
- [ ] E2E PASS
- [ ] Frontend build PASS

## Documentation / Proof
- [ ] README current
- [ ] stale info 제거
- [ ] unsupported compliance/performance claims 제거
- [ ] version/date consistent
- [ ] run instructions verified
- [ ] Grafana / Runtime screenshots
- [ ] Demo
- [ ] Published number별 benchmark evidence

**Final:** Human Review → `ASGARD v1.0 — PROOF PASS`

---

# 9. Evidence Registry

| ID | Evidence | Status | Location / Note |
|---|---|---|---|
| E-001 | Clean Build | PENDING | runtime blocked |
| E-002 | Heimdall Tests | PENDING | runtime blocked |
| E-003 | Bifrost Tests | PENDING | runtime blocked |
| E-004 | Frontend Build | PENDING | runtime blocked |
| E-005 | Real Local AI E2E | PENDING | runtime blocked |
| E-006 | Local vs Cloud Routing | PENDING | runtime blocked |
| E-007 | DLQ → Redrive → Success | PENDING | runtime blocked |
| E-008 | Grafana Metrics | PENDING | runtime blocked |
| E-009 | GitHub Actions Green | PENDING | current HEAD has no green status evidence |
| E-010 | Actual Benchmark | PENDING | published numbers unsupported until rerun |
| E-011 | Final Demo | PENDING | |
| E-012 | HP AI Server Run | PENDING | |
| E-013 | Remote main / branch state | VERIFIED | remote branch inspected; no required status checks |
| E-014 | Static runtime declarations | VERIFIED | Java 21 toolchain, Gradle 8.5 wrapper, Python >=3.8 declaration |
| E-015 | CI static mismatch | VERIFIED | Actions JDK 17 vs project Java 21; Python install fail-open pattern |
| E-016 | Frontend test contract | VERIFIED | build script exists; test script absent |
| E-017 | README claim risk | VERIFIED | static badge/production-ready/GDPR/coverage claims lack current execution evidence |
| E-018 | README ↔ Compose Grafana port drift | VERIFIED | README says 3000; Compose maps host 3001→container 3000 |
| E-019 | gRPC claim configuration caveat | VERIFIED | gRPC starter dependency exists; protobuf plugin/source generation blocks are commented out |

---

# 10. Claim Policy

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

Preferred:
- `GDPR-compliant` → `Designed to support privacy-sensitive local inference and data-residency requirements.`
- `Production-ready` → `Production-oriented architecture with reproducible E2E and failure-recovery evidence.`

---

# 11. Static Baseline Findings

## VERIFIED
- Project declares Java 21 toolchain.
- Gradle wrapper is 8.5.
- Python package declares `>=3.8`.
- Frontend has a Vite production build script.
- Remote `main` is not protected and has no required status checks.
- Repository contains Kafka control-plane, DLQ/redrive, observability and frontend implementation assets.

## BROKEN / INCONSISTENT FROM STATIC CONFIG
1. **CI Java version mismatch** — Actions uses JDK 17 while project toolchain is Java 21.
2. **CI Python fail-open** — dependency install path ends with `|| true`, permitting masked install failure.
3. **Frontend test truth risk** — frontend has no `test` script while unified testing language can imply all-service testing.
4. **Grafana URL drift** — README documents `localhost:3000`; `docker-compose.yml` publishes Grafana on host port `3001`.
5. **README status claims are not live evidence** — build/coverage badges are static claim badges rather than current workflow/coverage evidence.

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
- Runtime gRPC flow; starter exists but protobuf generation config is currently commented out

---

# 12. Reference Deployment

HP AI Server는 **Proof Environment**이며 hard dependency가 아니다.

```text
Asgard
  ↓
Local AI Provider Interface
├─ HP AI Server runtime
├─ Other local runtime
└─ Demo provider
```

Required:
- [ ] HP AI Server real inference
- [ ] Asgard → provider connection
- [ ] real result
- [ ] runtime evidence
- [ ] reproducible config

---

# 13. Known Risks

| ID | Risk | Mitigation |
|---|---|---|
| R-001 | README overclaim | Claim audit + evidence |
| R-002 | Java runtime mismatch | Java 21 통일 |
| R-003 | False green | Fail-fast CI/test |
| R-004 | Fallback-only E2E | Real-model mandatory |
| R-005 | Scope explosion | Frozen Scope |
| R-006 | Infra overbuild | Single-node PoC 종료 |
| R-007 | Docs/config drift | Runtime URLs/config를 evidence-backed single source로 정리 |

---

# 14. Work Rules

매 작업 세션:
1. `ASGARD_MASTER.md` first-read
2. `git status / branch / HEAD` 가능한 범위 확인
3. Current Phase / Batch 확인
4. Batch Scope 고정
5. 구현 또는 검증
6. 실제 실행 가능한 것은 실행
7. 테스트 / Evidence 수집
8. PASS / FAIL / BLOCKED 판정
9. MASTER 갱신
10. Next 하나 지정

모든 agent 종료 보고:
- **What Changed**
- **What Was Executed**
- **What Was Not Verified**
- **Remaining Risks**

Rules:
- Agent self-report ≠ final evidence
- Evidence 없는 완료 금지
- 한 Batch = 한 목표
- README보다 MASTER 우선
- Human Review가 최종 Gate
- 같은 environmental blocker만 반복하지 않는다.

---

# 15. Current Checkpoint — P0-B1 Repository Preflight

## Goal
코드 변경 없이 현재 Git / 환경 / 실행 준비 상태를 확정한다.

## In Scope
- git status / branch / HEAD / remote
- large files / secret-risk
- repo structure
- runtime prerequisites
- CI / README / config static preflight

## Out of Scope
- application code 수정
- feature 구현
- experimental scope
- dependency upgrade
- Phase 1 implementation

## Acceptance Criteria
- [ ] Local working tree 상태 — **BLOCKED**
- [x] Authoritative remote HEAD / branch state — observed before this checkpoint update: `f5fbe44d1598a7009ac3c389a28f97a24d5f78d7`
- [ ] Local↔remote sync — **PARTIAL**: remote known, local comparison unavailable
- [x] Secret-risk static check
- [x] Large-file risk static check
- [ ] Runtime prerequisites — **PARTIAL**: declarations known; installed versions/Docker daemon unverified
- [ ] Build baseline readiness — **BLOCKED** by execution environment
- [x] CI static preflight
- [x] README/config static preflight — known claim/port/config drift captured

## Result
**BLOCKED** — static uncertainty was reduced, but fresh execution evidence is still required to close P0-B1.

## What Changed
- Application code 변경 없음.
- `ASGARD_MASTER.md`를 현재 remote state와 정적 baseline findings 기준으로 정리.
- 새 Evidence 추가: Grafana README↔Compose port drift, README claim risk, gRPC configuration caveat.
- README 자체는 P0-B1 Out of Scope이므로 수정하지 않음.

## What Was Executed
- Root `ASGARD_MASTER.md` first-read.
- Remote `main` branch/HEAD inspection.
- README static claim and service URL audit.
- `docker-compose.yml` Grafana port mapping verification.
- `heimdall/build.gradle` gRPC dependency/plugin configuration verification.
- Existing CI/runtime declaration evidence reconciliation.

## What Was Not Verified
- Local working tree clean/dirty
- Local branch vs `origin/main`
- 실제 Java/Python/Node 설치 버전
- Docker / Compose daemon
- Clean build
- Heimdall/Bifrost tests
- Frontend production build
- Runtime E2E / actual Local or Cloud AI calls
- Live Grafana metrics

## Remaining Risks
- Execution runner에서 fresh checkout/build/test가 불가능하면 Gate 0 종료 불가.
- README의 여러 강한 claim은 runtime/benchmark evidence 없이 공개 상태.
- CI mismatch/fail-open은 확인됐지만 P0-B1에서는 수정하지 않음.
- Grafana URL drift는 실제 사용자의 startup 검증을 방해할 수 있음.

## Next — single task
**P0-B1 Runtime Preflight Closure:** outbound DNS/HTTPS로 `github.com`에 접근 가능한 execution runner에서 fresh clone 후 `git status`/HEAD sync → Java/Python/Node/Docker versions → clean build readiness를 한 번에 확인한다. 동일 runtime blocker가 또 지속되면 clone 재시도에 iteration을 소비하지 말고, P0-B1을 BLOCKED로 유지한 채 external prerequisite를 `GitHub-accessible build runner` 하나로 고정한다.

---

# 16. Final Target

```text
Clone → Configure → Start
→ Input Log → Analysis Job → Kafka
→ Hybrid AI Routing → Real AI Result
→ Dashboard / Metrics
→ Failure → DLQ → Redrive → Success

CI GREEN
E2E PASS
EVIDENCE ATTACHED
README TRUTHFUL

→ ASGARD v1.0 — PROOF PASS
```
