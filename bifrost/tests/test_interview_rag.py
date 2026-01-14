import os

import pytest

from bifrost.database import Database
from bifrost.on_device.rag.chunker import chunk_text
from bifrost.on_device.rag.ranking import normalize_query, score_chunks
from bifrost.on_device.rag.store import RunbookChunkStore
from bifrost.on_device.rag.ingest_service import RunbookIngestService
from bifrost.on_device.rag.retriever import RagRetriever
from bifrost.on_device.rag.context_builder import ContextBuilder


def test_chunker_splits_into_reasonable_sizes():
    text = "\n\n".join(["A" * 200, "B" * 200, "C" * 200, "D" * 200])
    chunks = chunk_text(text, min_chars=300, max_chars=800)
    assert len(chunks) >= 1
    assert all(1 <= len(c.content) <= 800 for c in chunks)


def test_normalize_query_supports_korean_tokens():
    tokens = normalize_query("카프카 consumer lag 급증 원인?")
    assert any(t.startswith("카프카") or t == "카프카" for t in tokens)


def test_ranking_scores_relevant_chunk_higher():
    q = normalize_query("postgres connection refused")
    chunks = [(1, "postgres connection refused error"), (2, "kafka consumer lag")]
    scored = score_chunks(q, chunks)
    assert scored
    assert scored[0].chunk_id == 1


def test_ingest_and_retrieve_roundtrip_sqlite_memory():
    db = Database("sqlite:///:memory:")
    db.init_db()

    store = RunbookChunkStore(db=db)
    ingest = RunbookIngestService(store=store)

    r = ingest.ingest(source="demo/runbook.md", tags=["demo"], text="postgres connection refused 발생\n\n대응 절차")
    assert r.chunks_ingested >= 1

    retriever = RagRetriever(store=store)
    results = retriever.retrieve("postgres connection refused", top_k=3)
    assert results
    assert any("postgres" in c.content.lower() for c in results)


def test_context_builder_includes_citations():
    builder = ContextBuilder(max_chars=2000)
    chunks = [
        type("C", (), {"id": 1, "source": "s", "content": "postgres connection refused", "score": 1.0})(),
    ]
    built = builder.build("postgres connection refused?", chunks)
    assert built.citations
    assert built.citations[0].chunk_id == 1
