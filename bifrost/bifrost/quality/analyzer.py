"""
Quality Analyzer - Evaluates AI analysis responses.
"""

from __future__ import annotations

import re
from typing import Optional, List, Dict, Any

from bifrost.quality.models import (
    QualityScore,
    QualityDimension,
    AnalysisQualityReport,
)
from bifrost.logger import logger


class QualityAnalyzer:
    """
    Analyzes AI responses for quality metrics.
    
    Evaluates multiple dimensions:
    - Accuracy: Correctness indicators
    - Completeness: Coverage of key points
    - Relevance: Alignment with question
    - Clarity: Readability
    - Structure: Organization
    - Citation Quality: Source attribution
    """
    
    def __init__(self):
        # Uncertainty markers that may indicate lower confidence
        self.uncertainty_markers = [
            "i don't know", "not sure", "might be", "possibly",
            "could be", "uncertain", "unclear",
            "모르", "확실하지 않", "아마", "불확실",
        ]
        
        # Structure indicators
        self.structure_markers = [
            "1.", "2.", "3.",  # Numbered lists
            "-", "•", "*",  # Bullet points
            "##", "###",  # Headers
            "first", "second", "finally",  # Sequential markers
            "첫째", "둘째", "마지막",  # Korean sequential
        ]
        
        # Citation patterns
        self.citation_patterns = [
            r'\[chunk:\d+',  # Chunk references
            r'\[source:',  # Source references
            r'according to',  # Attribution phrases
            r'based on',
            r'문서에 따르면',
            r'참고:',
        ]
    
    def analyze(
        self,
        question: str,
        answer: str,
        citations: Optional[List[Any]] = None,
        latency_ms: Optional[int] = None,
        token_count: Optional[int] = None,
        provider: Optional[str] = None,
        lane: Optional[str] = None,
        model: Optional[str] = None,
        request_id: str = "",
        job_id: Optional[str] = None,
    ) -> AnalysisQualityReport:
        """
        Analyze an AI response and generate quality report.
        
        Args:
            question: The original question
            answer: The AI's response
            citations: List of citations/sources used
            latency_ms: Response latency in milliseconds
            token_count: Total tokens used
            provider: LLM provider name
            lane: Routing lane used
            model: Model name
            request_id: Request identifier
            job_id: Heimdall job identifier
        
        Returns:
            AnalysisQualityReport with all quality scores
        """
        scores = []
        
        # Analyze each dimension
        scores.append(self._analyze_relevance(question, answer))
        scores.append(self._analyze_completeness(question, answer))
        scores.append(self._analyze_clarity(answer))
        scores.append(self._analyze_conciseness(question, answer))
        scores.append(self._analyze_structure(answer))
        scores.append(self._analyze_confidence(answer))
        scores.append(self._analyze_citation_quality(answer, citations))
        
        if latency_ms is not None:
            scores.append(self._analyze_latency(latency_ms))
        
        if token_count is not None:
            scores.append(self._analyze_token_efficiency(question, answer, token_count))
        
        # Create report
        report = AnalysisQualityReport(
            request_id=request_id,
            job_id=job_id,
            scores=scores,
            provider=provider,
            lane=lane,
            model=model,
            latency_ms=latency_ms,
            token_count=token_count,
        )
        report.calculate_overall()
        
        logger.info(
            "quality_analysis_complete",
            request_id=request_id,
            overall_score=report.overall_score,
            overall_grade=report.overall_grade,
            provider=provider,
        )
        
        return report
    
    def _analyze_relevance(self, question: str, answer: str) -> QualityScore:
        """
        Analyze relevance of answer to question.
        
        Checks keyword overlap and semantic alignment.
        """
        q_lower = question.lower()
        a_lower = answer.lower()
        
        # Extract question keywords (simple tokenization)
        q_words = set(re.findall(r'\b\w{3,}\b', q_lower))
        a_words = set(re.findall(r'\b\w{3,}\b', a_lower))
        
        # Calculate overlap
        if not q_words:
            score = 0.5  # Can't determine
        else:
            overlap = len(q_words & a_words) / len(q_words)
            score = min(1.0, overlap * 1.5)  # Scale up slightly
        
        # Penalty for empty or very short answers
        if len(answer.strip()) < 50:
            score *= 0.5
        
        return QualityScore(
            dimension=QualityDimension.RELEVANCE,
            score=score,
            weight=1.2,  # Higher weight for relevance
            details=f"Keyword overlap: {len(q_words & a_words)}/{len(q_words)}",
            factors={"keyword_overlap": len(q_words & a_words), "question_keywords": len(q_words)},
        )
    
    def _analyze_completeness(self, question: str, answer: str) -> QualityScore:
        """
        Analyze completeness of the answer.
        
        Checks if answer addresses all parts of the question.
        """
        # Check for multiple question indicators
        question_indicators = ['?', '어떻게', '무엇', '왜', 'what', 'how', 'why', 'when', 'where']
        question_count = sum(1 for ind in question_indicators if ind in question.lower())
        question_count = max(1, question_count)
        
        # Check answer length relative to question complexity
        answer_length = len(answer.strip())
        
        # Simple heuristic: longer questions need longer answers
        min_expected = question_count * 100
        
        if answer_length >= min_expected * 2:
            length_score = 1.0
        elif answer_length >= min_expected:
            length_score = 0.8
        elif answer_length >= min_expected * 0.5:
            length_score = 0.6
        else:
            length_score = 0.4
        
        # Check for multi-part structure
        has_multiple_points = any(
            marker in answer for marker in ['1.', '2.', '첫째', 'first', 'second', '-', '•']
        )
        
        if has_multiple_points:
            length_score = min(1.0, length_score + 0.1)
        
        return QualityScore(
            dimension=QualityDimension.COMPLETENESS,
            score=length_score,
            weight=1.0,
            details=f"Answer length: {answer_length}, expected min: {min_expected}",
            factors={"answer_length": answer_length, "expected_min": min_expected},
        )
    
    def _analyze_clarity(self, answer: str) -> QualityScore:
        """
        Analyze clarity and readability.
        
        Checks sentence structure, word complexity, and formatting.
        """
        if not answer.strip():
            return QualityScore(
                dimension=QualityDimension.CLARITY,
                score=0.0,
                details="Empty answer",
            )
        
        # Calculate average sentence length
        sentences = re.split(r'[.!?。]', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return QualityScore(
                dimension=QualityDimension.CLARITY,
                score=0.5,
                details="Could not parse sentences",
            )
        
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Ideal sentence length is 10-20 words
        if 10 <= avg_sentence_length <= 20:
            sentence_score = 1.0
        elif 5 <= avg_sentence_length <= 30:
            sentence_score = 0.8
        else:
            sentence_score = 0.6
        
        # Check for formatting (newlines, paragraphs)
        has_paragraphs = '\n\n' in answer or answer.count('\n') >= 2
        formatting_bonus = 0.1 if has_paragraphs else 0
        
        score = min(1.0, sentence_score + formatting_bonus)
        
        return QualityScore(
            dimension=QualityDimension.CLARITY,
            score=score,
            weight=0.8,
            details=f"Avg sentence length: {avg_sentence_length:.1f} words",
            factors={"avg_sentence_length": avg_sentence_length, "sentence_count": len(sentences)},
        )
    
    def _analyze_conciseness(self, question: str, answer: str) -> QualityScore:
        """
        Analyze conciseness - not too verbose, not too brief.
        """
        q_len = len(question)
        a_len = len(answer)
        
        # Ideal ratio: answer 3-10x question length
        ratio = a_len / max(q_len, 1)
        
        if 3 <= ratio <= 10:
            score = 1.0
        elif 2 <= ratio <= 15:
            score = 0.8
        elif 1 <= ratio <= 20:
            score = 0.6
        else:
            score = 0.4
        
        return QualityScore(
            dimension=QualityDimension.CONCISENESS,
            score=score,
            weight=0.6,
            details=f"Answer/Question ratio: {ratio:.1f}x",
            factors={"ratio": ratio, "question_length": q_len, "answer_length": a_len},
        )
    
    def _analyze_structure(self, answer: str) -> QualityScore:
        """
        Analyze structure and organization.
        """
        structure_count = 0
        
        for marker in self.structure_markers:
            if marker in answer:
                structure_count += 1
        
        # More structure markers = better organization
        if structure_count >= 3:
            score = 1.0
        elif structure_count >= 2:
            score = 0.8
        elif structure_count >= 1:
            score = 0.6
        else:
            # No structure markers, check for natural flow
            score = 0.5 if len(answer) > 100 else 0.4
        
        return QualityScore(
            dimension=QualityDimension.STRUCTURE,
            score=score,
            weight=0.6,
            details=f"Structure markers found: {structure_count}",
            factors={"structure_markers": structure_count},
        )
    
    def _analyze_confidence(self, answer: str) -> QualityScore:
        """
        Analyze model confidence based on language indicators.
        """
        a_lower = answer.lower()
        
        uncertainty_count = sum(1 for marker in self.uncertainty_markers if marker in a_lower)
        
        # More uncertainty markers = lower confidence
        if uncertainty_count == 0:
            score = 0.9
        elif uncertainty_count == 1:
            score = 0.7
        elif uncertainty_count == 2:
            score = 0.5
        else:
            score = 0.3
        
        return QualityScore(
            dimension=QualityDimension.CONFIDENCE,
            score=score,
            weight=0.8,
            details=f"Uncertainty markers: {uncertainty_count}",
            factors={"uncertainty_markers": uncertainty_count},
        )
    
    def _analyze_citation_quality(
        self,
        answer: str,
        citations: Optional[List[Any]],
    ) -> QualityScore:
        """
        Analyze quality of source citations.
        """
        # Check for citation patterns in text
        citation_refs = 0
        for pattern in self.citation_patterns:
            citation_refs += len(re.findall(pattern, answer, re.IGNORECASE))
        
        # Check provided citations
        citation_count = len(citations) if citations else 0
        
        # Score based on citations
        if citation_count >= 3 or citation_refs >= 3:
            score = 1.0
        elif citation_count >= 2 or citation_refs >= 2:
            score = 0.8
        elif citation_count >= 1 or citation_refs >= 1:
            score = 0.6
        else:
            score = 0.3  # No citations
        
        return QualityScore(
            dimension=QualityDimension.CITATION_QUALITY,
            score=score,
            weight=0.7,
            details=f"Citations: {citation_count}, refs in text: {citation_refs}",
            factors={"citation_count": citation_count, "text_references": citation_refs},
        )
    
    def _analyze_latency(self, latency_ms: int) -> QualityScore:
        """
        Analyze response latency quality.
        """
        # Latency thresholds
        if latency_ms <= 1000:  # < 1s is excellent
            score = 1.0
        elif latency_ms <= 3000:  # < 3s is good
            score = 0.8
        elif latency_ms <= 5000:  # < 5s is acceptable
            score = 0.6
        elif latency_ms <= 10000:  # < 10s is poor
            score = 0.4
        else:
            score = 0.2
        
        return QualityScore(
            dimension=QualityDimension.LATENCY,
            score=score,
            weight=0.5,
            details=f"Latency: {latency_ms}ms",
            factors={"latency_ms": latency_ms},
        )
    
    def _analyze_token_efficiency(
        self,
        question: str,
        answer: str,
        token_count: int,
    ) -> QualityScore:
        """
        Analyze token usage efficiency.
        """
        # Estimate expected tokens
        expected = (len(question) + len(answer)) // 4
        
        # Efficiency ratio
        if expected == 0:
            ratio = 1.0
        else:
            ratio = token_count / expected
        
        # Ideal: actual ≈ expected
        if 0.8 <= ratio <= 1.2:
            score = 1.0
        elif 0.6 <= ratio <= 1.5:
            score = 0.8
        elif 0.4 <= ratio <= 2.0:
            score = 0.6
        else:
            score = 0.4
        
        return QualityScore(
            dimension=QualityDimension.TOKEN_EFFICIENCY,
            score=score,
            weight=0.4,
            details=f"Token efficiency: {ratio:.2f}x",
            factors={"token_count": token_count, "expected": expected, "ratio": ratio},
        )


# Global analyzer getter
_analyzer_instance: Optional[QualityAnalyzer] = None


def get_quality_analyzer() -> QualityAnalyzer:
    """Get the singleton quality analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = QualityAnalyzer()
    return _analyzer_instance
