# API Reference

Technical documentation for Hobo Code's Python API.

## Core Modules

### hobo_code.skills

#### SkillRegistry

```python
from hobo_code.skills.registry import SkillRegistry

registry = SkillRegistry(project_dir="/path/to/project")
registry.load_skills()

skills = registry.list_skills()  # List all skills
skill = registry.get_skill("api_design")  # Get specific skill

# Get recommendations
recommendations = registry.get_recommended_skills("write a REST API")

# Get system prompt for skill
prompt = registry.get_system_prompt("python_expert")
```

#### SkillDetectionEngine

```python
from hobo_code.skills.detection import SkillDetectionEngine

engine = SkillDetectionEngine(project_dir="/path/to/project")
skill, confidence = engine.detect_skill(
    "Write unit tests for authentication",
    threshold=0.7
)

# Get ranked recommendations
recommendations = engine.detect_skills_ranked("debug this issue", top_n=5)
```

#### SkillClassifier

```python
from hobo_code.skills.classifier import SkillClassifier

classifier = SkillClassifier(project_dir="/path/to/project")
result = classifier.classify("Create a REST API", use_llm_fallback=True)

# result = {
#     "method": "llm",
#     "skill": "api_design",
#     "confidence": 0.85,
#     "intent": "REST API development",
#     "reasoning": "User wants to create an API"
# }
```

#### AutoSwitchManager

```python
from hobo_code.skills.auto_switch import AutoSwitchManager

manager = AutoSwitchManager(project_dir="/path/to/project")
skill, confidence, did_switch = await manager.process_message(
    "Write tests for my code",
    current_skill=None
)

# Configuration
manager.config.enabled = True
manager.config.min_keyword_confidence = 0.7
manager.config.min_llm_confidence = 0.6
manager.config.debounce_seconds = 3.0
```

### hobo_code.client

#### HoboApp

```python
from hobo_code.client.app import HoboApp

# Start with specific session
app = HoboApp(session_id="session-123")
app.run()

# Events
# - on_chat_input_submitted
# - on_skill_command
# - on_skill_switch
```

#### ChatInput

```python
from hobo_code.client.components import ChatInput

chat_input = ChatInput(placeholder="Type a message...")

# Callbacks
chat_input.on_skill_command(callback)
chat_input.on_regular_message(callback)
```

### hobo_code.server

#### ACPServer

```python
from hobo_code.server.acp import ACPServer

server = ACPServer(host="127.0.0.1", port=8765)
await server.start()
await server.stop()
```

#### SkillAwareAgent

```python
from hobo_code.server.agent import SkillAwareAgent

agent = SkillAwareAgent(project_dir="/path/to/project")
agent.set_skill("python_expert")

result = await agent.process_message(
    "Help me refactor this code",
    context={"files": ["src/main.py"]}
)
# result = {
#     "response": "...",
#     "thoughts": [...],
#     "skill_used": "python_expert"
# }
```

### hobo_code.auth

#### UserPreferences

```python
from hobo_code.auth.preferences import UserPreferences

prefs = UserPreferences()
prefs.auto_switch_enabled = True
prefs.min_confidence = 0.7
prefs.locked_skill = "python_expert"
prefs.save()
```

---

*Back to [Documentation Index](../index.md)*
