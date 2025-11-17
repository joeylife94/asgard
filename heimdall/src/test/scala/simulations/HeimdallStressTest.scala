package simulations

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

/**
 * Heimdall API Gateway Stress Test Simulation
 * 
 * 테스트 시나리오:
 * 1. 기본 헬스 체크 (낮은 부하)
 * 2. Echo API 테스트 (중간 부하)
 * 3. CPU/메모리 스트레스 테스트 (높은 부하)
 * 4. 랜덤 에러 처리 테스트 (Circuit Breaker)
 */
class HeimdallStressTest extends Simulation {

  // HTTP 설정
  val httpProtocol = http
    .baseUrl("http://localhost:8080")
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")
    .userAgentHeader("Gatling-StressTest/1.0")

  // 시나리오 1: 헬스 체크 (가벼운 부하)
  val healthCheckScenario = scenario("Health Check")
    .exec(
      http("Health Check")
        .get("/api/v1/health")
        .check(status.is(200))
        .check(jsonPath("$.status").is("UP"))
    )

  // 시나리오 2: Echo API (중간 부하)
  val echoScenario = scenario("Echo API")
    .exec(
      http("Echo Request")
        .post("/api/v1/echo")
        .body(StringBody("""{"message":"stress test","iteration":${iteration}}"""))
        .check(status.is(200))
        .check(jsonPath("$.echo.message").is("stress test"))
    )

  // 시나리오 3: CPU 스트레스 (높은 부하)
  val cpuStressScenario = scenario("CPU Stress")
    .exec(
      http("CPU Intensive Task")
        .get("/api/v1/stress/cpu?iterations=50")
        .check(status.is(200))
        .check(jsonPath("$.status").is("completed"))
    )

  // 시나리오 4: 메모리 스트레스
  val memoryStressScenario = scenario("Memory Stress")
    .exec(
      http("Memory Intensive Task")
        .get("/api/v1/stress/memory?arraySize=500")
        .check(status.is(200))
        .check(jsonPath("$.status").is("completed"))
    )

  // 시나리오 5: 지연 테스트 (타임아웃)
  val delayScenario = scenario("Delay Test")
    .exec(
      http("Delayed Response")
        .get("/api/v1/delay?milliseconds=500")
        .check(status.is(200))
    )

  // 시나리오 6: 랜덤 에러 (Circuit Breaker 테스트)
  val randomErrorScenario = scenario("Random Error Test")
    .exec(
      http("Random Error Endpoint")
        .get("/api/v1/random-error?errorRate=30")
        .check(status.in(200, 500)) // 성공 또는 에러 둘 다 허용
    )

  // 부하 테스트 설정
  setUp(
    // 1단계: 워밍업 (10초)
    healthCheckScenario.inject(
      rampUsers(10) during (10 seconds)
    ).protocols(httpProtocol),

    // 2단계: 정상 부하 (30초)
    echoScenario.inject(
      constantUsersPerSec(20) during (30 seconds)
    ).protocols(httpProtocol),

    // 3단계: 스파이크 테스트 (20초)
    cpuStressScenario.inject(
      rampUsers(50) during (10 seconds),
      constantUsersPerSec(10) during (10 seconds)
    ).protocols(httpProtocol),

    // 4단계: 메모리 부하 (20초)
    memoryStressScenario.inject(
      rampUsers(30) during (20 seconds)
    ).protocols(httpProtocol),

    // 5단계: 지연 테스트 (15초)
    delayScenario.inject(
      constantUsersPerSec(15) during (15 seconds)
    ).protocols(httpProtocol),

    // 6단계: 에러 핸들링 테스트 (20초)
    randomErrorScenario.inject(
      rampUsers(40) during (20 seconds)
    ).protocols(httpProtocol)
  ).assertions(
    // 전체 성공률 85% 이상
    global.successfulRequests.percent.gte(85),
    // 95% 응답시간 3초 이하
    global.responseTime.percentile3.lte(3000),
    // 평균 응답시간 1초 이하
    global.responseTime.mean.lte(1000)
  )
}
