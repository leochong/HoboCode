# Contributing to Hobo Code

Thank you for your interest in contributing! This guide will help you get started.

## Ways to Contribute

- **Bug Reports** - Find bugs and open issues
- **Feature Requests** - Suggest new features
- **Code Contributions** - Submit pull requests
- **Documentation** - Improve docs and examples
- **Skills** - Create new skill definitions
- **Translations** - Help localize Hobo Code

## Getting Started

### 1. Fork and Clone

```bash
git fork https://github.com/leochong/HoboCode
git clone https://github.com/YOUR-USERNAME/HoboCode
cd HoboCode
```

### 2. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows

pip install -e ".[dev]"
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature
```

### 4. Make Changes

Follow the coding standards in `AGENTS.md`:
- Use absolute imports
- Follow PEP 8 style
- Add type hints
- Write docstrings
- Add tests for new features

### 5. Run Tests

```bash
pytest           # Run all tests
pytest -v        # Verbose output
pytest -x        # Stop on first failure
```

### 6. Submit a Pull Request

1. Push your branch: `git push origin feature/your-feature`
2. Open a PR on GitHub
3. Describe your changes
4. Link any related issues

## Pull Request Guidelines

- **One feature per PR** - Keep PRs focused
- **Pass all tests** - Ensure CI passes
- **Add tests** - Cover new functionality
- **Update docs** - Document new features
- **Clear commit messages** - Use conventional commits

## Coding Standards

See `AGENTS.md` for detailed guidelines:

```python
# Correct imports
import os
from pathlib import Path

import click
from textual.app import App

from hobo_code.server import ACPServer
from hobo_code.tools import FileTool

# Type hints
def process_message(message: str, context: dict[str, str] | None = None) -> list[dict[str, object]]:
    ...

# Docstrings
def handle_request(self, request: ACPRequest) -> ACPResponse:
    """Handle a single ACP request.

    Args:
        request: The incoming ACP request.

    Returns:
        The response to send back.
    """
```

## Adding New Skills

Skills are stored in `skills/` directory:

```
skills/
├── language/
│   └── python_expert/
│       └── SKILL.md
├── task/
│   └── api_design/
│       └── SKILL.md
└── devops/
    └── docker_kubernetes/
        └── SKILL.md
```

See [Skill Creation Guide](skill-creation.md) for details.

---

*Next: [Architecture →](architecture.md)*
