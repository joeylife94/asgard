# 🧪 Asgard Testing Guide

종합 테스트 가이드 - Unit Tests, Integration Tests, Performance Tests, Stress Tests

## 📋 목차

- [테스트 환경 설정](#테스트-환경-설정)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Performance Tests](#performance-tests)
- [Stress Tests](#stress-tests)
- [CI/CD 통합](#cicd-통합)
- [테스트 결과 분석](#테스트-결과-분석)

---

## 🔧 테스트 환경 설정

### 필수 요구사항

```bash
# Java 17
java -version

# Docker & Docker Compose
docker --version
docker-compose --version

# K6 (성능 테스트용)
# Windows (Chocolatey)
choco install k6

# Windows (winget)
winget install k6 --source winget

# macOS
brew install k6

# Linux
sudo apt-get install k6
```

### 인프라 시작

```powershell
# 모든 인프라 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 서비스 준비 대기 (약 30초)
Start-Sleep -Seconds 30
```

---

## 🧪 Unit Tests

### 실행 방법

```powershell
# 모든 Unit 테스트 실행
.\gradlew.bat test

# 특정 모듈만 테스트
.\gradlew.bat :heimdall:test

# 특정 테스트 클래스만 실행
.\gradlew.bat test --tests HealthControllerTest

# 테스트 + 커버리지 리포트
.\gradlew.bat test jacocoTestReport
```

### 커버리지 리포트 확인

```powershell
# HTML 리포트 열기
start heimdall\build\reports\jacoco\test\html\index.html

# 커버리지 목표: 80% 이상
```

### Unit Test 작성 가이드

```java
@WebMvcTest(YourController.class)
@DisplayName("YourController Unit Tests")
class YourControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    @DisplayName("테스트 설명")
    void testMethod() throws Exception {
        mockMvc.perform(get("/api/endpoint"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.field").value("expected"));
    }
}
```

---

## 🔗 Integration Tests

### Kafka 통합 테스트

```java
@SpringBootTest
@EmbeddedKafka
@DisplayName("Kafka Integration Tests")
class KafkaIntegrationTest {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Test
    void shouldSendAndReceiveMessage() {
        // 테스트 코드
    }
}
```

### Redis 통합 테스트

```java
@SpringBootTest
@TestPropertySource(properties = {
    "spring.redis.host=localhost",
    "spring.redis.port=6379"
})
class RedisIntegrationTest {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    @Test
    void shouldStoreAndRetrieveData() {
        // 테스트 코드
    }
}
```

### 실행 방법

```powershell
# 통합 테스트 실행 (인프라 필요)
.\gradlew.bat integrationTest

# 또는 특정 프로파일로
.\gradlew.bat test -Dspring.profiles.active=test
```

---

## ⚡ Performance Tests (K6)

### 기본 성능 테스트

```powershell
# 스트레스 테스트 실행
k6 run heimdall\src\test\k6\stress-test.js

# 더 많은 가상 사용자로 테스트
k6 run --vus 200 --duration 5m heimdall\src\test\k6\stress-test.js

# 특정 시나리오만 테스트
k6 run --vus 50 --duration 2m heimdall\src\test\k6\stress-test.js
```

### 테스트 시나리오

#### 1. 워밍업 테스트 (부하 확인)

```powershell
k6 run --vus 10 --duration 30s heimdall\src\test\k6\stress-test.js
```

**목적**: 시스템이 정상적으로 응답하는지 확인

**기대 결과**:
- ✅ 에러율 < 5%
- ✅ 평균 응답시간 < 500ms
- ✅ P95 응답시간 < 1000ms

#### 2. 정상 부하 테스트

```powershell
k6 run --vus 50 --duration 5m heimdall\src\test\k6\stress-test.js
```

**목적**: 일반적인 운영 환경 시뮬레이션

**기대 결과**:
- ✅ 에러율 < 10%
- ✅ 평균 응답시간 < 800ms
- ✅ P95 응답시간 < 2000ms

#### 3. 스파이크 테스트 (급격한 부하 증가)

```powershell
k6 run --vus 200 --duration 3m heimdall\src\test\k6\stress-test.js
```

**목적**: 갑작스러운 트래픽 증가 대응 확인

**기대 결과**:
- ✅ 시스템 다운 없음
- ✅ 에러율 < 20%
- ✅ Circuit Breaker 정상 작동

#### 4. 장기 부하 테스트 (Endurance)

```powershell
k6 run --vus 30 --duration 30m heimdall\src\test\k6\stress-test.js
```

**목적**: 메모리 누수, 리소스 고갈 확인

**기대 결과**:
- ✅ 메모리 사용량 안정적
- ✅ 응답시간 일정 유지
- ✅ 리소스 정리 정상

---

## 🔥 Stress Tests (Extreme Load)

### 시스템 한계 테스트

#### 최대 동시 사용자 테스트

```powershell
# 점진적 증가
k6 run --vus 500 --duration 10m heimdall\src\test\k6\stress-test.js
```

#### CPU 집약 작업 스트레스

```powershell
# CPU 부하 집중 테스트
$iterations = 1..100
foreach ($i in $iterations) {
    Invoke-RestMethod -Uri "http://localhost:8080/api/v1/stress/cpu?iterations=100" -Method Get
}
```

#### 메모리 스트레스 테스트

```powershell
# 메모리 부하 집중 테스트
$iterations = 1..100
foreach ($i in $iterations) {
    Invoke-RestMethod -Uri "http://localhost:8080/api/v1/stress/memory?arraySize=1000" -Method Get
}
```

### 복합 스트레스 시나리오

```powershell
# 동시에 여러 스트레스 테스트 실행
Start-Job -ScriptBlock { k6 run --vus 100 heimdall\src\test\k6\stress-test.js }
Start-Job -ScriptBlock { 
    1..50 | ForEach-Object { 
        Invoke-RestMethod -Uri "http://localhost:8080/api/v1/stress/cpu?iterations=100" 
    }
}
Start-Job -ScriptBlock { 
    1..50 | ForEach-Object { 
        Invoke-RestMethod -Uri "http://localhost:8080/api/v1/stress/memory?arraySize=800" 
    }
}

# Job 상태 확인
Get-Job

# 결과 확인
Get-Job | Receive-Job
```

---

## 📊 모니터링 & 관찰

### 실시간 모니터링

#### Prometheus 메트릭 확인

```
http://localhost:9090
```

**주요 메트릭**:
```promql
# HTTP 요청률
rate(http_server_requests_seconds_count[1m])

# 평균 응답시간
rate(http_server_requests_seconds_sum[1m]) / rate(http_server_requests_seconds_count[1m])

# JVM 메모리 사용량
jvm_memory_used_bytes

# CPU 사용률
process_cpu_usage
```

#### Grafana 대시보드

```
http://localhost:3000
username: admin
password: admin
```

**대시보드 생성**:
1. Configuration → Data Sources → Add Prometheus
2. Dashboards → Import → Spring Boot Statistics (ID: 6756)

### 부하 테스트 중 체크리스트

- [ ] CPU 사용률 < 80%
- [ ] 메모리 사용량 안정적
- [ ] 응답시간 임계값 이내
- [ ] 에러율 허용 범위 내
- [ ] Circuit Breaker 작동 확인
- [ ] 로그에 심각한 에러 없음

---

## 📈 테스트 결과 분석

### K6 결과 해석

```
✓ http_req_duration..............: avg=245ms min=23ms max=3.2s  p(95)=987ms
✓ http_req_failed................: 8.45%
✓ iterations.....................: 15234
✓ vus............................: 100
```

**해석**:
- **avg=245ms**: 평균 응답시간 245ms (✅ 양호)
- **p(95)=987ms**: 95%의 요청이 987ms 이내 (✅ 목표 달성)
- **http_req_failed=8.45%**: 실패율 8.45% (✅ 허용 범위)
- **vus=100**: 동시 사용자 100명 처리 (✅ 목표 달성)

### 성능 기준

| 메트릭 | 우수 | 양호 | 개선 필요 |
|--------|------|------|----------|
| 평균 응답시간 | < 200ms | < 500ms | > 500ms |
| P95 응답시간 | < 500ms | < 1000ms | > 1000ms |
| P99 응답시간 | < 1000ms | < 2000ms | > 2000ms |
| 에러율 | < 0.1% | < 1% | > 1% |
| 처리량 (RPS) | > 1000 | > 500 | < 500 |

---

## 🤖 CI/CD 통합

### GitHub Actions에서 자동 테스트

`.github/workflows/ci-cd.yml`에 이미 설정되어 있습니다:

```yaml
- name: Run tests
  run: ./gradlew test

- name: Generate test report
  uses: dorny/test-reporter@v1
```

### 로컬에서 CI와 동일하게 테스트

```powershell
# 전체 CI 파이프라인 시뮬레이션
.\gradlew.bat clean build test jacocoTestReport

# 성능 테스트 추가
k6 run --vus 50 --duration 2m heimdall\src\test\k6\stress-test.js
```

---

## 📝 테스트 실행 체크리스트

### 개발 중 (Daily)

```powershell
# 1. Unit 테스트
.\gradlew.bat test

# 2. 빠른 통합 확인
docker-compose up -d
Start-Sleep -Seconds 30
Invoke-RestMethod http://localhost:8080/api/v1/health
```

### PR 전 (Before Merge)

```powershell
# 1. 전체 빌드 + 테스트
.\gradlew.bat clean build

# 2. 인프라 테스트
docker-compose up -d
Start-Sleep -Seconds 30

# 3. 기본 성능 테스트
k6 run --vus 20 --duration 1m heimdall\src\test\k6\stress-test.js

# 4. 정리
docker-compose down
```

### 배포 전 (Before Production)

```powershell
# 1. 전체 테스트 스위트
.\gradlew.bat clean build test integrationTest

# 2. 성능 테스트
docker-compose up -d
Start-Sleep -Seconds 30
k6 run --vus 100 --duration 5m heimdall\src\test\k6\stress-test.js

# 3. 스트레스 테스트
k6 run --vus 200 --duration 3m heimdall\src\test\k6\stress-test.js

# 4. 장기 부하 테스트
k6 run --vus 50 --duration 30m heimdall\src\test\k6\stress-test.js

# 5. 결과 분석 및 리포트
```

---

## 🚨 트러블슈팅

### 테스트 실패 시

#### "Connection refused" 에러

```powershell
# 인프라가 실행 중인지 확인
docker-compose ps

# 재시작
docker-compose restart

# 포트 확인
netstat -ano | findstr :8080
```

#### 메모리 부족 에러

```powershell
# Docker 메모리 증가 (Docker Desktop Settings)
# Gradle 메모리 증가
$env:GRADLE_OPTS="-Xmx2048m"
```

#### 테스트 타임아웃

```groovy
// build.gradle에 추가
test {
    testLogging {
        events "passed", "skipped", "failed"
    }
    maxHeapSize = "2g"
}
```

---

## 💡 Best Practices

### 1. 테스트 격리
- 각 테스트는 독립적으로 실행 가능해야 함
- 테스트 데이터 정리 필수
- 공유 리소스 최소화

### 2. 테스트 속도
- Unit 테스트는 빠르게 (< 1초)
- 통합 테스트는 필요시에만
- 성능 테스트는 주기적으로

### 3. 테스트 커버리지
- 핵심 비즈니스 로직: 90%+
- API 엔드포인트: 80%+
- 유틸리티 클래스: 70%+

### 4. 성능 테스트
- 프로덕션과 유사한 환경에서
- 다양한 부하 패턴 테스트
- 병목 지점 식별 및 개선

---

## 📚 참고 자료

- [K6 Documentation](https://k6.io/docs/)
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [Spring Boot Testing](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing)
- [Gatling Documentation](https://gatling.io/docs/gatling/)

---

**마지막 업데이트**: 2025년 11월
**버전**: 1.0.0
**상태**: Production Ready ✅
