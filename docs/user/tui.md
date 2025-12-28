# TUI Interface

The Hobo Code Terminal User Interface (TUI) is built with [Textual](https://textual.textualize.io/).

## Layout

```
+------------------------------------------+
| Hobo Code | Connected           [Status]  |
+------------------------------------------+
|          |                                  |
|  Chat    |  SKILLS                         |
|  History |  +----------------------------+ |
|          |  | [*] api_design (active)    | |
|          |  |   python_expert            | |
|          |  |   test_driven_development  | |
|          |  +----------------------------+ |
|          |  Active: task/api_design      |
+------------------------------------------+
| [Skill: task/api_design]                 |
| Type a message...                        |
+------------------------------------------+
| Ctrl+C: Quit  Ctrl+L: Clear  Ctrl+S: Skills  Ctrl+A: Auto |
+------------------------------------------+
```

## Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Ctrl+C` | Quit |
| `Ctrl+L` | Clear chat |
| `Ctrl+S` | Toggle skills panel |
| `Ctrl+A` | Toggle auto-switching |

## Chat Commands

In the chat input, you can use these commands:

| Command | Description |
|---------|-------------|
| `/skill list` | Show available skills |
| `/skill <name>` | Activate a skill |
| `/skill clear` | Deactivate current skill |
| `/skill info [name]` | Show skill details |

## Skills Panel

The skills panel shows:
- All available skills
- Currently active skill (marked with `[*]`)
- Skill description on hover

Press `Ctrl+S` to toggle visibility.

## Notifications

When auto-switch activates a skill, you'll see:

```
[Auto] Switched to task/test_driven_development (85%)
```

The notification auto-dismisses after 3 seconds.

---

*Next: [Command Reference →](commands.md)*
