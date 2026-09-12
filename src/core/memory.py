"""
Memory manager for my-rxer application.

Provides in-process memory storage with optional Redis backup for persistence.
Supports key-value caching and context management.
"""

import json
import os
from typing import Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import threading


@dataclass
class MemoryEntry:
    """Single memory entry with metadata."""
    key: str
    value: str
    created_at: str = ""
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class InProcessMemory:
    """
    Thread-safe in-process memory storage.
    
    Use for fast, shared memory access during single application lifecycle.
    Not suitable for distributed or persistent storage.
    """
    
    def __init__(self):
        """Initialize empty memory store with lock for thread safety."""
        self._store: dict = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key, returns None if not found."""
        with self._lock:
            return self._store.get(key)
    
    def set(self, key: str, value: str) -> None:
        """Set key-value pair."""
        with self._lock:
            self._store[key] = value
    
    def delete(self, key: str) -> bool:
        """Delete key if exists, returns True if deleted."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in store."""
        with self._lock:
            return key in self._store
    
    def clear(self) -> None:
        """Clear all entries from store."""
        with self._lock:
            self._store.clear()
    
    def keys(self) -> list:
        """Get all keys in store."""
        with self._lock:
            return list(self._store.keys())
    
    def items(self) -> list:
        """Get all key-value pairs in store."""
        with self._lock:
            return [{"key": k, "value": v} for k, v in self._store.items()]
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator."""
        return key in self._store
    
    def __len__(self) -> int:
        """Return number of items."""
        return len(self._store)


class RedisMemory:
    """
    Redis-backed memory storage for persistence.
    
    Use for distributed or long-running deployments.
    Data is persisted beyond application lifecycle.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initialize Redis memory handler.
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
        """
        self.host = host
        self.port = port
        self.db = db
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        # TODO: When Redis is available, implement actual Redis calls
        # For now, return None as placeholder
        return None  # Implement with Redis connection
    
    async def set(self, key: str, value: Optional[str] = None, expire: int = 3600) -> bool:
        """
        Set value in Redis.
        
        Args:
            key: Storage key
            value: Value to store (will be JSON serialized)
            expire: TTL in seconds (default 1 hour)
        
        Returns:
            True if set successful, False otherwise
        """
        # Placeholder - TODO: implement real Redis calls
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        # Placeholder - TODO: implement real Redis calls
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        # Placeholder - TODO: implement real Redis calls
        return False
    
    async def clear(self) -> None:
        """Clear all keys in current database."""
        # Placeholder - TODO: implement real Redis calls
        pass
    
    async def keys(self) -> list:
        """Get all keys in database."""
        # Placeholder - TODO: implement real Redis calls
        return []


class MemoryManager:
    """
    Unified memory manager combining in-process and Redis storage.
    
    Provides seamless switching between local and distributed memory
    based on configuration.
    """
    
    def __init__(
        self, 
        use_redis: bool = False, 
        redis_url: Optional[str] = None,
        local_data_path: Optional[str] = None
    ):
        """
        Initialize memory manager.
        
        Args:
            use_redis: Whether to use Redis for persistence
            redis_url: Redis connection URL (optional)
            local_data_path: Path for local file persistence (optional)
        """
        self.use_redis = use_redis
        self._memory = InProcessMemory()  # Always have local memory
        
        # Initialize Redis connection if configured
        if use_redis and redis_url:
            self._redis = RedisMemory()
        else:
            self._redis = None
        
        # Local file persistence support
        self._local_persist_path = None
        if local_data_path and os.path.exists(local_data_path):
            persist_file = os.path.join(local_data_path, "memory.json")
            self._local_persist_path = persist_file
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value by key.
        
        Checks local memory first, then Redis if available.
        If local file persistence exists, also checks there.
        """
        # Check in-process memory first (fastest)
        value = self._memory.get(key)
        if value is not None:
            return value
        
        # Try Redis if configured
        if self._redis and self.use_redis:
            value = await self._redis.get(key)
            if value is not None:
                # Also cache in local memory
                self._self._memory.set(key, value)
                return value
        
        # Check local file persistence
        if self._local_persist_path:
            value = self._read_local_file(key)
            if value is not None:
                self._memory.set(key, value)
                return value
        
        return None
    
    async def set(self, key: str, value: Optional[str] = None) -> None:
        """
        Set value by key.
        
        Stores in in-process memory, and persists to Redis and local file if available.
        """
        # Serialize value to JSON
        json_value = json.dumps(value) if value is not None else None
        
        # Store in local memory
        self._memory.set(key, json_value)
        
        # Persist to Redis if configured
        if self._redis and self.use_redis:
            await self._redis.set(key, json_value)
        
        # Save to local file if configured
        if self._local_persist_path:
            await self._write_local_file(key, json_value)
    
    async def delete(self, key: str) -> bool:
        """Delete key from all storage backends."""
        deleted = False
        
        # Delete from local memory
        if self._memory.delete(key):
            deleted = True
        
        # Delete from Redis if configured
        if self._redis:
            if await self._redis.delete(key):
                deleted = True
        
        # Delete from local file if configured
        if self._local_persist_path:
            if self._memory.exists(key):
                self._memory.delete(key)
                await self._write_local_file(key, None)
                deleted = True
        
        return deleted
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in any storage backend."""
        if self._memory.exists(key):
            return True
        
        if self._redis and self.use_redis:
            if await self._redis.exists(key):
                return True
        
        return False
    
    async def clear(self) -> None:
        """Clear all memory from all backends."""
        # Clear local memory
        self._memory.clear()
        
        # Clear Redis if configured
        if self._redis and self.use_redis:
            await self._redis.clear()
        
        # Clear local file if configured
        if self._local_persist_path:
            await self._write_local_file("", None)
    
    async def _write_local_file(self, key: str, value: str) -> None:
        """
        Write value to local file.
        
        Ignores value if empty, reads all values back.
        """
        if value is None:
            return  # No value to write
        
        os.makedirs(os.path.dirname(self._local_persist_path), exist_ok=True)
        with open(self._local_persist_path, "r", encoding="utf-8") as f:
            self._local_data = json.load(f)
    
    def _read_local_file(self, key: str) -> Optional[str]:
        """Read value from local file by key."""
        if self._local_persist_path is None:
            return None
        
        try:
            with open(self._local_persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get(key)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def _get_local_data(self) -> dict:
        """Get all local data from file."""
        if self._local_persist_path is None:
            return {}
        
        try:
            with open(self._local_persist_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}