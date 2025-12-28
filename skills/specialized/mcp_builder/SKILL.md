---
name: "MCP Builder"
description: "Expert in building Model Context Protocol (MCP) servers for extending agent capabilities. Specializes in creating custom MCP tools and integrations."
version: "1.0.0"
author: "Hobo Code"
tags: ["mcp", "model-context-protocol", "tool", "server", "integration", "extension"]
---

# MCP Builder

## Overview

You are an MCP server builder. Create custom MCP servers following the MCP specification. Implement proper tool definitions with input schemas. Handle authentication and rate limiting. Use proper error handling. Create servers that extend agent capabilities with external data sources and APIs.

## When to Use

- Building MCP servers
- Creating custom tools for agents
- Integrating external APIs with agents
- Extending agent capabilities

## When Not to Use

- Non-MCP related development
- Simple scripting without MCP requirements

## Guidelines

### MCP Server Structure
```python
from mcp.server import Server
from mcp.types import Tool, InputSchema

app = Server("custom-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_documents",
            description="Search through documents for matching content",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    if name == "search_documents":
        return search_documents(**arguments)
    raise ValueError(f"Unknown tool: {name}")
```

### Tool Implementation
```python
async def search_documents(query: str, max_results: int = 10) -> str:
    """Search documents and return results."""
    from elasticsearch import AsyncElasticsearch
    
    es = AsyncElasticsearch(["http://localhost:9200"])
    
    try:
        results = await es.search(
            index="documents",
            body={
                "query": {"match": {"content": query}},
                "size": max_results
            }
        )
        
        formatted = []
        for hit in results["hits"]["hits"]:
            formatted.append({
                "title": hit["_source"].get("title", "Untitled"),
                "score": hit["_score"],
                "snippet": hit["_source"].get("content", "")[:200]
            })
        
        return json.dumps(formatted, indent=2)
    finally:
        await es.close()
```

## Tools

- `file_read` - Read file contents
- `file_write` - Write files
- `shell_exec` - Execute shell commands
- `grep` - Search file contents
- `glob` - Find files by pattern
- `diff` - Show file differences
