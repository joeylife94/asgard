# ASGARD MASTER

> **Authoritative checkpoint**
> Asgard의 현재 상태, v1.0 종료선, Evidence, 다음 작업을 관리하는 단일 기준 문서.
> README보다 본 문서의 상태 판정을 우선한다.

## 0. Control
- **Target**: Asgard v1.0 — Wishket Proof
- **Target Level**: Usable Production-like PoC
- **Current Phase**: Phase 0 — Baseline Truth
- **Current Batch**: P0-B1 — Repository Preflight (BLOCKED: local execution unavailable)
- **Status**: IN PROGRESS
- **Repo**: `joeylife94/asgard`
- **Branch**: `main`
- **Authoritative Commit**: `230265640e9591e9f47364283806aedc41f68e93` (current repository HEAD; code baseline parent `bca6567919cbcac3f9039268c09526b25179f370`)
- **Updated**: 2026-08-18
- **Final Gate**: Human Review Required

---

# 1. Product Definition

**Asgard는 기업 로그/운영 데이터를 Local LLM 또는 Cloud LLM으로 선택적으로 분석하고, Kafka 기반 비동기 Job과 장애 복구·관측 기능을 제공하는 Hybrid AI Operations Platform이다.**

```text
Input
  ↓
Heimdall
  ↓
Analysis Job
  ↓
Kafka
  ↓
Bifrost
  ↓
Routing
├─ Local AI
└─ Cloud AI
  ↓
Result / DB
  ↓
Dashboard / Operator
```

Failure:

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

## Non-Goals
- Multi-tenancy 완성
- HA / Multi-region
- Kubernetes production
- Autoscaling
- Full RBAC / Enterprise Secret Manager
- SLA/SLO 운영
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
| E2E Repro | 5~6/10 | Real model run 필요 |
| Documentation Truth | 4/10 | Cleanup 필요 |
| Wishket Proof | 5~6/10 | NOT READY |

**Current Summary:** 기능은 충분하지만, 사용 흐름과 Evidence가 닫히지 않음.

> **Feature Development → Proof Hardening**

---

# 4. Baseline Classification

## Repository에서 확인된 것
- Heimdall / Spring Boot
- Bifrost / FastAPI
- React/Vite Frontend
- Kafka `analysis.request → analysis.result`
- Job persistence / idempotency
- DLQ / Redrive / Redrive Audit
- Circuit Breaker / Dynamic Routing
- Feedback / Quality / Experiment / Smart Cache
- Prometheus / Grafana
- Docker Compose
- E2E smoke script
- Java 21 Gradle toolchain

## 아직 실제 실행 검증이 필요한 것
- Fresh clone build
- One-command startup
- Real Local LLM E2E
- Real Cloud LLM E2E
- Frontend Golden Path
- Grafana real metrics
- Failure → DLQ → Redrive → Success
- Current CI green
- README benchmark / coverage / cost claims
- HP AI Server reference deployment

## Known Problems
1. **Gradle Java 21 vs GitHub Actions JDK 17**
2. **Python dependency install 실패가 masking될 수 있음**
3. **Frontend test script 부재 + unified runner false-pass 가능성**
4. **README overclaim / stale info / version-date drift**

---

# 5. Frozen Scope

## CORE — v1.0 Must Pass
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

**Rule:** Experimental 개선은 Core PASS 이후.

---

# 6. Required Use Cases

| UC | Goal | PASS 기준 |
|---|---|---|
| UC-01 Startup | 제3자 실행 | clone → config → all core services healthy |
| UC-02 Analysis | 실제 AI 분석 | Job → Kafka → real AI → result → SUCCEEDED |
| UC-03 Routing | Hybrid route | Sensitive→LOCAL / General→CLOUD 재현 |
| UC-04 Recovery | 장애 복구 | FAILED → DLQ → Redrive → Audit → SUCCEEDED |
| UC-05 Observability | 운영 가시성 | jobs/latency/routes/DLQ/redrive/health 확인 |

## UC-01 Evidence
- terminal
- `docker compose ps`
- health endpoints
- screenshot

## UC-02 Evidence
- request
- Job ID
- Kafka event
- AI result
- DB/result state
- route/provider/latency

## UC-03 Evidence
- Local input/output
- Cloud input/output
- route decision
- provider
- Cloud key 없음/장애 시 Local-only 생존

## UC-04 Evidence
- FAILED state
- DLQ event
- Redrive
- Audit
- final SUCCEEDED
- duplicate-safe result

