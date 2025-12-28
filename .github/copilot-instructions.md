# Copilot Instructions for Hobo Code

This file provides GitHub Copilot with guidance for working on the Hobo Code project.

## Project Description

Hobo Code is an open-source, terminal-native AI coding assistant using Agent Client Protocol (ACP) for client-server architecture. The system is written in Python and consists of:
- **Server**: Agentic core with ReAct loop, tool execution, LiteLLM integration
- **Client**: Terminal UI built with Python Textual
- **Skills**: Modular JSON-based skill definitions for specialized capabilities

## Language and Tools

- **Primary Language**: Python 3.10+
- **Framework**: Python Textual for TUI
- **Protocol**: ACP (Agent Client Protocol)
- **LLM Integration**: LiteLLM
- **Testing**: pytest with pytest-asyncio
- **Formatting**: Black, isort, ruff

## Code Style Requirements

### Type Hints (Mandatory)
Always use type hints for function signatures:

```python
def process_message(
    message: str,
    context: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    ...
```

### Import Organization
Order imports by category, alphabetize within each:

1. Standard library (`import os`, `from pathlib import Path`)
2. Third-party (`import click`, `from textual.app import App`)
3. Local application (`from hobo_code.server import ACPServer`)

Use absolute imports, never relative (`from .server import`).

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `acp_server.py` |
| Classes | PascalCase | `ACPServer` |
| Functions | snake_case | `execute_tool()` |
| Variables | snake_case | `user_message` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT` |

### Error Handling
Never use bare `except:` clauses. Always catch specific exceptions:

```python
try:
    result = await self._execute_tool(tool)
except FileNotFoundError as e:
    logger.error(f"Tool not found: {tool.name}")
    raise ToolExecutionError(f"Failed: {tool.name}") from e
```

### Async/Await Patterns
Use `async def` for all coroutines. Handle timeouts and cleanup:

```python
async def process(self, request: ACPRequest) -> ACPResponse:
    try:
        async with asyncio.timeout(30):
            return await self._handle(request)
    except asyncio.TimeoutError:
        return ACPResponse.error("Timeout")
```

## Project Structure

```
hobo_code/
├── server/          # ACP server, ReAct agent, tools
├── client/          # Textual TUI implementation
├── tools/           # File, shell, search tools
└── skills/          # JSON skill definitions by category

skills/
├── language/        # Python, Rust, Go, JS, etc.
├── framework/       # FastAPI, React, Spring, etc.
├── task/            # Debugging, testing, refactoring
├── devops/          # Docker, CI/CD, Kubernetes
├── specialized/     # Security, MCP, skills
└── general/         # Full-stack, architecture
```

## Skills Format

Skills are JSON files with this structure:

```json
{
  "name": "Skill Name",
  "description": "Clear description",
  "system_prompt": "Behavioral instructions",
  "tools": ["file_read", "shell_exec"],
  "model_config": {"temperature": 0.2, "max_tokens": 4096},
  "when_to_use": ["Pattern 1", "Pattern 2"],
  "when_not_to_use": ["Pattern 1", "Pattern 2"],
  "examples": ["Example 1", "Example 2"],
  "guidelines": ["Guideline 1", "Guideline 2"],
  "keywords": ["keyword1", "keyword2"]
}
```

### Skill Categories
- `language/` - Programming language expertise
- `framework/` - Framework-specific skills
- `task/` - Task-oriented capabilities
- `devops/` - DevOps and infrastructure
- `specialized/` - Security, integrations
- `general/` - General-purpose skills

### Creating Skills
1. Place in appropriate category folder
2. Follow existing skill structure
3. Include `when_to_use` patterns for activation
4. Add concrete `examples` and `guidelines`
5. Use `keywords` for skill discovery

## Testing

Use pytest with pytest-asyncio:

```python
@pytest.mark.asyncio
async def test_feature_scenario():
    # Arrange
    request = create_test_request()
    # Act
    response = await server.process(request)
    # Assert
    assert response.status == "success"
```

## Formatting Standards

- 4 spaces for indentation (no tabs)
- 100 character maximum line length
- Use Black for formatting
- Use isort for import sorting
- Add trailing commas in multi-line constructs

## Security Practices

- Validate all inputs before processing
- Never execute unsanitized shell commands
- Never commit secrets, API keys, or credentials
- Use parameterized queries for database operations
- Follow OWASP security guidelines

## Protocol Compliance

When working with ACP (Agent Client Protocol):
- Validate all message schemas before processing
- Handle protocol errors gracefully with proper error codes
- Log all protocol violations for debugging
- Ensure bidirectional communication works correctly

## Development Workflow

1. Read existing code before making changes
2. Add tests for new functionality
3. Run linting before committing
4. Update documentation/docstrings
5. Follow conventional commit messages

## Common Tasks

### Add New Language Skill
```bash
# Create skills/language/python_expert.json
# Follow structure of existing language skills
# Include language-specific guidelines
```

### Run Tests
```bash
pytest                    # All tests
pytest tests/test_x.py    # Single file
pytest -m unit           # By marker
```

### Format Code
```bash
black src/ tests/         # Format
isort src/ tests/         # Sort imports
ruff check src/           # Lint
```

## Important Notes

- Always read files before editing
- Preserve existing functionality when refactoring
- Add tests for new features
- Never make breaking changes without discussion
- Use AGENTS.md as the source of truth for code style
