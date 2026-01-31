"""FastAPI REST API 서버"""

import time
import os
import uuid
from typing import Optional, List
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, WebSocket, WebSocketDisconnect, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from bifrost.ollama import OllamaClient
from bifrost.bedrock import BedrockClient, is_bedrock_available
from bifrost.database import get_database, Database
from bifrost.preprocessor import LogPreprocessor
from bifrost.metrics import PrometheusMetrics
from bifrost.logger import logger
from bifrost.ratelimit import RateLimiter
from bifrost.exceptions import BifrostException, RateLimitError, handle_exception
from bifrost.validators import InputValidator
from bifrost.filters import LogFilter, SeverityLevel
from bifrost.export import DataExporter
from bifrost.slack import SlackNotifier
from bifrost.router import get_router  # Privacy Router 추가
from bifrost.on_device.rag.ingest_service import RunbookIngestService
from bifrost.orchestrator.orchestrator_service import OrchestratorService
from bifrost.contracts.ask import AnswerRequest, AnswerResponse


# Kafka 통합 관련 전역 변수
kafka_consumer_manager = None
kafka_producer_manager = None


async def _startup() -> None:
    """서버 시작 시"""
    global kafka_consumer_manager, kafka_producer_manager

    # Database 초기화
    db = get_database()
    db.init_db()
    print("🌈 Bifrost API Server started!")

    # Kafka 통합 활성화 (설정 기반)
    from bifrost.config import Config
    config = Config()

    kafka_enabled = config.get("kafka.enabled", False)
    heimdall_enabled = config.get("heimdall.enabled", False)

    if kafka_enabled and heimdall_enabled:
        try:
            from bifrost.kafka_consumer import KafkaConsumerManager
            from bifrost.kafka_producer import KafkaProducerManager
            from bifrost.heimdall_integration import HeimdallIntegrationService

            # Producer 초기화
            kafka_config = config.get("kafka", {})
            kafka_producer_manager = KafkaProducerManager(kafka_config)
            await kafka_producer_manager.start()

            # Integration Service 초기화
            integration_service = HeimdallIntegrationService(
                config=config.data,
                producer_manager=kafka_producer_manager
            )

            # Consumer 초기화 및 시작
            kafka_consumer_manager = KafkaConsumerManager(kafka_config)
            await kafka_consumer_manager.start(
                integration_service.process_analysis_request
            )

            logger.info(
                "Kafka integration enabled - Heimdall 연동 시작됨",
                bootstrap_servers=kafka_config.get("bootstrap_servers")
            )
            print("🔗 Kafka integration with Heimdall enabled!")

        except Exception as e:
            logger.error(f"Failed to initialize Kafka integration: {e}", exc_info=True)
            print(f"⚠️  Kafka integration failed: {e}")
    else:
        print("ℹ️  Kafka integration disabled (CLI mode)")


async def _shutdown() -> None:
    """서버 종료 시"""
    global kafka_consumer_manager, kafka_producer_manager

    # Kafka 리소스 정리
    if kafka_consumer_manager:
        await kafka_consumer_manager.stop()
        print("🛑 Kafka consumer stopped")

    if kafka_producer_manager:
        await kafka_producer_manager.stop()
        print("🛑 Kafka producer stopped")

    print("👋 Bifrost API Server shutting down...")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await _startup()
    try:
        yield
    finally:
        await _shutdown()


