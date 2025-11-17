"""로그 필터링"""

import re
from typing import List, Optional
from enum import Enum


class SeverityLevel(str, Enum):
    """로그 심각도"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    CRITICAL = "CRITICAL"


class LogFilter:
    """로그 필터"""
    
    # 심각도 우선순위
    SEVERITY_PRIORITY = {
        "TRACE": 0,
        "DEBUG": 1,
        "INFO": 2,
        "WARN": 3,
        "WARNING": 3,
        "ERROR": 4,
        "FATAL": 5,
        "CRITICAL": 5,
    }
    
    @staticmethod
    def filter_by_severity(
        log_content: str,
        min_level: SeverityLevel = SeverityLevel.INFO
    ) -> str:
        """심각도로 필터링"""
        lines = log_content.split('\n')
        filtered_lines = []
        
        min_priority = LogFilter.SEVERITY_PRIORITY.get(min_level.value, 2)
        
        for line in lines:
            # 심각도 감지
            severity = LogFilter._detect_severity(line)
            
            if severity:
                priority = LogFilter.SEVERITY_PRIORITY.get(severity, 0)
                if priority >= min_priority:
                    filtered_lines.append(line)
            else:
                # 심각도 없는 줄은 포함 (컨텍스트)
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    @staticmethod
    def _detect_severity(line: str) -> Optional[str]:
        """라인에서 심각도 추출"""
        # 대소문자 무시
        line_upper = line.upper()
        
        # 패턴 매칭
        patterns = [
            r'\b(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\b',
            r'\[(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\]',
            r'level[=:]?\s*(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line_upper)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def filter_by_keyword(
        log_content: str,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> str:
        """키워드로 필터링"""
        lines = log_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            search_line = line if case_sensitive else line.lower()
            search_keywords = keywords if case_sensitive else [k.lower() for k in keywords]
            
            if any(keyword in search_line for keyword in search_keywords):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    @staticmethod
    def filter_by_time_range(
        log_content: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> str:
        """시간 범위로 필터링 (간단한 구현)"""
        # 타임스탬프 패턴 (ISO 8601, 일반적인 형식)
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}',
        ]
        
        lines = log_content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # 타임스탬프 추출
            timestamp = None
            for pattern in timestamp_patterns:
                match = re.search(pattern, line)
                if match:
                    timestamp = match.group(0)
                    break
            
            # 타임스탬프 없으면 포함
            if not timestamp:
                filtered_lines.append(line)
                continue
            
            # 범위 체크 (간단한 문자열 비교)
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    @staticmethod
    def extract_errors_only(log_content: str) -> str:
        """에러만 추출 (ERROR, FATAL, CRITICAL)"""
        return LogFilter.filter_by_severity(
            log_content,
            min_level=SeverityLevel.ERROR
        )
    
    @staticmethod
    def get_log_statistics(log_content: str) -> dict:
        """로그 통계"""
        lines = log_content.split('\n')
        
        stats = {
            "total_lines": len(lines),
            "by_severity": {
                "TRACE": 0,
                "DEBUG": 0,
                "INFO": 0,
                "WARN": 0,
                "ERROR": 0,
                "FATAL": 0,
            },
            "unknown": 0,
        }
        
        for line in lines:
            severity = LogFilter._detect_severity(line)
            if severity:
                # WARNING -> WARN 통일
                if severity == "WARNING":
                    severity = "WARN"
                if severity == "CRITICAL":
                    severity = "FATAL"
                
                if severity in stats["by_severity"]:
                    stats["by_severity"][severity] += 1
            else:
                stats["unknown"] += 1
        
        return stats
