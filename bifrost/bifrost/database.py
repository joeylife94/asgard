"""데이터베이스 연결 및 세션 관리"""

import hashlib
from contextlib import contextmanager
from typing import Generator, Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from bifrost.models import Base, AnalysisResult, AnalysisMetric, PromptTemplate, APIKey


def utcnow() -> datetime:
    """UTC now as naive datetime (UTC)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Database:
    """데이터베이스 관리자"""
    
    def __init__(self, database_url: str = "sqlite:///bifrost.db"):
        """
        Args:
            database_url: SQLAlchemy 데이터베이스 URL
                - SQLite: sqlite:///bifrost.db
                - PostgreSQL: postgresql://user:pass@localhost/bifrost
        """
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        
        self.engine = create_engine(
            database_url,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
        """데이터베이스 초기화 (테이블 생성)"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_all(self):
        """모든 테이블 삭제 (주의!)"""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """세션 컨텍스트 매니저"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # ==================== Analysis Results ====================
    
    def save_analysis(
        self,
        source: str,
        model: str,
        log_content: str,
        response: str,
        duration: float,
        log_hash: Optional[str] = None,
        log_size_bytes: Optional[int] = None,
        log_lines: Optional[int] = None,
        response_size_bytes: Optional[int] = None,
        config: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        service_name: Optional[str] = None,
        environment: Optional[str] = None,
        tokens_used: Optional[int] = None,
        status: str = "completed",
        error_message: Optional[str] = None,
    ) -> int:
        """분석 결과 저장"""
        with self.get_session() as session:
            # 기본값 계산 (필요 시 호출자가 override 가능)
            computed_log_hash = hashlib.sha256(log_content.encode()).hexdigest()
            computed_log_size_bytes = len(log_content.encode())
            computed_log_lines = len(log_content.split('\n'))
            computed_response_size_bytes = len(response.encode())

            log_hash = log_hash or computed_log_hash
            log_size_bytes = log_size_bytes if log_size_bytes is not None else computed_log_size_bytes
            log_lines = log_lines if log_lines is not None else computed_log_lines
            response_size_bytes = (
                response_size_bytes if response_size_bytes is not None else computed_response_size_bytes
            )
            
            result = AnalysisResult(
                source=source,
                model=model,
                log_content=log_content,
                log_hash=log_hash,
                log_size_bytes=log_size_bytes,
                log_lines=log_lines,
                response=response,
                response_size_bytes=response_size_bytes,
                duration_seconds=duration,
                tokens_used=tokens_used,
                config=config or {},
                tags=tags or [],
                service_name=service_name,
                environment=environment,
                status=status,
                error_message=error_message,
            )
            
            session.add(result)
            session.flush()
            return result.id
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict]:
        """분석 결과 조회"""
        with self.get_session() as session:
            result = session.query(AnalysisResult).filter_by(id=analysis_id).first()
            return result.to_dict() if result else None
    
    def list_analyses(
        self,
        limit: int = 50,
        offset: int = 0,
        service_name: Optional[str] = None,
        model: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """분석 결과 목록 조회"""
        with self.get_session() as session:
            query = session.query(AnalysisResult)
            
            if service_name:
                query = query.filter_by(service_name=service_name)
            if model:
                query = query.filter_by(model=model)
            if status:
                query = query.filter_by(status=status)
            if start_date:
                query = query.filter(AnalysisResult.created_at >= start_date)
            if end_date:
                query = query.filter(AnalysisResult.created_at <= end_date)
            
            results = query.order_by(desc(AnalysisResult.created_at)).limit(limit).offset(offset).all()
            return [r.to_dict() for r in results]
    
    def get_duplicate_analyses(self, log_hash: str, hours: int = 24) -> List[Dict]:
        """중복 분석 찾기 (캐시 활용)"""
        with self.get_session() as session:
            cutoff = utcnow() - timedelta(hours=hours)
            results = (
                session.query(AnalysisResult)
                .filter_by(log_hash=log_hash, status="completed")
                .filter(AnalysisResult.created_at >= cutoff)
                .order_by(desc(AnalysisResult.created_at))
                .all()
            )
            return [r.to_dict() for r in results]
    
    # ==================== Metrics ====================
    
    def save_metric(
        self,
        analysis_id: int,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None,
    ):
        """메트릭 저장"""
        with self.get_session() as session:
            metric = AnalysisMetric(
                analysis_id=analysis_id,
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit,
            )
            session.add(metric)
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """메트릭 요약"""
        with self.get_session() as session:
            cutoff = utcnow() - timedelta(hours=hours)
            
            # 전체 통계
            total = session.query(func.count(AnalysisResult.id)).filter(
                AnalysisResult.created_at >= cutoff
            ).scalar()
            
            avg_duration = session.query(func.avg(AnalysisResult.duration_seconds)).filter(
                AnalysisResult.created_at >= cutoff
            ).scalar() or 0.0
            
            # 모델별 통계
            model_stats = session.query(
                AnalysisResult.model,
                func.count(AnalysisResult.id).label('count'),
                func.avg(AnalysisResult.duration_seconds).label('avg_duration'),
            ).filter(
                AnalysisResult.created_at >= cutoff
            ).group_by(AnalysisResult.model).all()
            
            return {
                "total_analyses": total,
                "avg_duration_seconds": round(avg_duration, 2),
                "model_stats": [
                    {
                        "model": m.model,
                        "count": m.count,
                        "avg_duration": round(m.avg_duration, 2),
                    }
                    for m in model_stats
                ],
            }
    
    # ==================== Prompt Templates ====================
    
    def save_prompt_template(
        self,
        name: str,
        version: str,
        template: str,
        description: Optional[str] = None,
    ) -> int:
        """프롬프트 템플릿 저장"""
        with self.get_session() as session:
            existing = session.query(PromptTemplate).filter_by(name=name).first()
            if existing:
                existing.version = version
                existing.template = template
                existing.description = description
                existing.updated_at = utcnow()
                return existing.id
            else:
                template_obj = PromptTemplate(
                    name=name,
                    version=version,
                    template=template,
                    description=description,
                )
                session.add(template_obj)
                session.flush()
                return template_obj.id
    
    def get_prompt_template(self, name: str) -> Optional[Dict]:
        """프롬프트 템플릿 조회"""
        with self.get_session() as session:
            template = session.query(PromptTemplate).filter_by(name=name, is_active=True).first()
            return template.to_dict() if template else None
    
    # ==================== API Keys ====================
    
    def create_api_key(
        self,
        name: str,
        rate_limit: int = 100,
        description: Optional[str] = None,
        owner: Optional[str] = None,
    ) -> str:
        """API 키 생성"""
        import secrets
        key = secrets.token_urlsafe(32)
        
        with self.get_session() as session:
            api_key = APIKey(
                key=key,
                name=name,
                rate_limit_per_hour=rate_limit,
                description=description,
                owner=owner,
            )
            session.add(api_key)
            return key
    
    def validate_api_key(self, key: str) -> bool:
        """API 키 검증"""
        with self.get_session() as session:
            api_key = session.query(APIKey).filter_by(key=key, is_active=True).first()
            if api_key:
                # 사용 기록 업데이트
                api_key.last_used_at = utcnow()
                api_key.usage_count += 1
                return True
            return False
    
    def list_api_keys(self) -> List[Dict]:
        """API 키 목록"""
        with self.get_session() as session:
            keys = session.query(APIKey).order_by(desc(APIKey.created_at)).all()
            return [k.to_dict() for k in keys]


# 싱글톤 인스턴스
_db_instance: Optional[Database] = None


def get_database(database_url: str = "sqlite:///bifrost.db") -> Database:
    """데이터베이스 인스턴스 가져오기"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(database_url)
        _db_instance.init_db()
    return _db_instance
