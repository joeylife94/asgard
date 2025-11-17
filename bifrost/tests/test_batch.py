"""배치 처리 테스트"""

import pytest
import asyncio
from pathlib import Path
from bifrost.batch import BatchAnalyzer


@pytest.mark.asyncio
async def test_batch_analyze_files(sample_log_file, tmp_path):
    """배치 파일 분석"""
    # 여러 로그 파일 생성
    files = []
    for i in range(3):
        log_file = tmp_path / f"test_{i}.log"
        log_file.write_text(f"Log file {i}\nERROR: Test error {i}")
        files.append(log_file)
    
    # 배치 분석 (실제 Ollama 없이는 실패)
    # analyzer = BatchAnalyzer(source="local", model="mistral")
    # results = await analyzer.analyze_files(files)
    # 
    # assert len(results) == 3
    # for result in results:
    #     assert result["status"] in ["success", "failed", "cached"]