## UC-05 Required Metrics
- Jobs Requested / Succeeded / Failed
- Success Rate
- Processing Latency
- Local / Cloud Requests
- DLQ / Redrive Count
- Service Health

---

# 7. Minimal Frontend

| Screen | Required |
|---|---|
| Overview | Health, total jobs, success/failed, local/cloud count |
| Analyze | input, question, AUTO/LOCAL/CLOUD, Analyze |
| Jobs | ID, status, route, provider, latency, result |
| Operations | failed jobs, DLQ, redrive, audit |

**Not Now:** Experiment UI, Feedback Admin, Model Registry, complex user admin, design-system polishing.

---

# 8. Phase Plan

## Phase 0 — BASELINE TRUTH
**Goal:** 현재 실제 상태 확정.

- [ ] git status / branch / HEAD / remote
- [ ] secret-risk / large-file scan
- [ ] runtime prerequisites
- [ ] clean build
- [ ] Heimdall tests
- [ ] Bifrost tests
- [ ] Frontend build
- [ ] Compose startup
- [ ] current E2E smoke
- [ ] Local / Cloud AI path
- [ ] CI audit
- [ ] README claim audit

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

# 9. Definition of Done

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

## Evidence
- [ ] Test
- [ ] E2E
- [ ] CI
- [ ] Grafana
- [ ] Runtime screenshots
- [ ] Demo
- [ ] Published number별 benchmark evidence

## Documentation
- [ ] README current
- [ ] stale info 제거
- [ ] unsupported compliance/performance claims 제거
- [ ] version/date consistent
- [ ] run instructions verified

**Final:** Human Review → `ASGARD v1.0 — PROOF PASS`

---

# 10. Evidence Registry

| ID | Evidence | Status | Location |
|---|---|---|---|
| E-001 | Clean Build | PENDING | |
| E-002 | Heimdall Tests | PENDING | |
| E-003 | Bifrost Tests | PENDING | |
| E-004 | Frontend Build | PENDING | |
| E-005 | Real Local AI E2E | PENDING | |
| E-006 | Local vs Cloud Routing | PENDING | |
| E-007 | DLQ → Redrive → Success | PENDING | |
| E-008 | Grafana Metrics | PENDING | |
| E-009 | GitHub Actions Green | PENDING | |
| E-010 | Actual Benchmark | PENDING | |
| E-011 | Final Demo | PENDING | |
| E-012 | HP AI Server Run | PENDING | |

---

# 11. Claim Policy

**Evidence 없는 숫자/품질 주장은 공개 문서에 넣지 않는다.**

검증 전 사용 금지:
- Production Ready
- GDPR Compliant / Article 32 Compliant
- 10,000+ req/s / 50K+ msg/s
- 80%+ coverage
- 60% cost reduction
- 70% MTTR reduction
- 80% local workload

Preferred:
- `GDPR-compliant` → `Designed to support privacy-sensitive local inference and data-residency requirements.`
- `Production-ready` → `Production-oriented architecture with reproducible E2E and failure-recovery evidence.`

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

---

# 14. Work Rules

매 작업 세션:
1. `ASGARD_MASTER.md`
2. `git status / branch / HEAD`
3. Current Phase / Batch
4. Batch Scope 고정
5. 구현
6. 실제 실행
7. 테스트
8. Evidence
9. PASS / FAIL
10. MASTER 갱신
11. Next 하나 지정

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

---

# 15. Batch Template

```markdown
## P{PHASE}-B{NUMBER} — Title

### Goal
-

### In Scope
-

### Out of Scope
-

### Acceptance Criteria
- [ ]

### Execution
-

### Evidence
-

### Result
PASS / FAIL / BLOCKED

### What Changed
-

### What Was Executed
-

### What Was Not Verified
-

### Remaining Risks
-

### Next
-
```

---

# 16. Current Checkpoint

```text
Feature-rich Engineering Project
              ↓
        Proof Hardening
              ↓
   Usable Production-like PoC
              ↓
         Wishket Proof
```

- **Phase**: Phase 0
- **State**: PARTIAL BASELINE — P0-B1 BLOCKED
- **Current Remote HEAD**: `230265640e9591e9f47364283806aedc41f68e93`
- **Code Baseline Parent**: `bca6567919cbcac3f9039268c09526b25179f370`
- **Verified Remotely**: main HEAD, tracked tree/large-file risk, secret-risk manifest, declared runtime prerequisites, Gradle wrapper, CI workflow mismatch/fail-open pattern, branch protection/status-check state
- **Blocked**: execution environment still cannot resolve `github.com`; fresh clone, local working-tree state, installed runtimes, Docker daemon, build/tests remain unverified.
- **Rule Applied**: 동일 blocker 반복만 하지 않고 GitHub-side static preflight를 추가 수행. 미실행 항목은 PASS 처리하지 않음.

