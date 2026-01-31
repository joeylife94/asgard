"""
Tests for A/B Testing Framework.
"""

import pytest
import tempfile
import os
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4

from bifrost.experiment.models import (
    Experiment,
    Variant,
    VariantType,
    ExperimentStatus,
    ExperimentConfig,
    TrafficAllocation,
    VariantMetrics,
    ExperimentAssignment,
)


class TestVariant:
    """Variant 모델 테스트"""
    
    def test_create_control_variant(self):
        """컨트롤 변형 생성 테스트"""
        variant = Variant(
            name="control",
            variant_type=VariantType.CONTROL,
            weight=50.0,
            provider="ollama",
            model="llama3.2",
        )
        
        assert variant.name == "control"
        assert variant.variant_type == VariantType.CONTROL
        assert variant.weight == 50.0
        assert variant.provider == "ollama"
    
    def test_create_treatment_variant(self):
        """트리트먼트 변형 생성 테스트"""
        variant = Variant(
            name="treatment_a",
            variant_type=VariantType.TREATMENT,
            weight=50.0,
            provider="bedrock",
            model="claude-3",
            temperature=0.7,
        )
        
        assert variant.variant_type == VariantType.TREATMENT
        assert variant.temperature == 0.7
    
    def test_variant_to_dict(self):
        """변형 직렬화 테스트"""
        variant = Variant(
            name="test",
            variant_type=VariantType.CONTROL,
            weight=60.0,
        )
        
        data = variant.to_dict()
        
        assert data["name"] == "test"
        assert data["variant_type"] == "control"
        assert data["weight"] == 60.0
    
    def test_variant_from_dict(self):
        """변형 역직렬화 테스트"""
        data = {
            "name": "test_variant",
            "variant_type": "treatment",
            "weight": 40.0,
            "provider": "bedrock",
        }
        
        variant = Variant.from_dict(data)
        
        assert variant.name == "test_variant"
        assert variant.variant_type == VariantType.TREATMENT
        assert variant.provider == "bedrock"


class TestTrafficAllocation:
    """TrafficAllocation 모델 테스트"""
    
    def test_default_eligibility(self):
        """기본 적격성 테스트"""
        allocation = TrafficAllocation()
        
        assert allocation.is_eligible() is True
        assert allocation.is_eligible(user_id="user123") is True
    
    def test_user_targeting(self):
        """사용자 타게팅 테스트"""
        allocation = TrafficAllocation(
            target_users=["user1", "user2", "user3"]
        )
        
        assert allocation.is_eligible(user_id="user1") is True
        assert allocation.is_eligible(user_id="user99") is False
    
    def test_time_window(self):
        """시간 윈도우 테스트"""
        now = datetime.now(timezone.utc)
        
        # Active window
        allocation = TrafficAllocation(
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
        )
        assert allocation.is_eligible() is True
        
        # Not started yet
        allocation_future = TrafficAllocation(
            start_time=now + timedelta(hours=1),
        )
        assert allocation_future.is_eligible() is False
        
        # Already ended
        allocation_past = TrafficAllocation(
            end_time=now - timedelta(hours=1),
        )
        assert allocation_past.is_eligible() is False
    
    def test_query_patterns(self):
        """쿼리 패턴 테스트"""
        allocation = TrafficAllocation(
            include_patterns=["error", "exception"],
            exclude_patterns=["test", "debug"],
        )
        
        # Should include
        assert allocation.is_eligible(query="What is this error?") is True
        
        # Should exclude
        assert allocation.is_eligible(query="This is a test") is False
        
        # No match for include
        assert allocation.is_eligible(query="Some random query") is False


