# Asgard 1차 갈무리 (Phase 1 Wrap-up)

> 작성 기준일: 2026-11-11 · 기준 커밋: `main` @ `fddd8c3df1c9cee21c4c6601d56ac038a402ccbe`
>
> 이 문서는 **요약·점검 문서**이며 권위 문서가 아니다. 상태·수용 증거·주장 경계가 이 문서와 [`ASGARD_MASTER.md`](../ASGARD_MASTER.md) 사이에서 어긋나면 MASTER와 실제 실행 증거가 우선한다. 이 문서는 어떤 주장 경계도 넓히지 않는다.

## 1. 한눈에 보는 현재 상태

| 항목 | 상태 (2026-11-11 확인) |
|---|---|
| 제품 단계 | v1.0 FROZEN · M1–M12 FROZEN · D1–D6 ACCEPTED / FROZEN |
| 다음 단계 | **D7 보류** — 2026-11-11 Human Review: 구체적인 사용자·구매자 요구가 생길 때까지 destination 미선정 |
| `main` 최신 커밋 | `fddd8c3` (2026-09-10, D6 closure). 이후 변경 없음 |
| `main` CI | CI `34435493783` SUCCESS · CI/CD `34435493690` SUCCESS |
| 열린 Issue / PR | 점검 시점 0 / 0 (마지막 Issue #73 CLOSED, 마지막 PR #74 MERGED). 이후 갈무리 정합화 Issue #75 개설 |
| Git 태그 / GitHub Release | 없음 — 정합화 배치 병합 커밋에 1차 종료 태그 예정 |
| 로컬 재확인 | `scripts/check-single-node-handoff-truth.sh` PASS · `scripts/check-d2-delivery-candidate.sh` PASS (`asgard-single-node-d5-config-1`) — Issue #75에서 강화한 gate 기준 |

이번 갈무리에서 애플리케이션 빌드·E2E는 다시 실행하지 않았다. 위 CI 결과는 동일 커밋에 대한 2026-09-10 실행 기록이다.

## 2. 1차에서 만든 것

**제품 정의** — 운영 로그/이벤트를 영속적인 비동기 Job으로 처리하고, Kafka 실행 흐름 · Local LLM(Ollama) 분석 · 결과 저장 · 실패 복구 · 감사 · 관측을 제공하는 Local-first AI Operations Platform. 핵심 증명 대상은 provider 개수가 아니라 **운영 가능한 AI Job lifecycle**이다.

```text
Input → Heimdall → Persistent Job → Kafka → Bifrost → Ollama → Result → Persistence → Operator/Metrics
Failure → FAILED/DLQ → Controlled Redrive → Audit → Retry → SUCCEEDED
```

### 진행 경로

| 구간 | 내용 | 결과 |
|---|---|---|
| v1.0 Proof | UC-01 Startup · UC-02 Real Local AI · UC-03 Local-first Policy · UC-04 Recovery · UC-05 Observability | PASS, Human Review 통과 후 FREEZE |
| M1–M4 | 로컬 재현/첫 Job · 읽기 전용 콘솔 · 통제된 복구 콘솔 · Bifrost 재시작 | 각 1건의 bounded 증명 |
| M5–M9 | 단일 노드 handoff · PostgreSQL 백업/복원 · 진단 스냅샷 · Kafka 재시작 · PostgreSQL 재시작 | 각 1건의 bounded 증명 |
| M10–M12 | handoff 진실성 정합화 · 변경 범위 기반 CI 신호 분리 · retained proof 정리 명령 | D1 도달 |
| D2 | 버전/출처(provenance)를 가진 단일 노드 전달 후보 | ACCEPTED |
| D3 (01–03) | 영속 단일 노드 파일럿 lifecycle · handoff 정합화 · 추출된 깨끗한 작업 공간에서 실행 | ACCEPTED |
| D4 (01–02) | 릴리스 디렉터리와 분리된 파일럿 소유권 · 동일 스키마 호환 A→B 전환 | ACCEPTED |
| D5 (01) | 운영자 소유 설정/민감 입력 분리, fail-closed 검증 | ACCEPTED |
| D6 (01) | 수동 백업 → 깨끗한 대상 복원 검증의 유지보수/복구 경로 | ACCEPTED |

각 항목의 exact head, merge SHA, workflow run, artifact digest는 MASTER §3, §6, §7에 있다.

### 운영자가 실제로 쓸 수 있는 명령 표면

| 스크립트 | 도입 | 역할 |
|---|---|---|
| `scripts/pilot.sh` | D3-01 | `validate / start / status / job / inspect / restart / stop / purge` — 영속 파일럿 lifecycle. `stop`은 상태 보존, `purge`만 파괴적 |
| `scripts/pilot-release.sh` | D4-01 | `ASGARD_PILOT_HOME` 기준 `claim / release` + lifecycle. 릴리스 출처 기록, 충돌/오래된 소유권은 fail-closed |
| `scripts/pilot-configured.sh` | D5-01 | `config-check` + 위 전체. `$ASGARD_PILOT_HOME/config/pilot.env`를 셸 소싱 없이 데이터로 파싱 (`delivery/single-node-candidate/PILOT_CONFIG.example`) |
| `scripts/pilot-maintenance.sh` | D6-01 | `backup / restore-verify`. 원본 DB는 건드리지 않고 깨끗한 복구 대상에만 복원 후 Job/result/audit 불변식 검증 |
| `scripts/local-proof.sh` | M1 | 일회성 증명/회귀 실행기 (영속 파일럿 경로 아님) |
| `scripts/operator-diagnostic-snapshot.sh` | M7 | 읽기 전용 진단 번들 |
| `scripts/m6-backup-restore-proof.sh` | M6 | bounded 백업/복원 증명 |
| `scripts/cleanup-retained-proof.sh` | M12 | retained proof 세션 정리 |

### 규모 (추적 파일 기준)

| 영역 | 파일 | 줄 수 |
|---|---|---|
| Heimdall `src/main` (Java) | 80 | 5,507 |
| Heimdall `src/test` (Java) | 10 | 1,296 |
| Bifrost (Python, 테스트 포함) | 94 | 18,408 |
| `scripts/*.sh` | 10 | 1,888 |
| `.github/workflows/*.yml` | 22 | 5,114 |

## 3. 주장 경계

**말할 수 있는 것** — 단일 Linux 호스트, 기술 운영자 1인, Local Ollama 조건에서: 영속 비동기 Job lifecycle, Kafka 요청/결과 handoff, 결과 영속화, fail-closed Local-first 라우팅, FAILED/DLQ → redrive → audit → retry 복구, Prometheus/Grafana 수준의 제한적 관측, 버전·출처가 있는 전달 후보, 영속 파일럿 운영(시작/점검/재시작/중지/명시적 purge), 동일 스키마 호환 릴리스 전환 1건, 운영자 소유 설정, 수동 백업/복원 검증 1건.

**말할 수 없는 것 (미검증)** — production/enterprise readiness, 공개 배포, HA·다중 노드·Kubernetes·multi-region, 클라우드 provider 실행(AWS Bedrock 포함), SLA/SLO·안정적 성능/비용, DR·PITR·RPO/RTO·연속/예약 백업·복제, 스키마가 바뀌는 마이그레이션과 production rollback, systemd/자동 부팅·무인 운영, Vault/secret manager, RBAC/SSO/multi-tenancy, 보안·법적 인증.

## 4. 열려 있는 부채 (MASTER §4 기준)

| ID | 내용 | 현재 처리 |
|---|---|---|
| R-001 | `idx_severity` 스키마 인덱스 이름 중복 | 비치명적 부채, 요구가 생길 때만 수정 |
| R-002 | Heimdall Checkstyle/build 부채 | 일괄 수정 금지, 필요한 gate가 생길 때만 |
| R-005 | hosted CPU Ollama 지연 변동 | 성능 주장 금지로 관리 |
| R-006 | ingestion 자동 분석이 추가 Job을 만들 수 있음 | 증명 경로에서 대상 Job 격리 |
| R-007 | legacy AWS/Bedrock 코드 잔존 | DEFER |
| R-008 | 라우팅 구현 세대 중복 | 마일스톤 요구 없이는 리팩터링 안 함 |

나머지 R 항목은 CLOSED이거나 "증명 1건을 일반화하지 말 것"이라는 경계 선언이다.

## 5. 갈무리 점검에서 확인한 정합성 갭과 처리

모두 문서/저장소 위생 문제이며 런타임 동작에는 영향이 없다. F-1, F-4, F-5는 Issue #75(MASTER R-029, R-030, R-004)로 처리했다.

| # | 발견 | 처리 |
|---|---|---|
| F-1 | 전달용 handoff 문서와 MANIFEST가 D3에서 멈춰 있었다. `pilot-release.sh` / `pilot-configured.sh` / `pilot-maintenance.sh`가 한 번도 나오지 않았고, 한정어 없는 "Version upgrade/rollback is not verified"를 truth gate가 필수로 요구했다. | **해소 (Issue #75)** — 두 문서에 D4/D5/D6 운영 경로를 추가하고 비주장 문구를 "동일 스키마 호환 A→B 전환 1건 외에는 미검증"으로 한정했다. 두 gate와 D2 번들 검증 단계가 이를 강제한다. |
| F-2 | README가 v1.0까지만 서술했다. | **해소** — "Post-v1.0 progression" 절 추가, 주장 확장 없음. |
| F-3 | 태그/Release가 없어 1차 종료 지점을 가리키는 고정 참조가 없다. | **병합 후 처리** — Issue #75 병합 커밋에 태그. |
| F-4 | 과거 문서의 과장 표현("production-grade", "Production Ready" 등)이 표시 없이 남아 있었다. | **부분 해소 (Issue #75)** — 루트의 과거 문서 10개에 `HISTORICAL / NON-AUTHORITATIVE` 배너를 넣고 gate로 강제한다. `heimdall/**`, `bifrost/**` 아래 문서는 손대지 않았다. 건드리면 Heimdall 애플리케이션 빌드가 돌아 R-002 부채가 이 배치에 섞이기 때문이다. 이 문서들은 R-004에 따라 계속 비권위다. |
| F-5 | `test-results/`에 2025-11-17 실행 산출물 105개가 커밋돼 전달 번들에 포함됐다. | **해소 (Issue #75)** — 삭제하고 `.gitignore`에 추가. 다시 생기면 gate가 실패한다. |
| F-6 | D-수준 수용 workflow는 `pull_request`에서만 돈다. `main` 그린은 CI와 CI/CD만 뜻한다. | 설계상 의도된 동작이라 변경하지 않음. 해석할 때 유의할 사실로만 기록. |

Issue #75는 문서, gate 스크립트, workflow 검증 단계 1곳, 파일 삭제만 다룬다. Heimdall/Bifrost/Compose/스키마/파일럿 스크립트는 바뀌지 않았고 `VERSION`도 그대로다.

## 6. Human Review 결정 (2026-11-11)

1. **1차 종료 지점 고정** — 승인. 정합화 배치가 `main`에 병합된 커밋에 태그를 찍는다.
2. **갈무리 정합화 배치** — 승인. Issue #75로 진행.
3. **D7** — 보류. 구체적인 사용자·구매자 요구가 생길 때 연다. D1–D6은 "단일 노드에서 한 사람이 운영하는 Local-first 파일럿"이라는 하나의 이야기를 이미 끝까지 채웠고, MASTER §5-13은 활동을 위한 작업 생성을 금지한다.

D7을 다시 검토할 때의 후보는 MASTER가 Human Review 전용으로 남겨 둔 항목이다: systemd/자동 부팅 소유권, 무인 운영, 예약 백업, 운영 DB에 대한 in-place 복원, Kubernetes/HA/다중 노드, PostgreSQL 복제, multi-broker Kafka, 클라우드 실행, RBAC/SSO, 공개/production 배포, SLA/SLO, 보안·컴플라이언스 인증. 지금까지의 경로와 가장 자연스럽게 이어지는 것은 systemd/자동 부팅 소유권이고, HA·클라우드·RBAC 계열은 제품 방향 자체를 바꾸는 결정이다.
