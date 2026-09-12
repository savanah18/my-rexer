"""
Memory management MCP API endpoints.

Provides HTTP interface for memory storage operations.
"""

from flask import Flask, request, jsonify


logger = logging.getLogger(__name__)


@flask.route("/memory/<key>", methods=["GET"])
@flask.route("/memory/search", methods=["GET"])
def memory_get(key):
    """
    Get value from memory store by key.
    
    Args:
        key: Value to retrieve from memory store
    """
    from .memory import MemoryManager
    
    try:
        if key:
            mem = MemoryManager()
            return jsonify({"key": key, "value": mem.get(key)})
        else:
            # Return all values
            return jsonify({"_all_values": list(mem.values())})
    except Exception as e:
        return jsonify({"error": str(e)})