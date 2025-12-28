# Installation

## Prerequisites

- Python 3.10+
- pip or poetry
- Terminal emulator

## Install from PyPI

```bash
pip install hobo
```

## Install from Source

```bash
git clone https://github.com/leochong/HoboCode
cd HoboCode
pip install -e ".[dev]"
```

## Verify Installation

```bash
hobo --version
hobo --help
```

## Configuration

Hobo Code stores configuration in `~/.hobo-code/`:

```
~/.hobo-code/
├── auto_switch.json   # Auto-switch preferences
├── credentials.json   # API keys
└── preferences.json   # User preferences
```

## API Keys

Set up your API keys for LLM providers:

```bash
hobo auth set anthropic <your-api-key>
hobo auth set openai <your-api-key>
```

---

*Next: [Quick Start →](quickstart.md)*
