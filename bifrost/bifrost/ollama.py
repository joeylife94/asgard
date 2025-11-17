"""Ollama API 통신 모듈"""

import time
import requests
from typing import Optional, Dict, Any, Iterator
from rich.console import Console


class OllamaClient:
    """Ollama API 클라이언트"""
    
    def __init__(
        self,
        url: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 120,
        max_retries: int = 3,
    ):
        self.url = url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.console = Console()
    
    def analyze(
        self,
        prompt: str,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        로그 분석 (재시도 로직 포함)
        
        Returns:
            {"response": str, "metadata": dict}
        """
        for attempt in range(self.max_retries):
            try:
                if stream:
                    return self._analyze_stream(prompt)
                else:
                    return self._analyze_blocking(prompt)
            
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # exponential backoff
                    self.console.print(
                        f"[yellow]⚠️  연결 실패, {wait_time}초 후 재시도... ({attempt+1}/{self.max_retries})[/yellow]"
                    )
                    time.sleep(wait_time)
                else:
                    raise Exception(
                        f"Ollama 서버에 연결할 수 없습니다. ({self.url})\n"
                        "Ollama가 실행 중인지 확인하세요: ollama serve"
                    )
            
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    self.console.print(
                        f"[yellow]⚠️  타임아웃, 재시도... ({attempt+1}/{self.max_retries})[/yellow]"
                    )
                else:
                    raise Exception(f"Ollama 응답 시간 초과 ({self.timeout}초)")
            
            except Exception as e:
                raise Exception(f"Ollama API 요청 실패: {e}")
    
    def _analyze_blocking(self, prompt: str) -> Dict[str, Any]:
        """블로킹 모드 분석"""
        api_endpoint = f"{self.url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        
        start_time = time.time()
        response = requests.post(
            api_endpoint,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        duration = time.time() - start_time
        
        result = response.json()
        
        return {
            "response": result.get("response", ""),
            "metadata": {
                "model": self.model,
                "duration": round(duration, 2),
                "done": result.get("done", False),
            }
        }
    
    def _analyze_stream(self, prompt: str) -> Dict[str, Any]:
        """스트리밍 모드 분석"""
        api_endpoint = f"{self.url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
        }
        
        start_time = time.time()
        response = requests.post(
            api_endpoint,
            json=payload,
            stream=True,
            timeout=self.timeout,
        )
        response.raise_for_status()
        
        # 스트림 수집
        full_response = []
        for line in response.iter_lines():
            if line:
                import json
                chunk = json.loads(line)
                if text := chunk.get("response"):
                    full_response.append(text)
                    # 실시간 출력
                    print(text, end='', flush=True)
        
        duration = time.time() - start_time
        print()  # 줄바꿈
        
        return {
            "response": ''.join(full_response),
            "metadata": {
                "model": self.model,
                "duration": round(duration, 2),
                "done": True,
            }
        }
    
    def health_check(self) -> bool:
        """Ollama 서버 헬스 체크"""
        try:
            response = requests.get(f"{self.url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


# 하위 호환성을 위한 레거시 함수
def analyze_with_ollama(
    prompt: str,
    ollama_url: str = "http://localhost:11434",
    model: str = "mistral",
    stream: bool = False,
) -> str:
    """레거시 함수 (하위 호환성)"""
    client = OllamaClient(url=ollama_url, model=model)
    result = client.analyze(prompt, stream=stream)
    return result["response"]
