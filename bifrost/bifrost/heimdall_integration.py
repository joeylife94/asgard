"""Kafka Integration Service - Heimdall 연동 핵심 로직"""

import os
import time
from decimal import Decimal
from typing import Optional

from bifrost.kafka_events import AnalysisRequestEvent, AnalysisResultEvent, DlqFailedEvent, TokenUsage
from bifrost.kafka_producer import KafkaProducerManager
from bifrost.heimdall_store import HeimdallStore
from bifrost.ollama import OllamaClient
from bifrost.bedrock import BedrockClient, is_bedrock_available
from bifrost.preprocessor import LogPreprocessor
from bifrost.database import get_database
from bifrost.logger import logger


# Master Prompt (기존 사용 중인 프롬프트)
MASTER_PROMPT = """당신은 전문 MLOps SRE입니다. 아래 로그를 분석하고 다음 형식으로 응답하세요:

## 📊 요약
로그의 핵심 내용을 3-5줄로 요약

## 🔍 주요 이슈
- 발견된 에러나 경고
- 중요한 패턴이나 이상 징후

## 💡 제안사항
- 문제 해결 방법
- 개선 방향

---
로그:
{log_content}
"""


class HeimdallIntegrationService:
    """Heimdall과의 Kafka 기반 통합 서비스"""
    
    def __init__(self, config: dict, producer_manager: KafkaProducerManager):
        self.config = config
        self.producer_manager = producer_manager
        self.preprocessor = LogPreprocessor()
        self.db = get_database()

        heimdall_db_url = os.getenv(
            "HEIMDALL_DATABASE_URL",
            "postgresql://asgard:asgard_password@localhost:5432/heimdall",
        )
        self.heimdall_store = HeimdallStore(heimdall_db_url)
    
    async def process_analysis_request(self, event: AnalysisRequestEvent):
        """
        분석 요청 처리 - Kafka Consumer가 호출
        
        Args:
            event: Heimdall로부터 받은 분석 요청 이벤트
        """
        start_time = time.time()

        job_id = event.normalized_job_id()
        trace_id = event.normalized_trace_id()
        
        logger.info(
            f"Processing analysis request from Heimdall",
            job_id=job_id,
            log_id=event.log_id,
            priority=event.priority
        )
        
        try:
            # 0. Heimdall DB에서 log_content 조회 (REST 제거)
            log_entry = self.heimdall_store.get_log_entry(event.log_id)
            if not log_entry:
                raise RuntimeError(f"Heimdall log entry not found: log_id={event.log_id}")

            # 1. 로그 전처리
            processed_log = self.preprocessor.process(log_entry.log_content)
            
            # 2. 프롬프트 생성
            prompt = MASTER_PROMPT.format(log_content=processed_log)
            
            # 3. AI 분석 수행
            analysis_response = await self._analyze_with_ai(
                prompt=prompt,
                source=self._get_source_from_config()
            )
            
            # 4. 분석 결과 저장 (Bifrost DB)
            bifrost_analysis_id = self._save_analysis_to_db(
                event=event,
                response=analysis_response,
                duration=time.time() - start_time,
                log_content=log_entry.log_content,
                service_name=log_entry.service_name,
                environment=log_entry.environment,
            )
            
            # 5. 분석 결과를 AnalysisResultData로 변환
            parsed = self._parse_analysis_response(
                response=analysis_response["response"],
                confidence=0.85
            )
            
            # 6. Kafka로 결과 발행 (Heimdall로 전송)
            latency_ms = int((time.time() - start_time) * 1000)
            usage = analysis_response.get("metadata", {}).get("usage", {}) or {}

            result_event = AnalysisResultEvent(
                schema_version=1,
                job_id=job_id,
                status="SUCCEEDED",
                summary=parsed.summary,
                root_cause=parsed.root_cause,
                recommendation=parsed.recommendation,
                severity=parsed.severity,
                confidence=parsed.confidence,
                model_used=analysis_response.get("metadata", {}).get("model"),
                token_usage=TokenUsage(
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    total_tokens=usage.get("total_tokens"),
                ),
                latency_ms=latency_ms,
                trace_id=trace_id,
                log_id=event.log_id,
            )
            
            success = await self.producer_manager.send_result(result_event)
            
            if success:
                logger.info(
                    f"Analysis completed and sent to Heimdall",
                    job_id=job_id,
                    log_id=event.log_id,
                    bifrost_analysis_id=bifrost_analysis_id,
                    latency_ms=latency_ms
                )
            else:
                logger.error(
                    f"Failed to send analysis result to Heimdall",
                    job_id=job_id,
                    log_id=event.log_id
                )
            
        except Exception as e:
            logger.error(
                f"Error processing analysis request",
                job_id=job_id,
                log_id=event.log_id,
                error=str(e),
                exc_info=True
            )

            # Failure path: publish FAILED result + DLQ signal
            try:
                failed_event = AnalysisResultEvent(
                    schema_version=1,
                    job_id=job_id,
                    status="FAILED",
                    error_code="PROCESSING_ERROR",
                    error_message=str(e),
                    trace_id=trace_id,
                    log_id=event.log_id,
                )
                await self.producer_manager.send_result(failed_event)

                dlq_event = DlqFailedEvent(
                    schema_version=1,
                    job_id=job_id,
                    idempotency_key=event.idempotency_key,
                    error_code="PROCESSING_ERROR",
                    error_message=str(e),
                    trace_id=trace_id,
                    original_topic=self.config.get("kafka", {}).get("topics", {}).get("analysis_request", "analysis.request"),
                    original_partition=-1,
                    original_offset=-1,
                    payload=getattr(event, "model_dump", lambda: {} )(),
                )
                await self.producer_manager.send_dlq(dlq_event)
            except Exception:
                logger.error("Failed to publish failure signals", exc_info=True)
            raise
    
    async def _analyze_with_ai(self, prompt: str, source: str) -> dict:
        """AI 모델로 로그 분석"""
        if source == "local":
            client = OllamaClient(
                url=self.config.get("ollama", {}).get("url", "http://localhost:11434"),
                model=self.config.get("ollama", {}).get("model", "mistral")
            )
            result = client.analyze(prompt, stream=False)
        elif source == "cloud":
            if not is_bedrock_available():
                raise RuntimeError("Bedrock not available (boto3 not installed)")
            
            client = BedrockClient(
                region=self.config.get("bedrock", {}).get("region", "us-east-1"),
                model_id=self.config.get("bedrock", {}).get(
                    "model", "anthropic.claude-3-sonnet-20240229-v1:0"
                )
            )
            result = client.analyze(prompt)
        else:
            raise ValueError(f"Invalid source: {source}")
        
        return result
    
    def _save_analysis_to_db(
        self,
        event: AnalysisRequestEvent,
        response: dict,
        duration: float,
        log_content: str,
        service_name: Optional[str],
        environment: Optional[str],
    ) -> int:
        """분석 결과를 Bifrost DB에 저장"""
        analysis_id = self.db.save_analysis(
            source=self._get_source_from_config(),
            model=response["metadata"]["model"],
            log_content=log_content,
            response=response["response"],
            duration=duration,
            tags=[
                f"heimdall:log_id:{event.log_id}",
                f"service:{service_name}",
                f"env:{environment}",
                f"priority:{event.priority}"
            ],
            service_name=service_name,
            environment=environment,
            tokens_used=response["metadata"].get("usage", {}).get("total_tokens"),
            status="completed"
        )
        
        return analysis_id
    
    def _parse_analysis_response(self, response: str, confidence: float):
        """
        AI 응답을 구조화된 데이터로 변환
        
        TODO: 더 정교한 파싱 로직 구현 (마크다운 파싱, 섹션 추출 등)
        """
        lines = response.strip().split('\n')
        
        summary = ""
        root_cause = ""
        recommendation = ""
        severity = "MEDIUM"
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "요약" in line or "Summary" in line:
                current_section = "summary"
            elif "주요 이슈" in line or "이슈" in line or "Issue" in line:
                current_section = "root_cause"
            elif "제안" in line or "권장" in line or "Recommendation" in line:
                current_section = "recommendation"
            elif line and not line.startswith('#'):
                if current_section == "summary":
                    summary += line + " "
                elif current_section == "root_cause":
                    root_cause += line + " "
                elif current_section == "recommendation":
                    recommendation += line + " "
        
        # 심각도 추론
        if "CRITICAL" in response.upper() or "FATAL" in response.upper():
            severity = "CRITICAL"
        elif "ERROR" in response.upper() or "실패" in response:
            severity = "HIGH"
        elif "WARN" in response.upper() or "경고" in response:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        class _Parsed:
            def __init__(self, summary: str, root_cause: str, recommendation: str, severity: str, confidence: Decimal):
                self.summary = summary
                self.root_cause = root_cause
                self.recommendation = recommendation
                self.severity = severity
                self.confidence = confidence

        return _Parsed(
            summary=summary.strip() or "분석 요약 정보 없음",
            root_cause=root_cause.strip() or "근본 원인 분석 중",
            recommendation=recommendation.strip() or "권장사항 분석 중",
            severity=severity,
            confidence=Decimal(str(confidence)),
        )
    
    def _get_source_from_config(self) -> str:
        """설정에서 AI 소스 결정"""
        return self.config.get("heimdall", {}).get("ai_source", "local")
