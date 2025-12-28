# Projects

Hobo Code projects include a `project-plan.md` file that helps the AI understand your project structure.

## Project Structure

```
my-project/
├── project-plan.md    # Project roadmap (read by AI)
├── skills/            # Skill files
├── .hobo-code/        # Hobo Code config
├── src/               # Your source code
└── tests/             # Your tests
```

## Creating a Project

```bash
hobo init my-project "My project description"
cd my-project
```

This creates:
- `project-plan.md` with project template
- `skills/` directory with default skills
- `.hobo-code/` configuration directory

## project-plan.md

This file guides Hobo Code through your project:

```markdown
# Project: my-project

## Overview
My project description

## Phases

### Phase 1: Foundation
- [x] Set up project structure
- [ ] Implement core functionality

### Phase 2: Features
- [ ] Feature implementation
- [ ] Security review (apply security_audit skill)

### Phase 3: Testing
- [ ] Comprehensive test coverage (apply test_driven_development skill)

## Skills Installed
| Skill | Description |
|-------|-------------|
| security_audit | Security-first design |
| test_driven_development | TDD methodology |
```

## Adding Skills to Project

```bash
# Add a skill to your project
hobo skills add api_design

# Sync all skills from repository
hobo skills sync
```

## Project-Aware Features

- **Context Awareness** - AI understands your project structure
- **Phase Tracking** - Mark phases as complete in project-plan.md
- **Skill Suggestions** - Get skill recommendations for your project phase

---

*Next: [TUI Interface →](tui.md)*
