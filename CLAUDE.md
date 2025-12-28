# CLAUDE.md

This file provides guidance for Claude Code when operating in this repository.

## Project Overview

Hobo Code is an open-source, terminal-native AI coding assistant with a nomadic, client-server architecture based on the Agent Client Protocol (ACP). It helps software engineers with coding tasks directly from the terminal.

## Architecture

```
hobo_code/
├── server/          # ACP Server - ReAct agent loop, tool execution
├── client/          # Textual TUI - Terminal user interface
├── tools/           # Core tool implementations (file, shell, etc.)
├── skills/          # Modular skill definitions (JSON-based)
└── ...
```

**Key Components:**
- **ACP Server** (`server/`): Python-based agentic core handling ReAct loop, tool execution, context management via LiteLLM
- **TUI Client** (`client/`): High-performance terminal interface built with Python Textual
- **Skills System** (`skills/`): JSON-based skill definitions for specialized agent personas
- **Protocol**: ACP (Agent Client Protocol) for client-server communication

## Development Commands

```bash
# Setup
python -m venv venv && .\venv\Scripts\activate && pip install -e ".[dev]"

# Testing
pytest                          # All tests
pytest tests/test_core.py       # Single file
pytest -m unit -v              # By marker

# Linting
make lint        # Run all linters
make format      # Auto-format code
ruff check src/  # Check without modifying
```

## Code Conventions

- Python 3.10+ with type hints using `|` operator (e.g., `str | None`)
- 4 spaces, 100 char limit, Black formatting
- Absolute imports: `from hobo_code.server import ACPServer`
- snake_case for functions/variables, PascalCase for classes
- Specific exception handling, never bare `except:`
- Async/await for all coroutines with proper cleanup

## Skills System

Skills are modular capabilities in `skills/` organized by category:
- `language/` - Language-specific skills (Python, Rust, Go, etc.)
- `framework/` - Framework skills (FastAPI, React, etc.)
- `task/` - Task-oriented skills (debugging, testing, etc.)
- `devops/` - DevOps skills (Docker, CI/CD, etc.)
- `specialized/` - Specialized skills (security, MCP builder, etc.)
- `general/` - General-purpose skills

Each skill is a JSON file with:
- `name`, `description`, `keywords`
- `system_prompt` with behavioral guidelines
- `when_to_use` / `when_not_to_use` patterns
- `examples` and `guidelines`

## Working with Skills

When creating or modifying skills:
1. Follow patterns from existing skills in the same category
2. Include `when_to_use` and `when_not_to_use` for activation
3. Provide concrete `examples` and detailed `guidelines`
4. Use `keywords` for skill discovery and routing
5. Ensure consistent structure across all skills

## ACP Protocol

When working on the ACP protocol:
- Validate message schemas before processing
- Handle protocol errors with proper error codes
- Log violations for debugging
- Ensure bidirectional communication

## Key Files

- `AGENTS.md` - Guidelines for AI agents
- `skills/` - All skill definitions
- `HOBO_CODE_PROJECT_PLAN.md` - Project roadmap
- `server/` - ACP server implementation
- `client/` - TUI implementation

## Common Tasks

**Add a new language skill:**
1. Create `skills/language/{language}_{domain}.json`
2. Follow structure of existing language skills
3. Include language-specific guidelines and examples

**Add a new task skill:**
1. Create `skills/task/{task_name}.json`
2. Define clear `when_to_use` patterns
3. Provide actionable `guidelines`

**Run tests:**
pytest -v --cov=src

**Format code:**
black src/ tests/ && isort src/ tests/
