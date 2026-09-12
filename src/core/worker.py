"""
Generic worker implementation for my-rxer.

Provides:
- Base Worker class
- WorkerManager for coordinating multiple workers
- WorkerResult for task outcomes
"""

import asyncio
import httpx
import json
import os
import uuid
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import logging

from .logger import Logger

# Use Priority enum from task_queue with comparison support
from .task_queue import Priority

def _priority_compare(self, other):
    """Compare two Priorities by value. Must be called as Priority(x).__lt__(other)."""
    if not isinstance(other, Priority):
        return NotImplemented
    return self.value < other.value

Priority.__lt__ = _priority_compare

logger = Logger("my-rxer.Worker")


@dataclass
class TaskResult:
    """Result of a worker task."""
    task_id: str
    worker_id: str
    status: str
    data: Any = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "worker_id": self.worker_id,
            "status": self.status,
            "data": self.data if self.data is not None else {},
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


@dataclass
class WorkerResult:
    """Aggregated results from a worker."""
    results: List[TaskResult]
    worker_id: str
    total_tasks: int
    success_count: int = 0
    error_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            "worker_id": self.worker_id,
            "total_tasks": self.total_tasks,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "results": [r.to_dict() for r in self.results]
        }


class Worker(ABC):
    """Abstract base worker implementation."""
    
    def __init__(self, worker_id: str, manager_ref: Optional["WorkerManager"] = None):
        self.worker_id = worker_id
        self.manager_ref = manager_ref
        self.memory: Optional["Memory"] = None
        self._started = False
        self._running = False
        self._completed_tasks: List[TaskResult] = []
    
    async def start(self) -> bool:
        """Start the worker."""
        if self._started:
            return True
        
        self._started = True
        asyncio.create_task(self.run_tasks())
        return True
    
    async def stop(self, graceful: bool = True) -> None:
        """Stop the worker."""
        self._running = False
    
    @abstractmethod
    async def run_tasks(self) -> None:
        """Run the worker's task loop. Must be overridden by subclasses."""
        pass
    
    async def process_task(self, task: Dict[str, Any]) -> TaskResult:
        """Process a single task and return result."""
        task_id = task.get("task_id", str(uuid.uuid4()))
        
        started_at = datetime.now().isoformat()
        
        try:
            result = await self.execute_task(task)
            return TaskResult(
                task_id=task_id,
                worker_id=self.worker_id,
                status="success",
                data=result,
                started_at=started_at,
                completed_at=datetime.now().isoformat()
            )
        except Exception as e:
            return TaskResult(
                task_id=task_id,
                worker_id=self.worker_id,
                status="error",
                data=None,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now().isoformat()
            )
    
    @abstractmethod
    async def execute_task(self, task: Dict) -> Any:
        """Execute a single task. Must be overridden."""
        pass
    
    async def run_worker(self) -> WorkerResult:
        """Run the worker and return aggregated results."""
        results = []
        
        while self._running:
            await asyncio.sleep(1)
        
        return WorkerResult(
            results=self._completed_tasks,
            worker_id=self.worker_id,
            total_tasks=len(self._completed_tasks),
            success_count=sum(1 for r in self._completed_tasks if r.status == "success"),
            error_count=sum(1 for r in self._completed_tasks if r.status == "error")
        )


class LLMWorker(Worker):
    """Worker for LLM processing tasks."""
    
    def __init__(self, worker_id: str, api_endpoint: str = "", api_key: str = ""):
        super().__init__(worker_id)
        self.api_endpoint = api_endpoint or os.getenv("vLLM_PORT", "http://127.0.0.1:8000") + "/v1/completions"
        self.api_key = api_key or os.getenv("STORAGE_API_KEY", "moto")
    
    async def execute_task(self, task: Dict) -> Any:
        """Execute an LLM task."""
        prompt = task.get("payload", {}).get("prompt")
        temperature = task.get("payload", {}).get("temperature", 0)
        max_tokens = task.get("payload", {}).get("max_tokens", 512)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_endpoint,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": task.get("payload", {}).get("model", "default"),
                        "prompt": prompt,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                return {
                    "response": response.text
                }
            except Exception as e:
                raise Exception(f"LLM request failed: {e}")
    
    async def run_tasks(self) -> None:
        """Run the LLM worker loop."""
        self._running = True
        
        while self._running:
            task = await self.manager_ref.task_queue.get()
            if not task:
                continue
            
            result = await self.process_task(task)
            self._completed_tasks.append(result)
            
            if task.get("callback"):
                await task["callback"](result.to_dict())
            
            await asyncio.sleep(0.1)


