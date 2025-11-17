"""로그 전처리 모듈"""

import re
from typing import List


class LogPreprocessor:
    """로그 전처리기"""
    
    def __init__(
        self,
        max_size_mb: float = 5.0,
        truncate: bool = True,
        remove_timestamps: bool = False,
    ):
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.truncate = truncate
        self.remove_timestamps = remove_timestamps
    
    def process(self, log_content: str) -> str:
        """로그 전처리 파이프라인"""
        # 1. 크기 제한
        if self.truncate and len(log_content.encode('utf-8')) > self.max_size_bytes:
            log_content = self._truncate_log(log_content)
        
        # 2. 타임스탬프 제거 (선택)
        if self.remove_timestamps:
            log_content = self._remove_timestamps(log_content)
        
        # 3. 기본 정리
        log_content = self._clean_log(log_content)
        
        return log_content
    
    def _truncate_log(self, content: str) -> str:
        """로그를 최대 크기로 자르기 (앞뒤 유지)"""
        lines = content.split('\n')
        total_lines = len(lines)
        
        # 앞 40%, 뒤 40% 유지
        keep_count = int(total_lines * 0.4)
        
        if keep_count < 10:
            # 너무 적으면 전체 유지
            truncated = '\n'.join(lines[:int(total_lines * 0.8)])
        else:
            head = lines[:keep_count]
            tail = lines[-keep_count:]
            truncated = '\n'.join(head) + \
                       f'\n\n... [중간 {total_lines - 2*keep_count}줄 생략] ...\n\n' + \
                       '\n'.join(tail)
        
        return truncated
    
    def _remove_timestamps(self, content: str) -> str:
        """일반적인 타임스탬프 패턴 제거"""
        patterns = [
            r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?',  # ISO
            r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',  # Apache
            r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',  # Syslog
        ]
        
        result = content
        for pattern in patterns:
            result = re.sub(pattern, '', result)
        
        return result
    
    def _clean_log(self, content: str) -> str:
        """기본 정리: 빈 줄 정리, 공백 정리"""
        # 연속된 빈 줄을 하나로
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # 각 줄의 앞뒤 공백 제거
        lines = [line.rstrip() for line in content.split('\n')]
        
        return '\n'.join(lines)
    
    def get_stats(self, content: str) -> dict:
        """로그 통계"""
        lines = content.split('\n')
        return {
            "total_lines": len(lines),
            "total_bytes": len(content.encode('utf-8')),
            "total_chars": len(content),
            "non_empty_lines": len([l for l in lines if l.strip()]),
        }
