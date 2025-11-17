"""Kafka 통합 테스트"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal

from bifrost.kafka_events import (
    AnalysisRequestEvent,
    AnalysisResultEvent,
    AnalysisResultData,
    AnalysisPriority
)


@pytest.fixture
def sample_analysis_request():
    """샘플 분석 요청 이벤트"""
    return AnalysisRequestEvent(
        request_id="test-request-123",
        log_id=12345,
        log_content="ERROR: Connection timeout to database",
        service_name="user-service",
        environment="test",
        analysis_type="error",
        priority=AnalysisPriority.HIGH,
        callback_topic="analysis.result",
        correlation_id="corr-123"
    )


@pytest.fixture
def sample_analysis_result():
    """샘플 분석 결과 이벤트"""
    result_data = AnalysisResultData(
        summary="Database connection timeout",
        root_cause="Connection pool exhausted",
        recommendation="Increase max_connections setting",
        severity="HIGH",
        confidence=Decimal("0.95")
    )
    
    return AnalysisResultEvent(
        request_id="test-request-123",
        correlation_id="corr-123",
        log_id=12345,
        analysis_result=result_data,
        bifrost_analysis_id=789,
        model="mistral-7b",
        duration_seconds=Decimal("2.5")
    )


class TestKafkaEvents:
    """Kafka 이벤트 스키마 테스트"""
    
    def test_analysis_request_event_creation(self, sample_analysis_request):
        """분석 요청 이벤트 생성 테스트"""
        event = sample_analysis_request
        
        assert event.request_id == "test-request-123"
        assert event.log_id == 12345
        assert event.service_name == "user-service"
        assert event.priority == AnalysisPriority.HIGH
    
    def test_analysis_request_event_serialization(self, sample_analysis_request):
        """분석 요청 이벤트 직렬화 테스트"""
        event = sample_analysis_request
        data = event.model_dump()
        
        assert isinstance(data, dict)
        assert data["request_id"] == "test-request-123"
        assert data["log_id"] == 12345
    
    def test_analysis_result_event_creation(self, sample_analysis_result):
        """분석 결과 이벤트 생성 테스트"""
        event = sample_analysis_result
        
        assert event.request_id == "test-request-123"
        assert event.log_id == 12345
        assert event.bifrost_analysis_id == 789
        assert event.analysis_result.severity == "HIGH"
        assert event.analysis_result.confidence == Decimal("0.95")


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
        
        mock_kafka_consumer = AsyncMock()
        mock_kafka_consumer.__aiter__ = lambda self: iter([mock_message])
        mock_kafka_consumer.commit = AsyncMock()
        
        consumer.consumer = mock_kafka_consumer
        consumer._running = False  # 1번만 실행
        
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
