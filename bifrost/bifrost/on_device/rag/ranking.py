"""Simple keyword/BM25-ish ranking (minimal deps)."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Tuple


_WORD_RE = re.compile(r"[A-Za-z0-9_\-]+", re.UNICODE)


def normalize_query(q: str) -> List[str]:
    q = (q or "").lower().strip()
    return [t for t in _WORD_RE.findall(q) if len(t) >= 2]


def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    return [t for t in _WORD_RE.findall(text) if len(t) >= 2]


@dataclass(frozen=True)
class Scored:
    chunk_id: int
    score: float


def score_chunks(query_tokens: List[str], chunks: Iterable[Tuple[int, str]]) -> List[Scored]:
    """Compute a lightweight BM25-ish score.

    - idf computed on the candidate set only (fast, deterministic)
    - tf is term frequency in a chunk
    """
    if not query_tokens:
        return []

    docs = []
    df = Counter()
    for chunk_id, content in chunks:
        tokens = tokenize(content)
        counts = Counter(tokens)
        docs.append((chunk_id, counts, len(tokens) or 1))
        for t in set(tokens):
            df[t] += 1

    N = len(docs) or 1

    def idf(t: str) -> float:
        # smoothed idf
        n = df.get(t, 0)
        return math.log((N + 1) / (n + 0.5))

    scored: List[Scored] = []
    for chunk_id, counts, length in docs:
        s = 0.0
        for t in query_tokens:
            tf = counts.get(t, 0)
            if tf:
                # small length normalization
                s += (tf / math.sqrt(length)) * idf(t)
        if s > 0:
            scored.append(Scored(chunk_id=chunk_id, score=s))

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored
