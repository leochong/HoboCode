# Command Reference

Complete reference for all Hobo Code CLI commands.

## Global Options

```bash
hobo --help      # Show help
hobo --version   # Show version
```

## Commands

### init

Initialize a new Hobo Code project.

```bash
hobo init <project-name> [description]
```

**Options:**
- `-p, --path PATH` - Project path
- `-t, --github-token TOKEN` - GitHub token for skill downloads

**Example:**
```bash
hobo init my-api "REST API for user management"
cd my-api
```

### chat

Start the TUI chat interface.

```bash
hobo chat
```

**Options:**
- `--session-id ID` - Resume a specific session

### skills

Manage AI skills.

```bash
hobo skills <subcommand>
```

#### skills list

List available skills.

```bash
hobo skills list
```

#### skills add

Add a skill from repository.

```bash
hobo skills add <skill-name>
```

**Options:**
- `--repo OWNER/REPO` - Source repository (default: leochong/HoboCode)

#### skills search

Search for skills.

```bash
hobo skills search <query>
```

#### skills detect

Detect which skill matches a message.

```bash
hobo skills detect "write a REST API"
```

**Options:**
- `-t, --top N` - Show top N recommendations

#### skills classify

Classify a message using LLM.

```bash
hobo skills classify "debug authentication issue"
```

**Options:**
- `--llm / --no-llm` - Use LLM classification (default: yes)

#### skills recommend

Get skill recommendations for a task.

```bash
hobo skills recommend "write tests for my code"
```

#### skills info

Show detailed skill information.

```bash
hobo skills info <skill-name>
```

### config

Manage user configuration.

```bash
hobo config <subcommand>
```

#### config show

Show current configuration.

```bash
hobo config show
```

#### config auto-switch

Enable/disable auto-switching.

```bash
hobo config auto-switch on
hobo config auto-switch off
```

#### config min-confidence

Set minimum confidence threshold.

```bash
hobo config min-confidence 0.7
```

#### config lock

Lock skill to prevent auto-switching.

```bash
hobo config lock python_expert  # Lock to skill
hobo config lock                # Unlock
```

#### config debounce

Set debounce time in seconds.

```bash
hobo config debounce 3.0
```

### session

Manage chat sessions.

```bash
hobo session list               # List sessions
hobo session resume <session-id> # Resume session
hobo session delete <session-id> # Delete session
```

### auth

Manage API credentials.

```bash
hobo auth set <provider> <key>  # Set API key
hobo auth list                  # List providers
hobo auth delete <provider>     # Delete key
hobo auth github <token>        # Set GitHub token
```

### models

Manage model providers.

```bash
hobo models list [provider]     # List models
hobo models info <model>        # Model information
```

### export

Export session data for training.

```bash
hobo export session <session-id> -o output.jsonl
hobo export all -o all_sessions.jsonl
hobo export stats               # Show statistics
```

---

*Next: [Configuration →](configuration.md)*
