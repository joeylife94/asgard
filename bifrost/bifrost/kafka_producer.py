"""Kafka Producer - Heimdall로 분석 결과 발행"""

import json
from aiokafka import AIOKafkaProducer
from typing import Optional
import logging

from bifrost.kafka_events import AnalysisResultEvent, DLQMessage
from bifrost.logger import logger


class AnalysisResultProducer:
    """분석 결과를 발행하는 Kafka Producer"""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        compression_type: str = "snappy"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.compression_type = compression_type
        self.producer: Optional[AIOKafkaProducer] = None
        
    async def start(self):
        """Producer 시작"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # 모든 replica 확인
            retries=3,
            max_in_flight_requests_per_connection=1,  # Ordering 보장
            compression_type=self.compression_type,
            linger_ms=10,  # 배치 처리
            batch_size=16384
        )
        await self.producer.start()
        logger.info(
            f"Kafka producer started",
            bootstrap_servers=self.bootstrap_servers
        )
        
    async def stop(self):
        """Producer 종료"""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def send_analysis_result(
        self,
        result_event: AnalysisResultEvent,
        topic: str = "analysis.result"
    ) -> bool:
        """
        분석 결과 발행
        
        Args:
            result_event: 분석 결과 이벤트
            topic: 발행할 토픽
            
        Returns:
            성공 여부
        """
        if not self.producer:
            raise RuntimeError("Producer not started. Call start() first.")
        
        try:
            # Pydantic 모델을 dict로 변환
            message = result_event.model_dump()
            
            # Key는 log_id로 설정 (파티셔닝 - 같은 로그는 같은 파티션으로)
            key = str(result_event.log_id)
            
            # 메시지 발행
            record_metadata = await self.producer.send_and_wait(
                topic,
                value=message,
                key=key
            )
            
            logger.info(
                f"Sent analysis result",
                request_id=result_event.request_id,
                log_id=result_event.log_id,
                topic=record_metadata.topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Failed to send analysis result",
                request_id=result_event.request_id,
                log_id=result_event.log_id,
                error=str(e),
                exc_info=True
            )
            return False


class DLQProducer:
    """Dead Letter Queue Producer"""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None
        
    async def start(self):
        """Producer 시작"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            acks='all'
        )
        await self.producer.start()
        logger.info("DLQ producer started")
        
    async def stop(self):
        """Producer 종료"""
        if self.producer:
            await self.producer.stop()
            logger.info("DLQ producer stopped")
    
    async def send_to_dlq(
        self,
        dlq_message: DLQMessage,
        topic: str = "dlq.failed"
    ) -> bool:
        """
        DLQ로 메시지 발행
        
        Args:
            dlq_message: DLQ 메시지
            topic: DLQ 토픽
            
        Returns:
            성공 여부
        """
        if not self.producer:
            raise RuntimeError("DLQ Producer not started. Call start() first.")
        
        try:
            message = dlq_message.model_dump()
            
            await self.producer.send_and_wait(topic, value=message)
            
            logger.info(
                f"Message sent to DLQ",
                original_topic=dlq_message.original_topic,
                original_offset=dlq_message.original_offset
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}", exc_info=True)
            return False


class KafkaProducerManager:
    """Kafka Producer 관리 클래스"""
    
    def __init__(self, config: dict):
        self.config = config
        self.producer: Optional[AnalysisResultProducer] = None
    
    async def start(self):
        """Producer 시작"""
        self.producer = AnalysisResultProducer(
            bootstrap_servers=self.config.get("bootstrap_servers", "localhost:9092"),
            compression_type=self.config.get("producer", {}).get(
                "compression_type", "snappy"
            )
        )
        await self.producer.start()
        logger.info("Kafka producer manager started")
    
    async def stop(self):
        """Producer 종료"""
        if self.producer:
            await self.producer.stop()
        logger.info("Kafka producer manager stopped")
    
    async def send_result(self, result_event: AnalysisResultEvent) -> bool:
        """분석 결과 전송"""
        if not self.producer:
            raise RuntimeError("Producer not started")
        
        topic = self.config.get("topics", {}).get("analysis_result", "analysis.result")
        return await self.producer.send_analysis_result(result_event, topic)
