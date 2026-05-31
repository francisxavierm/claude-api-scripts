# src/tools.py
import os
import json
from pathlib import Path

# ── Tool schemas (passed to the Anthropic API)
TOOL_SCHEMAS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information. Use this when you need "
            "up-to-date facts, news, documentation, or anything not in your "
            "training data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a local file and return them as text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                "type": "string",
                "description": "The file path to read (absolute or relative to cwd)."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write text content to a local file, creating it if it does not exist.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to write to."
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write."
                }
            },
            "required": ["path", "content"]
        }
    }
]

# ── Tool executors
def web_search(query: str) -> str:
    """Execute a web search using Tavily (falls back to Brave)."""
    # --- Tavily ---
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        from tavily import TavilyClient
        client = TavilyClient(api_key=tavily_key)
        result = client.search(query, max_results=3)
        # Format results as readable text
        lines = []
        for r in result.get("results", []):
            lines.append(f"[{r['title']}]({r['url']})\n{r['content']}\n")
        return "\n".join(lines) if lines else "No results found."

# --- Brave Search fallback ---
    brave_key = os.getenv("BRAVE_API_KEY")
    if brave_key:
        import requests
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": brave_key
        }
        params = {"q": query, "count": 3}
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers, params=params
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("web", {}).get("results", [])
        lines = []
        for r in results:
            lines.append(f"[{r['title']}]({r['url']})\n{r.get('description', '')}\n")
        return "\n".join(lines) if lines else "No results found."
    return "Error: No search API key configured. Set TAVILY_API_KEY or BRAVE_API_KEY."

def read_file(path: str) -> str:
    """Read a local file and return its contents."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: File not found at '{path}'."
    except Exception as e:
        return f"Error reading file: {e}"
 
def write_file(path: str, content: str) -> str:
    """Write content to a local file."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to '{path}'."
    except Exception as e:
        return f"Error writing file: {e}"

# ── Dispatch table
TOOL_EXECUTORS = {
    "web_search": lambda inp: web_search(inp["query"]),
    "read_file": lambda inp: read_file(inp["path"]),
    "write_file": lambda inp: write_file(inp["path"], inp["content"]),
}
def execute_tool(name: str, tool_input: dict) -> str:
    """Route a tool call to the correct executor."""
    executor = TOOL_EXECUTORS.get(name)
    if not executor:
        return f"Error: Unknown tool '{name}'."
    return executor(tool_input)