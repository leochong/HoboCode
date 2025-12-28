# Architecture

High-level architecture of Hobo Code.

## System Overview

```
┌─────────────────────────────────────────────────────┐
│                    Hobo Code                        │
├─────────────────────────────────────────────────────┤
│  Client (TUI)           │   Server (ACP)           │
│  - Textual App          │   - ReAct Loop           │
│  - Chat Interface       │   - Tool Execution       │
│  - Skills Panel         │   - Context Management   │
├─────────────────────────────────────────────────────┤
│                    Skills System                    │
│  - Skill Registry      │   - Detection Engine     │
│  - Skill Downloader    │   - Auto-Switch Manager  │
├─────────────────────────────────────────────────────┤
│                    Storage                          │
│  - Sessions            │   - Configuration        │
│  - Credentials         │   - Preferences          │
└─────────────────────────────────────────────────────┘
```

## Components

### Client (TUI)

Built with [Textual](https://textual.textualize.io/):

| Component | File | Purpose |
|-----------|------|---------|
| HoboApp | `client/app.py` | Main application |
| MessageList | `client/components.py` | Chat history |
| ChatInput | `client/components.py` | User input |
| SkillPanel | `client/skills.py` | Skills sidebar |
| SkillIndicator | `client/skills.py` | Active skill display |

### Server (ACP)

Agent Client Protocol implementation:

| Component | File | Purpose |
|-----------|------|---------|
| ACPServer | `server/acp.py` | Message routing |
| ACPMessage | `server/acp.py` | Message serialization |
| SkillAwareAgent | `server/agent.py` | ReAct agent |

### Skills System

| Component | File | Purpose |
|-----------|------|---------|
| SkillRegistry | `skills/registry.py` | Skill management |
| SkillDetectionEngine | `skills/detection.py` | Keyword matching |
| SkillClassifier | `skills/classifier.py` | LLM classification |
| AutoSwitchManager | `skills/auto_switch.py` | Auto-switch logic |
| SkillDownloader | `skills/downloader.py` | GitHub downloads |

## Data Flow

```
User Input → ChatInput → HoboApp
                        ↓
                  Auto-Switch Check
                        ↓
                  Skill Detection
                        ↓
                  ReAct Agent Loop
                        ↓
                  Tool Execution
                        ↓
                  Response + Context Update
                        ↓
                  UI Update
```

## ACP Protocol

The Agent Client Protocol (ACP) is a simple JSON-based protocol:

```json
// Request
{
  "type": "request",
  "payload": {
    "request_id": "abc123",
    "method": "skills.list",
    "params": {},
    "context": {}
  }
}

// Response
{
  "type": "response",
  "payload": {
    "request_id": "abc123",
    "status": "success",
    "result": {"skills": ["security_audit", "test_driven_development"]},
    "error": null
  }
}
```

## Directory Structure

```
hobo_code/
├── auth/           # Credentials and preferences
├── cli/            # Click command-line interface
├── client/         # Textual TUI
├── export/         # SFT training data export
├── github/         # GitHub integration
├── models/         # Model provider configuration
├── server/         # ACP server and agent
├── session/        # Chat session management
├── skills/         # Skill system
└── tools/          # Tool implementations
```

---

*Next: [Development Setup →](development.md)*
