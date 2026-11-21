"""Regression coverage for issue #83 on the normal request processing path."""
import asyncio
import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call

import pytest
from aiokafka import TopicPartition
from aiokafka.errors import CommitFailedError

from bifrost.heimdall_integration import HeimdallIntegrationService
from bifrost.kafka_consumer import AnalysisRequestConsumer
from bifrost.kafka_events import AnalysisRequestEvent
from bifrost.ollama import OllamaClient


def payload(i):
    return dict(job_id=f"job-{i}", trace_id="trace", idempotency_key=f"key-{i}", log_id=i)


@pytest.mark.asyncio
async def test_blocking_steps_leave_event_loop_available(monkeypatch):
    loop = asyncio.get_running_loop()
    ticks = []
    def blocking_step(name, value):
        def run(*args, **kwargs):
            tick = threading.Event()
            loop.call_soon_threadsafe(tick.set)
            ticks.append((name, tick.wait(1)))
            return value
        return run

    service = HeimdallIntegrationService.__new__(HeimdallIntegrationService)
    service.config = {}
    entry = SimpleNamespace(log_content="log", service_name="svc", environment="test")
    service.heimdall_store = SimpleNamespace(get_log_entry=blocking_step("read", entry))
    service.preprocessor = SimpleNamespace(process=blocking_step("prepare", "log"))
    service.producer_manager = AsyncMock()
    service._save_analysis_to_db = blocking_step("write", 1)
    monkeypatch.setattr(OllamaClient, "analyze", blocking_step("generate", {
        "response": "analysis", "metadata": {"model": "local"},
    }))
    await service.process_analysis_request(AnalysisRequestEvent(**payload(1)))
    assert ticks == [(step, True) for step in ("read", "prepare", "generate", "write")]
    service.producer_manager.send_result.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("processing_fails", [False, True])
async def test_lost_commit_does_not_end_loop_or_create_spurious_dlq(processing_fails):
    records = [SimpleNamespace(topic="analysis.request", partition=i, offset=17,
                               key=None, value=payload(i)) for i in (1, 2)]
    kafka = MagicMock()
    kafka.__aiter__.return_value = records
    kafka.commit = AsyncMock(side_effect=[CommitFailedError(), None])
    consumer = AnalysisRequestConsumer(dlq_producer=AsyncMock())
    consumer.consumer = kafka
    consumer._running = True
    process = AsyncMock(side_effect=[ValueError("processing failed") if processing_fails else None, None])

    await consumer.consume_messages(process)
    assert process.await_count == 2
    assert kafka.commit.await_args_list == [
        call({TopicPartition(record.topic, record.partition): record.offset + 1}) for record in records
    ]
    if processing_fails:
        consumer.dlq_producer.send_to_dlq.assert_awaited_once()
        assert consumer.dlq_producer.send_to_dlq.await_args.args[0].error_message == "processing failed"
    else:
        consumer.dlq_producer.send_to_dlq.assert_not_awaited()


@pytest.mark.asyncio
async def test_configured_poll_interval_covers_generation_retries(monkeypatch):
    factory = MagicMock(return_value=AsyncMock())
    monkeypatch.setattr("bifrost.kafka_consumer.AIOKafkaConsumer", factory)
    await AnalysisRequestConsumer().start()
    client = OllamaClient()
    backoff = sum(2 ** i for i in range(client.max_retries - 1))
    assert factory.call_args.kwargs["max_poll_interval_ms"] > 1000 * (
        client.timeout * client.max_retries + backoff
    )
