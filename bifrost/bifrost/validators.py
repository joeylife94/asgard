"""입력 검증"""

import re
from typing import Optional
from bifrost.exceptions import ValidationError


class InputValidator:
    """입력 검증기"""
    
    # 최대 크기 (10MB)
    MAX_LOG_SIZE = 10 * 1024 * 1024
    
    # 최소 크기 (10 bytes)
    MIN_LOG_SIZE = 10
    
    # 허용된 소스
    ALLOWED_SOURCES = ["local", "cloud"]
    
    # 허용된 포맷
    ALLOWED_FORMATS = ["markdown", "json", "plain"]
    
    @staticmethod
    def validate_log_content(content: str) -> str:
        """로그 내용 검증"""
        if not content or not content.strip():
            raise ValidationError("Log content cannot be empty")
        
        size = len(content.encode('utf-8'))
        
        if size < InputValidator.MIN_LOG_SIZE:
            raise ValidationError(f"Log content too small (min: {InputValidator.MIN_LOG_SIZE} bytes)")
        
        if size > InputValidator.MAX_LOG_SIZE:
            raise ValidationError(f"Log content too large (max: {InputValidator.MAX_LOG_SIZE} bytes)")
        
        return content
    
    @staticmethod
    def validate_source(source: str) -> str:
        """소스 검증"""
        if source not in InputValidator.ALLOWED_SOURCES:
            raise ValidationError(f"Invalid source. Allowed: {InputValidator.ALLOWED_SOURCES}")
        return source
    
    @staticmethod
    def validate_format(format_type: str) -> str:
        """포맷 검증"""
        if format_type not in InputValidator.ALLOWED_FORMATS:
            raise ValidationError(f"Invalid format. Allowed: {InputValidator.ALLOWED_FORMATS}")
        return format_type
    
    @staticmethod
    def validate_service_name(name: Optional[str]) -> Optional[str]:
        """서비스명 검증"""
        if not name:
            return None
        
        # 알파벳, 숫자, 하이픈, 언더스코어만 허용
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValidationError("Service name can only contain alphanumeric, hyphen, underscore")
        
        if len(name) > 100:
            raise ValidationError("Service name too long (max: 100)")
        
        return name
    
    @staticmethod
    def validate_tags(tags: list) -> list:
        """태그 검증"""
        if len(tags) > 20:
            raise ValidationError("Too many tags (max: 20)")
        
        validated = []
        for tag in tags:
            if not isinstance(tag, str):
                raise ValidationError("Tags must be strings")
            
            if len(tag) > 50:
                raise ValidationError(f"Tag too long: {tag} (max: 50)")
            
            validated.append(tag.strip())
        
        return validated
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """입력 새니타이징 (XSS 방지)"""
        # 기본적인 새니타이징
        dangerous_chars = ['<script>', '</script>', '<iframe>', '</iframe>']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text