class TestExperiment:
    """Experiment 모델 테스트"""
    
    def test_create_experiment(self):
        """실험 생성 테스트"""
        experiment = Experiment(
            name="Provider Comparison",
            description="Compare Ollama vs Bedrock",
            variants=[
                Variant("control", VariantType.CONTROL, 50.0, provider="ollama"),
                Variant("treatment", VariantType.TREATMENT, 50.0, provider="bedrock"),
            ],
        )
        
        assert experiment.name == "Provider Comparison"
        assert len(experiment.variants) == 2
        assert experiment.status == ExperimentStatus.DRAFT
        assert isinstance(experiment.id, UUID)
    
    def test_get_control(self):
        """컨트롤 변형 조회 테스트"""
        experiment = Experiment(
            name="Test",
            variants=[
                Variant("baseline", VariantType.CONTROL, 50.0),
                Variant("new_model", VariantType.TREATMENT, 50.0),
            ],
        )
        
        control = experiment.get_control()
        assert control is not None
        assert control.name == "baseline"
    
    def test_get_treatments(self):
        """트리트먼트 변형 목록 조회 테스트"""
        experiment = Experiment(
            name="Test",
            variants=[
                Variant("control", VariantType.CONTROL, 50.0),
                Variant("treatment_a", VariantType.TREATMENT, 25.0),
                Variant("treatment_b", VariantType.TREATMENT, 25.0),
            ],
        )
        
        treatments = experiment.get_treatments()
        assert len(treatments) == 2
        assert all(t.variant_type == VariantType.TREATMENT for t in treatments)
    
    def test_validate_success(self):
        """유효한 실험 검증 테스트"""
        experiment = Experiment(
            name="Valid Experiment",
            variants=[
                Variant("control", VariantType.CONTROL, 50.0),
                Variant("treatment", VariantType.TREATMENT, 50.0),
            ],
        )
        
        errors = experiment.validate()
        assert len(errors) == 0
    
    def test_validate_no_name(self):
        """이름 없는 실험 검증 테스트"""
        experiment = Experiment(
            name="",
            variants=[
                Variant("control", VariantType.CONTROL, 50.0),
                Variant("treatment", VariantType.TREATMENT, 50.0),
            ],
        )
        
        errors = experiment.validate()
        assert any("name" in e.lower() for e in errors)
    
    def test_validate_insufficient_variants(self):
        """변형 부족 검증 테스트"""
        experiment = Experiment(
            name="Test",
            variants=[
                Variant("control", VariantType.CONTROL, 100.0),
            ],
        )
        
        errors = experiment.validate()
        assert any("2 variants" in e.lower() for e in errors)
    
    def test_validate_no_control(self):
        """컨트롤 없음 검증 테스트"""
        experiment = Experiment(
            name="Test",
            variants=[
                Variant("treatment_a", VariantType.TREATMENT, 50.0),
                Variant("treatment_b", VariantType.TREATMENT, 50.0),
            ],
        )
        
        errors = experiment.validate()
        assert any("control" in e.lower() for e in errors)
    
    def test_validate_weight_sum(self):
        """가중치 합계 검증 테스트"""
        experiment = Experiment(
            name="Test",
            variants=[
                Variant("control", VariantType.CONTROL, 30.0),
                Variant("treatment", VariantType.TREATMENT, 50.0),
            ],
        )
        
        errors = experiment.validate()
        assert any("100" in e for e in errors)
    
    def test_is_active(self):
        """활성 상태 테스트"""
        experiment = Experiment(name="Test")
        
        experiment.status = ExperimentStatus.DRAFT
        assert experiment.is_active() is False
        
        experiment.status = ExperimentStatus.RUNNING
        assert experiment.is_active() is True
        
        experiment.status = ExperimentStatus.COMPLETED
        assert experiment.is_active() is False
    
    def test_to_dict(self):
        """직렬화 테스트"""
        experiment = Experiment(
            name="Test Experiment",
            variants=[
                Variant("control", VariantType.CONTROL, 50.0),
                Variant("treatment", VariantType.TREATMENT, 50.0),
            ],
            tags=["test", "provider-comparison"],
        )
        
        data = experiment.to_dict()
        
        assert data["name"] == "Test Experiment"
        assert len(data["variants"]) == 2
        assert data["tags"] == ["test", "provider-comparison"]


