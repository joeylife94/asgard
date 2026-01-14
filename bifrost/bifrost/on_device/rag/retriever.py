"""RAG-lite retriever (on-device)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .ranking import normalize_query, score_chunks
from .store import RunbookChunkStore, StoredChunk


@dataclass(frozen=True)
class RetrievedChunk:
    id: int
    source: str
    content: str
    score: float


class RagRetriever:
    def __init__(self, store: Optional[RunbookChunkStore] = None):
        self.store = store or RunbookChunkStore()

    def retrieve(self, question: str, top_k: int = 5, scan_limit: int = 400) -> List[RetrievedChunk]:
        q_tokens = normalize_query(question)
        candidates = self.store.list_recent(limit=scan_limit)
        scored = score_chunks(q_tokens, [(c.id, c.content) for c in candidates])
        if not scored:
            return []

        top = scored[:top_k]
        ids = [s.chunk_id for s in top]
        by_id = {c.id: c for c in candidates}

        out: List[RetrievedChunk] = []
        for s in top:
            c = by_id.get(s.chunk_id)
            if not c:
                continue
            out.append(RetrievedChunk(id=c.id, source=c.source, content=c.content, score=s.score))
        return out
