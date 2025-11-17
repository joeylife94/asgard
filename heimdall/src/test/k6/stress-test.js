import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// 커스텀 메트릭
const errorRate = new Rate('errors');
const cpuStressDuration = new Trend('cpu_stress_duration');
const memoryStressDuration = new Trend('memory_stress_duration');
const requestCounter = new Counter('requests');

// 테스트 설정
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // 워밍업: 10명까지 증가
    { duration: '1m', target: 50 },    // 부하 증가: 50명
    { duration: '2m', target: 100 },   // 스파이크: 100명
    { duration: '1m', target: 50 },    // 감소: 50명
    { duration: '30s', target: 0 },    // 쿨다운: 0명
  ],
  thresholds: {
    'http_req_duration': ['p(95)<3000'],  // 95% 요청이 3초 이내
    'http_req_failed': ['rate<0.15'],     // 실패율 15% 미만
    'errors': ['rate<0.20'],               // 에러율 20% 미만
  },
};

const BASE_URL = 'http://localhost:8080/api/v1';

export default function () {
  requestCounter.add(1);
  
  // 1. 헬스 체크 (20%)
  if (Math.random() < 0.2) {
    const res = http.get(`${BASE_URL}/health`);
    check(res, {
      'health check status is 200': (r) => r.status === 200,
      'health check has UP status': (r) => JSON.parse(r.body).status === 'UP',
    }) || errorRate.add(1);
  }
  
  // 2. Echo API (30%)
  else if (Math.random() < 0.5) {
    const payload = JSON.stringify({
      message: 'k6 stress test',
      timestamp: Date.now(),
      vu: __VU,
      iteration: __ITER,
    });
    
    const res = http.post(`${BASE_URL}/echo`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });
    
    check(res, {
      'echo status is 200': (r) => r.status === 200,
      'echo returns payload': (r) => JSON.parse(r.body).echo.message === 'k6 stress test',
    }) || errorRate.add(1);
  }
  
  // 3. CPU 스트레스 (20%)
  else if (Math.random() < 0.7) {
    const iterations = Math.floor(Math.random() * 50) + 10;
    const res = http.get(`${BASE_URL}/stress/cpu?iterations=${iterations}`);
    
    if (res.status === 200) {
      const body = JSON.parse(res.body);
      cpuStressDuration.add(body.duration_ms);
    }
    
    check(res, {
      'cpu stress status is 200': (r) => r.status === 200,
      'cpu stress completed': (r) => JSON.parse(r.body).status === 'completed',
    }) || errorRate.add(1);
  }
  
  // 4. 메모리 스트레스 (15%)
  else if (Math.random() < 0.85) {
    const arraySize = Math.floor(Math.random() * 300) + 100;
    const res = http.get(`${BASE_URL}/stress/memory?arraySize=${arraySize}`);
    
    if (res.status === 200) {
      const body = JSON.parse(res.body);
      memoryStressDuration.add(body.duration_ms);
    }
    
    check(res, {
      'memory stress status is 200': (r) => r.status === 200,
      'memory stress completed': (r) => JSON.parse(r.body).status === 'completed',
    }) || errorRate.add(1);
  }
  
  // 5. 랜덤 에러 테스트 (15%)
  else {
    const res = http.get(`${BASE_URL}/random-error?errorRate=30`);
    check(res, {
      'random error returns status': (r) => r.status === 200 || r.status === 500,
    });
    
    if (res.status !== 200) {
      errorRate.add(1);
    }
  }
  
  // 요청 간 간격
  sleep(Math.random() * 2 + 0.5); // 0.5~2.5초 랜덤 대기
}

// 테스트 종료 후 요약
export function handleSummary(data) {
  return {
    'stress-test-summary.json': JSON.stringify(data, null, 2),
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, opts) {
  return `
===========================================
  Heimdall Stress Test Summary
===========================================

Total Requests: ${data.metrics.requests.values.count}
Total Errors: ${data.metrics.errors.values.count}
Error Rate: ${(data.metrics.errors.values.rate * 100).toFixed(2)}%

HTTP Request Duration:
  - avg: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
  - min: ${data.metrics.http_req_duration.values.min.toFixed(2)}ms
  - max: ${data.metrics.http_req_duration.values.max.toFixed(2)}ms
  - p(95): ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms

CPU Stress Duration:
  - avg: ${data.metrics.cpu_stress_duration?.values.avg?.toFixed(2) || 'N/A'}ms

Memory Stress Duration:
  - avg: ${data.metrics.memory_stress_duration?.values.avg?.toFixed(2) || 'N/A'}ms

Virtual Users:
  - max: ${data.metrics.vus_max.values.max}

Test Duration: ${(data.state.testRunDurationMs / 1000).toFixed(2)}s
===========================================
`;
}
