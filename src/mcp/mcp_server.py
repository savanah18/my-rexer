"""
MCP (Model Context Protocol) server implementation for my-rxer.

Provides HTTP interface for LLM clients to interact with the system.
"""

from flask import Flask, request, jsonify
import logging
from tools_api import AVAILABLE_TOOLS

app = Flask(__name__)

logger = logging.getLogger(__name__)

# Available tools from tools_api
rapid_tools = list(AvailableTools)


def json_response(data):
    """Create a JSON response."""
    return jsonify(data)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return json_response({"status": "ok"})


@app.route("/mcp/status", methods=["GET"])
def mcp_status():
    """Get MCP server status."""
    return json_response({
        "status": "running",
        "version": "0.1.0"
    })


@app.route("/mcp/tools/search", methods=["GET"])
def mcp_tools_search():
    """
    Search/list available MCP tools.

    Args:
        types: Filter by tool type (e.g., "web", "file", "memory")

    Returns:
        List of available tools
    """
    tool_types = request.args.get("types")
    
    tools = rapid_tools.copy()
    
    if tool_types:
        filtered = []
        for tool in tools:
            if tool["type"] == tool_types.lower():
                filtered.append(tool)
        tools = filtered
    
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
    params = request.get_json(silent=True) if request.is_json else {}
    if request.method == "POST":
        params = request.get_json() or {}
    
    logger.info(f"MCP Tool invoke: {tool_name}, params: {params}")
    
    try:
        result = execute_tool(tool_name, params)
    except Exception as e:
        return jsonify({"error": str(e)})
    
    return jsonify({"result": result})


def execute_tool(tool_name, params):
    """Execute a tool and return its result."""
    tool_map = {
        "llm_generate": llm_generate,
        "web_scrape": web_scrape,
        "web_request": web_request,
        "file_read": file_read,
        "file_write": file_write,
        "memory_get": memory_get,
        "memory_set": memory_set
    }
    
    if tool_name not in tool_map:
        raise Exception(f"Unknown tool: {tool_name}")
    
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
    
    async def generate():
        async httpx.AsyncClient() as client:
            response = await client.post(
                "v1/completions",
                json={
                    "model": model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            return response.text
    
    # Run async function in thread pool
    result = asyncio.run(llm_generate())
    return {"result": result}


def web_scrape(url, headers=None):
    """
    Scrape content from URL.
    
    Args:
        url: URL to scrape
        headers: Optional HTTP headers
    
    Returns:
        Page content
    """
    from httpx import AsyncClient
    
    async def scrape():
        async with AsyncClient() as client:
            headers = headers or {}
            response = await client.get(url, headers=headers)
            return {
                "status": response.status_code,
                "content": response.text
            }
    
    return asyncio.run(scrape())


def web_request(method, url, body=None):
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
    
    async def request():
        async with AsyncClient() as client:
            json_data = body if body else None
            response = await client.request(method, url, json=json_data)
            return {
                "status": response.status_code,
                "text": response.text()
            }
    
    return asyncio.run(request())


def file_read(path):
    """
    Read file content.
    
    Args:
        path: File path to read
    
    Returns:
        File content
    """
    with open(str(path), "r") as f:
        return {"content": f.read(), "path": str(path)}


def file_write(path, content):
    """
    Write content to file.
    
    Args:
        path: File path to write
        content: Content to write
    
    Returns:
        Success status
    """
    with open(str(path), "w") as f:
        f.write(str(content))
    return {"path": str(path), "success": True}


def memory_get(key):
    """
    Get value from memory store.
    
    Args:
        key: Memory key to retrieve
    
    Returns:
        Stored value or None
    """
    # Placeholder - implements actual memory access
    return {"key": key, "value": None}


def memory_set(key, value):
    """
    Set value in memory store.
    
    Args:
        key: Memory key
        value: Value to store
    
    Returns:
        Success status
    """
    # Placeholder - implements actual memory storage
    return {"key": key, "value": value, "success": True}


@app.route("/llm/generate", methods=["POST"])
def generate_llm():
    """Direct endpoint for LLM generation."""
    data = request.get_json() or {}
    prompt = data.get("prompt", "")
    model = data.get("model", "gpt-3.5-turbo")
    max_tokens = data.get("max_tokens", 512)
    temperature = data.get("temperature", 0)
    
    result = llm_generate(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    return jsonify(result)


@app.route("/web/scrape", methods=["POST"])
def scrape_web():
    """Direct endpoint for web scraping."""
    data = request.get_json() or {}
    url = data.get("url", "")
    headers = data.get("headers", {})
    
    result = web_scrape(url=url, headers=headers)
    
    return jsonify(result)


@app.route("/web/request", methods=["POST"])
def request_web():
    """Direct endpoint for HTTP requests."""
    data = request.get_json() or {}
    method = data.get("method", "GET")
    url = data.get("url", "")
    body = data.get("body", {})
    
    result = web_request(method=method, url=url, body=body)
    
    return jsonify(result)


@app.route("/file/read", methods=["POST"])
def read_file():
    """Direct endpoint for file reading."""
    data = request.get_json() or {}
    path = data.get("path", "")
    
    result = file_read(path=path)
    
    return jsonify(result)


@app.route("/file/write", methods=["POST"])
def write_file():
    """Direct endpoint for file writing."""
    data = request.get_json() or {}
    path = data.get("path", "")
    content = data.get("content", "")
    
    result = file_write(path=path, content=content)
    
    return jsonify(result)


@app.route("/memory/get", methods=["POST"])
def get_memory():
    """Direct endpoint for memory retrieval."""
    data = request.get_json() or {}
    key = data.get("key", "")
    
    result = memory_get(key=key)
    
    return jsonify(result)


@app.route("/memory/set", methods=["POST"])
def set_memory():
    """Direct endpoint for memory storage."""
    data = request.get_json() or {}
    key = data.get("key", "")
    value = data.get("value", "")
    
    result = memory_set(key=key, value=value)
    
    return jsonify(result)


if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    debug = "debug" in sys.argv
    
    logger.info(f"Starting MCP server on port {port}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
