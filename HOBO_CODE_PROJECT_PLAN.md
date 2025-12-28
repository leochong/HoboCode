# Hobo Code: Project Plan

## Project Overview

Hobo Code is an open-source, terminal-native AI coding assistant. It uses a nomadic, client-server architecture based on the Agent Client Protocol (ACP). It is designed to be lightweight and highly modular via a "Skills" system, allowing it to perform complex refactors and bug fixes across any codebase.

## Technical Architecture

### Decoupled Architecture

**The Server**: A Python-based agentic core that handles the ReAct loop, tool execution, and context management via LiteLLM.

**The Client**: A high-performance TUI built with Python Textual that connects to the server via ACP.

**The Protocol**: Implementation of the Agent Client Protocol (ACP) to allow seamless communication between the TUI, headless servers, and external interfaces.

## Development Phases

### Phase 1: The ACP Engine & Core Agent

**ACP Server**
- Implementation of `hobo-code acp` to handle client-server handshakes
- Protocol definition for agent-client communication
- Connection management and session handling

**Core Toolset**
- Basic file operations: read, write, list
- Shell execution with safety constraints
- File system navigation and manipulation
- Error handling and recovery

**Headless Modes**
- `serve` command to run the agent as a background service
- `web` command for browser-based interface
- Daemonized agent processes
- API endpoints for external integrations

### Phase 2: TUI & Session Management

**Textual Interface**
- Responsive chat interface built with Python Textual
- Markdown rendering for rich text display
- Syntax highlighting for code blocks
- Real-time streaming responses

**Session Persistence**
- `hobo-code session` command implementation
- List historical coding trajectories
- Resume previous sessions
- Delete unwanted sessions
- Conversation state serialization

**Stats Dashboard**
- `stats` command for real-time monitoring
- Token usage tracking per session
- Cost estimation across providers
- Performance metrics and analytics

### Phase 3: Identity & Model Management

**Secure Auth**
- `hobo-code auth` for managing credentials
- Local API key storage with encryption
- GitHub token management
- Secure credential retrieval

**Model Provider Sync**
- `hobo-code models` to list available providers
- Dynamic provider discovery via LiteLLM
- Support for 100+ model providers
- Easy model switching and configuration

**Modular Skills**
- Specialized persona definitions
- Expertise domains and configurations
- Custom tool collections per skill
- Skill-based agent routing

### Phase 4: GitHub Integration & Workflow

**Pull Request Logic**
- `hobo-code pr` command implementation
- Fetch and checkout PRs locally
- Automated PR repair and debugging
- Diff analysis and change review

**GitHub Agent**
- Repository indexing and analysis
- Remote repository management
- Issue tracking integration
- Branch and commit navigation

### Phase 5: Open SFT Pipeline

**JSONL Training Data Export**
- `hobo-code export` for session data in JSONL (JSON Lines) format
- Each line contains a complete conversation turn for SFT (Supervised Fine-Tuning)
- Format includes system prompt, user prompt, assistant response, and reasoning trace
- Chain of Thought (CoT) recording: capture reasoning steps before each tool use
- Metadata: model used, token counts, timestamps, task type, success/failure status

**Trajectory Schema (JSONL)**
```jsonl
{"system": "You are an expert coding assistant...", "messages": [{"role": "user", "content": "Fix the bug in..."}, {"role": "assistant", "content": "Let me analyze this...", "reasoning": "First I'll check the file...", "tool_calls": [{"name": "read", "params": {...}}], "content": "The issue is..."}], "model": "gpt-4", "tokens": 1500, "task": "bug_fix", "success": true}
{"system": "...", "messages": [{"role": "user", "content": "Refactor this function..."}], ...}
```

**Privacy Filtering**
- Local PII (Personally Identifiable Information) detection and removal
- Secret and API key detection/removal before export
- File path sanitization (replace absolute paths with relative)
- Configurable filter rules and allowlists
- Dry-run mode to preview filtered data

**Hugging Face Integration**
- `hobo-code export --push` to push to HF datasets
- `hobo-code donate` slash command for quick contribution
- Dataset versioning and metadata tracking
- Contributor attribution (anonymous or named)
- Community data sharing with opt-in licensing

**Quality Metrics**
- Success rate tracking per task type
- Token efficiency analysis
- Error pattern detection
- Conversation length distribution
- Skill coverage statistics

## Technical Stack

- **Language**: Python
- **Agent Framework**: Custom ReAct loop with LiteLLM integration
- **TUI Framework**: Python Textual
- **Protocol**: Agent Client Protocol (ACP)
- **Model Management**: LiteLLM for multi-provider support
- **Authentication**: Encrypted local credential storage
- **Data Export**: JSON with privacy filtering

## Success Metrics

- Seamless client-server communication via ACP
- Comprehensive file and shell toolset
- Responsive and functional TUI
- Secure credential management
- Extensive model provider support
- Full GitHub workflow integration
- Privacy-preserving data export

## Roadmap Priorities

1. **Phase 1**: Establish reliable ACP engine and core agent capabilities
2. **Phase 2**: Deliver polished TUI with session management
3. **Phase 3**: Enable model flexibility and secure authentication
4. **Phase 4**: Deep GitHub integration for developer workflows
5. **Phase 5**: Community contribution through SFT data pipeline
