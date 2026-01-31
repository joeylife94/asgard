"""
Semantic Matcher - Text similarity for cache lookups.
"""

from __future__ import annotations

import hashlib
import re
from typing import Optional, List, Tuple

from bifrost.logger import logger


class SemanticMatcher:
    """
    Provides semantic similarity matching for cache lookups.
    
    Uses a combination of:
    - Text normalization
    - N-gram similarity
    - Keyword extraction
    """
    
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        
        # Common stop words to ignore
        self.stop_words = {
            "a", "an", "the", "is", "it", "to", "in", "on", "of", "for",
            "with", "and", "or", "but", "what", "how", "why", "when",
            "where", "who", "which", "that", "this", "these", "those",
            "can", "could", "would", "should", "will", "be", "been",
            "was", "were", "are", "am", "has", "have", "had", "do",
            "does", "did", "from", "by", "at", "as", "if", "than",
        }
    
    def get_hash(self, text: str) -> str:
        """Generate hash for exact matching."""
        normalized = self.normalize(text)
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]
    
    def normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        normalized = self.normalize(text)
        words = normalized.split()
        
        # Filter out stop words and short words
        keywords = [
            w for w in words 
            if w not in self.stop_words and len(w) > 2
        ]
        
        return keywords
    
    def get_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Generate character n-grams."""
        text = self.normalize(text)
        if len(text) < n:
            return [text]
        return [text[i:i+n] for i in range(len(text) - n + 1)]
    
    def jaccard_similarity(self, set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Combines:
        - Keyword overlap (50%)
        - N-gram similarity (30%)
        - Length similarity (20%)
        """
        # Exact match
        if self.normalize(text1) == self.normalize(text2):
            return 1.0
        
        # Keyword similarity (50%)
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        keyword_sim = self.jaccard_similarity(keywords1, keywords2)
        
        # N-gram similarity (30%)
        ngrams1 = set(self.get_ngrams(text1, 3))
        ngrams2 = set(self.get_ngrams(text2, 3))
        ngram_sim = self.jaccard_similarity(ngrams1, ngrams2)
        
        # Length similarity (20%)
        len1 = len(self.normalize(text1))
        len2 = len(self.normalize(text2))
        length_sim = min(len1, len2) / max(len1, len2) if max(len1, len2) > 0 else 0
        
        # Weighted combination
        total_sim = (
            keyword_sim * 0.50 +
            ngram_sim * 0.30 +
            length_sim * 0.20
        )
        
        return total_sim
    
    def is_similar(self, text1: str, text2: str) -> bool:
        """Check if two texts are similar enough."""
        return self.similarity(text1, text2) >= self.threshold
    
    def find_best_match(
        self,
        query: str,
        candidates: List[Tuple[str, any]],
    ) -> Optional[Tuple[any, float]]:
        """
        Find the best matching candidate for a query.
        
        Args:
            query: The query to match
            candidates: List of (text, data) tuples
            
        Returns:
            (best_match_data, similarity_score) or None if no match above threshold
        """
        if not candidates:
            return None
        
        best_match = None
        best_score = 0.0
        
        for candidate_text, candidate_data in candidates:
            score = self.similarity(query, candidate_text)
            if score > best_score:
                best_score = score
                best_match = candidate_data
        
        if best_score >= self.threshold:
            return (best_match, best_score)
        
        return None
    
    def batch_similarity(
        self,
        query: str,
        texts: List[str],
    ) -> List[Tuple[int, float]]:
        """
        Calculate similarity scores for multiple texts.
        
        Returns list of (index, score) sorted by score descending.
        """
        results = []
        
        for idx, text in enumerate(texts):
            score = self.similarity(query, text)
            results.append((idx, score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
