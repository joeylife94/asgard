"""Chunker for runbooks/docs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Chunk:
    content: str


def chunk_text(text: str, min_chars: int = 300, max_chars: int = 800) -> List[Chunk]:
    """Split input into rough 300-800 char chunks.

    Heuristic:
    - normalize newlines
    - split by blank lines
    - then pack paragraphs into chunks within bounds
    """
    cleaned = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", cleaned) if p.strip()]

    chunks: List[str] = []
    buf: List[str] = []
    size = 0

    def flush():
        nonlocal buf, size
        if not buf:
            return
        combined = "\n\n".join(buf).strip()
        if combined:
            chunks.append(combined)
        buf = []
        size = 0

    for para in paragraphs:
        # if a single paragraph is huge, split hard
        if len(para) > max_chars:
            flush()
            start = 0
            while start < len(para):
                part = para[start : start + max_chars]
                chunks.append(part.strip())
                start += max_chars
            continue

        if size and (size + len(para) + 2) > max_chars:
            flush()

        buf.append(para)
        size += len(para) + 2

        if size >= min_chars:
            flush()

    flush()

    return [Chunk(content=c) for c in chunks]
