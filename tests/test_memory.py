"""Unit tests for memory module."""
import pytest
import threading
from src.core.memory import MemoryEntry, InProcessMemory

class TestMemoryEntry:
    """Test MemoryEntry dataclass."""
    
    def test_memory_entry_default(self):
        """MemoryEntry with default values."""
        entry = MemoryEntry(key="test-key", value="test-value")
        assert entry.key == "test-key"
        assert entry.value == "test-value"
        assert isinstance(entry.created_at, str)
        assert entry.updated_at is None
    
    def test_memory_entry_with_update(self):
        """MemoryEntry with explicit update time."""
        entry = MemoryEntry(key="test-key", value="test-value", updated_at="2024-01-01")
        assert entry.key == "test-key"
        assert entry.value == "test-value"
        assert entry.updated_at == "2024-01-01"
    
    def test_memory_entry_to_dict(self):
        """MemoryEntry converts to dict properly."""
        entry = MemoryEntry(key="test-key", value="test-value")
        data = entry.to_dict()
        assert data["key"] == "test-key"
        assert data["value"] == "test-value"


class TestInProcessMemory:
    """Test in-process memory implementation."""
    
    def test_memory_initialization(self):
        """InProcessMemory is initialized with empty state."""
        memory = InProcessMemory()
        assert type(memory._lock).__name__ == "RLock"
        assert len(memory._store) == 0
    
    def test_memory_set_and_get(self):
        """Basic set and get operations."""
        memory = InProcessMemory()
        memory.set("key1", "value1")
        result = memory.get("key1")
        assert result == "value1"
        assert memory.get("nonexistent") is None
    
    def test_memory_delete(self):
        """Delete operations."""
        memory = InProcessMemory()
        memory.set("key1", "value1")
        assert memory.delete("key1") is True
        assert memory.delete("key1") is False  # Already deleted
    
    def test_memory_exists(self):
        """Check existence."""
        memory = InProcessMemory()
        assert not memory.exists("none")
        memory.set("exists", "value")
        assert memory.exists("exists")
    
    def test_memory_clear(self):
        """Clear operations."""
        memory = InProcessMemory()
        memory.set("a", "1")
        memory.set("b", "2")
        memory.clear()
        assert len(memory) == 0
        assert not memory.exists("a")
        assert not memory.exists("b")
    
    def test_memory_keys(self):
        """Get all keys."""
        memory = InProcessMemory()
        memory.set("x", "1")
        memory.set("y", "2")
        keys = memory.keys()
        assert "x" in keys
        assert "y" in keys
    
    def test_memory_items(self):
        """Get key-value pairs."""
        memory = InProcessMemory()
        memory.set("a", "1")
        memory.set("b", "2")
        items = memory.items()
        # items returns list of dicts: [{"key": "a", "value": "1"}, ...]
        found_a = any(item["key"] == "a" and item["value"] == "1" for item in items)
        assert found_a
        assert len(items) == 2
    
    def test_memory_contains_operator(self):
        """Use 'in' operator with memory."""
        memory = InProcessMemory()
        assert "existing" not in memory
        memory.set("existing", "value")
        assert "existing" in memory
    
    def test_memory_len_operator(self):
        """Use len() with memory."""
        memory = InProcessMemory()
        assert len(memory) == 0
        memory.set("one", "1")
        assert len(memory) == 1
        memory.set("two", "2")
        assert len(memory) == 2
    
    def test_memory_thread_safety_basic(self):
        """Basic thread safety test."""
        memory = InProcessMemory()
        results = []
        
        def write_key(i):
            for _ in range(10):
                memory.set(f"key{i}_{_}", f"value{i}_{_}")
            results.append(i)
        
        threads = [threading.Thread(target=write_key, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 5