# Configuration

## Configuration Files

Hobo Code uses the following configuration files:

| File | Location | Purpose |
|------|----------|---------|
| `auto_switch.json` | `~/.hobo-code/` | Auto-switch settings |
| `credentials.json` | `~/.hobo-code/` | API keys |
| `preferences.json` | `~/.hobo-code/` | User preferences |

## Auto-Switch Configuration

```json
{
  "enabled": true,
  "use_llm": true,
  "min_keyword_confidence": 0.7,
  "min_llm_confidence": 0.6,
  "debounce_seconds": 3.0,
  "show_notifications": true,
  "notification_sound": true,
  "locked_skill": null
}
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | `true` | Enable auto-switching |
| `use_llm` | `true` | Use LLM for classification |
| `min_keyword_confidence` | `0.7` | Minimum keyword confidence |
| `min_llm_confidence` | `0.6` | Minimum LLM confidence |
| `debounce_seconds` | `3.0` | Delay before switching |
| `show_notifications` | `true` | Show toast notifications |
| `locked_skill` | `null` | Lock to specific skill |

## CLI Configuration

Use `hobo config` commands:

```bash
# Show configuration
hobo config show

# Enable/disable auto-switch
hobo config auto-switch on
hobo config auto-switch off

# Set confidence threshold
hobo config min-confidence 0.8

# Lock a skill
hobo config lock python_expert
hobo config lock  # Unlock

# Set debounce time
hobo config debounce 5.0
```

## Project Configuration

Projects can have a `.hobo-code/config` file:

```ini
[project]
name = "my-project"
created_at = "2024-01-15"

[skills]
primary_source = "leochong/HoboCode"
auto_download = true
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `GITHUB_TOKEN` | GitHub token |

---

*Back to [User Guide →](README.md)*
