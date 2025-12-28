# Quick Start

Get up and running with Hobo Code in 5 minutes!

## Step 1: Initialize a Project

```bash
# Create a new project with default skills
hobo init my-project "My awesome project"
cd my-project
```

This creates:
- `project-plan.md` - Your project roadmap
- `skills/` directory - Skill files
- `.hobo-code/` - Hobo Code configuration

## Step 2: Start Chatting

```bash
hobo chat
```

This opens the TUI where you can:
- Type messages and press Enter to send
- Use `/skill` commands to activate specific skills
- Press `Ctrl+S` to toggle the skills panel
- Press `Ctrl+A` to toggle auto-switching

## Step 3: Try a Skill

In the chat, try:

```
/skill python_expert
Can you help me refactor this Python code?
```

Or let auto-switch handle it:

```
Write unit tests for my authentication module
```

The system will automatically detect the intent and switch to the appropriate skill.

## Step 4: Explore Commands

```bash
# List available skills
hobo skills list

# Detect which skill matches a task
hobo skills detect "Write a REST API"

# Show current configuration
hobo config show

# Toggle auto-switching
hobo config auto-switch off  # Manual mode
hobo config auto-switch on   # Auto mode (default)
```

## First Project Example

```bash
# Create a new project
hobo init web-api "REST API for user management"

# Start coding
hobo chat

# Try these commands in chat:
# 1. "/skill api_design" - Activate API design skill
# 2. "Create a REST API for user authentication with JWT"
# 3. "/skill test_driven_development" - Switch to TDD
# 4. "Write pytest tests for the authentication module"
```

---

*Next: [Skills System →](skills.md)*
