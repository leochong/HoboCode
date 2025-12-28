# Skills System

Skills are specialized AI personas that give Hobo Code specific expertise for different types of tasks.

## What Are Skills?

Each skill contains:
- **System prompt** - Persona instructions for the AI
- **Keywords** - For automatic detection
- **When to use** - Guidance on skill applicability
- **Tools** - Special capabilities for this skill

## Built-in Skills

### Default Skills
These are automatically installed with every project:

| Skill | Description |
|-------|-------------|
| `security_audit` | Security-first design and vulnerability checking |
| `test_driven_development` | TDD methodology and testing best practices |

### Language Skills

| Skill | Description |
|-------|-------------|
| `language/python_expert` | Python development best practices |
| `language/javascript_typescript` | JavaScript/TypeScript development |
| `language/go_backend` | Go backend development |
| `language/rust_systems` | Rust systems programming |
| `language/java_jvm` | Java/JVM development |
| `language/c_cpp` | C/C++ development |

### Framework Skills

| Skill | Description |
|-------|-------------|
| `framework/react_nextjs` | React/Next.js development |
| `framework/flask` | Flask web development |
| `framework/spring_boot` | Spring Boot development |
| `framework/vuejs` | Vue.js development |
| `framework/node_express` | Node.js Express development |

### Task Skills

| Skill | Description |
|-------|-------------|
| `task/api_design` | REST API architecture |
| `task/bug_debugging` | Debugging and issue fixing |
| `task/code_refactoring` | Code improvement and cleanup |
| `task/code_review` | Code review and feedback |
| `task/database_schema` | Database design |
| `task/test_generation` | Automated test generation |

### DevOps Skills

| Skill | Description |
|-------|-------------|
| `devops/docker_kubernetes` | Container orchestration |
| `devops/ci_cd` | CI/CD pipelines |
| `devops/git_workflows` | Git best practices |
| `devops/cloud_infra` | Cloud infrastructure |

## Using Skills

### Manual Activation

```bash
hobo chat
```

In chat:
```
/skill python_expert
```

### Auto-Switching

Hobo Code automatically detects which skill you need:

```
User: "Write unit tests for my authentication module"
→ System detects: test_driven_development
→ Auto-switches: [Auto] Switched to task/test_driven_development (85%)
```

### List Available Skills

```bash
hobo skills list
```

### Get Recommendations

```bash
hobo skills recommend "write a REST API"
```

### Add More Skills

```bash
hobo skills add api_design
hobo skills add security_audit
hobo skills add docker_kubernetes
```

### Detect Skill for Message

```bash
hobo skills detect "debug this authentication issue"
```

Output:
```
Detecting skills for: "debug this authentication issue"
Keyword Detection:
  - bug_debugging: 72%
  - security_audit: 45%
```

---

*Next: [Auto-Switching →](auto-switch.md)*
