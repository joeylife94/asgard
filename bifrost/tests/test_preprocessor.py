"""전처리 테스트"""

import pytest
from bifrost.preprocessor import LogPreprocessor


def test_truncate_large_log():
    """큰 로그 자르기"""
    preprocessor = LogPreprocessor(max_size_mb=0.001, truncate=True)
    
    # 큰 로그 생성
    large_log = "\n".join([f"Line {i}" for i in range(1000)])
    
    processed = preprocessor.process(large_log)
    
    # 크기가 줄어들었는지 확인
    assert len(processed) < len(large_log)
    assert "생략" in processed or "omit" in processed.lower()


def test_remove_timestamps():
    """타임스탬프 제거"""
    preprocessor = LogPreprocessor(remove_timestamps=True)
    
    log = "2024-10-25 10:15:32 INFO Application started"
    processed = preprocessor.process(log)
    
    # 타임스탬프가 제거되었는지 확인
    assert "2024-10-25" not in processed
    assert "Application started" in processed


def test_get_stats():
    """로그 통계"""
    preprocessor = LogPreprocessor()
    
    log = "Line 1\nLine 2\n\nLine 3"
    stats = preprocessor.get_stats(log)
    
    assert stats["total_lines"] == 4
    assert stats["non_empty_lines"] == 3
    assert stats["total_bytes"] > 0


def test_clean_log():
    """로그 정리"""
    preprocessor = LogPreprocessor()
    
    log = "Line 1  \n\n\n\nLine 2   \n"
    processed = preprocessor.process(log)
    
    # 불필요한 빈 줄 제거
    assert "\n\n\n" not in processed
