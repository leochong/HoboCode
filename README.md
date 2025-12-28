# Hobo Code

An open-source, terminal-native AI coding assistant with a nomadic, client-server architecture based on the Agent Client Protocol (ACP).

## What Makes Hobo Code Different

### Open-SFT Pipeline: Build Your Own Coding AI

**Hobo Code is the only AI coding assistant that exports conversation data for training your own models.**

```bash
# Export sessions as JSONL training data
hobo export --format jsonl --push-to-hf

# Each line captures the full reasoning trace:
# {"system": "...", "messages": [{"role": "user", "content": "..."}], 
#  "reasoning": "Let me analyze this step by step...", 
#  "tool_calls": [...], "content": "The solution is..."}
```

**Training Data Features:**
- **Chain of Thought Recording**: Captures reasoning steps before each tool use
- **Tool Call Traces**: Every file read, search, and edit is logged
- **Privacy-Filtered**: Automatic PII and secret detection/removal
- **Hugging Face Integration**: Push curated datasets with one command
- **SFT-Ready Format**: Each JSONL line is a complete training example

This makes Hobo Code invaluable for:
- Training domain-specific coding assistants
- Researching agent reasoning patterns
- Building fine-tuned models for your codebase

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

### Skills System

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
5. **Open SFT Pipeline**: JSONL data export with Chain of Thought, privacy filtering, HF integration

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
├── github/          # GitHub integration (PR, issues, repo management)
├── auth/            # Encrypted credential storage
├── models/          # Model provider management
├── skills/          # JSON skill definitions
└── session/         # Session persistence and export

tests/
├── conftest.py
├── test_acp.py
├── test_client.py
├── test_file_tool.py
├── test_session.py
├── test_auth.py
├── test_models.py
├── test_github.py
└── test_pr.py
```

## Documentation

### User Guide
- [Installation](docs/user/installation.md) - Setup and configuration
- [Quickstart](docs/user/quickstart.md) - 5-minute getting started guide
- [Skills](docs/user/skills.md) - Using the skills system
- [Auto-Switch](docs/user/auto-switch.md) - Automatic skill detection
- [Commands](docs/user/commands.md) - Complete CLI command reference
- [Configuration](docs/user/configuration.md) - Customizing Hobo Code
- [TUI](docs/user/tui.md) - Terminal interface guide

### API & Development
- [API Reference](docs/api/README.md) - Python API documentation
- [Contributing](docs/community/contributing.md) - Developer guide
- [Architecture](docs/community/architecture.md) - System architecture overview

### Other
- [Project Plan](HOBO_CODE_PROJECT_PLAN.md) - Detailed roadmap
- [AGENTS.md](AGENTS.md) - Guidelines for AI agents
- [CLAUDE.md](CLAUDE.md) - Claude Code specific guidance
- [skills/](skills/) - All skill definitions

## License

Open-source project.
