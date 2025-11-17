"""MLflow 실험 트래킹 연동 - 분석 메트릭, 파라미터, 아티팩트 로깅"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import os

try:
    import mlflow
    import mlflow.tracking
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

from bifrost.logger import logger


class MLflowTracker:
    """MLflow 실험 트래킹 클래스"""
    
    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: str = "bifrost-log-analysis",
    ):
        """
        MLflow Tracker 초기화
        
        Args:
            tracking_uri: MLflow tracking server URI (기본: local file)
            experiment_name: 실험 이름
        """
        if not MLFLOW_AVAILABLE:
            logger.warning("MLflow not installed. Run: pip install mlflow")
            self.enabled = False
            return
        
        self.enabled = True
        self.tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI",
            "file:./mlruns"
        )
        self.experiment_name = experiment_name
        
        # MLflow 설정
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        
        logger.info(f"MLflow tracking initialized: {self.tracking_uri}")
    
    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Optional[Any]:
        """
        새 실험 run 시작
        
        Args:
            run_name: Run 이름
            tags: 태그 딕셔너리
        
        Returns:
            MLflow run 객체
        
        Examples:
            >>> tracker = MLflowTracker()
            >>> with tracker.start_run(run_name="prod-analysis"):
            ...     tracker.log_params({"model": "claude-3"})
            ...     tracker.log_metrics({"accuracy": 0.95})
        """
        if not self.enabled:
            return None
        
        return mlflow.start_run(run_name=run_name, tags=tags)
    
    def log_params(self, params: Dict[str, Any]):
        """
        파라미터 로깅
        
        Args:
            params: 파라미터 딕셔너리
        
        Examples:
            >>> tracker.log_params({
            ...     "model": "ollama/mistral",
            ...     "temperature": 0.7,
            ...     "max_tokens": 2000,
            ... })
        """
        if not self.enabled:
            return
        
        try:
            mlflow.log_params(params)
            logger.debug(f"Logged params: {params}")
        except Exception as e:
            logger.error(f"Failed to log params: {e}")
    
    def log_metrics(
        self,
        metrics: Dict[str, float],
        step: Optional[int] = None,
    ):
        """
        메트릭 로깅
        
        Args:
            metrics: 메트릭 딕셔너리
            step: 스텝 번호 (시계열)
        
        Examples:
            >>> tracker.log_metrics({
            ...     "response_time": 1.23,
            ...     "log_size_kb": 45.6,
            ...     "error_count": 3,
            ... })
        """
        if not self.enabled:
            return
        
        try:
            mlflow.log_metrics(metrics, step=step)
            logger.debug(f"Logged metrics: {metrics}")
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")
    
    def log_artifact(
        self,
        local_path: str,
        artifact_path: Optional[str] = None,
    ):
        """
        아티팩트 (파일) 로깅
        
        Args:
            local_path: 로컬 파일 경로
            artifact_path: MLflow 내 저장 경로
        
        Examples:
            >>> tracker.log_artifact("analysis_result.json", "results/")
        """
        if not self.enabled:
            return
        
        try:
            mlflow.log_artifact(local_path, artifact_path)
            logger.debug(f"Logged artifact: {local_path}")
        except Exception as e:
            logger.error(f"Failed to log artifact: {e}")
    
    def log_text(self, text: str, artifact_file: str):
        """
        텍스트를 아티팩트로 로깅
        
        Args:
            text: 로깅할 텍스트
            artifact_file: 아티팩트 파일명
        
        Examples:
            >>> tracker.log_text("분석 결과...", "analysis.txt")
        """
        if not self.enabled:
            return
        
        try:
            mlflow.log_text(text, artifact_file)
            logger.debug(f"Logged text artifact: {artifact_file}")
        except Exception as e:
            logger.error(f"Failed to log text: {e}")
    
    def log_dict(self, dictionary: Dict, artifact_file: str):
        """
        딕셔너리를 JSON 아티팩트로 로깅
        
        Args:
            dictionary: 로깅할 딕셔너리
            artifact_file: 아티팩트 파일명 (*.json)
        
        Examples:
            >>> tracker.log_dict({"status": "success"}, "result.json")
        """
        if not self.enabled:
            return
        
        try:
            mlflow.log_dict(dictionary, artifact_file)
            logger.debug(f"Logged dict artifact: {artifact_file}")
        except Exception as e:
            logger.error(f"Failed to log dict: {e}")
    
    def set_tags(self, tags: Dict[str, str]):
        """
        태그 설정
        
        Args:
            tags: 태그 딕셔너리
        
        Examples:
            >>> tracker.set_tags({
            ...     "environment": "production",
            ...     "service": "api-server",
            ... })
        """
        if not self.enabled:
            return
        
        try:
            mlflow.set_tags(tags)
            logger.debug(f"Set tags: {tags}")
        except Exception as e:
            logger.error(f"Failed to set tags: {e}")
    
    def log_analysis_run(
        self,
        log_content: str,
        response: str,
        source: str,
        model: str,
        duration: float,
        metadata: Optional[Dict] = None,
    ) -> Optional[str]:
        """
        전체 분석 run 로깅 (All-in-one)
        
        Args:
            log_content: 입력 로그
            response: 분석 결과
            source: 소스 (local/cloud)
            model: 모델명
            duration: 소요 시간 (초)
            metadata: 추가 메타데이터
        
        Returns:
            Run ID (string)
        
        Examples:
            >>> run_id = tracker.log_analysis_run(
            ...     log_content="ERROR: Failed",
            ...     response="에러 분석 결과...",
            ...     source="local",
            ...     model="ollama/mistral",
            ...     duration=2.34,
            ...     metadata={"service": "api", "environment": "prod"}
            ... )
        """
        if not self.enabled:
            return None
        
        try:
            with mlflow.start_run() as run:
                # 파라미터
                self.log_params({
                    "source": source,
                    "model": model,
                    "log_size_bytes": len(log_content.encode('utf-8')),
                })
                
                # 메트릭
                self.log_metrics({
                    "duration_seconds": duration,
                    "response_length": len(response),
                })
                
                # 태그
                tags = {
                    "timestamp": datetime.utcnow().isoformat(),
                }
                if metadata:
                    tags.update(metadata)
                self.set_tags(tags)
                
                # 아티팩트
                self.log_text(log_content, "input_log.txt")
                self.log_text(response, "analysis_response.txt")
                
                logger.info(f"Logged analysis run: {run.info.run_id}")
                return run.info.run_id
        
        except Exception as e:
            logger.error(f"Failed to log analysis run: {e}")
            return None
    
    def get_run(self, run_id: str) -> Optional[Dict]:
        """
        Run 정보 조회
        
        Args:
            run_id: 조회할 Run ID
        
        Returns:
            Run 정보 딕셔너리
        """
        if not self.enabled:
            return None
        
        try:
            run = mlflow.get_run(run_id)
            return {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "status": run.info.status,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "params": run.data.params,
                "metrics": run.data.metrics,
                "tags": run.data.tags,
            }
        except Exception as e:
            logger.error(f"Failed to get run: {e}")
            return None
    
    def search_runs(
        self,
        filter_string: Optional[str] = None,
        max_results: int = 100,
        order_by: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Run 검색
        
        Args:
            filter_string: 필터 문자열 (MLflow query syntax)
            max_results: 최대 결과 수
            order_by: 정렬 기준
        
        Returns:
            Run 리스트
        
        Examples:
            >>> runs = tracker.search_runs(
            ...     filter_string="params.model = 'ollama/mistral'",
            ...     max_results=10,
            ...     order_by=["metrics.duration_seconds DESC"]
            ... )
        """
        if not self.enabled:
            return []
        
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return []
            
            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=filter_string,
                max_results=max_results,
                order_by=order_by,
            )
            
            return runs.to_dict('records')
        
        except Exception as e:
            logger.error(f"Failed to search runs: {e}")
            return []
    
    def get_experiment_info(self) -> Optional[Dict]:
        """
        현재 실험 정보 조회
        
        Returns:
            실험 정보 딕셔너리
        """
        if not self.enabled:
            return None
        
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return None
            
            return {
                "experiment_id": experiment.experiment_id,
                "name": experiment.name,
                "artifact_location": experiment.artifact_location,
                "lifecycle_stage": experiment.lifecycle_stage,
                "creation_time": experiment.creation_time,
            }
        except Exception as e:
            logger.error(f"Failed to get experiment info: {e}")
            return None
    
    def compare_runs(
        self,
        run_ids: List[str],
        metric_names: Optional[List[str]] = None,
    ) -> Dict:
        """
        여러 run 비교
        
        Args:
            run_ids: 비교할 Run ID 리스트
            metric_names: 비교할 메트릭 이름 리스트
        
        Returns:
            비교 결과 딕셔너리
        """
        if not self.enabled:
            return {}
        
        comparison = {
            "run_ids": run_ids,
            "runs": [],
        }
        
        for run_id in run_ids:
            run_info = self.get_run(run_id)
            if run_info:
                comparison["runs"].append(run_info)
        
        # 메트릭 통계
        if metric_names and comparison["runs"]:
            stats = {}
            for metric in metric_names:
                values = [
                    run["metrics"].get(metric, 0)
                    for run in comparison["runs"]
                ]
                stats[metric] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                }
            comparison["metric_stats"] = stats
        
        return comparison


