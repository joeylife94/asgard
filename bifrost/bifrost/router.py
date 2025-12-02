"""
Privacy Router - Intelligent Track A/B Routing
==============================================

GDPR-Compliant Log Analysis Routing:
- Track A (Local): Sensitive data → Ollama (Llama 3.1 8B)
- Track B (Cloud): General queries → AWS Bedrock (Claude 3 Sonnet)

Author: DongPT Lab
License: Apache 2.0
"""

import re
from typing import Tuple, Dict, List
from enum import Enum


class Track(str, Enum):
    """AI 처리 트랙"""
    A = "local"   # Privacy-First: Ollama
    B = "cloud"   # Performance: AWS Bedrock


class SensitivityLevel(str, Enum):
    """데이터 민감도 레벨"""
    HIGH = "high"       # PII, 금융정보, 인증정보
    MEDIUM = "medium"   # 내부 IP, 사용자 ID, 세션 데이터
    LOW = "low"         # 일반 로그, 시스템 메트릭


class PrivacyRouter:
    """
    Privacy-based intelligent routing for Two-Track AI Strategy.
    
    Automatically classifies log content sensitivity and routes to:
    - Track A (Local Ollama): High/Medium sensitivity data (GDPR compliance)
    - Track B (Cloud Bedrock): Low sensitivity data (cost-effective)
    """
    
    # High-sensitivity patterns (PII, Financial, Authentication)
    HIGH_PATTERNS = [
        # Personal Identifiable Information  
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',  # Email (removed \b for Korean compat)
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN (US)
        r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card (16 digits)
        
        # Financial & Payment
        r'\b(?:IBAN|BIC|SWIFT)[\s:]+[A-Z0-9]{4,}\b',  # Relaxed length requirement
        r'\b(?:card|credit|debit|payment)[\s_-]?(?:number|num|no)[\s:]+\d{4,}\b',
        r'\b(?:account|acct)[\s_-]?(?:number|num|no)[\s:]+\d{5,}\b',
        
        # Authentication & Security (more specific patterns)
        r'\b(?:password|passwd|pwd)[\s:=]+\S{3,}\b',
        r'\b(?:secret|api[_-]?key|auth[_-]?key)[\s:=]+[A-Za-z0-9\-_.]{8,}\b',
        r'\bbearer[\s]+[A-Za-z0-9\-_.]{20,}\b',
        r'(?:jwt|token)[\s:]+eyJ[A-Za-z0-9\-_.]+',  # JWT pattern (relaxed boundaries)
        r'\bauthorization[\s]*:[\s]*(?:bearer|basic)[\s]+[A-Za-z0-9\-_.]{20,}\b',
        
        # GDPR-specific EU identifiers
        r'\b(?:passport|driving[_-]?license|national[_-]?id)[\s:]+[A-Z0-9]{6,}\b',
        r'\b(?:patient|member|customer)[_-]?id[\s:]+\d{6,}\b',
    ]
    
    # Medium-sensitivity patterns (Internal IPs, User IDs, Session Data)
    MEDIUM_PATTERNS = [
        # Internal network
        r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # Private IP 10.x.x.x
        r'\b172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}\b',  # Private IP 172.16-31.x.x
        r'\b192\.168\.\d{1,3}\.\d{1,3}\b',  # Private IP 192.168.x.x
        
        # Session & User identifiers
        r'\b(?:user|session|trace)[_-]?id[\s:=]+[A-Za-z0-9\-_]+\b',
        r'\bcookie[\s]*:[\s]*[A-Za-z0-9\-_=;]+\b',
        r'\bx-(?:request|correlation|trace)-id[\s]*:[\s]*[A-Za-z0-9\-_]+\b',
        
        # Database connection strings (without passwords)
        r'\bjdbc:(?:mysql|postgresql|oracle|sqlserver)://[\w\.\-:/@]+\b',
        r'\bmongodb(?:\+srv)?://[\w\.\-:/@]+\b',
    ]
    
    # GDPR keywords (EU data protection context)
    GDPR_KEYWORDS = [
        'gdpr', 'dsgvo', 'rgpd',  # GDPR in various languages
        'personal data', 'personenbezogene daten', 'données personnelles',
        'data subject', 'betroffene person', 'personne concernée',
        'consent', 'einwilligung', 'consentement',
        'right to erasure', 'recht auf löschung', 'droit à l\'effacement',
        'data breach', 'datenpanne', 'violation de données',
    ]
    
    def __init__(self):
        """Initialize Privacy Router with compiled regex patterns."""
        self.high_regex = [re.compile(p, re.IGNORECASE) for p in self.HIGH_PATTERNS]
        self.medium_regex = [re.compile(p, re.IGNORECASE) for p in self.MEDIUM_PATTERNS]
    
    def classify_sensitivity(self, content: str) -> Tuple[SensitivityLevel, List[str]]:
        """
        Classify content sensitivity level.
        
        Args:
            content: Log content to analyze
            
        Returns:
            Tuple of (SensitivityLevel, list of detected patterns)
        """
        detected = []
        
        # Check HIGH patterns (PII, Financial, Auth)
        for pattern in self.high_regex:
            if pattern.search(content):
                detected.append(f"HIGH: {pattern.pattern[:50]}...")
        
        if detected:
            return SensitivityLevel.HIGH, detected
        
        # Check GDPR keywords
        content_lower = content.lower()
        gdpr_found = [kw for kw in self.GDPR_KEYWORDS if kw in content_lower]
        if gdpr_found:
            detected.append(f"GDPR keywords: {', '.join(gdpr_found[:3])}")
            return SensitivityLevel.HIGH, detected
        
        # Check MEDIUM patterns (Internal IPs, Sessions)
        for pattern in self.medium_regex:
            if pattern.search(content):
                detected.append(f"MEDIUM: {pattern.pattern[:50]}...")
        
        if detected:
            return SensitivityLevel.MEDIUM, detected
        
        # Default: LOW sensitivity
        return SensitivityLevel.LOW, ["No sensitive data detected"]
    
    def route(self, content: str) -> Dict[str, any]:
        """
        Route content to appropriate AI track.
        
        Args:
            content: Log content to route
            
        Returns:
            Dictionary with routing decision:
            {
                "track": "local" or "cloud",
                "sensitivity": "high" / "medium" / "low",
                "reason": "Detected: ...",
                "detected_patterns": [...]
            }
        """
        sensitivity, detected = self.classify_sensitivity(content)
        
        # Routing logic: HIGH/MEDIUM → Track A, LOW → Track B
        if sensitivity in (SensitivityLevel.HIGH, SensitivityLevel.MEDIUM):
            track = Track.A
            reason = f"Privacy-sensitive data detected ({sensitivity.value})"
        else:
            track = Track.B
            reason = "General log data - using cloud for cost efficiency"
        
        return {
            "track": track.value,
            "sensitivity": sensitivity.value,
            "reason": reason,
            "detected_patterns": detected,
        }
    
    def explain_route(self, content: str) -> str:
        """
        Human-readable explanation of routing decision.
        
        Args:
            content: Log content
            
        Returns:
            Formatted explanation string
        """
        result = self.route(content)
        
        explanation = f"""
🎯 Routing Decision: Track {result['track'].upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Sensitivity: {result['sensitivity'].upper()}
💡 Reason: {result['reason']}

🔍 Detected Patterns:
"""
        for pattern in result['detected_patterns']:
            explanation += f"  • {pattern}\n"
        
        if result['track'] == 'local':
            explanation += "\n✅ Processing with Ollama (GDPR-compliant on-premise)"
        else:
            explanation += "\n☁️  Processing with AWS Bedrock (cost-effective cloud)"
        
        return explanation


# Singleton instance for global use
_router_instance = None

def get_router() -> PrivacyRouter:
    """Get or create singleton Privacy Router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = PrivacyRouter()
    return _router_instance
