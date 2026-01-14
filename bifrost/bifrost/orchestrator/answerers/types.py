"""Shared answerer types.

This module intentionally contains no lane-specific imports.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from bifrost.contracts.ask import Citation


@dataclass(frozen=True)
class AnswerAttempt:
    answer: str
    citations: List[Citation]
    provider: str
    token_estimate: Optional[int]
    char_estimate: int
