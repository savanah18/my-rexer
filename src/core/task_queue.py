"""
Async task queue for my-rxer application.

Handles task scheduling, execution, result collection, and error handling
with support for prioritized execution.
"""

import asyncio
import json
import uuid
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import os

from .logger import Logger

logger = Logger("my-rxer.TaskQueue")


class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    duration: float = 0.0
    created_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        """Initialize timestamps after object creation."""
        self.created_at = datetime.now().isoformat()
        self.completed_at = datetime.now().isoformat()


@dataclass
class Task:
    """Task definition with metadata."""
    task_id: str
    name: str
    priority: Priority = Priority.MEDIUM
    result_callback: Optional[Callable] = None
    created_at: str = ""
    timeout: Optional[float] = 60.0
    func: Optional[Callable] = None
    args: List = field(default_factory=list)
    kwargs: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Initialize task timestamps."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "priority": self.priority.name,
            "created_at": self.created_at,
            "timeout": self.timeout
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        priority_map = {
            "LOW": Priority.LOW,
            "MEDIUM": Priority.MEDIUM,
            "HIGH": Priority.HIGH,
            "URGENT": Priority.URGENT
        }
        return cls(
            task_id=data["task_id"],
            name=data["name"],
            priority=priority_map.get(data.get("priority", "MEDIUM"), Priority.MEDIUM),
            timeout=data.get("timeout", 60.0)
        )