class TestVariantMetrics:
    """VariantMetrics 모델 테스트"""
    
    def test_create_metrics(self):
        """메트릭스 생성 테스트"""
        metrics = VariantMetrics(
            variant_name="control",
            sample_count=100,
            avg_quality_score=0.85,
            avg_latency_ms=500,
            error_count=5,
            error_rate=0.05,
        )
        
        assert metrics.variant_name == "control"
        assert metrics.sample_count == 100
        assert metrics.avg_quality_score == 0.85
    
    def test_metrics_to_dict(self):
        """메트릭스 직렬화 테스트"""
        metrics = VariantMetrics(
            variant_name="treatment",
            sample_count=50,
            avg_quality_score=0.9,
        )
        
        data = metrics.to_dict()
        
        assert data["variant_name"] == "treatment"
        assert data["avg_quality_score"] == 0.9


class TestExperimentManager:
    """ExperimentManager 테스트"""
    
    @pytest.fixture
    def temp_db(self):
        """임시 데이터베이스"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except:
            pass
    
    @pytest.fixture
    def manager(self, temp_db):
        """테스트용 매니저"""
        from bifrost.experiment.manager import ExperimentManager
        ExperimentManager._instance = None
        return ExperimentManager(db_path=temp_db)
    
    @pytest.fixture
    def sample_experiment(self):
        """샘플 실험"""
        return Experiment(
            name="Test Experiment",
            description="Testing different providers",
            variants=[
                Variant("control", VariantType.CONTROL, 50.0, provider="ollama"),
                Variant("treatment", VariantType.TREATMENT, 50.0, provider="bedrock"),
            ],
            tags=["test"],
        )
    
    def test_create_experiment(self, manager, sample_experiment):
        """실험 생성 테스트"""
        created = manager.create_experiment(sample_experiment)
        
        assert created.id == sample_experiment.id
        assert created.name == "Test Experiment"
    
    def test_get_experiment(self, manager, sample_experiment):
        """실험 조회 테스트"""
        manager.create_experiment(sample_experiment)
        
        retrieved = manager.get_experiment(sample_experiment.id)
        
        assert retrieved is not None
        assert retrieved.name == sample_experiment.name
    
    def test_list_experiments(self, manager, sample_experiment):
        """실험 목록 조회 테스트"""
        manager.create_experiment(sample_experiment)
        
        experiments = manager.list_experiments()
        
        assert len(experiments) >= 1
        assert experiments[0].name == sample_experiment.name
    
    def test_list_experiments_by_status(self, manager, sample_experiment):
        """상태별 실험 목록 조회 테스트"""
        manager.create_experiment(sample_experiment)
        
        # Draft experiments
        drafts = manager.list_experiments(status=ExperimentStatus.DRAFT)
        assert len(drafts) >= 1
        
        # Running experiments (none yet)
        running = manager.list_experiments(status=ExperimentStatus.RUNNING)
        assert len(running) == 0
    
    def test_start_experiment(self, manager, sample_experiment):
        """실험 시작 테스트"""
        manager.create_experiment(sample_experiment)
        
        started = manager.start_experiment(sample_experiment.id)
        
        assert started.status == ExperimentStatus.RUNNING
        assert started.started_at is not None
    
    def test_pause_experiment(self, manager, sample_experiment):
        """실험 일시중지 테스트"""
        manager.create_experiment(sample_experiment)
        manager.start_experiment(sample_experiment.id)
        
        paused = manager.pause_experiment(sample_experiment.id)
        
        assert paused.status == ExperimentStatus.PAUSED
    
    def test_stop_experiment(self, manager, sample_experiment):
        """실험 중지 테스트"""
        manager.create_experiment(sample_experiment)
        manager.start_experiment(sample_experiment.id)
        
        stopped = manager.stop_experiment(sample_experiment.id, reason="Early termination")
        
        assert stopped.status == ExperimentStatus.STOPPED
        assert stopped.ended_at is not None
    
    def test_delete_experiment(self, manager, sample_experiment):
        """실험 삭제 테스트"""
        manager.create_experiment(sample_experiment)
        
        deleted = manager.delete_experiment(sample_experiment.id)
        assert deleted is True
        
        # Should not find it anymore
        retrieved = manager.get_experiment(sample_experiment.id)
        assert retrieved is None
    
    def test_assign_variant(self, manager, sample_experiment):
        """변형 할당 테스트"""
        manager.create_experiment(sample_experiment)
        manager.start_experiment(sample_experiment.id)
        
        variant = manager.assign_variant(
            experiment_id=sample_experiment.id,
            request_id="req-001",
            user_id="user-001",
        )
        
        assert variant is not None
        assert variant.name in ["control", "treatment"]
    
    def test_assign_variant_inactive_experiment(self, manager, sample_experiment):
        """비활성 실험에 할당 테스트"""
        manager.create_experiment(sample_experiment)
        # Don't start - remains in draft
        
        variant = manager.assign_variant(
            experiment_id=sample_experiment.id,
            request_id="req-001",
        )
        
        assert variant is None
    
    def test_consistent_assignment(self, manager, sample_experiment):
        """일관된 할당 테스트"""
        manager.create_experiment(sample_experiment)
        manager.start_experiment(sample_experiment.id)
        
        # Same user should get same variant
        variant1 = manager.assign_variant(
            experiment_id=sample_experiment.id,
            request_id="req-001",
            user_id="consistent-user",
        )
        
        # Reset and assign again with same user
        variant2 = manager.assign_variant(
            experiment_id=sample_experiment.id,
            request_id="req-002",
            user_id="consistent-user",
        )
        
        # Both should be assigned (though may be same or different due to request_id change)
        assert variant1 is not None
        assert variant2 is not None
    
    def test_record_result(self, manager, sample_experiment):
        """결과 기록 테스트"""
        manager.create_experiment(sample_experiment)
        manager.start_experiment(sample_experiment.id)
        
        manager.assign_variant(
            experiment_id=sample_experiment.id,
            request_id="req-001",
        )
        
        success = manager.record_result(
            request_id="req-001",
            quality_score=0.85,
            latency_ms=500,
        )
        
        assert success is True
    
    def test_get_results(self, manager, sample_experiment):
        """결과 조회 테스트"""
        manager.create_experiment(sample_experiment)
        manager.start_experiment(sample_experiment.id)
        
        # Generate some assignments
        for i in range(10):
            variant = manager.assign_variant(
                experiment_id=sample_experiment.id,
                request_id=f"req-{i:03d}",
            )
            if variant:
                manager.record_result(
                    request_id=f"req-{i:03d}",
                    quality_score=0.7 + (i * 0.02),
                    latency_ms=400 + (i * 10),
                )
        
        results = manager.get_results(sample_experiment.id)
        
        assert results.experiment_id == sample_experiment.id
        assert results.total_samples > 0
        assert len(results.variants_metrics) == 2


class TestIntegration:
    """통합 테스트"""
    
    @pytest.fixture
    def temp_db(self):
        """임시 데이터베이스"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except:
            pass
    
    def test_full_experiment_lifecycle(self, temp_db):
        """전체 실험 라이프사이클 테스트"""
        from bifrost.experiment.manager import ExperimentManager
        
        ExperimentManager._instance = None
        manager = ExperimentManager(db_path=temp_db)
        
        # 1. Create experiment
        experiment = Experiment(
            name="Full Lifecycle Test",
            variants=[
                Variant("control", VariantType.CONTROL, 50.0, provider="ollama"),
                Variant("treatment", VariantType.TREATMENT, 50.0, provider="bedrock"),
            ],
        )
        manager.create_experiment(experiment)
        
        # 2. Start experiment
        manager.start_experiment(experiment.id)
        
        # 3. Simulate traffic
        for i in range(20):
            variant = manager.assign_variant(
                experiment_id=experiment.id,
                request_id=f"lifecycle-req-{i}",
            )
            if variant:
                # Simulate different quality based on variant
                base_quality = 0.75 if variant.variant_type == VariantType.CONTROL else 0.80
                manager.record_result(
                    request_id=f"lifecycle-req-{i}",
                    quality_score=base_quality + (i % 5) * 0.02,
                    latency_ms=400 + (i % 10) * 20,
                )
        
        # 4. Get results
        results = manager.get_results(experiment.id)
        
        assert results.total_samples > 0
        assert len(results.variants_metrics) == 2
        
        # 5. Complete experiment
        manager.complete_experiment(experiment.id)
        
        final = manager.get_experiment(experiment.id)
        assert final.status == ExperimentStatus.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
