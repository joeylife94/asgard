"""Context builder for incident/runbook assistant (on-device)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from bifrost.contracts.ask import Citation

from .retriever import RetrievedChunk


SYSTEM_INSTRUCTION = (
    "당신은 장애 대응/런북 Q&A 어시스턴트입니다. "
    "가능하면 제공된 런북 스니펫에 근거해서만 답하세요. "
    "런북에 충분한 정보가 없으면 '확신할 수 없다'고 명확히 말하세요. "
    "임의의 커맨드/자격증명/위험한 조치를 지어내지 마세요. "
    "검증 절차가 포함된 단계별(운영 안전) 가이드를 선호합니다."
)


@dataclass(frozen=True)
class BuiltContext:
    prompt: str
    citations: List[Citation]
    char_estimate: int


def _preview(text: str, limit: int = 160) -> str:
    t = " ".join((text or "").split())
    if len(t) <= limit:
        return t
    return t[: limit - 1] + "…"


class ContextBuilder:
    def __init__(self, max_chars: int = 6500):
        self.max_chars = max_chars

    def build(self, question: str, chunks: List[RetrievedChunk]) -> BuiltContext:
        citations: List[Citation] = [
            Citation(chunk_id=c.id, source=c.source, preview=_preview(c.content)) for c in chunks
        ]

        parts: List[str] = []
        parts.append(f"SYSTEM:\n{SYSTEM_INSTRUCTION}\n")
        parts.append(f"QUESTION:\n{question.strip()}\n")

        if chunks:
            parts.append("RUNBOOK SNIPPETS (with citations):\n")
            for c in chunks:
                parts.append(f"[chunk:{c.id} source:{c.source}]\n{c.content.strip()}\n")
        else:
            parts.append("RUNBOOK SNIPPETS: (none available)\n")

        parts.append(
            "INSTRUCTIONS:\n"
            "- Answer using the snippets, cite chunk ids like [chunk:123].\n"
            "- If not enough info, say you cannot answer confidently and summarize the closest snippets.\n"
        )

        prompt = "\n".join(parts)
        if len(prompt) > self.max_chars:
            # Trim by dropping tail of snippets first
            head = "\n".join(parts[:3])
            tail_budget = max(self.max_chars - len(head) - 20, 0)
            snippet_text = "\n".join(parts[3:])
            prompt = head + "\n" + snippet_text[:tail_budget]

        return BuiltContext(prompt=prompt, citations=citations, char_estimate=len(prompt))
