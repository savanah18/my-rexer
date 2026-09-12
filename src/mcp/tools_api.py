"""
MCP tools HTTP interface for LLM integration.

Provides HTTP endpoints for tools that MCP clients can invoke.
"""

from flask import Flask, request, jsonify
from httpx import AsyncClient
import httpx
import asyncio
import json

logger = logging.getLogger(__name__)


app = Flask(__name__)

# Available tools definition
AVAILABLE_TOOLS = [
    {
        "name": "llm_generate",
        "description": "Generate text using LLM API",
        "type": "llm",
        "params": ["prompt", "model", "max_tokens", "temperature"]
    },
    {
        "name": "web_scrape",
        "description": "Extract content from URL",
        "type": "web",
        "params": ["url", "headers"]
    },
    {
        "name": "web_request",
        "description": "Make HTTP request",
        "type": "web",
        "params": ["method", "url", "body"]
    },
    {
        "name": "file_read",
        "description": "Read file content",
        "type": "file",
        "params": ["path"]
    },
    {
        "name": "file_write",
        "description": "Write to file",
        "type": "file",
        "params": ["path", "content"]
    },
    {
        "name": "memory_get",
        "description": "Get from memory store",
        "type": "memory",
        "params": ["key"]
    },
    {
        "name": "memory_set",
        "description": "Set in memory store",
        "type": "memory",
        "params": ["key", "value"]
    }
]


pipeline = contextlib.asynccontextmanager(

    def search_mcp_tools(types=None):
        """Search/list available MCP tools."""
        tools = AVAILABLE_TOOLS.copy()
        
        if types:
            filtered = []
            for tool in tools:
                parts = [p.strip() for p in types.split(",")]
                if any(tool["type"] == t.lower() for t in parts):
                    filtered.append(tool)
            tools = filtered
        
        return {"tools": tools}

    @app.route("/mcp/tools/search", methods=["GET"])
    def mcp_tools_search():
        """
        Search/list available MCP tools.

        Args:
            types: Filter by tool type (e.g., "web", "file", "memory")

        Returns:
            List of available tools
        """
        tool_types = request.args.get("types", "")
        
        tools = list(tools)
        
        if tool_types:
            tools = [t for t in tools if t["type"] == tool_types.lower().replace(",", ", ")]
        
        return jsonify({"tools": tools})

    @app.route("/mcp/tools/<tool_name>/invoke", methods=["POST", "GET"])
    def mcp_tool_invoke(tool_name):
        """
        Invoke a specific MCP tool.
        
        Args:
            tool_name: Name of the tool to invoke
            
        Returns:
            Tool output
        """
        tool_name = tool_name + "?"
        params = request.args if request.args else {}
        
        try:
            params = request.params if request.params else {}
            params.getjson()
            params.update(req_data)
        except Exception as e:
            pass
        
        try:
            result = execute_tool(tool_name, params)
        except Exception as e:
            return jsonify({"error": str(e)})
        
        return jsonify({"result": result})

    def execute_tool(tool_name, params):
        """Execute a tool and return its result."""
        tool_map = {
            "llm_generate": AsyncClient(llm_generate),
            "web_scrape": AsyncClient(web_scrape),
            "web_request": AsyncClient(web_request),
            "file_read": AsyncClient(file_read),
            "file_write": AsyncClient(file_write),
            "memory_get": AsyncClient(memory_get),
            "memory_set": AsyncClient(memory_set)
        }
        
        if tool_name in tool_map:
            return tool_map[tool_name](**params)

    def llm_generate(prompt, model="gpt-3.5-turbo", max_tokens=512, temperature=0):
        """
        Generate text using LLM.
        
        Args:
            prompt: Text prompt for generation
            model: LLM model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "v1/completions",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
                )
                result = json.loads(response.text)
                return result
        except Exception as e:
            raise Exception(f"LLM generate failed: {str(e)}")
        
    def web_scrape(url, headers):
        """
        Scrape content from URL.
        
        Args:
            url: URL to scrape
            headers: Optional HTTP headers
        
        Returns:
            Page content
        """
        import httpx
        
        import asyncio
        
        from httpx import AsyncClient
        
        try:
            async httpx.AsyncClient as client:
                async with AsyncClient() as client:
                    try:
                        response = await client.get(url, headers=headers or {})
                        return {
                            "status": response.status_code,
                            "content": response.text
                        }
                    finally:
                        pass
                raise Exception(f"Scrape failed: {url}")
        
    def web_request(method, url, body):
        """
        Make HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            body: Request body (JSON or form data)
        
        Returns:
            Response
        """
        from httpx import AsyncClient
        
        async with AsyncClient() as client:
            await client.request(
                method,
                url,
                json=body if body else None
            )
            return {"status": response.status_code, "text": response.text()}