class WebWorker(Worker):
    """Worker for web requests and scraping."""
    
    def __init__(self, worker_id: str):
        super().__init__(worker_id)
        self._running = False
    
    async def execute_task(self, task: Dict) -> Any:
        """Execute a web worker task."""
        url = task.get("payload", {}).get("url")
        method = task.get("action", {}).get("method", "GET")
        headers = task.get("action", {}).get("headers", {})
        body = task.get("payload", {}).get("body")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method,
                    url,
                    params=task.get("payload", {}).get("params"),
                    headers=headers,
                    json=body if body else None
                )
                return {
                    "status": response.status_code,
                    "text": response.text
                }
            except Exception as e:
                raise Exception(f"Request failed: {e}")
    
    async def run_tasks(self) -> None:
        """Run the web worker loop."""
        self._running = True
        
        while self._running:
            task = await self.manager_ref.task_queue.get()
            if task is None:
                continue
            
            result = await self.process_task(task)
            self._completed_tasks.append(result)
            
            if task.get("callback"):
                await task["callback"](result.to_dict())
            
            await asyncio.sleep(0.1)


class MemoryWorker(Worker):
    """Worker for memory operations."""
    
    def __init__(self, worker_id: str):
        super().__init__(worker_id)
        self.memory: Optional["Memory"] = None
    
    async def execute_task(self, task: Dict) -> Any:
        """Execute a memory task."""
        task_type = task.get("action", {}).get("type")
        
        if task_type == "get":
            return await self.memory.get(task.get("payload", {}))
        elif task_type == "set":
            return await self.memory.set(task.get("payload", {}))
        elif task_type == "delete":
            return await self.memory.delete(task.get("payload", {}))
        elif task_type == "batch":
            return await self.memory.batch(task.get("payload", {}))
        
        raise Exception(f"Unknown memory operation: {task_type}")
    
    async def run_tasks(self) -> None:
        """Run the memory worker loop."""
        self._running = True
        
        while self._running:
            task = await self.manager_ref.task_queue.get()
            if task is None:
                continue
            
            result = await self.process_task(task)
            self._completed_tasks.append(result)
            
            if task.get("callback"):
                await task["callback"](result.to_dict())
            
            await asyncio.sleep(0.1)

class WorkerManager:
    """
    Manages a pool of workers and their lifecycle.
    
    Provides:
    - Worker registration and management
    - Configuration handling (memory limit, worker quantity)
    - Worker lifecycle coordination
    """
    
    def __init__(
        self,
        memory_limit: Optional[str] = None,
        workers_quantity: int = 1,
        worker_registry_ref: Optional["WorkerRegistry"] = None
    ):
        """
        Initialize WorkerManager.
        
        Args:
            memory_limit: Memory limit for workers (e.g., "512m")
            workers_quantity: Number of workers to create
            worker_registry_ref: Reference to WorkerRegistry instance
        """
        self._memory_limit = memory_limit
        self._workers_quantity = workers_quantity
        self._worker_registry_ref = worker_registry_ref
        self._workers = []
        self._workers_lock = asyncio.Lock()
        self._failed_tasks = {}
    
    def register_worker(self, worker: Worker) -> None:
        """Register a worker in the manager."""
        self._workers.append(worker)
    
    async def start_workers(self) -> None:
        """Start all registered workers."""
        async with self._workers_lock:
            for i, worker in enumerate(self._workers):
                # Create unique worker ID if needed
                worker_id = f"worker_{i}"
                worker = Worker(worker_id=worker_id, manager_ref=self)
                await worker.start()
                self._workers.append(worker)
    
    async def stop_workers(self) -> None:
        """Stop all workers gracefully."""
        async with self._workers_lock:
            for worker in self._workers:
                await worker.stop(graceful=True)
            self._workers.clear()
    
    def unregister_worker(self, worker: Optional[Worker] = None) -> bool:
        """
        Remove a worker from the manager.
        
        Args:
            worker: Worker to remove (if None, doesn't actually remove anything)
        
        Returns:
            True if successful, False otherwise
        """
        if worker is None:
            return True
        
        try:
            self._workers.remove(worker)
            return True
        except ValueError:
            return False
    
    def unregister(self, worker: Optional[Worker] = None) -> bool:
        """
        Remove a worker from the manager.
        
        Args:
            worker: Worker to remove (if None, doesn't actually remove anything)
        
        Returns:
            True if successful, False otherwise
        """
        return self.unregister_worker(worker)

    async def dispatch(self, task: Dict[str, Any]) -> TaskResult:
        """
        Dispatch a task to an available worker.
        
        Args:
            task: Task definition
        
        Returns:
            TaskResult from the worker
        """
        async with self._workers_lock:
            available_workers = [
                worker for worker in self._workers
                if worker._running and not worker._completed_tasks
            ]
        
        if not available_workers:
            raise RuntimeError("No available workers")
        
        # Select first available worker
        worker = available_workers[0]
        return await worker.process_task(task)
    
    @property
    def worker_count(self) -> int:
        """Get number of registered workers."""
        return len(self._workers)