# FastAPI 앱
app = FastAPI(
    title="Bifrost API",
    description="🌈 The Rainbow Bridge for MLOps - AI-powered log analysis",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS 설정
cors_origins_env = os.getenv("BIFROST_CORS_ORIGINS")
if cors_origins_env is None or not cors_origins_env.strip():
    cors_origins = ["http://localhost:5173", "http://localhost:3000"]
else:
    cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

if "*" in cors_origins and os.getenv("BIFROST_ALLOW_WILDCARD_CORS", "false").lower() != "true":
    raise RuntimeError(
        "Wildcard CORS origins are disabled. Set BIFROST_CORS_ORIGINS to an explicit origin list, or set BIFROST_ALLOW_WILDCARD_CORS=true (not recommended)."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus 메트릭
metrics = PrometheusMetrics()

# Rate Limiter 초기화
rate_limiter = RateLimiter(requests_per_hour=100)

# 전역 예외 핸들러
@app.exception_handler(BifrostException)
async def bifrost_exception_handler(request: Request, exc: BifrostException):
    logger.error(
        f"Bifrost error: {exc.message}",
        error_code=exc.code,
        path=str(request.url.path) if hasattr(request.url, 'path') else str(request.url)
    )
    return JSONResponse(
        status_code=400,
        content=handle_exception(exc)
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled error: {str(exc)}",
        path=str(request.url.path) if hasattr(request.url, 'path') else str(request.url),
        exception_type=type(exc).__name__
    )
    return JSONResponse(
        status_code=500,
        content=handle_exception(exc)
    )


# ==================== Pydantic Models ====================

class AnalyzeRequest(BaseModel):
    """분석 요청"""
    log_content: str = Field(..., description="로그 내용")
    source: Optional[str] = Field(None, description="분석 소스 (local/cloud) - None이면 자동 라우팅")
    model: Optional[str] = Field(None, description="모델명")
    service_name: Optional[str] = Field(None, description="서비스 이름")
    environment: Optional[str] = Field(None, description="환경 (prod/staging)")
    tags: Optional[List[str]] = Field(default_factory=list, description="태그")
    stream: bool = Field(False, description="스트리밍 모드")


class AnalyzeResponse(BaseModel):
    """분석 응답"""
    id: int
    response: str
    duration_seconds: float
    model: str
    cached: bool = False


class HistoryQuery(BaseModel):
    """히스토리 조회"""
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)
    service_name: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None


class MetricsResponse(BaseModel):
    """메트릭 응답"""
    total_analyses: int
    avg_duration_seconds: float
    model_stats: List[dict]


class FilterSeverityRequest(BaseModel):
    """심각도 필터링 요청"""
    log_content: str = Field(..., description="로그 내용")
    min_level: SeverityLevel = Field(SeverityLevel.INFO, description="최소 심각도")


class FilterErrorsRequest(BaseModel):
    """에러 필터링 요청"""
    log_content: str = Field(..., description="로그 내용")


class FilterKeywordsRequest(BaseModel):
    """키워드 필터링 요청"""
    log_content: str = Field(..., description="로그 내용")
    keywords: List[str] = Field(..., description="키워드 목록")
    case_sensitive: bool = Field(False, description="대소문자 구분")


class SlackNotificationRequest(BaseModel):
    """Slack 알림 요청"""
    webhook_url: str = Field(..., description="Slack Webhook URL")
    result: dict = Field(..., description="분석 결과")
    service_name: Optional[str] = Field(None, description="서비스 이름")


class CreatePromptRequest(BaseModel):
    """프롬프트 생성 요청"""
    name: str = Field(..., description="프롬프트 이름")
    content: str = Field(..., description="프롬프트 내용")
    description: Optional[str] = Field(None, description="프롬프트 설명")
    tags: Optional[List[str]] = Field(None, description="태그 목록")


class CompareMLflowRunsRequest(BaseModel):
    """MLflow Run 비교 요청"""
    run_ids: List[str] = Field(..., description="비교할 Run ID 리스트")
    metric_names: Optional[List[str]] = Field(None, description="메트릭 이름 목록")


class RunbookIngestRequest(BaseModel):
    source: str = Field(..., min_length=1, description="문서 소스 식별자 (예: service/runbook.md)")
    tags: Optional[List[str]] = Field(default=None, description="선택 태그")
    text: str = Field(..., min_length=1, description="Plain text or markdown")


class RunbookIngestResponse(BaseModel):
    chunks_ingested: int


# ==================== Dependencies ====================

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """API 키 검증

    - 개발/로컬: 키 없이도 통과 가능 (config.security.require_api_key=false)
    - 운영/오픈: 키 필수 (BIFROST_REQUIRE_API_KEY=true)
    """
    from bifrost.config import Config
    require_api_key = Config().get("security.require_api_key", False)

    if not x_api_key:
        if require_api_key:
            raise HTTPException(status_code=401, detail="API key required")
        return None

    db = get_database()
    if not db.validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# ==================== Routes ====================

@app.get("/")
async def root():
    """헬스 체크"""
    return {
        "name": "Bifrost API",
        "version": "0.2.0",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health():
    """상세 헬스 체크"""
    db = get_database()
    
    ollama_healthy = False
    try:
        client = OllamaClient()
        ollama_healthy = client.health_check()
    except:
        pass
    
    # Kafka 상태 확인
    kafka_status = "disabled"
    if kafka_consumer_manager or kafka_producer_manager:
        kafka_status = "enabled"
    
    # Circuit Breaker 상태 확인
    from bifrost.resilience import circuit_breaker_registry
    cb_stats = circuit_breaker_registry.get_all_stats()
    
    return {
        "status": "healthy",
        "components": {
            "database": "ok",
            "ollama": "ok" if ollama_healthy else "unavailable",
            "bedrock": "ok" if is_bedrock_available() else "not_configured",
            "kafka": kafka_status,
            "heimdall_integration": "enabled" if kafka_consumer_manager else "disabled",
        },
        "circuit_breakers": cb_stats,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/heimdall/status")
async def heimdall_integration_status(_: bool = Depends(verify_api_key)):
    """Heimdall 연동 상태 확인"""
    from bifrost.config import Config
    config = Config()
    
    kafka_enabled = config.get("kafka.enabled", False)
    heimdall_enabled = config.get("heimdall.enabled", False)
    
    status = {
        "integration_enabled": kafka_enabled and heimdall_enabled,
        "kafka": {
            "enabled": kafka_enabled,
            "bootstrap_servers": config.get("kafka.bootstrap_servers"),
            "consumer_running": kafka_consumer_manager is not None,
            "producer_running": kafka_producer_manager is not None,
        },
        "heimdall": {
            "enabled": heimdall_enabled,
            "callback_topic": config.get("heimdall.callback_topic"),
            "ai_source": config.get("heimdall.ai_source"),
        },
        "topics": config.get("kafka.topics", {}),
    }
    
    return status


@app.post("/analyze", response_model=AnalyzeResponse, dependencies=[Depends(verify_api_key)])
async def analyze_log(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    로그 분석 API - Two-Track AI Strategy
    
    자동 라우팅:
    - Track A (Local): HIGH/MEDIUM 민감도 → Ollama (GDPR-compliant)
    - Track B (Cloud): LOW 민감도 → AWS Bedrock (cost-effective)
    """
    start_time = time.time()
    db = get_database()
    from bifrost.config import Config
    cfg = Config()
    store_raw_log = cfg.get("storage.store_raw_log", True)
    store_raw_response = cfg.get("storage.store_raw_response", True)
    redacted_placeholder = cfg.get("storage.redacted_placeholder", "[REDACTED]")
    
    # ===== Privacy Router: 자동 라우팅 =====
    privacy_router = get_router()
    routing_decision = privacy_router.route(request.log_content)
    
    # 사용자가 명시한 source가 있으면 우선, 없으면 자동 라우팅
    if not request.source:
        request.source = routing_decision["track"]  # "local" or "cloud"
        logger.info(f"Auto-routed to {request.source}: {routing_decision['reason']}")
    
    # 캐시 확인 (중복 분석 방지)
    import hashlib
    log_hash = hashlib.sha256(request.log_content.encode()).hexdigest()
    log_size_bytes = len(request.log_content.encode())
    log_lines = len(request.log_content.split("\n"))
    from starlette.concurrency import run_in_threadpool
    from functools import partial

    cached_results = await run_in_threadpool(db.get_duplicate_analyses, log_hash, 24)
    
    if cached_results and not request.stream:
        cached = cached_results[0]
        metrics.increment_cache_hits()
        return AnalyzeResponse(
            id=cached["id"],
            response=cached["response"],
            duration_seconds=cached["duration_seconds"],
            model=cached["model"],
            cached=True,
        )
    
    # 전처리
    preprocessor = LogPreprocessor()
    log_content = preprocessor.process(request.log_content)
    
    # 프롬프트
    from bifrost.main import MASTER_PROMPT
    prompt = MASTER_PROMPT.format(log_content=log_content)
    
    try:
        # 분석 실행
        if request.source == "local":
            client = OllamaClient(model=request.model or "llama3.1:8b")  # 업데이트: Llama 3.1 8B
            result = await run_in_threadpool(partial(client.analyze, prompt, stream=False))  # API는 스트리밍 미지원
        elif request.source == "cloud":
            if not is_bedrock_available():
                raise HTTPException(status_code=400, detail="Bedrock not available (boto3 not installed)")
            client = BedrockClient(model_id=request.model or "anthropic.claude-3-sonnet-20240229-v1:0")
            result = await run_in_threadpool(partial(client.analyze, prompt))
        else:
            raise HTTPException(status_code=400, detail="Invalid source (local or cloud)")
        
        duration = time.time() - start_time

        stored_log_content = request.log_content if store_raw_log else redacted_placeholder
        stored_response = result["response"] if store_raw_response else redacted_placeholder
        response_size_bytes = len(result["response"].encode())
        
        # DB 저장 (백그라운드) - Privacy Router 메타데이터 추가
        analysis_id = await run_in_threadpool(
            partial(
                db.save_analysis,
                source=request.source,
                model=result["metadata"]["model"],
                log_content=stored_log_content,
                response=stored_response,
                duration=duration,
                log_hash=log_hash,
                log_size_bytes=log_size_bytes,
                log_lines=log_lines,
                response_size_bytes=response_size_bytes,
                tags=request.tags,
                service_name=request.service_name,
                environment=request.environment,
                tokens_used=result["metadata"].get("usage", {}).get("total_tokens"),
                status="completed",
            )
        )
        
        # 메트릭 업데이트
        metrics.increment_analysis_count(request.source)
        metrics.observe_analysis_duration(duration, request.source)
        
        # 응답에 Privacy Router 메타데이터 포함
        response_data = AnalyzeResponse(
            id=analysis_id,
            response=result["response"],
            duration_seconds=round(duration, 2),
            model=result["metadata"]["model"],
            cached=False,
        )
        
        # Privacy Router 정보를 응답에 추가 (dict로 변환 후)
        response_dict = response_data.dict()
        response_dict["routing"] = routing_decision
        
        return response_dict
    
    except Exception as e:
        # 에러 저장
        stored_log_content = request.log_content if store_raw_log else redacted_placeholder
        await run_in_threadpool(
            partial(
                db.save_analysis,
                source=request.source,
                model=request.model or "unknown",
                log_content=stored_log_content,
                response="",
                duration=time.time() - start_time,
                log_hash=log_hash,
                log_size_bytes=log_size_bytes,
                log_lines=log_lines,
                response_size_bytes=0,
                status="failed",
                error_message=str(e),
            )
        )
        
        metrics.increment_error_count(request.source)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ==================== Compatibility (v1) ====================

@app.post("/api/v1/analyze", dependencies=[Depends(verify_api_key)])
async def analyze_log_v1(payload: dict, background_tasks: BackgroundTasks):
    """Compatibility endpoint for older clients.

    Accepts either {log_content: ...} or {log: ...}.
    """
    log_content = payload.get("log_content") or payload.get("log")
    if not log_content:
        raise HTTPException(status_code=422, detail="log_content is required")

    req = AnalyzeRequest(
        log_content=log_content,
        source=payload.get("source"),
        model=payload.get("model"),
        service_name=payload.get("service_name"),
        environment=payload.get("environment"),
        tags=payload.get("tags") or [],
        stream=bool(payload.get("stream", False)),
    )
    return await analyze_log(req, background_tasks)


@app.get("/api/v1/history", dependencies=[Depends(verify_api_key)])
async def get_history_v1(page: int = 0, size: int = 20):
    """Compatibility endpoint for older clients (pagination via query params)."""
    if page < 0 or size < 1:
        raise HTTPException(status_code=422, detail="Invalid pagination params")

    query = HistoryQuery(limit=min(size, 500), offset=page * size)
    return await get_history(query)


@app.post("/history", response_model=List[dict])
async def get_history(query: HistoryQuery, _: bool = Depends(verify_api_key)):
    """분석 히스토리 조회"""
    db = get_database()
    results = db.list_analyses(
        limit=query.limit,
        offset=query.offset,
        service_name=query.service_name,
        model=query.model,
        status=query.status,
    )
    return results


@app.get("/history/{analysis_id}", response_model=dict)
async def get_analysis_detail(analysis_id: int, _: bool = Depends(verify_api_key)):
    """특정 분석 결과 조회"""
    db = get_database()
    result = db.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics(hours: int = 24, _: bool = Depends(verify_api_key)):
    """메트릭 조회"""
    db = get_database()
    summary = db.get_metrics_summary(hours=hours)
    return MetricsResponse(**summary)


@app.get("/metrics/prometheus")
async def get_prometheus_metrics(_: Optional[str] = Depends(verify_api_key)):
    """Prometheus 메트릭 엔드포인트"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ==================== Circuit Breaker Management API ====================

@app.get("/api/v1/circuit-breakers")
async def get_circuit_breakers(_: bool = Depends(verify_api_key)):
    """
    모든 Circuit Breaker 상태 조회
    
    Returns:
        각 Circuit Breaker의 상태, 통계, 설정 정보
    """
    from bifrost.resilience import circuit_breaker_registry
    
    stats = circuit_breaker_registry.get_all_stats()
    
    return {
        "circuit_breakers": stats,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/circuit-breakers/{name}")
async def get_circuit_breaker_by_name(name: str, _: bool = Depends(verify_api_key)):
    """
    특정 Circuit Breaker 상태 조회
    
    Args:
        name: Circuit Breaker 이름 (on_device_rag, cloud_direct 등)
    """
    from bifrost.resilience import circuit_breaker_registry
    
    stats = circuit_breaker_registry.get_all_stats()
    
    if name not in stats:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit breaker '{name}' not found"
        )
    
    return {
        "name": name,
        **stats[name],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/circuit-breakers/{name}/reset")
async def reset_circuit_breaker(name: str, _: bool = Depends(verify_api_key)):
    """
    특정 Circuit Breaker 수동 리셋
    
    운영자가 Circuit이 OPEN 상태일 때 수동으로 CLOSED로 복구할 수 있습니다.
    주의: 실제 서비스가 복구되지 않은 상태에서 리셋하면 다시 OPEN될 수 있습니다.
    """
    from bifrost.resilience import circuit_breaker_registry
    
    stats = circuit_breaker_registry.get_all_stats()
    
    if name not in stats:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit breaker '{name}' not found"
        )
    
    cb = circuit_breaker_registry.get(name)
    previous_state = cb.state.value
    cb.reset()
    
    logger.info(
        "circuit_breaker_manual_reset",
        name=name,
        previous_state=previous_state,
    )
    
    return {
        "name": name,
        "previous_state": previous_state,
        "current_state": cb.state.value,
        "message": f"Circuit breaker '{name}' has been reset",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/circuit-breakers/reset-all")
async def reset_all_circuit_breakers(_: bool = Depends(verify_api_key)):
    """
    모든 Circuit Breaker 수동 리셋
    
    주의: 실제 서비스가 복구되지 않은 상태에서 리셋하면 다시 OPEN될 수 있습니다.
    """
    from bifrost.resilience import circuit_breaker_registry
    
    stats_before = circuit_breaker_registry.get_all_stats()
    circuit_breaker_registry.reset_all()
    stats_after = circuit_breaker_registry.get_all_stats()
    
    logger.info("circuit_breaker_reset_all")
    
    return {
        "message": "All circuit breakers have been reset",
        "before": stats_before,
        "after": stats_after,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ==================== End Circuit Breaker API ====================


# ==================== Feedback System API ====================

class FeedbackRequest(BaseModel):
    """Feedback submission request."""
    request_id: str = Field(..., description="Analysis request ID")
    feedback_type: str = Field(..., description="Type of feedback")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Star rating 1-5")
    comment: Optional[str] = Field(None, max_length=2000, description="User comment")
    tags: Optional[List[str]] = Field(None, description="Categorization tags")
    job_id: Optional[str] = Field(None, description="Heimdall job ID")
    session_id: Optional[str] = Field(None, description="Browser session ID")
    metadata: Optional[dict] = Field(None, description="Additional context")


class QuickFeedbackRequest(BaseModel):
    """Quick thumbs up/down feedback."""
    request_id: str = Field(..., description="Analysis request ID")
    is_positive: bool = Field(..., description="True for thumbs up, False for thumbs down")
    job_id: Optional[str] = Field(None, description="Heimdall job ID")
    session_id: Optional[str] = Field(None, description="Browser session ID")
    metadata: Optional[dict] = Field(None, description="Additional context")


@app.post("/api/v1/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    _: bool = Depends(verify_api_key),
):
    """
    Submit detailed feedback for an AI analysis response.
    
    Feedback types:
    - thumbs_up, thumbs_down: Quick reactions
    - rating: Star rating (1-5)
    - inaccurate, incomplete, irrelevant, too_slow: Issue types
    - helpful, accurate, well_formatted: Positive feedback
    """
    from bifrost.feedback import FeedbackService
    
    service = FeedbackService()
    feedback = service.submit_feedback(
        request_id=request.request_id,
        feedback_type=request.feedback_type,
        rating=request.rating,
        comment=request.comment,
        tags=request.tags,
        job_id=request.job_id,
        session_id=request.session_id,
        metadata=request.metadata,
    )
    
    return {
        "success": True,
        "feedback_id": str(feedback.id),
        "is_positive": feedback.is_positive(),
        "timestamp": feedback.created_at.isoformat(),
    }


@app.post("/api/v1/feedback/quick")
async def submit_quick_feedback(
    request: QuickFeedbackRequest,
    _: bool = Depends(verify_api_key),
):
    """
    Submit quick thumbs up/down feedback.
    
    Simplified endpoint for binary feedback collection.
    """
    from bifrost.feedback import FeedbackService
    
    service = FeedbackService()
    feedback = service.submit_quick_feedback(
        request_id=request.request_id,
        is_positive=request.is_positive,
        job_id=request.job_id,
        session_id=request.session_id,
        metadata=request.metadata,
    )
    
    return {
        "success": True,
        "feedback_id": str(feedback.id),
        "feedback_type": feedback.feedback_type.value,
        "timestamp": feedback.created_at.isoformat(),
    }


@app.get("/api/v1/feedback/stats")
async def get_feedback_stats(
    hours: int = 24,
    provider: Optional[str] = None,
    lane: Optional[str] = None,
    _: bool = Depends(verify_api_key),
):
    """
    Get aggregated feedback statistics.
    
    Args:
        hours: Time period for statistics (default: 24)
        provider: Filter by AI provider (ollama, bedrock, etc.)
        lane: Filter by routing lane (on_device_rag, cloud_direct)
    """
    from bifrost.feedback import FeedbackService
    
    service = FeedbackService()
    stats = service.get_stats(hours=hours, provider=provider, lane=lane)
    
    return stats.to_dict()


@app.get("/api/v1/feedback/satisfaction")
async def get_satisfaction_score(
    hours: int = 24,
    _: bool = Depends(verify_api_key),
):
    """
    Get overall satisfaction score with breakdown by provider/lane.
    
    Returns NPS-like score and satisfaction rates.
    """
    from bifrost.feedback import FeedbackService
    
    service = FeedbackService()
    return service.get_satisfaction_score(hours=hours)


@app.get("/api/v1/feedback/trends")
async def get_feedback_trends(
    days: int = 7,
    _: bool = Depends(verify_api_key),
):
    """
    Get daily feedback trends for the specified period.
    """
    from bifrost.feedback import FeedbackService
    
    service = FeedbackService()
    trends = service.get_trends(days=days)
    
    return trends.to_dict()


@app.get("/api/v1/feedback/recent")
async def get_recent_feedback(
    hours: int = 24,
    limit: int = 100,
    feedback_type: Optional[str] = None,
    _: bool = Depends(verify_api_key),
):
    """
    Get recent feedback entries.
    """
    from bifrost.feedback import FeedbackService
    
    service = FeedbackService()
    feedbacks = service.get_recent_feedback(
        hours=hours,
        limit=limit,
        feedback_type=feedback_type,
    )
    
    return {
        "count": len(feedbacks),
        "feedbacks": [f.to_dict() for f in feedbacks],
    }


@app.get("/api/v1/feedback/negative")
async def get_negative_feedback(
    hours: int = 24,
    limit: int = 50,
    _: bool = Depends(verify_api_key),
):
    """
    Get recent negative feedback for review and improvement.
    """
    from bifrost.feedback import FeedbackService
    
    service = FeedbackService()
    feedbacks = service.get_negative_feedback(hours=hours, limit=limit)
    
    return {
        "count": len(feedbacks),
        "feedbacks": [f.to_dict() for f in feedbacks],
    }


@app.get("/api/v1/feedback/request/{request_id}")
async def get_feedback_for_request(
    request_id: str,
    _: bool = Depends(verify_api_key),
):
    """
    Get all feedback for a specific analysis request.
    """
    from bifrost.feedback import FeedbackService
    
    service = FeedbackService()
    feedbacks = service.get_feedback_for_request(request_id)
    
    return {
        "request_id": request_id,
        "count": len(feedbacks),
        "feedbacks": [f.to_dict() for f in feedbacks],
    }


# ==================== End Feedback System API ====================


# ==================== Multi-LLM Routing API ====================

class RouteRequest(BaseModel):
    """Request for routing decision."""
    input_text: str = Field(..., description="Input text/prompt for routing decision")
    strategy: Optional[str] = Field(None, description="Routing strategy")
    required_capabilities: Optional[List[str]] = Field(None, description="Required capabilities")
    exclude_providers: Optional[List[str]] = Field(None, description="Providers to exclude")


@app.post("/api/v1/routing/decide")
async def get_routing_decision(
    request: RouteRequest,
    request_id: str = Header(None, alias="X-Request-ID"),
    _: bool = Depends(verify_api_key),
):
    """
    Get routing decision for an LLM request.
    
    Returns the best provider based on the specified strategy
    and current provider availability.
    
    Strategies:
    - cost_optimized: Minimize cost
    - latency_optimized: Minimize latency
    - quality_optimized: Best model quality
    - balanced: Balance cost/latency/quality
    - failover: Primary with fallback chain
    - round_robin: Distribute evenly
    """
    from bifrost.routing import DynamicRouter, RoutingStrategy
    
    router = DynamicRouter()
    
    strategy = None
    if request.strategy:
        try:
            strategy = RoutingStrategy(request.strategy)
        except ValueError:
            raise HTTPException(400, f"Invalid strategy: {request.strategy}")
    
    decision = router.route(
        input_text=request.input_text,
        strategy=strategy,
        required_capabilities=request.required_capabilities,
        exclude_providers=request.exclude_providers,
        request_id=request_id,
    )
    
    return decision.to_dict()


@app.get("/api/v1/routing/providers")
async def list_providers(_: bool = Depends(verify_api_key)):
    """
    List all registered LLM providers with their configurations.
    """
    from bifrost.routing import DynamicRouter
    
    router = DynamicRouter()
    providers = router.list_providers()
    
    return {
        "providers": [p.to_dict() for p in providers],
        "count": len(providers),
    }


@app.get("/api/v1/routing/providers/{name}")
async def get_provider(name: str, _: bool = Depends(verify_api_key)):
    """
    Get configuration for a specific provider.
    """
    from bifrost.routing import DynamicRouter
    
    router = DynamicRouter()
    provider = router.get_provider(name)
    
    if not provider:
        raise HTTPException(404, f"Provider '{name}' not found")
    
    return provider.to_dict()


@app.get("/api/v1/routing/health")
async def get_providers_health(_: bool = Depends(verify_api_key)):
    """
    Get health status of all providers including circuit breaker state.
    """
    from bifrost.routing import DynamicRouter
    
    router = DynamicRouter()
    health = router.get_provider_health()
    
    return {
        "providers": [h.to_dict() for h in health],
        "healthy_count": sum(1 for h in health if h.is_healthy),
        "total_count": len(health),
    }


@app.get("/api/v1/routing/metrics")
async def get_routing_metrics(_: bool = Depends(verify_api_key)):
    """
    Get routing metrics and statistics.
    """
    from bifrost.routing import DynamicRouter
    
    router = DynamicRouter()
    metrics = router.get_metrics()
    
    return metrics.to_dict()


@app.get("/api/v1/routing/cost")
async def get_routing_cost(hours: int = 24, _: bool = Depends(verify_api_key)):
    """
    Get cost summary for LLM usage.
    """
    from bifrost.routing import DynamicRouter
    
    router = DynamicRouter()
    return router.get_cost_summary(hours=hours)


@app.put("/api/v1/routing/strategy")
async def set_routing_strategy(strategy: str, _: bool = Depends(verify_api_key)):
    """
    Set the default routing strategy.
    """
    from bifrost.routing import DynamicRouter, RoutingStrategy
    
    try:
        strategy_enum = RoutingStrategy(strategy)
    except ValueError:
        raise HTTPException(400, f"Invalid strategy: {strategy}")
    
    router = DynamicRouter()
    router.set_default_strategy(strategy_enum)
    
    return {
        "success": True,
        "strategy": strategy,
        "message": f"Default routing strategy set to '{strategy}'",
    }


# ==================== End Multi-LLM Routing API ====================


# ==================== Quality Metrics API ====================

class QualityAnalyzeRequest(BaseModel):
    """Request model for quality analysis."""
    request_id: str = Field(..., description="Analysis request ID")
    job_id: Optional[str] = Field(None, description="Job ID")
    query: str = Field(..., description="Original query/prompt")
    response: str = Field(..., description="AI response to analyze")
    expected_keywords: Optional[List[str]] = Field(None, description="Expected keywords in response")
    expected_sections: Optional[List[str]] = Field(None, description="Expected sections/headings")
    provider: Optional[str] = Field(None, description="LLM provider used")
    lane: Optional[str] = Field(None, description="Inference lane (on_device/cloud)")
    model: Optional[str] = Field(None, description="Model name")
    latency_ms: Optional[int] = Field(None, description="Response latency in ms")
    token_count: Optional[int] = Field(None, description="Total tokens used")
    save: bool = Field(True, description="Whether to save the report")


@app.post("/api/v1/quality/analyze")
async def analyze_quality(request: QualityAnalyzeRequest, _: bool = Depends(verify_api_key)):
    """
    Analyze the quality of an AI response.
    
    Evaluates:
    - Relevance to query
    - Completeness of information
    - Clarity and structure
    - Conciseness
    - Confidence level
    - Token efficiency
    """
    from bifrost.quality import QualityAnalyzer, get_quality_tracker
    
    analyzer = QualityAnalyzer()
    
    report = analyzer.analyze(
        request_id=request.request_id,
        job_id=request.job_id,
        query=request.query,
        response=request.response,
        expected_keywords=request.expected_keywords,
        expected_sections=request.expected_sections,
        provider=request.provider,
        lane=request.lane,
        model=request.model,
        latency_ms=request.latency_ms,
        token_count=request.token_count,
    )
    
    if request.save:
        tracker = get_quality_tracker()
        tracker.save_report(report)
    
    return {
        "report_id": str(report.id),
        "request_id": report.request_id,
        "overall_score": report.overall_score,
        "overall_grade": report.overall_grade,
        "scores": [
            {
                "dimension": s.dimension.value,
                "score": s.score,
                "weight": s.weight,
                "details": s.details,
            }
            for s in report.scores
        ],
        "recommendations": report.recommendations,
        "metadata": report.metadata,
        "analyzed_at": report.analyzed_at.isoformat(),
    }


@app.get("/api/v1/quality/stats")
async def get_quality_stats(
    hours: int = 24,
    provider: Optional[str] = None,
    _: bool = Depends(verify_api_key),
):
    """
    Get aggregated quality statistics.
    """
    from bifrost.quality import get_quality_tracker
    
    tracker = get_quality_tracker()
    return tracker.get_stats(hours=hours, provider=provider)


@app.get("/api/v1/quality/dimensions")
async def get_dimension_stats(
    hours: int = 24,
    dimension: Optional[str] = None,
    _: bool = Depends(verify_api_key),
):
    """
    Get quality statistics by dimension.
    """
    from bifrost.quality import get_quality_tracker, QualityDimension
    
    tracker = get_quality_tracker()
    dim = QualityDimension(dimension) if dimension else None
    return tracker.get_dimension_stats(hours=hours, dimension=dim)


@app.get("/api/v1/quality/trends")
async def get_quality_trends(days: int = 7, _: bool = Depends(verify_api_key)):
    """
    Get daily quality trends.
    """
    from bifrost.quality import get_quality_tracker
    
    tracker = get_quality_tracker()
    trend = tracker.get_trends(days=days)
    
    return {
        "period": trend.period,
        "data_points": trend.data_points,
    }


@app.get("/api/v1/quality/reports")
async def get_quality_reports(
    hours: int = 24,
    limit: int = 50,
    provider: Optional[str] = None,
    min_grade: Optional[str] = None,
    _: bool = Depends(verify_api_key),
):
    """
    Get recent quality reports.
    """
    from bifrost.quality import get_quality_tracker
    
    tracker = get_quality_tracker()
    reports = tracker.get_recent_reports(
        hours=hours,
        limit=limit,
        provider=provider,
        min_grade=min_grade,
    )
    
    return {
        "count": len(reports),
        "reports": [
            {
                "report_id": str(r.id),
                "request_id": r.request_id,
                "overall_score": r.overall_score,
                "overall_grade": r.overall_grade,
                "provider": r.provider,
                "analyzed_at": r.analyzed_at.isoformat(),
            }
            for r in reports
        ],
    }


@app.get("/api/v1/quality/reports/{report_id}")
async def get_quality_report(report_id: str, _: bool = Depends(verify_api_key)):
    """
    Get a specific quality report.
    """
    from uuid import UUID
    from bifrost.quality import get_quality_tracker
    
    try:
        rid = UUID(report_id)
    except ValueError:
        raise HTTPException(400, "Invalid report ID format")
    
    tracker = get_quality_tracker()
    report = tracker.get_report(rid)
    
    if not report:
        raise HTTPException(404, "Report not found")
    
    return {
        "report_id": str(report.id),
        "request_id": report.request_id,
        "job_id": report.job_id,
        "overall_score": report.overall_score,
        "overall_grade": report.overall_grade,
        "provider": report.provider,
        "lane": report.lane,
        "model": report.model,
        "latency_ms": report.latency_ms,
        "token_count": report.token_count,
        "scores": [
            {
                "dimension": s.dimension.value,
                "score": s.score,
                "weight": s.weight,
                "details": s.details,
                "factors": s.factors,
            }
            for s in report.scores
        ],
        "recommendations": report.recommendations,
        "metadata": report.metadata,
        "analyzed_at": report.analyzed_at.isoformat(),
    }


@app.get("/api/v1/quality/low-quality")
async def get_low_quality_reports(
    hours: int = 24,
    threshold: float = 0.6,
    limit: int = 50,
    _: bool = Depends(verify_api_key),
):
    """
    Get reports with quality below threshold.
    """
    from bifrost.quality import get_quality_tracker
    
    tracker = get_quality_tracker()
    reports = tracker.get_low_quality_reports(
        hours=hours,
        threshold=threshold,
        limit=limit,
    )
    
    return {
        "threshold": threshold,
        "count": len(reports),
        "reports": [
            {
                "report_id": str(r.id),
                "request_id": r.request_id,
                "overall_score": r.overall_score,
                "overall_grade": r.overall_grade,
                "provider": r.provider,
                "recommendations": r.recommendations,
                "analyzed_at": r.analyzed_at.isoformat(),
            }
            for r in reports
        ],
    }


# ==================== End Quality Metrics API ====================


# ==================== A/B Testing API ====================

class ExperimentCreateRequest(BaseModel):
    """Request model for creating an experiment."""
    name: str = Field(..., description="Experiment name")
    description: Optional[str] = Field(None, description="Experiment description")
    variants: List[Dict[str, Any]] = Field(..., description="List of variants")
    allocation: Optional[Dict[str, Any]] = Field(None, description="Traffic allocation")
    config: Optional[Dict[str, Any]] = Field(None, description="Experiment configuration")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


@app.post("/api/v1/experiments")
async def create_experiment(request: ExperimentCreateRequest, _: bool = Depends(verify_api_key)):
    """
    Create a new A/B test experiment.
    """
    from bifrost.experiment import (
        get_experiment_manager,
        Experiment,
        Variant,
        VariantType,
        TrafficAllocation,
        ExperimentConfig,
    )
    
    try:
        # Parse variants
        variants = []
        for v_data in request.variants:
            variant = Variant(
                name=v_data["name"],
                variant_type=VariantType(v_data.get("variant_type", "treatment")),
                weight=v_data.get("weight", 50.0),
                provider=v_data.get("provider"),
                model=v_data.get("model"),
                lane=v_data.get("lane"),
                temperature=v_data.get("temperature"),
                max_tokens=v_data.get("max_tokens"),
                config=v_data.get("config", {}),
            )
            variants.append(variant)
        
        # Create experiment
        experiment = Experiment(
            name=request.name,
            description=request.description or "",
            variants=variants,
            tags=request.tags or [],
        )
        
        manager = get_experiment_manager()
        created = manager.create_experiment(experiment)
        
        return {
            "success": True,
            "experiment_id": str(created.id),
            "name": created.name,
            "status": created.status.value,
        }
    
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/api/v1/experiments")
async def list_experiments(
    status: Optional[str] = None,
    limit: int = 50,
    _: bool = Depends(verify_api_key),
):
    """
    List all experiments.
    """
    from bifrost.experiment import get_experiment_manager, ExperimentStatus
    
    manager = get_experiment_manager()
    
    status_filter = ExperimentStatus(status) if status else None
    experiments = manager.list_experiments(status=status_filter, limit=limit)
    
    return {
        "count": len(experiments),
        "experiments": [
            {
                "id": str(e.id),
                "name": e.name,
                "status": e.status.value,
                "variants_count": len(e.variants),
                "created_at": e.created_at.isoformat(),
            }
            for e in experiments
        ],
    }


@app.get("/api/v1/experiments/{experiment_id}")
async def get_experiment(experiment_id: str, _: bool = Depends(verify_api_key)):
    """
    Get experiment details.
    """
    from uuid import UUID
    from bifrost.experiment import get_experiment_manager
    
    try:
        eid = UUID(experiment_id)
    except ValueError:
        raise HTTPException(400, "Invalid experiment ID")
    
    manager = get_experiment_manager()
    experiment = manager.get_experiment(eid)
    
    if not experiment:
        raise HTTPException(404, "Experiment not found")
    
    return experiment.to_dict()


@app.post("/api/v1/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str, _: bool = Depends(verify_api_key)):
    """
    Start an experiment.
    """
    from uuid import UUID
    from bifrost.experiment import get_experiment_manager
    
    try:
        eid = UUID(experiment_id)
    except ValueError:
        raise HTTPException(400, "Invalid experiment ID")
    
    manager = get_experiment_manager()
    
    try:
        experiment = manager.start_experiment(eid)
        return {
            "success": True,
            "experiment_id": str(experiment.id),
            "status": experiment.status.value,
            "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/v1/experiments/{experiment_id}/pause")
async def pause_experiment(experiment_id: str, _: bool = Depends(verify_api_key)):
    """
    Pause a running experiment.
    """
    from uuid import UUID
    from bifrost.experiment import get_experiment_manager
    
    try:
        eid = UUID(experiment_id)
    except ValueError:
        raise HTTPException(400, "Invalid experiment ID")
    
    manager = get_experiment_manager()
    
    try:
        experiment = manager.pause_experiment(eid)
        return {
            "success": True,
            "experiment_id": str(experiment.id),
            "status": experiment.status.value,
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.post("/api/v1/experiments/{experiment_id}/stop")
async def stop_experiment(
    experiment_id: str,
    reason: Optional[str] = None,
    _: bool = Depends(verify_api_key),
):
    """
    Stop an experiment.
    """
    from uuid import UUID
    from bifrost.experiment import get_experiment_manager
    
    try:
        eid = UUID(experiment_id)
    except ValueError:
        raise HTTPException(400, "Invalid experiment ID")
    
    manager = get_experiment_manager()
    
    try:
        experiment = manager.stop_experiment(eid, reason or "")
        return {
            "success": True,
            "experiment_id": str(experiment.id),
            "status": experiment.status.value,
            "ended_at": experiment.ended_at.isoformat() if experiment.ended_at else None,
        }
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/api/v1/experiments/{experiment_id}")
async def delete_experiment(experiment_id: str, _: bool = Depends(verify_api_key)):
    """
    Delete an experiment.
    """
    from uuid import UUID
    from bifrost.experiment import get_experiment_manager
    
    try:
        eid = UUID(experiment_id)
    except ValueError:
        raise HTTPException(400, "Invalid experiment ID")
    
    manager = get_experiment_manager()
    deleted = manager.delete_experiment(eid)
    
    if not deleted:
        raise HTTPException(404, "Experiment not found")
    
    return {"success": True, "message": "Experiment deleted"}


@app.get("/api/v1/experiments/{experiment_id}/results")
async def get_experiment_results(experiment_id: str, _: bool = Depends(verify_api_key)):
    """
    Get experiment results and analysis.
    """
    from uuid import UUID
    from bifrost.experiment import get_experiment_manager
    
    try:
        eid = UUID(experiment_id)
    except ValueError:
        raise HTTPException(400, "Invalid experiment ID")
    
    manager = get_experiment_manager()
    
    try:
        results = manager.get_results(eid)
        return results.to_dict()
    except ValueError as e:
        raise HTTPException(404, str(e))


class AssignVariantRequest(BaseModel):
    """Request model for variant assignment."""
    experiment_id: str = Field(..., description="Experiment ID")
    request_id: str = Field(..., description="Request ID for assignment")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    query: Optional[str] = Field(None, description="Query for eligibility check")


@app.post("/api/v1/experiments/assign")
async def assign_variant(request: AssignVariantRequest, _: bool = Depends(verify_api_key)):
    """
    Assign a request to an experiment variant.
    """
    from uuid import UUID
    from bifrost.experiment import get_experiment_manager
    
    try:
        eid = UUID(request.experiment_id)
    except ValueError:
        raise HTTPException(400, "Invalid experiment ID")
    
    manager = get_experiment_manager()
    
    variant = manager.assign_variant(
        experiment_id=eid,
        request_id=request.request_id,
        user_id=request.user_id,
        session_id=request.session_id,
        query=request.query,
    )
    
    if not variant:
        return {
            "assigned": False,
            "reason": "Not eligible or experiment not active",
        }
    
    return {
        "assigned": True,
        "experiment_id": str(eid),
        "variant": variant.to_dict(),
    }


class RecordResultRequest(BaseModel):
    """Request model for recording experiment results."""
    request_id: str = Field(..., description="Request ID")
    quality_score: Optional[float] = Field(None, description="Quality score (0-1)")
    latency_ms: Optional[int] = Field(None, description="Latency in ms")
    satisfaction_score: Optional[float] = Field(None, description="Satisfaction score")
    error_occurred: bool = Field(False, description="Whether an error occurred")
    token_count: Optional[int] = Field(None, description="Token count")


@app.post("/api/v1/experiments/record")
async def record_experiment_result(
    request: RecordResultRequest,
    _: bool = Depends(verify_api_key),
):
    """
    Record the result of an experiment assignment.
    """
    from bifrost.experiment import get_experiment_manager
    
    manager = get_experiment_manager()
    
    success = manager.record_result(
        request_id=request.request_id,
        quality_score=request.quality_score,
        latency_ms=request.latency_ms,
        satisfaction_score=request.satisfaction_score,
        error_occurred=request.error_occurred,
        token_count=request.token_count,
    )
    
    return {
        "success": success,
        "request_id": request.request_id,
    }


# ==================== End A/B Testing API ====================


# ==================== Smart Cache API ====================

class CachePutRequest(BaseModel):
    """Request model for adding cache entry."""
    query: str = Field(..., description="Query to cache")
    response: str = Field(..., description="Response to cache")
    ttl_seconds: Optional[int] = Field(None, description="TTL in seconds")
    provider: Optional[str] = Field(None, description="Provider name")
    model: Optional[str] = Field(None, description="Model name")
    lane: Optional[str] = Field(None, description="Inference lane")
    quality_score: Optional[float] = Field(None, description="Quality score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


@app.post("/api/v1/cache/put")
async def cache_put(request: CachePutRequest, _: bool = Depends(verify_api_key)):
    """
    Add an entry to the smart cache.
    """
    from bifrost.smart_cache import get_cache_manager
    
    manager = get_cache_manager()
    
    entry = manager.put(
        query=request.query,
        response=request.response,
        ttl_seconds=request.ttl_seconds,
        provider=request.provider,
        model=request.model,
        lane=request.lane,
        quality_score=request.quality_score,
        metadata=request.metadata,
    )
    
    return {
        "success": True,
        "entry_id": str(entry.id),
        "query_hash": entry.query_hash,
        "ttl_remaining": entry.ttl_remaining,
    }


class CacheLookupRequest(BaseModel):
    """Request model for cache lookup."""
    query: str = Field(..., description="Query to look up")
    use_semantic: Optional[bool] = Field(None, description="Use semantic matching")


@app.post("/api/v1/cache/lookup")
async def cache_lookup(request: CacheLookupRequest, _: bool = Depends(verify_api_key)):
    """
    Look up a query in the cache.
    """
    from bifrost.smart_cache import get_cache_manager
    
    manager = get_cache_manager()
    
    result = manager.get(
        query=request.query,
        use_semantic=request.use_semantic,
    )
    
    return result.to_dict()


@app.get("/api/v1/cache/stats")
async def get_cache_stats(_: bool = Depends(verify_api_key)):
    """
    Get cache statistics.
    """
    from bifrost.smart_cache import get_cache_manager
    
    manager = get_cache_manager()
    stats = manager.get_stats()
    
    return stats.to_dict()


@app.get("/api/v1/cache/entries")
async def list_cache_entries(
    limit: int = 50,
    include_expired: bool = False,
    _: bool = Depends(verify_api_key),
):
    """
    List cache entries.
    """
    from bifrost.smart_cache import get_cache_manager
    
    manager = get_cache_manager()
    entries = manager.get_entries(limit=limit, include_expired=include_expired)
    
    return {
        "count": len(entries),
        "entries": [e.to_dict() for e in entries],
    }


@app.delete("/api/v1/cache/invalidate")
async def invalidate_cache_entry(
    query: str,
    _: bool = Depends(verify_api_key),
):
    """
    Invalidate a cache entry by query.
    """
    from bifrost.smart_cache import get_cache_manager
    
    manager = get_cache_manager()
    success = manager.invalidate(query)
    
    return {
        "success": success,
        "message": "Entry invalidated" if success else "Entry not found",
    }


@app.delete("/api/v1/cache/clear")
async def clear_cache(_: bool = Depends(verify_api_key)):
    """
    Clear all cache entries.
    """
    from bifrost.smart_cache import get_cache_manager
    
    manager = get_cache_manager()
    count = manager.clear()
    
    return {
        "success": True,
        "cleared_count": count,
    }


@app.post("/api/v1/cache/cleanup")
async def cleanup_expired_cache(_: bool = Depends(verify_api_key)):
    """
    Remove expired cache entries.
    """
    from bifrost.smart_cache import get_cache_manager
    
    manager = get_cache_manager()
    count = manager.cleanup_expired()
    
    return {
        "success": True,
        "cleaned_count": count,
    }


# ==================== End Smart Cache API ====================


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """WebSocket 스트리밍 분석"""
    from bifrost.config import Config
    require_api_key = Config().get("security.require_api_key", False)
    if require_api_key:
        api_key = websocket.headers.get("x-api-key")
        if not api_key or not get_database().validate_api_key(api_key):
            await websocket.close(code=1008)
            return

    await websocket.accept()
    
    try:
        while True:
            # 요청 받기
            data = await websocket.receive_json()
            log_content = data.get("log_content", "")
            source = data.get("source", "local")
            model = data.get("model")
            
            if not log_content:
                await websocket.send_json({"error": "log_content is required"})
                continue
            
            # 전처리
            preprocessor = LogPreprocessor()
            log_content = preprocessor.process(log_content)
            
            from bifrost.main import MASTER_PROMPT
            prompt = MASTER_PROMPT.format(log_content=log_content)
            
            from starlette.concurrency import run_in_threadpool
            from functools import partial

            # 스트리밍 분석
            if source == "local":
                client = OllamaClient(model=model or "mistral")
                # TODO: WebSocket용 스트리밍 구현
                result = await run_in_threadpool(partial(client.analyze, prompt, stream=False))
                await websocket.send_json({
                    "type": "complete",
                    "response": result["response"],
                    "metadata": result["metadata"],
                })
            else:
                await websocket.send_json({"error": "Cloud streaming not supported yet"})
    
    except WebSocketDisconnect:
        pass


@app.post("/api-keys", dependencies=[Depends(verify_api_key)])
async def create_api_key(name: str, rate_limit: int = 100, description: Optional[str] = None):
    """API 키 생성 (관리자용)"""
    db = get_database()
    key = db.create_api_key(name=name, rate_limit=rate_limit, description=description)
    return {"key": key, "name": name, "rate_limit": rate_limit}


@app.get("/api-keys", dependencies=[Depends(verify_api_key)])
async def list_api_keys():
    """API 키 목록"""
    db = get_database()
    return db.list_api_keys()


 # Startup/Shutdown is handled via FastAPI lifespan


# ==================== 새로운 기능 엔드포인트 ====================

@app.get("/", response_class=HTMLResponse)
async def web_ui():
    """웹 UI (htmx)"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Web UI not found. Please check static/index.html</h1>"


@app.post("/api/analyze-web")
async def analyze_web(
    log_content: str = Form(...),
    source: str = Form("local"),
    severity: str = Form(None),
    service_name: str = Form(None),
    environment: str = Form(None),
    _: Optional[str] = Depends(verify_api_key),
):
    """웹 UI용 분석 엔드포인트 (Form 데이터)"""
    try:
        start_time = time.time()
        from bifrost.config import Config
        cfg = Config()
        store_raw_log = cfg.get("storage.store_raw_log", True)
        store_raw_response = cfg.get("storage.store_raw_response", True)
        redacted_placeholder = cfg.get("storage.redacted_placeholder", "[REDACTED]")
        # 심각도 필터링
        filtered_log = log_content
        if severity:
            filtered_log = LogFilter.filter_by_severity(
                log_content,
                min_level=SeverityLevel(severity)
            )
        
        # 분석 실행
        preprocessor = LogPreprocessor()
        processed_log = preprocessor.process(filtered_log)

        from bifrost.main import MASTER_PROMPT
        prompt = MASTER_PROMPT.format(log_content=processed_log)
        
        from starlette.concurrency import run_in_threadpool
        from functools import partial

        if source == "local":
            client = OllamaClient()
            result = await run_in_threadpool(partial(client.analyze, prompt, stream=False))
        else:
            client = BedrockClient()
            result = await run_in_threadpool(partial(client.analyze, prompt))
        
        # DB 저장
        db = get_database()
        duration = time.time() - start_time
        stored_log_content = log_content if store_raw_log else redacted_placeholder
        stored_response = result.get("response", "") if store_raw_response else redacted_placeholder
        import hashlib
        log_hash = hashlib.sha256(log_content.encode()).hexdigest()
        analysis_id = await run_in_threadpool(
            partial(
                db.save_analysis,
                source=source,
                model=(result.get("metadata") or {}).get("model")
                or (result.get("model") if isinstance(result, dict) else None)
                or "unknown",
                log_content=stored_log_content,
                response=stored_response,
                duration=duration,
                log_hash=log_hash,
                log_size_bytes=len(log_content.encode()),
                log_lines=len(log_content.split("\n")),
                response_size_bytes=len((result.get("response") or "").encode()) if isinstance(result, dict) else 0,
                service_name=service_name,
                environment=environment,
                status="completed",
            )
        )
        
        # HTML 응답
        html = f"""
        <div class="result">
            <div class="alert alert-success">
                ✅ 분석 완료! (ID: {analysis_id})
            </div>
            <h3>📊 분석 결과</h3>
            <pre>{result.get('response', 'No response')}</pre>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="number">{result.get('model', 'N/A')}</div>
                    <div class="label">모델</div>
                </div>
                <div class="stat-card">
                    <div class="number">{source}</div>
                    <div class="label">소스</div>
                </div>
                <div class="stat-card">
                    <div class="number">{service_name or 'N/A'}</div>
                    <div class="label">서비스</div>
                </div>
            </div>
        </div>
        """
        
        return HTMLResponse(content=html)
    
    except Exception as e:
        error_html = f"""
        <div class="result">
            <div class="alert alert-error">
                ❌ 에러 발생: {str(e)}
            </div>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=400)


@app.get("/api/export/csv")
async def export_csv(
    limit: int = 100,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """분석 결과를 CSV로 export"""
    db = get_database()
    results = db.list_analyses(limit=limit, offset=0)
    
    csv_content = DataExporter.to_csv(results)
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=bifrost_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


@app.get("/api/export/json")
async def export_json(
    limit: int = 100,
    pretty: bool = True,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """분석 결과를 JSON으로 export"""
    db = get_database()
    results = db.list_analyses(limit=limit, offset=0)
    
    json_content = DataExporter.to_json(results, pretty=pretty)
    
    return StreamingResponse(
        iter([json_content]),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=bifrost_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


@app.post("/api/filter/severity")
async def filter_by_severity(
    request: FilterSeverityRequest,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """심각도로 필터링"""
    filtered = LogFilter.filter_by_severity(request.log_content, request.min_level)
    stats = LogFilter.get_log_statistics(filtered)
    
    return {
        "filtered_log": filtered,
        "statistics": stats
    }


@app.post("/api/filter/errors")
async def filter_errors_only(
    request: FilterErrorsRequest,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """에러만 추출"""
    filtered = LogFilter.extract_errors_only(request.log_content)
    
    return {
        "filtered_log": filtered,
        "line_count": len(filtered.split('\n'))
    }


@app.post("/api/slack/send")
async def send_to_slack(
    request: SlackNotificationRequest,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """분석 결과를 Slack으로 전송"""
    slack = SlackNotifier(request.webhook_url)
    success = slack.send_analysis_result(request.result, request.service_name)
    
    return {
        "success": success,
        "message": "Slack 전송 성공" if success else "Slack 전송 실패"
    }


@app.get("/api/log/stats")
async def get_log_statistics(
    log_content: str,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """로그 통계"""
    stats = LogFilter.get_log_statistics(log_content)
    
    return stats


# ==================== 프롬프트 관리 엔드포인트 ====================

@app.post("/api/prompts")
async def create_prompt(
    request: CreatePromptRequest,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """프롬프트 템플릿 생성"""
    from bifrost.prompt_editor import PromptEditor
    
    editor = PromptEditor()
    prompt_id = editor.create_prompt(
        name=request.name,
        content=request.content,
        description=request.description,
        tags=request.tags or []
    )
    
    return {
        "prompt_id": prompt_id,
        "message": f"Prompt '{request.name}' created successfully"
    }


@app.get("/api/prompts")
async def list_prompts(
    tags: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """프롬프트 템플릿 리스트"""
    from bifrost.prompt_editor import PromptEditor
    
    editor = PromptEditor()
    tag_list = tags.split(',') if tags else None
    prompts = editor.list_prompts(tags=tag_list, search=search, limit=limit)
    
    return {
        "prompts": prompts,
        "count": len(prompts)
    }


@app.get("/api/prompts/{prompt_id}")
async def get_prompt(
    prompt_id: int,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """프롬프트 템플릿 조회"""
    from bifrost.prompt_editor import PromptEditor
    
    editor = PromptEditor()
    prompt = editor.get_prompt(prompt_id)
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return prompt


@app.put("/api/prompts/{prompt_id}")
async def update_prompt(
    prompt_id: int,
    content: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """프롬프트 템플릿 업데이트"""
    from bifrost.prompt_editor import PromptEditor
    
    editor = PromptEditor()
    success = editor.update_prompt(
        prompt_id=prompt_id,
        content=content,
        description=description,
        tags=tags
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return {"message": "Prompt updated successfully"}


@app.delete("/api/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: int,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """프롬프트 템플릿 삭제"""
    from bifrost.prompt_editor import PromptEditor
    
    editor = PromptEditor()
    success = editor.delete_prompt(prompt_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    return {"message": "Prompt deleted successfully"}


# ==================== MLflow 엔드포인트 ====================

@app.get("/api/mlflow/experiments")
async def get_mlflow_experiments(
    api_key: Optional[str] = Depends(verify_api_key)
):
    """MLflow 실험 정보 조회"""
    from bifrost.mlflow_tracker import MLflowTracker
    
    tracker = MLflowTracker()
    if not tracker.enabled:
        raise HTTPException(
            status_code=503,
            detail="MLflow not available. Install with: pip install mlflow"
        )
    
    experiment = tracker.get_experiment_info()
    return experiment or {}


@app.get("/api/mlflow/runs")
async def search_mlflow_runs(
    filter: Optional[str] = None,
    max_results: int = 100,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """MLflow Run 검색"""
    from bifrost.mlflow_tracker import MLflowTracker
    
    tracker = MLflowTracker()
    if not tracker.enabled:
        raise HTTPException(status_code=503, detail="MLflow not available")
    
    runs = tracker.search_runs(
        filter_string=filter,
        max_results=max_results
    )
    
    return {
        "runs": runs,
        "count": len(runs)
    }


@app.get("/api/mlflow/runs/{run_id}")
async def get_mlflow_run(
    run_id: str,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """MLflow Run 상세 조회"""
    from bifrost.mlflow_tracker import MLflowTracker
    
    tracker = MLflowTracker()
    if not tracker.enabled:
        raise HTTPException(status_code=503, detail="MLflow not available")
    
    run = tracker.get_run(run_id)
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return run


@app.post("/api/mlflow/runs/compare")
async def compare_mlflow_runs(
    request: CompareMLflowRunsRequest,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """MLflow Run 비교"""
    from bifrost.mlflow_tracker import MLflowTracker
    
    tracker = MLflowTracker()
    if not tracker.enabled:
        raise HTTPException(status_code=503, detail="MLflow not available")
    
    comparison = tracker.compare_runs(request.run_ids, request.metric_names)
    
    return comparison


# ==================== Interview Edition: Incident/Runbook Q&A (Plan A) ====================


@app.post("/api/v1/runbooks/ingest", response_model=RunbookIngestResponse, dependencies=[Depends(verify_api_key)])
async def ingest_runbook(req: RunbookIngestRequest):
    """Ingest runbook/docs into on-device RAG store."""
    ingest = RunbookIngestService()
    result = ingest.ingest(source=req.source, tags=req.tags, text=req.text)
    return RunbookIngestResponse(chunks_ingested=result.chunks_ingested)


@app.post("/api/v1/ask", response_model=AnswerResponse, dependencies=[Depends(verify_api_key)])
@app.post("/ask", response_model=AnswerResponse, dependencies=[Depends(verify_api_key)])
async def ask(req: AnswerRequest, request: Request):
    """Incident / Runbook Q&A assistant.

    IMPORTANT:
    - API handler must NOT call providers directly.
    - It delegates to OrchestratorService.
    """
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    orchestrator = OrchestratorService()

    start = time.time()
    outcome = "ok"
    response: Optional[AnswerResponse] = None

    try:
        response = await orchestrator.ask(req, request_id=request_id)
        outcome = "fallback" if response.route.fallback_used else "ok"
        return response
    except Exception:
        outcome = "error"
        raise
    finally:
        latency_ms = int((time.time() - start) * 1000)
        lane = response.route.lane if response else "unknown"
        try:
            metrics.increment_ask_requests(lane=lane, outcome=outcome)
            metrics.observe_ask_latency_ms(lane=lane, latency_ms=latency_ms)
        except Exception:
            # metrics must never break the request
            pass


# ==================== Privacy Router API ====================

@app.post("/api/router/classify")
async def classify_sensitivity(
    request: dict,
    api_key: Optional[str] = Depends(verify_api_key)
):
    """
    Privacy Router: 데이터 민감도 분류
    
    로그 컨텐츠의 민감도를 분석하고 적절한 AI Track을 추천합니다.
    """
    log_content = request.get("log_content", "")
    if not log_content:
        raise HTTPException(status_code=400, detail="log_content is required")
    
    privacy_router = get_router()
    routing_decision = privacy_router.route(log_content)
    explanation = privacy_router.explain_route(log_content)
    
    return {
        "routing": routing_decision,
        "explanation": explanation,
        "recommended_track": routing_decision["track"],
    }


@app.get("/api/router/status")
async def router_status():
    """Privacy Router 상태 확인"""
    privacy_router = get_router()
    
    return {
        "status": "operational",
        "high_patterns": len(privacy_router.HIGH_PATTERNS),
        "medium_patterns": len(privacy_router.MEDIUM_PATTERNS),
        "gdpr_keywords": len(privacy_router.GDPR_KEYWORDS),
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
