"""DB-backed runbook chunk store."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from bifrost.database import get_database, Database
from bifrost.models import RunbookChunk


@dataclass(frozen=True)
class StoredChunk:
    id: int
    source: str
    tags: List[str]
    content: str


class RunbookChunkStore:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_database()

    def ingest(self, *, source: str, tags: Optional[List[str]], contents: Sequence[str]) -> int:
        if not contents:
            return 0
        tags_list = tags or []
        with self.db.get_session() as session:
            for c in contents:
                session.add(RunbookChunk(source=source, tags=tags_list, content=c))
            # commit occurs in context manager
            return len(contents)

    def list_recent(self, limit: int = 500) -> List[StoredChunk]:
        with self.db.get_session() as session:
            rows = (
                session.query(RunbookChunk)
                .order_by(RunbookChunk.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                StoredChunk(id=r.id, source=r.source, tags=(r.tags or []), content=r.content)
                for r in rows
            ]

    def get_by_ids(self, ids: List[int]) -> List[StoredChunk]:
        if not ids:
            return []
        with self.db.get_session() as session:
            rows = session.query(RunbookChunk).filter(RunbookChunk.id.in_(ids)).all()
            # preserve input order
            mapping = {r.id: r for r in rows}
            out: List[StoredChunk] = []
            for cid in ids:
                r = mapping.get(cid)
                if r:
                    out.append(StoredChunk(id=r.id, source=r.source, tags=(r.tags or []), content=r.content))
            return out
