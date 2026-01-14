"""Kafka 통합 테스트"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal

from bifrost.kafka_events import (
    AnalysisRequestEvent,
    AnalysisResultEvent,
    AnalysisPriority
)


# This module exercises Kafka/event wiring and is intentionally excluded
# from the default unit test run (see test-all.ps1: -m "not integration").
pytestmark = pytest.mark.integration


@pytest.fixture
def sample_analysis_request():
    """샘플 분석 요청 이벤트"""
    return AnalysisRequestEvent(
        job_id="00000000-0000-0000-0000-000000000123",
        idempotency_key="idem-test-123",
        log_id=12345,
        priority=AnalysisPriority.HIGH,
        trace_id="trace-test-123",
        # legacy aliases (optional)
        request_id="test-request-123",
        correlation_id="corr-123",
    )


@pytest.fixture
def sample_analysis_result():
    """샘플 분석 결과 이벤트"""
    return AnalysisResultEvent(
        job_id="00000000-0000-0000-0000-000000000123",
        status="SUCCEEDED",
        summary="Database connection timeout",
        root_cause="Connection pool exhausted",
        recommendation="Increase max_connections setting",
        severity="HIGH",
        confidence=Decimal("0.95"),
        model_used="mistral-7b",
        latency_ms=2500,
        trace_id="trace-test-123",
        log_id=12345,
    )


class TestKafkaEvents:
    """Kafka 이벤트 스키마 테스트"""
    
    def test_analysis_request_event_creation(self, sample_analysis_request):
        """분석 요청 이벤트 생성 테스트"""
        event = sample_analysis_request
        
        assert event.job_id == "00000000-0000-0000-0000-000000000123"
        assert event.log_id == 12345
        assert event.priority == AnalysisPriority.HIGH
        assert event.trace_id == "trace-test-123"
    
    def test_analysis_request_event_serialization(self, sample_analysis_request):
        """분석 요청 이벤트 직렬화 테스트"""
        event = sample_analysis_request
        data = event.model_dump()
        
        assert isinstance(data, dict)
        assert data["job_id"] == "00000000-0000-0000-0000-000000000123"
        assert data["log_id"] == 12345
    
    def test_analysis_result_event_creation(self, sample_analysis_result):
        """분석 결과 이벤트 생성 테스트"""
        event = sample_analysis_result
        
        assert event.job_id == "00000000-0000-0000-0000-000000000123"
        assert event.log_id == 12345
        assert event.severity == "HIGH"
        assert event.confidence == Decimal("0.95")


@pytest.mark.asyncio
class TestKafkaProducer:
    """Kafka Producer 테스트"""
    
    async def test_send_analysis_result(self, sample_analysis_result):
        """분석 결과 발행 테스트"""
        from bifrost.kafka_producer import AnalysisResultProducer
        
        producer = AnalysisResultProducer()
        
        # Mock producer
        mock_kafka_producer = AsyncMock()
        mock_kafka_producer.send_and_wait = AsyncMock(
            return_value=MagicMock(topic="analysis.result", partition=0, offset=123)
        )
        producer.producer = mock_kafka_producer
        
        # 테스트
        result = await producer.send_analysis_result(sample_analysis_result)
        
        assert result is True
        mock_kafka_producer.send_and_wait.assert_called_once()


@pytest.mark.asyncio
class TestKafkaConsumer:
    """Kafka Consumer 테스트"""
    
    async def test_consume_analysis_request(self, sample_analysis_request):
        """분석 요청 소비 테스트"""
        from bifrost.kafka_consumer import AnalysisRequestConsumer

        class _FakeKafkaConsumer:
            def __init__(self, messages):
                self._messages = messages
                self.commit = AsyncMock()

            def __aiter__(self):
                async def _gen():
                    for msg in self._messages:
                        yield msg

                return _gen()
        
        # Mock processor
        processor = AsyncMock()
        
        consumer = AnalysisRequestConsumer()
        
        # Mock consumer
        mock_message = MagicMock()
        mock_message.topic = "analysis.request"
        mock_message.partition = 0
        mock_message.offset = 456
        mock_message.key = b"12345"
        mock_message.value = sample_analysis_request.model_dump()

        consumer.consumer = _FakeKafkaConsumer([mock_message])
        consumer._running = True  # allow processing
        
        # 테스트
        await consumer.consume_messages(processor)
        
        # 검증
        processor.assert_called_once()
        called_event = processor.call_args[0][0]
        assert called_event.request_id == sample_analysis_request.request_id


@pytest.mark.asyncio
class TestHeimdallIntegration:
    """Heimdall 통합 서비스 테스트"""
    
    async def test_process_analysis_request(self, sample_analysis_request):
        """분석 요청 처리 테스트"""
        from bifrost.heimdall_integration import HeimdallIntegrationService
        from bifrost.kafka_producer import KafkaProducerManager
        from bifrost.heimdall_store import HeimdallLogEntry
        
        # Mock config
        config = {
            "ollama": {"url": "http://localhost:11434", "model": "mistral"},
            "heimdall": {"ai_source": "local"}
        }
        
        # Mock producer manager
        producer_manager = AsyncMock(spec=KafkaProducerManager)
        producer_manager.send_result = AsyncMock(return_value=True)
        
        # Service 생성
        service = HeimdallIntegrationService(config, producer_manager)

        # Stub Heimdall DB access (avoid real Postgres connection)
        service.heimdall_store.get_log_entry = MagicMock(
            return_value=HeimdallLogEntry(
                log_id=sample_analysis_request.log_id,
                log_content="ERROR: connection timeout\nWARN: pool exhausted",
                service_name="test-service",
                environment="test",
                severity="HIGH",
                event_id="evt-123",
            )
        )
        
        # Mock AI 분석
        service._analyze_with_ai = AsyncMock(return_value={
            "response": "Test analysis response",
            "metadata": {"model": "mistral"}
        })
        
        # Mock DB 저장
        service._save_analysis_to_db = MagicMock(return_value=789)
        
        # 테스트
        await service.process_analysis_request(sample_analysis_request)
        
        # 검증
        service._analyze_with_ai.assert_called_once()
        service._save_analysis_to_db.assert_called_once()
        producer_manager.send_result.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
