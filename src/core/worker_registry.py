"""
Worker registry module for managing worker lifecycle and task distribution.
"""
import asyncio
import os
import json
import uuid
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .logger import Logger

logger = Logger("my-rxer.WorkerRegistry")


@dataclass
class WorkerConfig:
    """Configuration for worker creation."""
    name: str
    worker_type: str
    memory_limit: Optional[int] = None
    cpu_limit: Optional[float] = None
    timeout: float = 3600.0
    parallelism: int = 1
    workers_quantity: int = 1

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.worker_type,
            "memory_limit_mb": self.memory_limit,
            "cpu_limit": self.cpu_limit,
            "timeout_seconds": self.timeout,
            "parallelism": self.parallelism,
            "quantity": self.workers_quantity
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkerConfig":
        return cls(
            name=data.get("name", "default"),
            worker_type=data.get("worker_type", "generic"),
            memory_limit=data.get("memory_limit"),
            cpu_limit=data.get("cpu_limit"),
            timeout=data.get("timeout", 3600.0),
            parallelism=data.get("parallelism", 1),
            workers_quantity=data.get("quantity", 1)
        )


# Worker type registry - namespace for worker type registrations
class WorkerRegistryTypes:
    """Namespace for worker type registrations."""
    _workers: Dict[str, Any] = {}

    def __getitem__(self, key: str) -> Any:
        return self._workers[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._workers[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._workers

    def __iter__(self):
        return iter(self._workers)

    def __len__(self) -> int:
        return len(self._workers)

    def __setstate__(self, state):
        """Restore state after pickling."""
        self._workers = state.get('_workers', {})


WORKER_TYPES = WorkerRegistryTypes()


def register_worker_type(name: str, worker_class: Type) -> None:
    """Register a worker class by type."""
    WORKER_TYPES[name] = worker_class


@dataclass
class WorkerInfo:
    """Information about a running worker."""
    worker_id: str
    config: WorkerConfig
    started_at: str
    status: str
    task_count: int = 0
    recent_tasks: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "worker_id": self.worker_id,
            "config": self.config.to_dict(),
            "started_at": self.started_at,
            "status": self.status,
            "task_count": self.task_count,
            "recent_tasks": self.recent_tasks[-100:]
        }


class WorkerRegistry:
    """Registry for managing worker lifecycle and finding best worker."""

    def __init__(self, state_dir: Optional[str] = None):
        self._worker_configs: Dict[str, Any] = {}
        self._worker_info: Dict[str, WorkerInfo] = {}
        self._workers_lock = asyncio.Lock()
        self._state_dir = state_dir

    async def register_worker_callback(
        self,
        worker_func: Callable,
        name: str = "default",
        weight: int = 1
    ) -> None:
        self._worker_configs[name] = {
            "func": worker_func,
            "name": name or worker_func.__name__,
            "weight": weight
        }
        logger.info(f"Registered worker: {name} (weight={weight})")

    async def spawn_worker(self, config: WorkerConfig) -> WorkerInfo:
        """Spawn a new worker."""
        worker_id = str(uuid.uuid4())
        worker_info = WorkerInfo(
            worker_id=worker_id,
            config=config,
            started_at=datetime.now().isoformat(),
            status="running"
        )

        async with self._workers_lock:
            self._worker_info[worker_id] = worker_info
            logger.info(f"Spawned worker: {worker_id} ({config.worker_type})")
        return worker_info

    async def stop_worker(self, worker_id: str, graceful: bool = True) -> bool:
        """Stop a worker."""
        async with self._workers_lock:
            if worker_id not in self._worker_info:
                return False

            worker = self._worker_info[worker_id]
            logger.info(f"Stopping worker: {worker_id}")
            del self._worker_info[worker_id]
            return True

    async def stop_all_workers(self, graceful: bool = True) -> None:
        """Stop all workers."""
        worker_ids = list(self._worker_info.keys())
        for worker_id in worker_ids:
            await self.stop_worker(worker_id, graceful)

    async def get_worker(self, worker_id: str) -> Optional[WorkerInfo]:
        """Get worker by ID."""
        async with self._workers_lock:
            return self._worker_info.get(worker_id) if worker_id in self._worker_info else None

    async def get_active_workers(self) -> List[WorkerInfo]:
        """Get all active workers."""
        async with self._workers_lock:
            return list(self._worker_info.values())

    async def get_worker_count(self) -> int:
        """Get number of active workers."""
        async with self._workers_lock:
            return len(self._worker_info)

    def count_workers(self) -> int:
        """Get number of active workers (sync method)."""
        return len(self._worker_info)

    async def find_best_worker(self) -> Optional[WorkerInfo]:
        """
        Select the best worker based on weights.
        Returns worker with highest weight (highest priority).
        """
        best_weight = 0
        best_worker_id = None

        async with self._workers_lock:
            for _, name, weight in self._worker_configs.items():
                for worker_id, worker in self._worker_info.items():
                    if weight > best_weight or (weight == best_weight and not best_worker_id):
                        best_weight = weight
                        best_worker_id = worker_id

        return self._worker_info[best_worker_id] if best_worker_id else None

    async def select_worker(self) -> Optional[WorkerInfo]:
        """
        Select the best worker based on weights.
        Returns worker with highest weight (highest priority).
        """
        if not self._worker_configs:
            return None

        best_weight = 0
        best_worker_id = None

        async with self._workers_lock:
            for _, name, weight in self._worker_configs.items():
                for worker_id, worker in self._worker_info.items():
                    if weight > best_weight or (weight == best_weight and not best_worker_id):
                        best_weight = weight
                        best_worker_id = worker_id

        return self._worker_info[best_worker_id] if best_worker_id else None

    async def list_workers(self) -> List[WorkerInfo]:
        """List all registered workers."""
        async with self._workers_lock:
            return list(self._worker_info.values())

    def save_state(self) -> None:
        """Save current state to file."""
        if not self._state_dir:
            return

        os.makedirs(self._state_dir, exist_ok=True)
        state_file = os.path.join(self._state_dir, "workers.state")

        state = {
            "workers": {wid: w.to_dict() for wid, w in self._worker_info.items()}
        }

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> None:
        """Load previous state from file."""
        if not self._state_dir:
            return

        state_file = os.path.join(self._state_dir, "workers.state")

        if not os.path.exists(state_file):
            return

        with open(state_file, "r") as f:
            state = json.load(f)
            self._worker_info.update({
                wid: WorkerInfo(
                    worker_id=info["worker_id"],
                    config=config,
                    started_at=info["started_at"],
                    status=info["status"],
                    task_count=info["task_count"]
                )
                for wid, info in state["workers"].items()
            })


# Initialize default registry
WORKER_REGISTRY: WorkerRegistry = WorkerRegistry()

# Export for backward compatibility - export the instance, not the class
WorkerTypes = WORKER_TYPES
