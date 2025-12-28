# AGENTS.md - Guidelines for AI Coding Agents

This document provides guidelines for AI coding agents operating in the Hobo Code repository.

## Project Overview

Hobo Code is an open-source, terminal-native AI coding assistant with a nomadic, client-server architecture based on the Agent Client Protocol (ACP). The system consists of:
- **Server**: Python-based agentic core (ReAct loop, tool execution, context management via LiteLLM)
- **Client**: High-performance TUI built with Python Textual
- **Protocol**: Agent Client Protocol (ACP) for seamless communication

## Build, Lint, and Test Commands

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_core.py

# Run a single test function
pytest tests/test_core.py::test_agent_initialization

# Run tests with specific marker
pytest -m unit
pytest -m integration

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run tests in verbose mode
pytest -v

# Run tests and stop on first failure
pytest -x
```

### Linting and Formatting

```bash
# Run all linters
make lint

# Format code
make format  # or: black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
make typecheck  # or: mypy src/

# Lint without modifying files
make lint-check  # or: ruff check src/ tests/
```

### Pre-commit Checks

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
pre-commit run ruff
```

## Code Style Guidelines

### Imports

- Use absolute imports: `from hobo_code.core import Agent` (not relative `from .core import Agent`)
- Group imports in this order: standard library, third-party, local application
- Sort imports alphabetically within each group
- Use `isort` to enforce import order
- Avoid wildcard imports (`from module import *`)

```python
# Correct
import os
import sys
from pathlib import Path

import click
from textual.app import App

from hobo_code.server import ACPServer
from hobo_code.tools import FileTool
```

### Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use Black for automatic formatting
- Add trailing commas in multi-line constructs
- Use parentheses for long function calls

```python
# Correct
result = some_long_function_name(
    arg_one,
    arg_two,
    arg_three=True,
)

# Incorrect
result = some_long_function_name(arg_one, arg_two, arg_three=True)
```

### Type Hints

- Use type hints for all function signatures (Python 3.10+)
- Use `|` operator for union types: `str | None` (not `Optional[str]`)
- Use `object` instead of `Any` when possible
- Import generics from `typing`: `from typing import List, Dict`
- Avoid type comments (use inline types)

```python
# Correct
def process_message(
    message: str,
    context: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    ...

# Incorrect
def process_message(message, context=None):
    # type: (str, dict | None) -> list[dict]
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | lowercase with underscores | `acp_server.py` |
| Classes | PascalCase | `ACPServer`, `TextualClient` |
| Functions | snake_case | `handle_message()`, `execute_tool()` |
| Variables | snake_case | `user_message`, `tool_result` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT`, `MAX_RETRIES` |
| Private methods | snake_case with leading underscore | `_validate_request()` |
| Type variables | PascalCase | `T = TypeVar("T")` |

### Error Handling

- Use specific exception types, never bare `except:` clauses
- Wrap external calls (file I/O, network) in try/except
- Log errors with appropriate level before re-raising
- Create custom exception classes for domain errors

```python
# Correct
try:
    result = await self._execute_tool(tool)
except FileNotFoundError as e:
    logger.error(f"Tool file not found: {tool.name}")
    raise ToolExecutionError(f"Failed to execute {tool.name}") from e
except Exception as e:
    logger.exception("Unexpected error during tool execution")
    raise

# Incorrect
try:
    result = await self._execute_tool(tool)
except:
    pass  # Silent failure
```

### Async/Await

- Use `async def` for all coroutines
- Never block on async code; use `await` consistently
- Handle cancellation with `try/finally` for cleanup
- Use `asyncio.timeout()` for timeout handling (Python 3.11+)

```python
async def process_request(self, request: ACPRequest) -> ACPResponse:
    try:
        async with asyncio.timeout(30):
            result = await self._process(request)
        return ACPResponse.success(result)
    except asyncio.TimeoutError:
        logger.warning(f"Request {request.id} timed out")
        return ACPResponse.error("Request timed out")
    finally:
        await self._cleanup(request)
```

### Docstrings and Comments

- Use docstrings for all public functions, classes, and modules
- Follow Google docstring format
- Document exceptions that functions may raise
- Keep comments concise; explain "why", not "what"

```python
class ACPServer:
    """Manages ACP protocol communication between client and agent.

    The server handles client connections, parses ACP messages,
    and routes requests to the appropriate agent handlers.

    Attributes:
        host: Server bind address.
        port: Server bind port.
        agent: The agent instance for processing requests.
    """

    async def handle_client(
        self,
        client: ACPClient,
    ) -> None:
        """Handle a single client connection.

        Args:
            client: The client connection to handle.

        Raises:
            ConnectionError: If the client disconnects unexpectedly.
        """
```

### Testing Guidelines

- Write tests using pytest with async support (`pytest-asyncio`)
- Use descriptive test names: `test_feature_scenario`
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies (file system, network)
- Keep tests independent and fast
- Aim for meaningful coverage, not arbitrary percentage

```python
@pytest.mark.asyncio
async def test_server_handles_valid_request(server: ACPServer):
    """Test that server processes valid ACP requests correctly."""
    # Arrange
    request = create_test_request()

    # Act
    response = await server.process(request)

    # Assert
    assert response.status == "success"
    assert response.result is not None
```

### File Organization

- Keep files under 500 lines when possible
- Use `src/` for application code, `tests/` for tests
- Create `__init__.py` files for packages
- Place configuration at module level when possible

```
hobo_code/
├── __init__.py
├── server/
│   ├── __init__.py
│   ├── acp.py          # ACP protocol handling
│   └── agent.py        # ReAct agent loop
├── client/
│   ├── __init__.py
│   └── textual.py      # TUI implementation
├── tools/
│   ├── __init__.py
│   ├── file.py         # File operations
│   └── shell.py        # Shell execution
└── skills/
    └── ...
tests/
├── conftest.py
├── server/
├── client/
└── tools/
```

### Protocol Compliance

When working with ACP (Agent Client Protocol):
- Validate all message schemas before processing
- Handle protocol errors gracefully with proper error codes
- Log all protocol violations for debugging
- Ensure bidirectional communication works correctly

## Additional Guidelines

1. **Read before editing**: Always read existing files before making changes
2. **Preserve functionality**: Maintain existing behavior when refactoring
3. **Add tests**: Include tests for new functionality
4. **Update documentation**: Keep docstrings and comments current
5. **Commit messages**: Follow conventional commits format
6. **No breaking changes**: Avoid changes that break existing functionality
7. **Security first**: Validate all inputs; never execute unsanitized commands
