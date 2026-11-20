"""Consumer liveness tests (R-034).

A long, blocking generation must not starve the asyncio event loop (the
aiokafka heartbeat runs on it), a failed commit must not be treated as a
processing failure, and the client-side poll interval must cover the worst
case of one analysis. No broker, network or real DB is used.
"""

import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiokafka.errors import CommitFailedError

import bifrost.heimdall_integration as heimdall_integration
import bifrost.kafka_consumer as kafka_consumer
from bifrost.kafka_consumer import (
    AnalysisRequestConsumer,
    KafkaConsumerManager,
)
from bifrost.kafka_events import AnalysisRequestEvent
from bifrost.ollama import OllamaClient

# Upper bound for any awaited call so that a defect can never hang the run.
GUARD_SECONDS = 60


def _valid_payload(n: int) -> dict:
    return {
        "job_id": "00000000-0000-0000-0000-00000000000%d" % n,
        "idempotency_key": "idem-%d" % n,
        "log_id": 1000 + n,
        "priority": "HIGH",
        "trace_id": "trace-%d" % n,
    }


def _make_event(n: int = 1) -> AnalysisRequestEvent:
    return AnalysisRequestEvent(**_valid_payload(n))


def _make_message(n: int, offset: int, topic: str = "analysis.request", partition: int = 0):
    return SimpleNamespace(
        topic=topic,
        partition=partition,
        offset=offset,
        key=None,
        value=_valid_payload(n),
    )


class FakeConsumer:
    """Async-iterable stand-in for AIOKafkaConsumer."""

    def __init__(self, messages, commit_side_effect=None):
        self._messages = list(messages)
        self.commit = AsyncMock(side_effect=commit_side_effect)

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for message in self._messages:
            yield message


