"""배치 로그 분석"""

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import time

from bifrost.ollama import OllamaClient
from bifrost.bedrock import BedrockClient, is_bedrock_available
from bifrost.preprocessor import LogPreprocessor
from bifrost.database import get_database
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn


class BatchAnalyzer:
    """배치 로그 분석기"""
    
    def __init__(
        self,
        source: str = "local",
        model: Optional[str] = None,
        max_workers: int = 4,
        use_cache: bool = True,
    ):
        self.source = source
        self.model = model
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.console = Console()
        self.db = get_database()
        self.preprocessor = LogPreprocessor()
    
    async def analyze_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """여러 파일 동시 분석"""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"[cyan]분석 중...", total=len(file_paths))
            
            # 비동기 태스크 생성
            tasks = []
            for file_path in file_paths:
                tasks.append(self._analyze_file(file_path))
            
            # 동시 실행
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.advance(task)
        
        return results
    
    async def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """단일 파일 분석"""
        start_time = time.time()
        
        try:
            # 파일 읽기 (비동기)
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                log_content = await f.read()
            
            # 캐시 확인
            if self.use_cache:
                import hashlib
                log_hash = hashlib.sha256(log_content.encode()).hexdigest()
                cached = self.db.get_duplicate_analyses(log_hash, hours=24)
                
                if cached:
                    return {
                        "file": str(file_path),
                        "status": "cached",
                        "analysis_id": cached[0]["id"],
                        "response": cached[0]["response"],
                        "duration": time.time() - start_time,
                        "cached": True,
                    }
            
            # 전처리
            log_content = self.preprocessor.process(log_content)
            
            # 프롬프트
            from bifrost.main import MASTER_PROMPT
            prompt = MASTER_PROMPT.format(log_content=log_content)
            
            # 분석 (동기 함수를 비동기로 실행)
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                if self.source == "local":
                    client = OllamaClient(model=self.model or "mistral")
                    result = await loop.run_in_executor(
                        executor,
                        lambda: client.analyze(prompt, stream=False)
                    )
                elif self.source == "cloud":
                    if not is_bedrock_available():
                        raise Exception("Bedrock not available")
                    client = BedrockClient(model_id=self.model or "anthropic.claude-3-sonnet-20240229-v1:0")
                    result = await loop.run_in_executor(
                        executor,
                        lambda: client.analyze(prompt)
                    )
                else:
                    raise ValueError(f"Invalid source: {self.source}")
            
            duration = time.time() - start_time
            
            # DB 저장
            analysis_id = self.db.save_analysis(
                source=self.source,
                model=result["metadata"]["model"],
                log_content=log_content,
                response=result["response"],
                duration=duration,
                tags=[file_path.stem],
                service_name=file_path.stem,
                status="completed",
            )
            
            return {
                "file": str(file_path),
                "status": "success",
                "analysis_id": analysis_id,
                "response": result["response"],
                "duration": duration,
                "cached": False,
            }
        
        except Exception as e:
            return {
                "file": str(file_path),
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time,
            }
    
    def analyze_directory(self, directory: Path, pattern: str = "*.log") -> List[Dict[str, Any]]:
        """디렉토리 내 로그 파일 일괄 분석"""
        log_files = list(directory.glob(pattern))
        
        if not log_files:
            self.console.print(f"[yellow]⚠️  {directory}에서 {pattern} 파일을 찾을 수 없습니다.[/yellow]")
            return []
        
        self.console.print(f"[cyan]📁 {len(log_files)}개 파일 발견[/cyan]")
        
        # asyncio 실행
        return asyncio.run(self.analyze_files(log_files))


async def analyze_stream(log_stream: asyncio.Queue, source: str = "local", model: Optional[str] = None):
    """스트림 로그 분석 (실시간)"""
    db = get_database()
    preprocessor = LogPreprocessor()
    
    if source == "local":
        client = OllamaClient(model=model or "mistral")
    elif source == "cloud":
        client = BedrockClient(model_id=model or "anthropic.claude-3-sonnet-20240229-v1:0")
    else:
        raise ValueError(f"Invalid source: {source}")
    
    while True:
        # 큐에서 로그 가져오기
        log_content = await log_stream.get()
        
        if log_content is None:  # 종료 신호
            break
        
        try:
            # 전처리
            log_content = preprocessor.process(log_content)
            
            from bifrost.main import MASTER_PROMPT
            prompt = MASTER_PROMPT.format(log_content=log_content)
            
            # 분석
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                result = await loop.run_in_executor(
                    executor,
                    lambda: client.analyze(prompt, stream=False)
                )
            
            # DB 저장
            db.save_analysis(
                source=source,
                model=result["metadata"]["model"],
                log_content=log_content,
                response=result["response"],
                duration=result["metadata"]["duration"],
                status="completed",
            )
            
            print(f"✅ 분석 완료: {len(log_content)} bytes")
        
        except Exception as e:
            print(f"❌ 분석 실패: {e}")
        
        finally:
            log_stream.task_done()
