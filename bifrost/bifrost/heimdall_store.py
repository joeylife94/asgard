"""Heimdall data access (read-only) for Kafka worker.

We avoid Heimdall<->Bifrost REST on the main path; Bifrost fetches the input
payload via Postgres using log_id.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import create_engine, text


@dataclass(frozen=True)
class HeimdallLogEntry:
    log_id: int
    log_content: str
    service_name: Optional[str]
    environment: Optional[str]
    severity: Optional[str]
    event_id: Optional[str]


class HeimdallStore:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)

    def get_log_entry(self, log_id: int) -> Optional[HeimdallLogEntry]:
        sql = text(
            """
            SELECT id, log_content, service_name, environment, severity, event_id
            FROM log_entries
            WHERE id = :log_id
            """
        )
        with self.engine.connect() as conn:
            row = conn.execute(sql, {"log_id": log_id}).mappings().first()
            if not row:
                return None
            return HeimdallLogEntry(
                log_id=int(row["id"]),
                log_content=str(row["log_content"]),
                service_name=row.get("service_name"),
                environment=row.get("environment"),
                severity=row.get("severity"),
                event_id=row.get("event_id"),
            )
