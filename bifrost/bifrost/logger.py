"""구조화된 로깅"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json


class StructuredLogger:
    """JSON 구조화 로거"""
    
    def __init__(self, name: str = "bifrost", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 핸들러가 없으면 추가
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JsonFormatter())
            self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """구조화된 로그 출력"""
        extra = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        getattr(self.logger, level.lower())(message, extra={"structured": extra})
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)


class JsonFormatter(logging.Formatter):
    """JSON 포맷터"""
    
    def format(self, record):
        if hasattr(record, 'structured'):
            return json.dumps(record.structured, ensure_ascii=False)
        return super().format(record)


# 전역 로거
logger = StructuredLogger()
