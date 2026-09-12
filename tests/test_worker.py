"""Unit tests for worker module."""
import asyncio
import pytest
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

from src.core.worker import Worker, WorkerResult, TaskResult, Priority, WorkerManager


class TestWorkerResult:
    """Test WorkerResult dataclass."""
    
    def test_worker_result_minimal(self):
        results = []
        worker_result = WorkerResult(results=[], worker_id="w1", total_tasks=0)
        assert worker_result.worker_id == "w1"
        assert worker_result.total_tasks == 0
    
    def test_worker_result_with_results(self):
        results = [
            TaskResult(task_id="t1", worker_id="w1", status="completed", data="result1"),
            TaskResult(task_id="t2", worker_id="w1", status="completed", data="result2"),
        ]
        worker_result = WorkerResult(results=results, worker_id="w1", total_tasks=2, success_count=2)
        
        assert worker_result.success_count == 2
        assert worker_result.error_count == 0
        
        d = worker_result.to_dict()
        assert d["worker_id"] == "w1"
        assert d["total_tasks"] == 2
        assert len(d["results"]) == 2


class TestTaskResult:
    """Test TaskResult in worker context."""
    
    def test_task_result_minimal(self):
        result = TaskResult(
            task_id="task-1",
            worker_id="worker-1",
            status="completed",
            data={"response": "success"}
        )
        assert result.status == "completed"
        assert result.data["response"] == "success"
    
    def test_task_result_with_error(self):
        result = TaskResult(
            task_id="task-2",
            worker_id="worker-1",
            status="failed",
            data=None,
            error="Connection timeout"
        )
        assert result.status == "failed"
        assert result.error == "Connection timeout"
    
    def test_task_result_predefined_stats(self):
        result = TaskResult(
            task_id="task-3",
            worker_id="worker-1",
            status="completed",
            data="ok"
        )
        assert result.task_id == "task-3"
        assert result.worker_id == "worker-1"
    
    def test_task_result_to_dict(self):
        result = TaskResult(
            task_id="task-4",
            worker_id="worker-1",
            status="completed",
            data={"key": "value"},
            error=None,
            started_at="2024-01-01",
            completed_at="2024-01-02"
        )
        d = result.to_dict()
        assert d["task_id"] == "task-4"
        assert d["status"] == "completed"
        assert d["data"]["key"] == "value"
        # error should be None in dict
        assert d.get("error") is None


class TestWorkerManager:
    """Test WorkerManager class."""
    
    def test_manager_initialization(self):
        manager = WorkerManager()
        assert manager._workers == []
        assert manager._workers_lock is not None
        assert manager._failed_tasks == {}
    
    def test_register_worker_memory_limit(self):
        manager = WorkerManager(memory_limit="512m")
        assert manager._memory_limit == "512m"
    
    def test_register_worker_workers_quantity(self):
        class TestWorker(Worker):
            async def run_tasks(self):
                await asyncio.sleep(0.1)
            
            async def execute_task(self, task: Dict[str, Any]) -> TaskResult:
                pass
        
        manager = WorkerManager(workers_quantity=3)
        for _ in range(3):
            w = TestWorker(worker_id=f"test-worker-{_}")
            manager.register_worker(w)
        assert len(manager._workers) == 3
        assert manager.worker_count == 3


class TestPriority:
    """Test Priority enum."""
    
    def test_priority_values(self):
        assert Priority.LOW.value == 1
        assert Priority.MEDIUM.value == 2
        assert Priority.HIGH.value == 3
    
    def test_priority_comparison(self):
        assert Priority.LOW < Priority.MEDIUM
        assert Priority.MEDIUM < Priority.HIGH
        assert Priority.LOW < Priority.HIGH
    
    def test_priority_names(self):
        assert Priority.LOW.name == "LOW"
        assert Priority.MEDIUM.name == "MEDIUM"
        assert Priority.HIGH.name == "HIGH"
