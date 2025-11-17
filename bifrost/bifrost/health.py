"""헬스 체크 & 시스템 상태"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
import psutil
import platform

from bifrost.database import Database
from bifrost.ollama import OllamaClient
from bifrost.config import Config

router = APIRouter()


def get_system_info() -> Dict[str, Any]:
    """시스템 정보"""
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "memory_available_gb": round(psutil.virtual_memory().available / (1024 ** 3), 2),
        "memory_percent": psutil.virtual_memory().percent,
    }


def check_database_health(db: Database) -> Dict[str, Any]:
    """데이터베이스 헬스 체크"""
    try:
        # 간단한 쿼리로 연결 확인
        with db.get_session() as session:
            result = session.execute("SELECT 1")
            result.fetchone()
        
        return {
            "status": "healthy",
            "database_url": db.db_url.split("@")[-1] if "@" in db.db_url else "sqlite",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


def check_ollama_health(ollama: OllamaClient) -> Dict[str, Any]:
    """Ollama 헬스 체크"""
    try:
        response = ollama._make_request(
            f"{ollama.base_url}/api/tags",
            method="GET"
        )
        
        models = [m["name"] for m in response.get("models", [])]
        
        return {
            "status": "healthy",
            "base_url": ollama.base_url,
            "available_models": models,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@router.get("/health")
async def health_check():
    """전체 헬스 체크"""
    config = Config()
    db = Database(config.get("database.url", "sqlite:///bifrost.db"))
    ollama = OllamaClient(config=config)
    
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.2.0",
        "components": {
            "database": check_database_health(db),
            "ollama": check_ollama_health(ollama),
        },
    }


@router.get("/health/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe"""
    config = Config()
    db = Database(config.get("database.url", "sqlite:///bifrost.db"))
    
    db_health = check_database_health(db)
    
    if db_health["status"] == "healthy":
        return {"status": "ready"}
    else:
        return {"status": "not_ready", "reason": db_health.get("error")}


@router.get("/system/info")
async def system_info():
    """시스템 정보"""
    return get_system_info()
