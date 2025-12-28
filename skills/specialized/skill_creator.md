---
name: Skill Creator
description: Meta-skill for creating new skills following Agent Skills open standard (v1.0). Expert in SKILL.md format, progressive disclosure, and skill architecture patterns.
---

# Skill Creator

Meta-skill for creating new skills following Agent Skills open standard (v1.0). Expert in SKILL.md format, progressive disclosure, and skill architecture patterns.

## When to use

- Creating new agent skills
- Converting workflows into skills
- Documenting skill best practices
- Extending existing skills
- Organizing skills into categories

## When NOT to use

- General programming tasks
- Non-skill related development
- Tasks better suited for specific domain skills

## Examples

- "Create a skill for database migrations"
- "Convert this workflow into a skill"
- "Add activation patterns to this skill"
- "Document best practices for a new skill"

## Guidelines

### Agent Skills Standard v1.0

#### Frontmatter (YAML)
```yaml
---
name: Skill Name
description: Clear, concise description of what this skill does
---
```

#### Required Sections
- `# Skill Name` - Title matching frontmatter
- `## When to use` - Concrete patterns for activation
- `## When NOT to use` - Clear exclusion patterns
- `## Examples` - Real usage examples
- `## Guidelines` - Detailed behavioral instructions

#### Optional Sections
- `## Tools Available` - List of tools the skill can use
- `## Model Configuration` - Temperature, max tokens, etc.
- `## Keywords` - Discovery keywords

### Progressive Disclosure
- **Metadata (always loaded)**: Name, description, keywords
- **Instructions (when activated)**: Full guidelines and examples
- **Resources (on demand)**: Deep technical details

### Naming Conventions
- Use kebab-case for skill file names: `python-expert.md`
- Use PascalCase for skill name: "Python Expert"
- Use descriptive, action-oriented names
- Keep names under 50 characters

### Categories
- `language/` - Programming language expertise
- `framework/` - Framework-specific skills
- `task/` - Task-oriented capabilities
- `devops/` - DevOps and infrastructure
- `specialized/` - Security, integrations
- `general/` - General-purpose skills

### Activation Patterns
- Include specific `when_to_use` patterns
- Provide concrete examples of usage
- Define clear `when_not_to_use` to avoid false positives
- Use keywords for skill discovery

### Guidelines Structure
- Group related guidelines under subheadings
- Use numbered lists for sequential steps
- Use bullet points for general guidelines
- Include code examples when helpful

### Best Practices
- Follow patterns from established skills
- Test activation with various phrasings
- Keep guidelines actionable and specific
- Update skills based on usage feedback
- Maintain consistency across skills

## Tools Available

- file_read, file_write, shell_exec, grep, glob, diff

## Model Configuration

- Temperature: 0.2
- Max Tokens: 4096

## Keywords

skill, creation, agent-skills, standard, meta, custom-skill, progressive-disclosure, activation
