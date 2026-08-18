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
- **Observed main before this checkpoint update**: `4c740a6b04d1e7643a938f90bfdb9b6df581c21a`
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
| Spring Backend | 8/10 | Strong |
| Kafka Control Plane | 8/10 | Strong |
| AI Routing | 6~7/10 | Runtime proof 필요 |
| DLQ / Redrive | 7~8/10 | Demo proof 필요 |
| Docker Infra | 7/10 | Repro check 필요 |
| Observability | 6~7/10 | Startup Grafana URL corrected; live evidence 필요 |
| Frontend | 5/10 | test truth fixed; Golden Path/runtime proof 부족 |
| CI/CD | 5.5/10 | Java 21 정렬 완료; execution evidence pending |
| E2E Reproducibility | 5~6/10 | Real model run 필요 |
| Documentation Truth | 4.5/10 | Grafana README drift 3곳 mutation blocked by safe-edit limitation |
| Wishket Proof | 5~6/10 | NOT READY |

**Current Summary:** 기능은 충분하지만 실제 사용 흐름과 runtime Evidence가 닫히지 않았다.

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
- [ ] Frontend build — **BLOCKED**
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

**Gate 0:** 거짓말 없는 Baseline 확보.

---

# 7. Evidence Registry

| ID | Evidence | Status | Note |
|---|---|---|---|
| E-001 | Clean Build | PENDING | runtime blocked |
| E-002 | Heimdall Tests | PENDING | runtime blocked |
| E-003 | Bifrost Tests | PENDING | runtime blocked |
| E-004 | Frontend Build | PENDING | runtime blocked |
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
| E-025 | Current commit status lookup | VERIFIED | no attached combined statuses; absence of evidence, not green CI |
| E-026 | Fresh clone blocker reproduction | VERIFIED | `git clone` failed with `Could not resolve host: github.com` in execution environment |
| E-027 | README mutation safety check | VERIFIED | available repository editor replaces whole file only; no partial-line patch path available, so 3-line README edit was not risked |

---

# 8. Static Baseline Findings

## VERIFIED / CORRECTED
1. Project declares Java 21 toolchain; Gradle wrapper 8.5; Python package `>=3.8`.
2. Primary CI uses JDK 21 and Bifrost dependency install is fail-fast.
3. Secondary CI Java setup steps use JDK 21.
4. Unified frontend test runner no longer converts `No tests` / `Skipped` into `Passed`.
5. Frontend has a production build script but no actual `test` script.
6. `start-all.ps1` Grafana URL matches Compose: `http://localhost:3001`.
7. README infra ports match Compose except Grafana.
8. Current commit status lookup returned no statuses; CI remains unverified.
9. README mutation cannot be performed safely through the current connector without reconstructing and replacing the entire file.

**Important:** static correction ≠ runtime/CI PASS.

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
1. README Grafana 3-entry mutation pending.
2. Frontend actual test suite absent.
3. README build/coverage badges are static claims, not live Evidence.
4. Startup completion banner is not health-check proof.

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
| R-003 | Frontend test coverage absent | keep status truthful; add later only if scoped |
| R-004 | Fallback-only E2E | Real-model mandatory |
| R-005 | Scope explosion | Frozen Scope |
| R-006 | Infra overbuild | Single-node PoC 종료 |
| R-007 | Docs/config drift | Evidence-backed docs |
| R-008 | Runtime environment unavailable | GitHub-accessible execution runner required |
| R-009 | Connector whole-file replacement only | do not mutate large files until full-file safe reconstruction or patch-capable editor exists |
| R-010 | Startup banner can overstate readiness | require actual health evidence before UC-01 PASS |
| R-011 | No status checks attached to current commit | never interpret missing statuses as successful CI |

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
**BLOCKED** — fresh-clone/runtime evidence가 없어 Gate 0 종료 불가. README Grafana drift는 정확히 식별됐지만 현재 repository editor가 partial patch를 지원하지 않아 안전한 3-line mutation도 보류했다.

## What Changed
- `ASGARD_MASTER.md`
  - observed `main`을 `4c740a6b04d1e7643a938f90bfdb9b6df581c21a`로 최신화
  - E-027 README mutation safety check 추가
  - connector whole-file replacement risk 명시
  - checkpoint / risk / next 최신화
- README / application / experimental code 변경 없음

## What Was Executed
- MASTER first-read
- remote `main` inspection → `4c740a6b04d1e7643a938f90bfdb9b6df581c21a`
- README current blob 확인 → `63756f3b63431cd4593deeb139752e54def289dd`
- README Grafana drift search → known 3-entry mismatch 유지 확인
- GitHub repository write capability inspection → existing-file mutation은 complete UTF-8 replacement만 지원, partial-line patch 없음
- unsafe whole-file README replacement는 실행하지 않음

## What Was Not Verified
- README 세 Grafana 표현 actual mutation / drift 0건
- Fresh clone / local working tree / local↔remote sync
- 실제 Java/Python/Node/Docker versions
- Clean build / Heimdall tests / Bifrost tests / Frontend build
- Compose/E2E
- GitHub Actions green result
- Real AI calls / Grafana live metrics

## Remaining Risks
- GitHub-accessible runtime runner 없이는 P0-B1 PASS 불가.
- README Grafana drift 3곳이 실제 문서에 남아 있음.
- 현재 editor로 README 전체를 재구성 없이 수정하면 문서 손상 위험이 있음.
- CI workflow 수정은 static evidence만 있고 execution PASS 없음.
- README performance/compliance claims는 unsupported.

## Next — single task
**P0-B1 Runtime Preflight OR Safe README Patch, whichever becomes executable first:**
1. `github.com` DNS/HTTPS가 가능한 checkout runner 확보 시 fresh clone → HEAD/sync → Java/Python/Node/Docker versions → clean build readiness를 실행한다.
2. patch-capable repository editor가 먼저 확보되면 README의 Grafana 3곳만 `3001`로 수정하고 재검색하여 drift 0건을 확인한다.

**Concrete external prerequisite:** GitHub-accessible checkout runner 또는 partial-line patch를 지원하는 repository editor.

---

# 13. Final Target

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
