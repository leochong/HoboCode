# Hobo Code Skills Index

This directory contains Agent Skills following the [Agent Skills open standard (v1.0)](https://github.com/anthropics/skills).

## Skill Categories

### Language Skills
Specialized skills for specific programming languages and runtimes.

- **[python_expert.md](language/python_expert.md)** - Python development with async, decorators, type hints
- **[javascript_typescript.md](language/javascript_typescript.md)** - JavaScript/TypeScript, ES6+, Node.js, React
- **[rust_systems.md](language/rust_systems.md)** - Rust systems programming, ownership, performance
- **[go_backend.md](language/go_backend.md)** - Go backend, concurrency, microservices
- **[c_cpp.md](language/c_cpp.md)** - C/C++ low-level, memory management, optimization
- **[java_jvm.md](language/java_jvm.md)** - Java/JVM, Spring, enterprise patterns
- **[dotnet.md](language/dotnet.md)** - C#/.NET, ASP.NET Core, Azure
- **[php_web.md](language/php_web.md)** - PHP web, Laravel, Symfony, security
- **[shell_scripting.md](language/shell_scripting.md)** - Shell scripting, automation, DevOps

### Framework Skills
Skills for specific frameworks and libraries.

- **[python_web.md](framework/python_web.md)** - FastAPI, Django, Flask web frameworks
- **[react_nextjs.md](framework/react_nextjs.md)** - React, Next.js, TypeScript frontend
- **[node_express.md](framework/node_express.md)** - Node.js, Express, TypeScript backend
- **[spring_boot.md](framework/spring_boot.md)** - Spring Boot, Java enterprise
- **[vuejs.md](framework/vuejs.md)** - Vue.js 3, Composition API, Pinia

### Task Skills
Skills for specific development tasks.

- **[code_refactoring.md](task/code_refactoring.md)** - Refactoring, technical debt reduction
- **[systematic_debugging.md](task/systematic_debugging.md)** - Debugging methodology, root cause analysis
- **[test_generation.md](task/test_generation.md)** - Unit, integration, e2e testing
- **[api_design.md](task/api_design.md)** - REST, GraphQL, gRPC API design
- **[code_review.md](task/code_review.md)** - Code review, quality, security
- **[database_schema.md](task/database_schema.md)** - Database design, schema, optimization

### DevOps Skills
Skills for DevOps and infrastructure.

- **[git_worktrees.md](devops/git_worktrees.md)** - Git worktrees, parallel development
- **[ci_cd.md](devops/ci_cd.md)** - CI/CD pipelines, GitHub Actions, automation
- **[docker_kubernetes.md](devops/docker_kubernetes.md)** - Docker, Kubernetes, containers

### Specialized Skills
Specialized skills for security, integrations, and meta-tasks.

- **[security_audit.md](specialized/security_audit.md)** - Security analysis, vulnerability assessment
- **[skill_creator.md](specialized/skill_creator.md)** - Creating new Agent Skills (meta-skill)
- **[mcp_builder.md](specialized/mcp_builder.md)** - Model Context Protocol server creation

### General Skills
General-purpose skills applicable across domains.

- **[fullstack.md](general/fullstack.md)** - Full-stack development, end-to-end
- **[architecture.md](general/architecture.md)** - Software architecture, design patterns
- **[problem_solving.md](general/problem_solving.md)** - Analytical problem-solving

## Skill Format

Skills follow the Agent Skills open standard (v1.0):

```yaml
---
name: Skill Name
description: Brief description of the skill
---

# Skill Name

## When to use
- Pattern 1
- Pattern 2

## When NOT to use
- Pattern 1
- Pattern 2

## Examples
- Example 1
- Example 2

## Guidelines
### Section 1
- Guideline 1
- Guideline 2

## Tools Available
- tool1, tool2

## Model Configuration
- Temperature: 0.2
- Max Tokens: 4096

## Keywords
keyword1, keyword2, keyword3
```

## Using Skills

Skills are automatically activated based on:
1. **When to use patterns** - Matches user queries
2. **Keywords** - Used for skill discovery
3. **Examples** - Training data for activation

Each skill includes:
- Clear activation patterns
- Concrete usage examples
- Detailed behavioral guidelines
- Tool and model configuration
- Keywords for discovery

## Adding New Skills

To add a new skill:
1. Create a new `.md` file in the appropriate category
2. Follow the Agent Skills standard format
3. Include all required sections
4. Test activation with example queries
5. Add to this index

## References

- [Agent Skills specification](https://github.com/anthropics/skills)
- [Awesome Agent Skills](https://github.com/skillmatic-ai/awesome-agent-skills)
- [Claude Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
