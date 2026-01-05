"""캐시 관리자"""

import hashlib
import json
from typing import Optional, Any, Dict
from datetime import datetime, timedelta, timezone
from pathlib import Path


class CacheManager:
    """파일 기반 캐시 (Redis 대안)"""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_hours = ttl_hours
    
    def _get_cache_path(self, key: str) -> Path:
        """캐시 파일 경로"""
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        cache_file = self._get_cache_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # TTL 확인
            cached_at = datetime.fromisoformat(data["cached_at"])
            if cached_at.tzinfo is None:
                cached_at = cached_at.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            if now - cached_at > timedelta(hours=self.ttl_hours):
                cache_file.unlink()  # 만료된 캐시 삭제
                return None
            
            return data["value"]
        
        except Exception:
            return None
    
    def set(self, key: str, value: Any):
        """캐시 저장"""
        cache_file = self._get_cache_path(key)
        
        data = {
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "value": value,
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def delete(self, key: str):
        """캐시 삭제"""
        cache_file = self._get_cache_path(key)
        if cache_file.exists():
            cache_file.unlink()
    
    def clear_expired(self):
        """만료된 캐시 정리"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                cached_at = datetime.fromisoformat(data["cached_at"])
                if cached_at.tzinfo is None:
                    cached_at = cached_at.replace(tzinfo=timezone.utc)

                now = datetime.now(timezone.utc)
                if now - cached_at > timedelta(hours=self.ttl_hours):
                    cache_file.unlink()
                    count += 1
            except:
                cache_file.unlink()
                count += 1
        
        return count
    
    def stats(self) -> Dict[str, int]:
        """캐시 통계"""
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)
        
        return {
            "total_entries": len(files),
            "total_size_bytes": total_size,
            "cache_dir": str(self.cache_dir),
        }
