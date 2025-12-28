# Hobo Code Documentation

Welcome to Hobo Code's documentation! This is your comprehensive guide to using and understanding the terminal-native AI coding assistant.

## Quick Links

- **[User Guide](user/README.md)** - Get started with Hobo Code
- **[Community Guide](community/README.md)** - Contributing and development
- **[API Reference](api/README.md)** - Technical documentation

## What is Hobo Code?

Hobo Code is an open-source, terminal-native AI coding assistant with:

- **Skill-based persona system** - Switch between specialized AI behaviors
- **Automatic skill detection** - Intelligently suggests skills based on your tasks
- **Project-aware** - Understands your codebase structure
- **TUI-first design** - Built for developers who live in the terminal
- **Open Source** - Transparent, customizable, community-driven

## Core Features

### 1. AI Skills System
Skills are specialized personas that give the AI specific expertise:

| Skill | Description |
|-------|-------------|
| `security_audit` | Security-first design and vulnerability checking |
| `test_driven_development` | TDD methodology and testing best practices |
| `api_design` | REST API architecture and design patterns |
| `python_expert` | Python development best practices |
| `javascript_typescript` | JS/TS frontend development |
| `docker_kubernetes` | Container orchestration |

[Learn more about skills →](user/skills.md)

### 2. Auto-Switching
Hobo Code automatically switches skills based on your tasks:

```
User: "Write unit tests for authentication"
→ System detects: test_driven_development (85% confidence)
→ Auto-switches to TDD skill
```

[Learn more about auto-switching →](user/auto-switch.md)

### 3. Project Management
Create project-plan.md files and let Hobo Code understand your project structure.

[Learn more about projects →](user/projects.md)

### 4. TUI Interface
Terminal-native interface with skill panels, chat history, and more.

[Learn more about the TUI →](user/tui.md)

## Installation

**Windows (recommended):**
```bash
pip install pipx
pipx install hobo
```

**Other platforms:**
```bash
pip install hobo

# Or install from source
git clone https://github.com/leochong/HoboCode
cd HoboCode
pip install -e .
```

[Full installation guide →](user/installation.md)

## Getting Started

1. **Initialize a project:**
   ```bash
   hobo init my-project "My new project"
   cd my-project
   ```

2. **Start the chat:**
   ```bash
   hobo chat
   ```

3. **Activate a skill:**
   ```
   /skill python_expert
   ```

4. **Or let auto-switch handle it!**

## Command Reference

| Command | Description |
|---------|-------------|
| `hobo chat` | Start the TUI chat interface |
| `hobo init <name> [desc]` | Initialize a new project |
| `hobo skills list` | List available skills |
| `hobo skills add <name>` | Add a skill from repository |
| `hobo skills detect <msg>` | Detect skill for a message |
| `hobo config show` | Show current configuration |
| `hobo config auto-switch on/off` | Toggle auto-switching |

[Full command reference →](user/commands.md)

## Architecture

```
Hobo Code
├── Server (ACP)     - ReAct agent loop, tool execution
├── Client (TUI)     - Textual-based terminal UI
├── Skills           - Persona/system prompt definitions
├── Tools            - File operations, git, etc.
└── Session          - Chat history and context
```

[Architecture overview →](community/architecture.md)

## Contributing

We welcome contributions! Here's how you can help:

- **Add skills** - Create new skill definitions
- **Improve docs** - Fix typos, add examples
- **Report bugs** - Open issues on GitHub
- **Submit PRs** - Contribute code

[Contributing guide →](community/contributing.md)

## Links

- **GitHub:** https://github.com/leochong/HoboCode
- **Issues:** https://github.com/leochong/HoboCode/issues
- **Discussions:** https://github.com/leochong/HoboCode/discussions

---

*Built with ❤️ for developers who love the terminal*
