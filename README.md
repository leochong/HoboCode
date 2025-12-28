# Hobo Code

An open-source, terminal-native AI coding assistant with a nomadic, client-server architecture based on the Agent Client Protocol (ACP).

## Overview

Hobo Code is designed to be lightweight and highly modular via a "Skills" system, allowing it to perform complex refactors and bug fixes across any codebase. It provides intelligent assistance directly from the terminal.

## Architecture

### The Server
Python-based agentic core that handles:
- **ReAct Loop**: Reasoning and acting for complex tasks
- **Tool Execution**: File operations, shell commands, search
- **Context Management**: Via LiteLLM for model integration

### The Client
High-performance terminal interface built with Python Textual:
- Responsive chat interface
- Markdown rendering
- Code highlighting
- Session management

### The Protocol
Agent Client Protocol (ACP) for seamless communication:
- Client-server handshakes
- Message parsing and routing
- Bidirectional communication

## Skills System

Modular skill definitions enable specialized agent personas:

```
skills/
├── language/          # Python, Rust, Go, JavaScript, etc.
├── framework/         # FastAPI, React, Spring Boot, etc.
├── task/              # Debugging, testing, refactoring, code review
├── devops/            # Docker, Kubernetes, CI/CD, Git workflows
├── specialized/       # Security audit, MCP builder, skill creation
└── general/           # Full-stack, architecture, problem-solving
```

Each skill is a JSON file containing:
- Name, description, and keywords
- System prompt with behavioral instructions
- Activation patterns (`when_to_use`, `when_not_to_use`)
- Examples and guidelines

## Development Phases

1. **ACP Engine & Core Agent**: Server implementation, core tools, headless modes
2. **TUI & Session Management**: Textual interface, session persistence, stats
3. **Identity & Model Management**: Auth, model provider sync, modular skills
4. **GitHub Integration & Workflow**: PR logic, repository management
5. **Open SFT Pipeline**: Data export, privacy filtering, HF integration

## Getting Started

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
make format && make lint
```

## Project Structure

```
hobo_code/
├── __init__.py
├── server/          # ACP server, agent loop, tools
├── client/          # Textual TUI implementation
├── tools/           # Tool implementations
└── skills/          # JSON skill definitions

tests/
├── conftest.py
├── server/
├── client/
└── tools/
```

## Documentation

- [Project Plan](HOBO_CODE_PROJECT_PLAN.md) - Detailed roadmap
- [AGENTS.md](AGENTS.md) - Guidelines for AI agents
- [CLAUDE.md](CLAUDE.md) - Claude Code specific guidance
- [skills/](skills/) - All skill definitions

## License

Open-source project.
