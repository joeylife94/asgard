"""Runbook ingestion (on-device)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .chunker import chunk_text
from .store import RunbookChunkStore


@dataclass(frozen=True)
class IngestResult:
    chunks_ingested: int


class RunbookIngestService:
    def __init__(self, store: Optional[RunbookChunkStore] = None):
        self.store = store or RunbookChunkStore()

    def ingest(self, *, source: str, tags: Optional[List[str]], text: str) -> IngestResult:
        chunks = chunk_text(text)
        count = self.store.ingest(source=source, tags=tags, contents=[c.content for c in chunks])
        return IngestResult(chunks_ingested=count)