# 편의 함수

def create_tracker(
    tracking_uri: Optional[str] = None,
    experiment_name: str = "bifrost-log-analysis",
) -> MLflowTracker:
    """MLflow Tracker 생성"""
    return MLflowTracker(tracking_uri, experiment_name)


def is_mlflow_available() -> bool:
    """MLflow 설치 여부 확인"""
    return MLFLOW_AVAILABLE


if __name__ == "__main__":
    # 데모
    tracker = MLflowTracker()
    
    if tracker.enabled:
        # 분석 run 로깅
        run_id = tracker.log_analysis_run(
            log_content="ERROR: Database connection failed",
            response="분석 결과: DB 연결 실패, 재시도 권장",
            source="local",
            model="ollama/mistral",
            duration=2.5,
            metadata={
                "service": "api-server",
                "environment": "production",
            }
        )
        
        print(f"✅ Logged run: {run_id}")
        
        # Run 조회
        run_info = tracker.get_run(run_id)
        print(f"\n📊 Run Info:")
        print(f"  Duration: {run_info['metrics']['duration_seconds']}s")
        print(f"  Model: {run_info['params']['model']}")
        
        # 실험 정보
        exp_info = tracker.get_experiment_info()
        print(f"\n🧪 Experiment: {exp_info['name']}")
        print(f"  Location: {exp_info['artifact_location']}")
    else:
        print("⚠️ MLflow not available. Install with: pip install mlflow")
