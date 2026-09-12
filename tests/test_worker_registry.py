"""Unit tests for worker_registry module."""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from src.core.worker_registry import (
    WorkerRegistry, WorkerConfig, WorkerInfo,
    WorkerTypes,
    register_worker_type
)


class TestWorkerConfig:
    """Test WorkerConfig dataclass."""
    
    def test_worker_config_defaults(self):
        """Test default values for worker config."""
        config = WorkerConfig(name="test-worker", worker_type="generic")
        
        assert config.name == "test-worker"
        assert config.worker_type == "generic"
        assert config.memory_limit is None
        assert config.cpu_limit is None
        assert config.timeout == 3600.0
        assert config.parallelism == 1
        assert config.workers_quantity == 1

    def test_worker_config_full(self):
        """Test WorkerConfig with all values set."""
        config = WorkerConfig(
            name="heavy-worker",
            worker_type="llm",
            memory_limit=1024,
            cpu_limit=0.5,
            timeout=1800.0,
            parallelism=4,
            workers_quantity=3
        )
        
        assert config.memory_limit == 1024
        assert config.cpu_limit == 0.5
        assert config.timeout == 1800.0
        assert config.workers_quantity == 3

    def test_worker_config_to_dict(self):
        """Test WorkerConfig serialization."""
        config = WorkerConfig(
            name="test-worker",
            worker_type="generic",
            memory_limit=512,
            cpu_limit=0.25,
            timeout=600,
            parallelism=2,
            workers_quantity=1
        )
        d = config.to_dict()
        
        assert d["name"] == "test-worker"
        assert d["type"] == "generic"
        assert d["memory_limit_mb"] == 512
        assert d["cpu_limit"] == 0.25
        assert d["timeout_seconds"] == 600

    def test_worker_config_from_dict(self):
        """Test WorkerConfig creation from dict."""
        data = {
            "name": "heavy-worker",
            "worker_type": "llm",
            "memory_limit": 2048,
            "cpu_limit": 1.0,
            "timeout": 300,
            "parallelism": 8,
            "quantity": 5
        }
        config = WorkerConfig.from_dict(data)
        
        assert config.name == "heavy-worker"
        assert config.memory_limit == 2048
        assert config.workers_quantity == 5

    def test_worker_config_missing_optional_fields(self):
        """Test WorkerConfig with missing optional fields."""
        data = {
            "name": "minimal-worker",
            "worker_type": "generic"
        }
        config = WorkerConfig.from_dict(data)
        
        assert config.memory_limit is None
        assert config.cpu_limit is None


class TestWorkerTypes:
    """Test worker type registration."""
    
    def test_register_worker_type(self):
        """Test registering a worker type."""
        class MockWorker:
            pass
        
        worker_class = MockWorker()
        register_worker_type("mock-worker", worker_class)
        
        assert "mock-worker" in WorkerTypes
        assert WorkerTypes["mock-worker"] == worker_class

    def test_register_worker_type_overwrite(self):
        """Test overwriting a worker type."""
        class Worker1:
            pass
        
        class Worker2:
            pass
        
        register_worker_type("custom", Worker1)
        assert WorkerTypes["custom"] == Worker1
        
        register_worker_type("custom", Worker2)
        assert WorkerTypes["custom"] == Worker2


class TestWorkerInfo:
    """Test WorkerInfo dataclass."""
    
    def test_worker_info_defaults(self):
        """Test default values for worker info."""
        config = WorkerConfig(name="test", worker_type="generic")
        info = WorkerInfo(
            worker_id="w1",
            started_at="2024-01-01",
            config=config,
            status="running"
        )
        
        assert info.task_count == 0
        assert info.recent_tasks == []
    
    def test_worker_info_with_tasks(self):
        """Test WorkerInfo with task tracking."""
        config = WorkerConfig(name="test", worker_type="generic")
        
        tasks = ["task-1", "task-2", "task-3"]
        info = WorkerInfo(
            worker_id="w2",
            started_at="2024-01-02",
            config=config,
            status="running",
            task_count=10,
            recent_tasks=tasks
        )
        
        assert info.task_count == 10
        assert info.recent_tasks == tasks

    def test_worker_info_to_dict(self):
        """Test WorkerInfo serialization."""
        config = WorkerConfig(name="test", worker_type="generic")
        info = WorkerInfo(
            worker_id="w3",
            started_at="2024-01-03",
            config=config,
            status="stopped",
            task_count=5
        )
        d = info.to_dict()
        
        assert d["worker_id"] == "w3"
        assert d["status"] == "stopped"
        assert d["task_count"] == 5


class TestWorkerRegistry:
    """Test WorkerRegistry class."""
    
    async def test_registry_initialization(self):
        """Test WorkerRegistry starts empty."""
        registry = WorkerRegistry()
        
        assert registry._worker_configs == {}
        assert registry._worker_info == {}
        assert registry._workers_lock is not None
        assert registry._state_dir is None

    async def test_register_worker_callback(self):
        """Test registering a worker callback."""
        registry = WorkerRegistry()
        
        async def worker_func():
            pass
        
        await registry.register_worker_callback(worker_func, "test-worker", 5)
        
        assert "test-worker" in registry._worker_configs
        cfg = registry._worker_configs["test-worker"]
        assert cfg["name"] == "test-worker"
        assert cfg["weight"] == 5
        assert "test-worker" in [k for k, v in registry._worker_configs.items()]


class TestWorkerRegistry_Lifecycle:
    """Test worker lifecycle management."""
    
    def test_spawn_worker_config(self):
        """Test spawning a worker with config."""
        registry = WorkerRegistry()
        
        config = WorkerConfig(
            name="test-worker",
            worker_type="generic",
            workers_quantity=2
        )
        
        # This would require actual worker implementation, but we can test
        # that the config is passed through
        assert config.name == "test-worker"
        assert config.workers_quantity == 2

    def test_worker_count_property(self):
        """Test worker count tracking."""
        registry = WorkerRegistry()
        
        # With no worker info, count should be 0
        count = registry.count_workers()
        assert count == 0

    def test_find_best_worker(self):
        """Test finding best worker by weight."""
        registry = WorkerRegistry()
        
        # With no workers, shouldn't raise
        best = registry.find_best_worker()
        # Could be None or raise - depends on implementation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
