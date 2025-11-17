"""에러 핸들러 & 커스텀 예외"""

from typing import Optional


class BifrostException(Exception):
    """Bifrost 기본 예외"""
    def __init__(self, message: str, code: str = "BIFROST_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class OllamaConnectionError(BifrostException):
    """Ollama 연결 실패"""
    def __init__(self, message: str = "Failed to connect to Ollama server"):
        super().__init__(message, "OLLAMA_CONNECTION_ERROR")


class BedrockAuthError(BifrostException):
    """Bedrock 인증 실패"""
    def __init__(self, message: str = "Bedrock authentication failed"):
        super().__init__(message, "BEDROCK_AUTH_ERROR")


class RateLimitError(BifrostException):
    """Rate limit 초과"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_ERROR")


class CacheError(BifrostException):
    """캐시 오류"""
    def __init__(self, message: str = "Cache operation failed"):
        super().__init__(message, "CACHE_ERROR")


class ValidationError(BifrostException):
    """입력 검증 실패"""
    def __init__(self, message: str = "Input validation failed"):
        super().__init__(message, "VALIDATION_ERROR")


class DatabaseError(BifrostException):
    """데이터베이스 오류"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")


def handle_exception(exc: Exception) -> dict:
    """예외를 구조화된 에러 응답으로 변환"""
    if isinstance(exc, BifrostException):
        return {
            "error": True,
            "code": exc.code,
            "message": exc.message,
        }
    else:
        return {
            "error": True,
            "code": "INTERNAL_ERROR",
            "message": str(exc),
        }
