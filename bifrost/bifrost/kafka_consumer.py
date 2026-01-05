"""Kafka Consumer - Heimdall로부터 분석 요청 수신"""

import asyncio
import json
from typing import Optional, Callable, Awaitable
import logging
from datetime import datetime

try:
    from aiokafka import AIOKafkaConsumer
except Exception:  # pragma: no cover
    AIOKafkaConsumer = None

from bifrost.kafka_events import AnalysisRequestEvent, DlqFailedEvent
from bifrost.logger import logger


class AnalysisRequestConsumer:
    """분석 요청을 소비하는 Kafka Consumer"""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "bifrost-consumer-group",
        topics: list = None,
        dlq_producer=None
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topics = topics or ["analysis.request"]
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.dlq_producer = dlq_producer
        self._running = False
        
    async def start(self):
        """Consumer 시작"""
        if AIOKafkaConsumer is None:
            raise RuntimeError(
                "aiokafka is required to start Kafka consumers. Install aiokafka or run the service in Docker/Linux."
            )
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=False,  # Manual commit
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            session_timeout_ms=30000,
            max_poll_records=100,
            max_poll_interval_ms=300000  # 5분
        )
        await self.consumer.start()
        self._running = True
        logger.info(
            f"Kafka consumer started",
            bootstrap_servers=self.bootstrap_servers,
            topics=self.topics,
            group_id=self.group_id
        )
        
    async def stop(self):
        """Consumer 종료"""
        self._running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
    
    async def consume_messages(
        self,
        processor_func: Callable[[AnalysisRequestEvent], Awaitable[None]]
    ):
        """
        메시지 소비 및 처리
        
        Args:
            processor_func: 메시지 처리 함수 (async)
        """
        if not self.consumer:
            raise RuntimeError("Consumer not started. Call start() first.")
        
        try:
            async for message in self.consumer:
                if not self._running:
                    break
                
                try:
                    # 메시지 수신 로깅
                    logger.debug(
                        f"Received message",
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset,
                        key=message.key.decode('utf-8') if message.key else None
                    )
                    
                    # 이벤트 파싱
                    event = AnalysisRequestEvent(**message.value)

                    job_id = event.normalized_job_id()
                    
                    logger.info(
                        f"Processing analysis request",
                        job_id=job_id,
                        log_id=event.log_id,
                        priority=event.priority
                    )
                    
                    # 비즈니스 로직 처리
                    await processor_func(event)
                    
                    # Manual commit (성공 시에만)
                    await self.consumer.commit()
                    
                    logger.info(
                        f"Analysis request processed successfully",
                        job_id=job_id,
                        log_id=event.log_id
                    )
                    
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Invalid JSON message",
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset,
                        error=str(e)
                    )
                    await self._send_to_dlq(message, str(e))
                    await self.consumer.commit()  # Skip invalid message
                    
                except Exception as e:
                    logger.error(
                        f"Error processing message",
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset,
                        error=str(e),
                        exc_info=True
                    )
                    
                    # DLQ로 전송
                    await self._send_to_dlq(message, str(e))
                    
                    # 메시지 건너뛰기 (무한 재처리 방지)
                    await self.consumer.commit()
                    
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
            raise
    
    async def _send_to_dlq(self, message, error_message: str):
        """실패한 메시지를 DLQ로 전송"""
        if not self.dlq_producer:
            logger.warning("DLQ producer not configured, message dropped")
            return
        
        try:
            payload = message.value if isinstance(message.value, dict) else {}
            dlq_msg = DlqFailedEvent(
                schema_version=1,
                job_id=payload.get("job_id") or payload.get("request_id"),
                idempotency_key=payload.get("idempotency_key"),
                error_code="CONSUMER_ERROR",
                error_message=error_message,
                trace_id=payload.get("trace_id") or payload.get("correlation_id"),
                original_topic=message.topic,
                original_partition=message.partition,
                original_offset=message.offset,
                payload=payload,
            )
            
            await self.dlq_producer.send_to_dlq(dlq_msg)
            
            logger.info(
                f"Message sent to DLQ",
                original_topic=message.topic,
                original_offset=message.offset
            )
            
        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {e}", exc_info=True)


class KafkaConsumerManager:
    """Kafka Consumer 관리 클래스"""
    
    def __init__(self, config: dict):
        self.config = config
        self.consumer: Optional[AnalysisRequestConsumer] = None
        self._task: Optional[asyncio.Task] = None
    
    async def start(self, processor_func):
        """Consumer 시작 및 백그라운드 실행"""
        from bifrost.kafka_producer import DLQProducer
        
        # DLQ Producer 초기화
        dlq_producer = DLQProducer(
            bootstrap_servers=self.config.get("bootstrap_servers", "localhost:9092")
        )
        await dlq_producer.start()
        
        # Consumer 초기화
        self.consumer = AnalysisRequestConsumer(
            bootstrap_servers=self.config.get("bootstrap_servers", "localhost:9092"),
            group_id=self.config.get("consumer", {}).get("group_id", "bifrost-consumer-group"),
            topics=[self.config.get("topics", {}).get("analysis_request", "analysis.request")],
            dlq_producer=dlq_producer
        )
        
        await self.consumer.start()
        
        # 백그라운드 태스크로 실행
        self._task = asyncio.create_task(
            self.consumer.consume_messages(processor_func)
        )
        
        logger.info("Kafka consumer manager started")
    
    async def stop(self):
        """Consumer 종료"""
        if self.consumer:
            await self.consumer.stop()
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Kafka consumer manager stopped")