def _fail_first_commit():
    calls = []

    async def commit(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise CommitFailedError()

    return commit


def _make_consumer(messages, commit_side_effect=None):
    dlq = MagicMock()
    dlq.send_to_dlq = AsyncMock(return_value=True)
    consumer = AnalysisRequestConsumer(dlq_producer=dlq)
    consumer.consumer = FakeConsumer(messages, commit_side_effect)
    consumer._running = True
    return consumer, dlq


# --------------------------------------------------------------------------
# Event loop responsiveness during blocking work
# --------------------------------------------------------------------------

class _FakeStore:
    def __init__(self, delay: float = 0.0):
        self.delay = delay

    def get_log_entry(self, log_id):
        if self.delay:
            time.sleep(self.delay)
        return SimpleNamespace(
            log_content="ERROR something failed",
            service_name="svc",
            environment="test",
        )


class _FakeDb:
    def __init__(self, delay: float = 0.0):
        self.delay = delay

    def save_analysis(self, **kwargs):
        if self.delay:
            time.sleep(self.delay)
        return 42


def _build_service(store_delay: float = 0.0, db_delay: float = 0.0):
    producer = MagicMock()
    producer.send_result = AsyncMock(return_value=True)
    producer.send_dlq = AsyncMock(return_value=True)
    with patch.object(heimdall_integration, "get_database", return_value=_FakeDb(db_delay)), \
            patch.object(heimdall_integration, "HeimdallStore", return_value=_FakeStore(store_delay)):
        service = heimdall_integration.HeimdallIntegrationService(
            config={"heimdall": {"ai_source": "local"}}, producer_manager=producer
        )
    return service, producer


def _fake_ollama(delay: float):
    class FakeOllamaClient:
        def __init__(self, *args, **kwargs):
            pass

        def analyze(self, prompt, stream=False):
            if delay:
                time.sleep(delay)
            return {
                "response": "## Summary\nok\n## Issues\nnone\n## Recommendation\nnone",
                "metadata": {
                    "model": "fake-model",
                    "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
                },
            }

    return FakeOllamaClient


async def _run_with_ticker(coro):
    ticks = 0
    stop = asyncio.Event()

    async def ticker():
        nonlocal ticks
        while not stop.is_set():
            await asyncio.sleep(0.05)
            ticks += 1

    ticker_task = asyncio.ensure_future(ticker())
    try:
        await asyncio.wait_for(coro, timeout=GUARD_SECONDS)
    finally:
        stop.set()
        await ticker_task
    return ticks


@pytest.mark.asyncio
async def test_blocking_analyze_keeps_event_loop_responsive(monkeypatch):
    monkeypatch.setattr(heimdall_integration, "OllamaClient", _fake_ollama(1.0))
    service, producer = _build_service()

    ticks = await _run_with_ticker(service.process_analysis_request(_make_event()))

    assert ticks >= 10, "event loop was blocked during analyze (ticks=%d)" % ticks
    producer.send_result.assert_awaited_once()
    sent = producer.send_result.await_args.args[0]
    assert sent.status == "SUCCEEDED"


@pytest.mark.asyncio
async def test_blocking_store_and_save_keep_event_loop_responsive(monkeypatch):
    monkeypatch.setattr(heimdall_integration, "OllamaClient", _fake_ollama(0.0))
    service, producer = _build_service(store_delay=0.5, db_delay=0.5)

    ticks = await _run_with_ticker(service.process_analysis_request(_make_event()))

    assert ticks >= 10, "event loop was blocked by store/db calls (ticks=%d)" % ticks
    producer.send_result.assert_awaited_once()
    assert producer.send_result.await_args.args[0].status == "SUCCEEDED"


# --------------------------------------------------------------------------
# Commit handling
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_commit_failure_after_success_is_not_sent_to_dlq():
    consumer, dlq = _make_consumer(
        [_make_message(1, 10), _make_message(2, 11)],
        commit_side_effect=_fail_first_commit(),
    )
    processed = []

    async def processor(event):
        processed.append(event.log_id)

    await asyncio.wait_for(consumer.consume_messages(processor), timeout=GUARD_SECONDS)

    assert processed == [1001, 1002]
    dlq.send_to_dlq.assert_not_awaited()


@pytest.mark.asyncio
async def test_commit_failure_on_error_branch_does_not_end_the_loop():
    consumer, dlq = _make_consumer(
        [_make_message(1, 10), _make_message(2, 11)],
        commit_side_effect=CommitFailedError(),
    )
    processed = []

    async def processor(event):
        processed.append(event.log_id)
        if event.log_id == 1001:
            raise RuntimeError("boom")

    await asyncio.wait_for(consumer.consume_messages(processor), timeout=GUARD_SECONDS)

    assert processed == [1001, 1002]
    assert dlq.send_to_dlq.await_count == 1
    dlq_event = dlq.send_to_dlq.await_args.args[0]
    assert dlq_event.original_offset == 10


@pytest.mark.asyncio
async def test_processing_failure_goes_to_dlq_and_commits_once():
    message = _make_message(1, 10, topic="analysis.request", partition=3)
    consumer, dlq = _make_consumer([message])

    async def processor(event):
        raise RuntimeError("boom")

    await asyncio.wait_for(consumer.consume_messages(processor), timeout=GUARD_SECONDS)

    assert dlq.send_to_dlq.await_count == 1
    assert consumer.consumer.commit.await_count == 1
    args = consumer.consumer.commit.await_args
    offsets = args.args[0] if args.args else args.kwargs.get("offsets")
    assert offsets is not None, "commit must name the processed message's offset explicitly"
    assert len(offsets) == 1
    (tp, offset), = offsets.items()
    assert (tp.topic, tp.partition) == ("analysis.request", 3)
    assert offset == 11


# --------------------------------------------------------------------------
# Client settings
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_max_poll_interval_covers_worst_case_analyze():
    captured = {}

    class RecordingConsumer:
        def __init__(self, *topics, **kwargs):
            captured["topics"] = topics
            captured["kwargs"] = kwargs

        async def start(self):
            pass

        async def stop(self):
            pass

    default_client = OllamaClient()
    worst_case_seconds = (
        default_client.timeout * default_client.max_retries
        + sum(2 ** i for i in range(default_client.max_retries - 1))
    )

    with patch.object(kafka_consumer, "AIOKafkaConsumer", RecordingConsumer):
        consumer = AnalysisRequestConsumer()
        await asyncio.wait_for(consumer.start(), timeout=GUARD_SECONDS)

    kwargs = captured["kwargs"]
    assert kwargs["max_poll_interval_ms"] / 1000 > worst_case_seconds
    assert kwargs["session_timeout_ms"] == 30000
    assert kwargs["enable_auto_commit"] is False


# --------------------------------------------------------------------------
# Background task visibility
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_consumer_task_death_is_logged():
    class FakeDLQProducer:
        def __init__(self, *args, **kwargs):
            pass

        async def start(self):
            pass

    class DyingConsumer:
        def __init__(self, *args, **kwargs):
            pass

        async def start(self):
            pass

        async def stop(self):
            pass

        async def consume_messages(self, processor_func):
            raise RuntimeError("consumer loop died")

    fake_logger = MagicMock()
    manager = KafkaConsumerManager({"bootstrap_servers": "unused:9092"})

    with patch("bifrost.kafka_producer.DLQProducer", FakeDLQProducer), \
            patch.object(kafka_consumer, "AnalysisRequestConsumer", DyingConsumer), \
            patch.object(kafka_consumer, "logger", fake_logger):
        await asyncio.wait_for(manager.start(AsyncMock()), timeout=GUARD_SECONDS)
        try:
            await asyncio.wait_for(manager._task, timeout=GUARD_SECONDS)
        except RuntimeError:
            pass
        # let done-callbacks run
        await asyncio.sleep(0)
        await asyncio.sleep(0)

    error_messages = [str(c.args[0]) for c in fake_logger.error.call_args_list if c.args]
    assert any("consumer" in m.lower() and "ended" in m.lower() for m in error_messages), (
        "expected an error log when the consumer task dies, got: %r" % error_messages
    )
