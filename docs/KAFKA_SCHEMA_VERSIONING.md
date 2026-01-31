# Kafka 메시지 스키마 버전 관리 가이드

## 개요

이 문서는 Asgard 플랫폼에서 사용되는 Kafka 메시지의 스키마 버전 관리 정책과 호환성 가이드라인을 정의합니다.

## 스키마 버전 정책

### 버전 필드

모든 Kafka 메시지에는 `schemaVersion` 필드가 포함되어야 합니다.

```json
{
  "schemaVersion": 1,
  "jobId": "...",
  "timestamp": "..."
}
```

### 버전 번호 규칙

| 변경 유형 | 버전 증가 | 예시 |
|----------|----------|------|
| 호환 가능한 추가 | Minor (선택) | 선택적 필드 추가 |
| 필수 필드 추가 | Major | `schemaVersion` 1 → 2 |
| 필드 제거 | Major | `schemaVersion` 1 → 2 |
| 필드 타입 변경 | Major | `schemaVersion` 1 → 2 |
| 필드 이름 변경 | Major | `schemaVersion` 1 → 2 |

## 현재 메시지 스키마

### 1. AnalysisRequestEvent (v1)

**토픽**: `analysis.request`

```json
{
  "schemaVersion": 1,
  "jobId": "uuid",
  "idempotencyKey": "string",
  "logId": 12345,
  "traceId": "string (optional)",
  "timestamp": "2026-01-31T10:00:00Z",
  "priority": "INFO|WARN|ERROR|CRITICAL",
  "modelPolicy": {
    "provider": "ollama|bedrock",
    "model": "llama3.2"
  }
}
```

**필수 필드**: `schemaVersion`, `jobId`, `idempotencyKey`, `logId`, `timestamp`
**선택 필드**: `traceId`, `priority`, `modelPolicy`

### 2. AnalysisResultEvent (v1)

**토픽**: `analysis.result`

```json
{
  "schemaVersion": 1,
  "jobId": "uuid",
  "logId": 12345,
  "status": "SUCCEEDED|FAILED",
  "traceId": "string (optional)",
  "timestamp": "2026-01-31T10:00:00Z",
  
  // Success fields
  "summary": "분석 요약",
  "rootCause": "근본 원인",
  "recommendation": "권장 조치",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "confidence": 0.95,
  "modelUsed": "llama3.2",
  "latencyMs": 1234,
  
  // Failure fields
  "errorCode": "TIMEOUT|MODEL_ERROR|...",
  "errorMessage": "상세 에러 메시지"
}
```

**필수 필드**: `schemaVersion`, `jobId`, `logId`, `status`, `timestamp`
**성공 시 필수**: `summary`, `severity`
**실패 시 필수**: `errorCode`

### 3. DlqFailedEvent (v1)

**토픽**: `dlq.failed`

```json
{
  "schemaVersion": 1,
  "jobId": "uuid (optional)",
  "idempotencyKey": "string (optional)",
  "originalTopic": "analysis.request",
  "errorCode": "PROCESSING_ERROR",
  "errorMessage": "상세 에러 메시지",
  "traceId": "string (optional)",
  "timestamp": "2026-01-31T10:00:00Z",
  "originalPayload": "원본 메시지 (optional)"
}
```

## 호환성 가이드라인

### Forward Compatibility (전방 호환성)

**Consumer는 알 수 없는 필드를 무시해야 합니다.**

```java
// ✅ Good: 알 수 없는 필드 무시
@JsonIgnoreProperties(ignoreUnknown = true)
public class AnalysisResultEvent {
    // ...
}
```

### Backward Compatibility (후방 호환성)

**새로운 필드는 기본값을 가져야 합니다.**

```java
// ✅ Good: 기본값 제공
@Column(name = "schema_version")
private int schemaVersion = 1;

@Column(name = "new_field")
private String newField = "default_value";
```

### 버전별 처리

```java
public void processEvent(AnalysisResultEvent event) {
    switch (event.getSchemaVersion()) {
        case 1:
            processV1(event);
            break;
        case 2:
            processV2(event);
            break;
        default:
            if (event.getSchemaVersion() > LATEST_SUPPORTED) {
                log.warn("Unknown schema version: {}, attempting best-effort processing", 
                    event.getSchemaVersion());
                processLatest(event);
            } else {
                throw new UnsupportedSchemaVersionException(event.getSchemaVersion());
            }
    }
}
```

## 마이그레이션 절차

### 새 스키마 버전 배포 시

1. **단계 1: Consumer 업데이트**
   - 새 스키마를 처리할 수 있도록 Consumer 먼저 배포
   - 기존 버전 + 새 버전 모두 처리 가능하게

2. **단계 2: Producer 업데이트**
   - Consumer가 준비된 후 Producer 배포
   - 새 스키마 버전으로 메시지 발행 시작

3. **단계 3: 구버전 제거 (선택)**
   - 충분한 유예 기간 후 구버전 처리 코드 제거
   - 최소 2-3개 버전은 지원 유지 권장

### 롤백 시나리오

```yaml
# application.yml
kafka:
  schema:
    # 긴급 롤백 시 구버전으로 발행
    force-version: 1
    # 지원할 최소 버전
    min-supported-version: 1
```

## 스키마 레지스트리 (향후 도입 고려)

현재는 코드 레벨에서 스키마를 관리하지만, 향후 Confluent Schema Registry 도입을 고려할 수 있습니다.

### 장점
- 중앙 집중식 스키마 관리
- 자동 호환성 검증
- 스키마 진화 히스토리 추적

### 도입 시 고려사항
- 추가 인프라 운영 부담
- 직렬화/역직렬화 오버헤드
- 학습 곡선

## 체크리스트

### 새 필드 추가 시
- [ ] 기본값 설정 여부 확인
- [ ] 선택적 필드인지 명시
- [ ] Consumer가 필드 누락 시 처리 가능한지 확인
- [ ] 문서 업데이트

### 스키마 버전 변경 시
- [ ] 버전 번호 증가
- [ ] 마이그레이션 계획 수립
- [ ] Consumer 먼저 배포
- [ ] 테스트 환경에서 검증
- [ ] 문서 업데이트
- [ ] 팀 공지

## 참고 자료

- [Apache Kafka Schema Evolution](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)
- [JSON Schema Compatibility](https://json-schema.org/)