---

# 17. P0-B1 — Repository Preflight

## Goal
코드 변경 없이 현재 Git / 환경 / 실행 준비 상태를 확정.

## In Scope
- git status
- branch / HEAD / remote
- large files
- secret-risk
- repo structure
- Java / Python / Node / Docker prerequisites

## Out of Scope
- 코드 수정
- README 수정
- dependency upgrade
- feature 구현
- refactor

## Acceptance Criteria
- [ ] Working tree 상태 — **BLOCKED**: fresh clone 불가
- [x] Authoritative remote HEAD — `230265640e9591e9f47364283806aedc41f68e93`
- [ ] Remote sync — **PARTIAL**: remote `main` HEAD 확인, local comparison 불가
- [x] Secret-risk — tracked secret manifest는 placeholder credential; `.env*` ignore 정책 확인
- [x] Large-file risk — tracked tree에서 50MB 초과 blob 없음
- [ ] Runtime prerequisites — **PARTIAL**: Java 21 toolchain, Gradle 8.5 wrapper, Python >=3.8, frontend build config 선언 확인; 실제 설치 버전/Docker daemon 미검증
- [ ] Build baseline 진행 가능 여부 — **BLOCKED**: execution environment DNS failure

## Evidence
- Remote `main`: `230265640e9591e9f47364283806aedc41f68e93`; parent `bca6567919cbcac3f9039268c09526b25179f370`
- Branch protection: `main` unprotected; required status checks 없음
- Current commit combined statuses: empty — CI green evidence 없음
- Gradle wrapper: `gradle-8.5-all.zip`
- Java project declaration: Gradle toolchain 21
- Python declaration: `python_requires=">=3.8"`
- Frontend: React/Vite `build` script 존재, `test` script 없음
- CI static audit: `.github/workflows/ci.yml` uses JDK 17 while project toolchain is 21
- CI static audit: Bifrost dependency install ends with `|| true`, so dependency failure masking 가능
- Blocker reproduction: `git clone --depth 1 https://github.com/joeylife94/asgard.git` → `Could not resolve host: github.com`

## Result
**BLOCKED** — GitHub-side static preflight는 추가 진전했지만 fresh execution evidence 부족으로 PASS 불가.

## What Changed
- Application code 변경 없음.
- `ASGARD_MASTER.md`의 remote HEAD를 현재 상태로 갱신.
- P0-B1에 Gradle wrapper / branch protection / CI static evidence 추가.
- 반복 blocker만 기록하지 않고 정적 사전검증 범위를 확장.

## What Was Executed
- `ASGARD_MASTER.md` first-read
- GitHub `main` branch 조회
- Current HEAD/parent 확인
- Current commit combined status 조회
- `.github/workflows/ci.yml` 정적 검사
- `gradle/wrapper/gradle-wrapper.properties` 정적 검사
- `bifrost/setup.py` Python requirement 재확인
- Fresh clone 1회 재현 → DNS blocker 지속

## What Was Not Verified
- Local working tree clean/dirty
- Local branch vs `origin/main` sync
- 실제 Java/Python/Node 설치 버전
- Docker / Compose daemon
- Clean build
- Heimdall/Bifrost tests
- Frontend production build
- Runtime E2E

## Remaining Risks
- 실행 환경이 `github.com`을 resolve하지 못하는 한 P0-B1 종료 불가.
- `main`에 required status checks가 없어 현재는 CI 통과가 merge/write gate가 아님.
- CI JDK 17 vs project Java 21 mismatch 유지.
- Python dependency install fail-open 및 frontend no-test false-pass risk 유지.

## Next
**External prerequisite: outbound DNS/HTTPS access to `github.com`이 가능한 execution runner 확보.** 다음 iteration에서는 동일 clone 재시도만 하지 말고, runner가 열리면 즉시 fresh clone → `git status`/HEAD sync → Java/Python/Node/Docker versions → clean build readiness 순으로 남은 P0-B1 criteria를 닫는다. Runner가 여전히 막히면 Phase 0 범위 안에서 README/CI claim audit의 정적 Evidence를 추가하되 runtime PASS는 금지한다.

---

# 18. Final Target

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
