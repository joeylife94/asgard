# Runbook: Postgres "Connection refused" 대응

## 증상
- 애플리케이션 로그에 `Connection refused` 또는 `could not connect to server`가 발생
- DB 커넥션 풀 에러, 재시도 폭증

## 빠른 확인(5분)
1) 서비스에서 DB Host/Port 확인
- 환경변수/설정의 `DB_HOST`, `DB_PORT` 또는 JDBC/SQLAlchemy URL 확인

2) 네트워크 연결 확인
- 같은 네트워크/노드에서 `tcp` 연결 확인
  - 예: `nc -vz <db-host> 5432`

3) Postgres 프로세스/리스닝 확인(서버 측)
- `systemctl status postgresql`
- `ss -lntp | grep 5432`

## 원인 후보
- Postgres가 내려가 있음(프로세스 종료, OOM, 장애)
- 방화벽/보안그룹/네트워크 정책 변경
- 잘못된 포트/호스트 배포
- 커넥션 수 상한 초과로 일시 거부(다른 에러로 나타날 수도 있음)

## 대응 절차
1) DB 서비스 상태 복구
- Postgres 재시작 후 헬스 확인

2) 설정 롤백/수정
- 최근 배포에서 DB URL 변경 여부 확인

3) 커넥션 풀 보호
- 재시도/타임아웃/최대 커넥션 값 조정

## 검증
- 애플리케이션에서 `SELECT 1` 성공
- 에러율/재시도율 감소

## 참고
- 장애 타임라인과 변경 이력(배포/네트워크 정책)을 함께 확인