class TaskQueue:
    """
    Async task queue with priority support.

    Supports:
    - Multiple priority levels
    - Task timeout handling
    - Result collection and callbacks
    - Task tracking and monitoring
    """

    def __init__(
        self,
        queue_path: Optional[str] = None,
        max_concurrent: int = 1
    ):
        """
        Initialize task queue.

        Args:
            queue_path: Path to persist task state (optional)
            max_concurrent: Maximum concurrent task execution
        """
        self._queue: Dict[str, Task] = {}
        self._results: Dict[str, TaskResult] = {}
        self._lock = asyncio.Lock()
        self._processing: set = set()
        self._workers: List[asyncio.Task] = []
        self._max_concurrent = max_concurrent

        # Container directory for state persistence
        self._queue_path = queue_path
        self._state_file = None
        if queue_path and os.path.exists(queue_path):
            self._state_file = os.path.join(queue_path, "tasks.json")

    async def start_workers(self) -> None:
        """
        Start worker coroutines to process tasks.

        Must be called before submitting tasks.
        """
        self._workers = []
        for i in range(self._max_concurrent):
            worker = asyncio.create_task(self._worker_worker(i))
            self._workers.append(worker)

        logger.info(f"Started {len(self._workers)} task workers")

    async def stop_workers(self) -> None:
        """Stop all workers gracefully."""
        # Force exit workers
        for worker in self._workers:
            worker.cancel()
        
        # Wait for all workers to finish (with timeout to prevent hanging)
        try:
            await asyncio.wait_for(
                asyncio.gather(*self._workers, return_exceptions=True),
                timeout=2.0
            )
        except asyncio.TimeoutError:
            pass  # Some workers might still be running, but we can try to exit
        
        self._workers.clear()

    async def cancel_all_tasks(self, wait: bool = True) -> None:
        """Cancel all pending and running tasks."""
        task_ids = list(self._queue.keys())
        for task_id in task_ids:
            await self.cancel_task(task_id)

        if wait:
            await asyncio.sleep(0.2)  # Brief pause to let running tasks finish

    async def stop_all_tasks(self, wait: bool = True) -> None:
        """Cancel all pending and running tasks."""
        await self.cancel_all_tasks(wait=wait)
        # Cancel any workers still processing
        for worker in self._workers:
            if not worker.done():
                worker.cancel()

        # Wait for workers to finish or be cancelled
        if wait:
            await asyncio.gather(*self._workers, return_exceptions=True)

    async def _worker_worker(self, worker_id: int) -> None:
        """Worker coroutine that processes tasks."""
        while not asyncio.get_event_loop().is_closed():
            try:
                # Get next high-priority task
                # Use a shorter timeout to prevent long blocking
                task = await asyncio.wait_for(
                    self._get_next_task(),
                    timeout=15.0
                )
                
                if task:
                    await self.execute_task(task)
                else:
                    # No task available, brief sleep before checking again
                    await asyncio.sleep(0.1)

            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(0.1)

    async def _get_next_task(self) -> Optional[Task]:
        """Get next available task by priority."""
        async with self._lock:
            # Sort tasks by priority (highest first)
            ready = [
                task for task in list(self._queue.values())
                if task.task_id not in self._processing
            ]

            ready.sort(key=lambda t: t.priority.value, reverse=True)

            if ready:
                task = ready[0]
                self._queue.pop(task.task_id)
                self._processing.add(task.task_id)
                logger.info(f"Worker selected task: {task.task_id} [{task.name}]")
                return task
            return None

    async def submit(
        self,
        task_func: Callable,
        args: List,
        kwargs: Dict,
        name: str,
        priority: Priority = Priority.MEDIUM,
        timeout: Optional[float] = None,
        result_callback: Optional[Callable] = None
    ) -> str:
        """
        Submit a task for execution.

        Args:
            task_func: Async function to execute
            args: Positional arguments for task_func
            kwargs: Keyword arguments for task_func
            name: Human-readable task name
            priority: Task priority level
            timeout: Maximum execution time in seconds
            result_callback: Optional callback to invoke on completion

        Returns:
            Task ID string
        """
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            name=name,
            priority=priority,
            timeout=timeout,
            func=task_func,
            args=args,
            kwargs=kwargs,
            result_callback=result_callback
        )

        async with self._lock:
            self._queue[task_id] = task

        # Log submission
        logger.info(f"Task submitted: {task_id} [{name}] [{priority.name}]")

        return task_id

    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a single task.

        Args:
            task: Task to execute

        Returns:
            TaskResult object
        """
        start_time = datetime.now()
        result = None
        error = None
        success = False

        effective_timeout = task.timeout or self._max_concurrent
        try:
            # Use asyncio timeout - proper async context manager
            result = await asyncio.wait_for(
                task.func(*task.args, **task.kwargs),
                timeout=effective_timeout
            )
            success = True
        except asyncio.TimeoutError:
            error = f"Task timed out after {effective_timeout}s"
            logger.error(f"Task timed out: {task.task_id}. Error: {error}")
        except Exception as e:
            error = str(e)
            logger.error(f"Task failed: {task.task_id}. Error: {error}")

        # Create result object
        elapsed = (datetime.now() - start_time).total_seconds()
        completed = TaskResult(
            task_id=task.task_id,
            success=success,
            result=result,
            error=error,
            duration=elapsed
        )

        # Store result
        async with self._lock:
            self._results[task.task_id] = completed

        # Trigger callback if provided
        if task.result_callback:
            try:
                await task.result_callback(completed)
            except Exception as callback_error:
                logger.warning(f"Callback failed: {callback_error}")

        return completed

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        async with self._lock:
            if task_id in self._queue:
                task = self._queue.pop(task_id)
                if task_id in self._processing:
                    self._processing.remove(task_id)
                    task.func = None
                    # Re-add task to queue so it can be retried
                    self._queue[task.task_id] = task
                logger.info(f"Task cancelled: {task_id}")
                return True
        return False

    async def cancel_pending_tasks(self) -> None:
        """Cancel only pending (not yet running) tasks."""
        async with self._lock:
            pending_ids = [tid for tid in list(self._queue.keys()) 
                          if tid not in self._processing]
            
            for task_id in pending_ids:
                self._queue.pop(task_id)

    async def cancel_all_tasks(self, wait: bool = True) -> None:
        """Cancel all pending and running tasks."""
        task_ids = list(self._queue.keys())
        for task_id in task_ids:
            await self.cancel_task(task_id)

        # Wait for running tasks to finish
        if wait:
            for worker in self._workers:
                if not worker.done():
                    worker.cancel()
            await asyncio.gather(*self._workers, return_exceptions=True)

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get completed task result by ID."""
        return self._results.get(task_id)

    def get_results(self) -> Dict[str, TaskResult]:
        """Get all completed results."""
        return self._results.copy()

    def get_queue_size(self) -> int:
        """Get number of pending tasks."""
        return len(self._queue)

    def get_processing_count(self) -> int:
        """Get number of running tasks."""
        return len(self._processing)

    def save_state(self) -> None:
        """Save current state to file."""
        if not self._state_file:
            return

        os.makedirs(os.path.dirname(self._state_file), exist_ok=True)
        state = {
            "queue": {tid: task.to_dict() for tid, task in self._queue.items()},
            "results": {tid: {
                "task_id": tid,
                "success": res.success,
                "result": res.result,
                "error": res.error,
                "duration": res.duration
            } for tid, res in self._results.items()},
            "running": list(self._queue.keys())
        }

        with open(self._state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> None:
        """Load previous state from file."""
        if not self._state_file:
            return

        if not os.path.exists(self._state_file):
            return

        with open(self._state_file, "r") as f:
            state = json.load(f)
            for tid, task_data in state.get("queue", {}).items():
                self._queue[tid] = Task.from_dict(task_data)
            for tid, res_data in state.get("results", {}).items():
                self._results[tid] = TaskResult(**{
                    "task_id": tid,
                    **res_data
                })
