# Runbook: Kafka Consumer Lag 급증 대응

## 증상
- `consumer lag`가 지속적으로 증가
- 처리 지연으로 다운스트림 SLA 위반
- 재처리/중복 처리 위험 증가

## 빠른 확인(5~10분)
1) 컨슈머 그룹 상태
- `kafka-consumer-groups --describe --group <group>`

2) 처리량/에러 확인
- 애플리케이션 로그에서 예외/재시도 패턴 확인
- 메시지 처리 평균 시간(핫스팟) 확인

3) 파티션/리밸런싱
- 잦은 리밸런싱(JoinGroup/SyncGroup) 여부
- 파티션 수 대비 컨슈머 인스턴스 수 확인

## 원인 후보
- 처리 로직의 병목(외부 API 지연, DB 락, 대용량 페이로드)
- 컨슈머 인스턴스 부족/리소스 제한(CPU/메모리)
- 브로커/네트워크 이슈
- 잘못된 `max.poll.interval.ms` 또는 배치 설정

## 대응 절차
1) 병목 제거
- 느린 의존성(외부 API/DB)을 먼저 확인
- 타임아웃/서킷브레이커/캐시 적용

2) 스케일 아웃
- 컨슈머 수 증가(파티션 수 이하로)

3) 설정 조정
- `max.poll.records`, `fetch.max.bytes`, `max.poll.interval.ms` 점검

## 검증
- lag 감소 추세 확인
- 처리율(throughput) 정상화

## 참고
- lag는 원인이 아니라 결과이므로, 처리 시간/에러율/리밸런싱 빈도를 같이 본다
