# Auto-Switching

Hobo Code automatically detects which skill you need based on your messages and switches to it.

## How It Works

1. **Keyword Detection** - Matches words in your message to skill keywords
2. **LLM Classification** - Uses AI to understand your intent
3. **Confidence Scoring** - Calculates match confidence (0-100%)
4. **Auto-Switch** - Switches skill when confidence exceeds threshold

## Default Thresholds

| Method | Confidence Threshold |
|--------|---------------------|
| Keyword | 70% |
| LLM | 60% |

## Example

```
User: "Write unit tests for my authentication module"

Detection Process:
1. Keyword detection → test_driven_development (55% confidence)
2. Below keyword threshold (70%) → try LLM
3. LLM classifies intent → "unit testing for auth code"
4. LLM recommends test_driven_development (85% confidence)
5. Above LLM threshold (60%) → auto-switch!

Result: [Auto] Switched to task/test_driven_development (85%)
```

## Controls

### Toggle Auto-Switching

**CLI:**
```bash
hobo config auto-switch on   # Enable (default)
hobo config auto-switch off  # Disable
```

**TUI:**
- Press `Ctrl+A` to toggle auto-switching

### Set Confidence Threshold

```bash
# Set minimum confidence for auto-switch
hobo config min-confidence 0.8
```

### Lock a Skill

Prevent auto-switching to always use a specific skill:

```bash
hobo config lock python_expert  # Lock to Python skill
hobo config lock                # Unlock (allow auto-switch)
```

### Set Debounce Time

Prevent rapid skill switching:

```bash
hobo config debounce 5.0  # 5 second delay before switching
```

## Configuration File

Settings are stored in `~/.hobo-code/auto_switch.json`:

```json
{
  "enabled": true,
  "use_llm": true,
  "min_keyword_confidence": 0.7,
  "min_llm_confidence": 0.6,
  "debounce_seconds": 3.0,
  "show_notifications": true,
  "locked_skill": null
}
```

---

*Next: [Projects →](projects.md)*
