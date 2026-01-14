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

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """API 키 검증"""
    if not x_api_key:
        return True  # 개발 모드: API 키 선택
    
    db = get_database()
    if not db.validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


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
    
    return {
        "status": "healthy",
        "components": {
            "database": "ok",
            "ollama": "ok" if ollama_healthy else "unavailable",
            "bedrock": "ok" if is_bedrock_available() else "not_configured",
            "kafka": kafka_status,
            "heimdall_integration": "enabled" if kafka_consumer_manager else "disabled",
        },
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
    cached_results = db.get_duplicate_analyses(log_hash, hours=24)
    
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
            result = client.analyze(prompt, stream=False)  # API는 스트리밍 미지원
        elif request.source == "cloud":
            if not is_bedrock_available():
                raise HTTPException(status_code=400, detail="Bedrock not available (boto3 not installed)")
            client = BedrockClient(model_id=request.model or "anthropic.claude-3-sonnet-20240229-v1:0")
            result = client.analyze(prompt)
        else:
            raise HTTPException(status_code=400, detail="Invalid source (local or cloud)")
        
        duration = time.time() - start_time
        
        # DB 저장 (백그라운드) - Privacy Router 메타데이터 추가
        analysis_id = db.save_analysis(
            source=request.source,
            model=result["metadata"]["model"],
            log_content=request.log_content,
            response=result["response"],
            duration=duration,
            tags=request.tags,
            service_name=request.service_name,
            environment=request.environment,
            tokens_used=result["metadata"].get("usage", {}).get("total_tokens"),
            status="completed",
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
        db.save_analysis(
            source=request.source,
            model=request.model or "unknown",
            log_content=request.log_content,
            response="",
            duration=time.time() - start_time,
            status="failed",
            error_message=str(e),
        )
        
        metrics.increment_error_count(request.source)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


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
async def get_prometheus_metrics():
    """Prometheus 메트릭 엔드포인트"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """WebSocket 스트리밍 분석"""
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
            
            # 스트리밍 분석
            if source == "local":
                client = OllamaClient(model=model or "mistral")
                # TODO: WebSocket용 스트리밍 구현
                result = client.analyze(prompt, stream=False)
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
):
    """웹 UI용 분석 엔드포인트 (Form 데이터)"""
    try:
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
        
        if source == "local":
            client = OllamaClient()
        else:
            client = BedrockClient()
        
        result = client.analyze(processed_log)
        
        # DB 저장
        db = get_database()
        analysis_id = db.save_analysis(
            log_content=log_content,
            response=result.get("response", ""),
            source=source,
            service_name=service_name,
            environment=environment,
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
    api_key: str = Depends(verify_api_key)
):
    """분석 결과를 CSV로 export"""
    db = get_database()
    results = db.get_analysis_history(limit=limit)
    
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
    api_key: str = Depends(verify_api_key)
):
    """분석 결과를 JSON으로 export"""
    db = get_database()
    results = db.get_analysis_history(limit=limit)
    
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
):
    """로그 통계"""
    stats = LogFilter.get_log_statistics(log_content)
    
    return stats


# ==================== 프롬프트 관리 엔드포인트 ====================

@app.post("/api/prompts")
async def create_prompt(
    request: CreatePromptRequest,
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
    api_key: str = Depends(verify_api_key)
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
