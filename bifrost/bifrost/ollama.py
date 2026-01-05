"""Ollama API 통신 모듈"""

import os
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
                # Ollama returns HTTP 404 when the requested model isn't available locally.
                # For E2E/CI environments we optionally allow a deterministic fallback so
                # the orchestration loop can be validated without downloading large models.
                if self._is_model_not_found(e) and self._allow_fallback():
                    return self._fallback_analysis(prompt, reason="ollama_model_not_available")
                raise Exception(f"Ollama API 요청 실패: {e}")

    def _allow_fallback(self) -> bool:
        return os.getenv("BIFROST_OLLAMA_ALLOW_FALLBACK", "false").lower() in (
            "true",
            "1",
            "yes",
        )

    def _is_model_not_found(self, error: Exception) -> bool:
        if not isinstance(error, requests.exceptions.HTTPError):
            return False
        response = getattr(error, "response", None)
        if response is None:
            return False
        return response.status_code == 404

    def _fallback_analysis(self, prompt: str, reason: str) -> Dict[str, Any]:
        start_time = time.time()
        response = (
            "## 📊 요약\n"
            "Ollama 모델이 준비되지 않아(다운로드/로드 필요) 임시 분석으로 대체했습니다.\n\n"
            "## 🔍 주요 이슈\n"
            "- LLM 모델이 로컬에 존재하지 않아 `/api/generate` 요청이 404로 실패했습니다.\n"
            "- Kafka 기반 오케스트레이션 경로(요청→처리→결과)는 정상 동작 중입니다.\n\n"
            "## 💡 제안사항\n"
            "- E2E 환경에서 모델을 미리 준비하세요: `ollama pull <model>`\n"
            "- 또는 E2E에서는 `BIFROST_OLLAMA_ALLOW_FALLBACK=true` 유지 후, 프로덕션에서는 끄세요.\n"
        )
        duration = time.time() - start_time
        return {
            "response": response,
            "metadata": {
                "model": "fallback",
                "duration": round(duration, 2),
                "done": True,
                "fallback_reason": reason,
                "requested_model": self.model,
            },
        }
    
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
