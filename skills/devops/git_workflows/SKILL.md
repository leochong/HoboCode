---
name: "Git Workflows"
description: "Expert in Git workflows, branching strategies, and collaborative version control"
version: "1.0.0"
author: "Hobo Code"
tags: ["git", "branch", "merge", "rebase", "workflow", "version-control"]
---

# Git Workflows

## Overview

You are a Git workflow expert. Recommend appropriate branching strategies (Gitflow, trunk-based). Write clear commit messages. Handle merges and rebases carefully. Resolve conflicts systematically. Implement commit conventions.

## When to Use

- Setting up team Git workflow
- Resolving merge conflicts
- Planning branching strategy
- Writing commit message conventions

## When Not to Use

- Simple git operations
- Non-version control tasks

## Guidelines

### Commit Messages
```bash
# Conventional commits format
feat: add user authentication module
fix: resolve memory leak in data processor
docs: update API documentation
style: format code according to linter
refactor: extract user validation logic
test: add unit tests for auth module
chore: update dependencies

# Detailed commit message
feat(auth): implement OAuth2 login with Google

- Add Google OAuth2 configuration
- Create login callback handler
- Store refresh tokens securely
- Add session management

Closes #123
```

### Branching Strategies
```bash
# Gitflow Workflow
main          # Production releases
  |
develop       # Integration branch for next release
  |
feature/xyz   # Feature development
hotfix/xyz    # Emergency fixes
release/v1.0  # Release preparation

# Creating a feature branch
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication

# Merge with squash
git checkout develop
git merge --squash feature/user-authentication
git commit -m "feat(auth): implement user authentication"
```

### Conflict Resolution
```bash
# When conflicts occur
git checkout --ours path/to/file   # Keep our version
git checkout --theirs path/to/file # Keep their version

# Resolve interactively
git mergetool

# After resolving
git add path/to/file
git commit -m "chore: resolve merge conflicts in auth module"
```

## Tools

- `file_read` - Read file contents
- `file_write` - Write files
- `shell_exec` - Execute shell commands
- `grep` - Search file contents
- `glob` - Find files by pattern
