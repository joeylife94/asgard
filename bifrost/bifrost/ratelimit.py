"""Rate Limiter (API 보호)"""

import time
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """토큰 버킷 기반 Rate Limiter"""
    
    def __init__(self, requests_per_hour: int = 100):
        self.requests_per_hour = requests_per_hour
        self.buckets: Dict[str, Dict] = defaultdict(lambda: {
            "tokens": requests_per_hour,
            "last_update": time.time()
        })
        self.lock = Lock()
    
    def _refill_tokens(self, bucket: Dict):
        """토큰 리필 (시간 경과에 따라)"""
        now = time.time()
        elapsed = now - bucket["last_update"]
        
        # 시간당 requests_per_hour 비율로 리필
        tokens_to_add = (elapsed / 3600) * self.requests_per_hour
        bucket["tokens"] = min(
            self.requests_per_hour,
            bucket["tokens"] + tokens_to_add
        )
        bucket["last_update"] = now
    
    def is_allowed(self, key: str) -> bool:
        """요청 허용 여부 확인"""
        with self.lock:
            bucket = self.buckets[key]
            self._refill_tokens(bucket)
            
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True
            return False
    
    def get_remaining(self, key: str) -> int:
        """남은 요청 수"""
        with self.lock:
            bucket = self.buckets[key]
            self._refill_tokens(bucket)
            return int(bucket["tokens"])
    
    def reset(self, key: str):
        """특정 키 리셋"""
        with self.lock:
            if key in self.buckets:
                del self.buckets[key]


class WindowRateLimiter:
    """슬라이딩 윈도우 Rate Limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, key: str) -> bool:
        """요청 허용 여부"""
        with self.lock:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            cutoff = now - timedelta(seconds=self.window_seconds)
            
            # 오래된 요청 제거
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            # 제한 확인
            if len(self.requests[key]) < self.max_requests:
                self.requests[key].append(now)
                return True
            return False
    
    def get_remaining(self, key: str) -> int:
        """남은 요청 수"""
        with self.lock:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            cutoff = now - timedelta(seconds=self.window_seconds)
            
            # 오래된 요청 제거
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            return max(0, self.max_requests - len(self.requests[key]))
