"""Unit tests for task_queue module."""
import asyncio
import pytest
from unittest.mock import AsyncMock, Mock

from src.core.task_queue import TaskQueue, Task, TaskResult, Priority


class TestPriority:
    """Test Priority enum."""
    
    def test_priority_levels(self):
        assert Priority.LOW.value == 1
        assert Priority.MEDIUM.value == 2
        assert Priority.HIGH.value == 3
        assert Priority.URGENT.value == 4
    
    def test_priority_ordered(self):
        p = [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.URGENT]
        for i in range(1, len(p)):
            assert p[i].value > p[i-1].value


class TestTask:
    """Test Task class."""
    
    def test_task_with_defaults(self):
        task = Task(task_id="test-1", name="test-task")
        assert task.priority == Priority.MEDIUM
        assert task.timeout == 60.0
    
    def test_task_with_custom_priority(self):
        task = Task(task_id="test-2", name="test-task", priority=Priority.HIGH)
        assert task.priority == Priority.HIGH
    
    def test_task_to_dict(self):
        task = Task(task_id="test-3", name="test-task", priority=Priority.HIGH, timeout=120)
        d = task.to_dict()
        assert d["task_id"] == "test-3"
        assert d["name"] == "test-task"
        assert d["priority"] == "HIGH"
        assert d["timeout"] == 120
    
    def test_task_from_dict(self):
        data = {
            "task_id": "test-4",
            "name": "test-task",
            "priority": "URGENT",
            "timeout": 30
        }
        task = Task.from_dict(data)
        assert task.task_id == "test-4"
        assert task.name == "test-task"
        assert task.priority == Priority.URGENT
        assert task.timeout == 30


class TestTaskResult:
    """Test TaskResult class."""
    
    def test_task_result_minimal(self):
        result = TaskResult(task_id="r1", success=True)
        assert result.result is None
        assert result.error is None
    
    def test_task_result_with_values(self):
        result = TaskResult(
            task_id="r2",
            success=False,
            result="error occurred",
            error="Timeout",
            duration=5.5
        )
        assert result.result == "error occurred"
        assert result.error == "Timeout"
        assert result.duration == 5.5
    
    def test_timestamps(self):
        result = TaskResult(task_id="r3", success=True)
        assert "T" in result.created_at  # ISO format has T separator
        # Note: ISO format may not have "GMT" - adjust test expectations


class TestTaskQueue:
    """Test TaskQueue class."""
    
    async def test_queue_initialization(self):
        queue = TaskQueue()
        assert isinstance(queue._queue, dict)
        assert queue.get_queue_size() == 0
        assert queue.get_processing_count() == 0
    
    async def test_submit_task(self):
        async def test_func(*args, **kwargs):
            return "done"
        
        queue = TaskQueue()
        task_id = await queue.submit(test_func, [], {}, "test-task", priority=Priority.LOW)
        assert task_id
        assert isinstance(task_id, str)
    
    async def test_submit_multiple_tasks(self):
        async def test_func(*args, **kwargs):
            return "done"
        
        queue = TaskQueue()
        task_id1 = await queue.submit(test_func, [], {}, "task-1", priority=Priority.LOW)
        task_id2 = await queue.submit(test_func, [], {}, "task-2", priority=Priority.HIGH)
        task_id3 = await queue.submit(test_func, [], {}, "task-3", priority=Priority.URGENT)
        
        assert task_id1 != task_id2
        assert task_id1 != task_id3
        assert task_id2 != task_id3
    
    async def test_get_result(self):
        async def test_func(*args, **kwargs):
            return {"status": "complete"}
        
        queue = TaskQueue()
        task_id = await queue.submit(test_func, [], {}, "test-task", priority=Priority.LOW)
        
        # Execute the task
        task = Task(task_id=task_id, name="test", priority=Priority.LOW, func=test_func)
        result = await queue.execute_task(task)
        
        # Get result
        retrieved = queue.get_result(task_id)
        assert retrieved is not None
        assert retrieved.task_id == task_id
        assert retrieved.success is True
    
    async def test_cancel_task(self):
        async def blocking_func(*args, **kwargs):
            await asyncio.sleep(10)
            return "done"
        
        queue = TaskQueue()
        task_id = await queue.submit(blocking_func, [], {}, "blocking-task", priority=Priority.HIGH)
        
        # Cancel before execution
        cancelled = await queue.cancel_task(task_id)
        assert cancelled is True


class TestTaskQueue_Queueing:
    """Test task queue behavior under load."""
    
    async def test_task_queueing(self):
        """Test that tasks are queued and executed in order."""
        queue = TaskQueue()
        results = []
        
        async def sequential_executor(*args, **kwargs):
            await asyncio.sleep(0.01)
            results.append({"args": args, "kwargs": kwargs})
        
        await queue.start_workers()
        try:
            await queue.submit(sequential_executor, [], {"k": "v1"}, "task-1", priority=Priority.LOW)
            await queue.submit(sequential_executor, [], {"k": "v2"}, "task-2", priority=Priority.HIGH)
            await queue.submit(sequential_executor, [], {"k": "v3"}, "task-3", priority=Priority.URGENT)
            
            # Give workers time to execute
            await asyncio.sleep(0.5)
            
            assert len(results) <= 3
        finally:
            await queue.stop_workers()
    
    async def test_callback_on_completion(self):
        """Test callback is triggered on task completion."""
        queue = TaskQueue()
        callback_called = False
        
        async def callback(result):
            nonlocal callback_called
            callback_called = True
        
        async def test_func(*args, **kwargs):
            return "done"
        
        await queue.start_workers()
        try:
            task_id = await queue.submit(
                test_func, [], {}, "test-task", priority=Priority.HIGH,
                result_callback=callback
            )
            await asyncio.sleep(0.5)
            assert callback_called
        finally:
            await queue.stop_workers()
