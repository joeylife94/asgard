"""Prometheus 메트릭"""

from prometheus_client import Counter, Histogram, Gauge, Info


class PrometheusMetrics:
    """Prometheus 메트릭 관리"""
    
    def __init__(self):
        # 분석 카운터
        self.analysis_count = Counter(
            'bifrost_analysis_total',
            'Total number of log analyses',
            ['source', 'status']
        )
        
        # 분석 소요 시간
        self.analysis_duration = Histogram(
            'bifrost_analysis_duration_seconds',
            'Log analysis duration in seconds',
            ['source'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
        )
        
        # 캐시 히트
        self.cache_hits = Counter(
            'bifrost_cache_hits_total',
            'Total number of cache hits'
        )
        
        # 에러 카운터
        self.error_count = Counter(
            'bifrost_errors_total',
            'Total number of errors',
            ['source', 'error_type']
        )
        
        # 현재 진행 중인 분석
        self.in_progress = Gauge(
            'bifrost_analyses_in_progress',
            'Number of analyses currently in progress',
            ['source']
        )
        
        # 로그 크기
        self.log_size = Histogram(
            'bifrost_log_size_bytes',
            'Size of analyzed logs in bytes',
            buckets=[1024, 10240, 102400, 1024000, 10240000]
        )
        
        # 응답 크기
        self.response_size = Histogram(
            'bifrost_response_size_bytes',
            'Size of analysis responses in bytes',
            buckets=[1024, 10240, 102400, 1024000]
        )
        
        # 시스템 정보
        self.info = Info('bifrost_info', 'Bifrost system information')
        self.info.info({
            'version': '0.2.0',
            'component': 'api',
        })

        # Interview Edition: /ask metrics
        self.ask_requests_total = Counter(
            'bifrost_ask_requests_total',
            'Total number of /ask requests',
            ['lane', 'outcome']
        )
        self.ask_latency_ms = Histogram(
            'bifrost_ask_latency_ms',
            'Latency for /ask in milliseconds',
            ['lane'],
            buckets=[50, 100, 250, 500, 1000, 2000, 5000, 10000, 20000]
        )
    
    def increment_analysis_count(self, source: str, status: str = "success"):
        """분석 카운트 증가"""
        self.analysis_count.labels(source=source, status=status).inc()
    
    def observe_analysis_duration(self, duration: float, source: str):
        """분석 소요 시간 기록"""
        self.analysis_duration.labels(source=source).observe(duration)
    
    def increment_cache_hits(self):
        """캐시 히트 증가"""
        self.cache_hits.inc()
    
    def increment_error_count(self, source: str, error_type: str = "unknown"):
        """에러 카운트 증가"""
        self.error_count.labels(source=source, error_type=error_type).inc()
    
    def set_in_progress(self, source: str, count: int):
        """진행 중인 분석 설정"""
        self.in_progress.labels(source=source).set(count)
    
    def observe_log_size(self, size: int):
        """로그 크기 기록"""
        self.log_size.observe(size)
    
    def observe_response_size(self, size: int):
        """응답 크기 기록"""
        self.response_size.observe(size)

    # ==================== Interview Edition: /ask ====================

    def increment_ask_requests(self, lane: str, outcome: str):
        self.ask_requests_total.labels(lane=lane, outcome=outcome).inc()

    def observe_ask_latency_ms(self, lane: str, latency_ms: int):
        self.ask_latency_ms.labels(lane=lane).observe(latency_ms)
