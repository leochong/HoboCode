"""Agent implementation for skill-aware message processing."""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from hobo_code.skills.registry import SkillRegistry, Skill, AnthropicSkill
from hobo_code.tools.file import FileTool


@dataclass
class Thought:
    """Represents a reasoning step in the agent's thought process."""

    thought: str
    action: str | None = None
    action_input: dict[str, Any] | None = None
    observation: str | None = None


@dataclass
class AgentMessage:
    """Represents a message in the agent conversation."""

    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    thought_history: list[Thought] = field(default_factory=list)


class SkillAwareAgent:
    """Agent that processes messages with skill awareness using ReAct pattern."""

    def __init__(
        self,
        project_dir: str | None = None,
        skills_dir: str | None = None,
    ):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.skills_dir = Path(skills_dir) if skills_dir else self.project_dir / "skills"
        self.registry = SkillRegistry(
            project_dir=str(self.project_dir) if self.project_dir.exists() else None,
            skills_dir=str(self.skills_dir) if self.skills_dir.exists() else None,
        )
        self.current_skill: Skill | None = None
        self.file_tool = FileTool()
        self.tool_mapping = self._build_tool_mapping()

    def _build_tool_mapping(self) -> dict[str, Any]:
        """Build mapping of tool names to tool instances."""
        return {
            "file_read": self.file_tool.read,
            "file_write": self.file_tool.write,
            "file_list": self.file_tool.list,
            "file_search": self.file_tool.search,
        }

    def load_skills(self) -> None:
        """Load available skills."""
        self.registry.load_project_skills()

    def set_skill(self, skill_name: str) -> bool:
        """Activate a specific skill."""
        skill = self.registry.get_skill(skill_name)
        if skill:
            self.current_skill = skill
            return True
        return False

    def clear_skill(self) -> None:
        """Clear the current skill context."""
        self.current_skill = None

    def get_system_prompt(self) -> str:
        """Get the appropriate system prompt based on current skill."""
        if self.current_skill:
            if isinstance(self.current_skill, AnthropicSkill):
                return self.current_skill.full_content
            return self.current_skill.system_prompt
        return "You are Hobo Code, a helpful AI coding assistant."

    def get_available_tools(self) -> list[str]:
        """Get list of available tool names."""
        if self.current_skill and hasattr(self.current_skill, "tools"):
            return self.current_skill.tools
        return ["file_read", "file_write", "file_list", "file_search"]

    def suggest_skills(self, task: str) -> list[tuple[Skill, float]]:
        """Suggest skills for a given task."""
        return self.registry.get_recommended_skills(task)

    async def process_message(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process a user message with skill awareness.

        Args:
            message: The user's message
            context: Optional context (e.g., current file, project info)

        Returns:
            Dict with response and thought history
        """
        thought_history: list[Thought] = []

        if self.current_skill:
            thought_history.append(Thought(
                thought=f"Using skill: {self.current_skill.name}",
                action="activate_skill",
                action_input={"skill": self.current_skill.name}
            ))

        context_files = context.get("files", []) if context else []
        if context_files:
            thought_history.append(Thought(
                thought=f"Context includes {len(context_files)} files",
                action="read_context",
                action_input={"files": context_files}
            ))

        system_prompt = self.get_system_prompt()
        thought_history.append(Thought(
            thought="Analyzing the user's request",
            action="analyze",
            action_input={"message": message}
        ))

        tools_to_use = self.get_available_tools()
        relevant_tools = self._identify_relevant_tools(message, tools_to_use)

        if relevant_tools:
            thought_history.append(Thought(
                thought=f"Will use tools: {', '.join(relevant_tools)}",
                action="select_tools",
                action_input={"tools": relevant_tools}
            ))

        response = await self._generate_response(message, system_prompt)

        thought_history.append(Thought(
            thought="Generating response",
            action="generate",
            action_input={}
        ))

        return {
            "response": response,
            "thoughts": thought_history,
            "skill_used": self.current_skill.name if self.current_skill else None,
        }

    def _identify_relevant_tools(
        self,
        message: str,
        available_tools: list[str],
    ) -> list[str]:
        """Identify which tools are relevant for a message."""
        message_lower = message.lower()
        relevant = []

        tool_keywords = {
            "file_read": ["read", "show", "view", "display", "open", "cat"],
            "file_write": ["write", "create", "make", "add", "new"],
            "file_list": ["list", "ls", "dir", "directory", "files"],
            "file_search": ["find", "search", "locate", "where"],
        }

        for tool in available_tools:
            keywords = tool_keywords.get(tool, [])
            if any(kw in message_lower for kw in keywords):
                relevant.append(tool)

        return relevant if relevant else available_tools[:2]

    async def _generate_response(
        self,
        message: str,
        system_prompt: str,
    ) -> str:
        """Generate a response (placeholder for LLM integration)."""
        return f"I understand you want me to: {message}\n\nWith the current skill context, I'm ready to help. This is a placeholder response - integrate with your LLM provider to generate actual responses."

    async def execute_tool(
        self,
        tool_name: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a tool and return the result."""
        tool_func = self.tool_mapping.get(tool_name)

        if not tool_func:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            if tool_name == "file_read":
                result = tool_func(params.get("path", ""))
            elif tool_name == "file_write":
                result = tool_func(
                    params.get("path", ""),
                    params.get("content", ""),
                )
            elif tool_name == "file_list":
                result = tool_func(params.get("path", "."))
            elif tool_name == "file_search":
                result = tool_func(
                    params.get("pattern", ""),
                    params.get("path", "."),
                )
            else:
                result = tool_func(**params)

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    async def run_react_loop(
        self,
        message: str,
        max_iterations: int = 5,
    ) -> dict[str, Any]:
        """Run the ReAct loop for complex tasks.

        Args:
            message: The user's task
            max_iterations: Maximum number of thought/action/observation cycles

        Returns:
            Dict with final response and full trace
        """
        trace: list[dict[str, Any]] = []
        thought_history: list[Thought] = []

        trace.append({
            "step": 0,
            "thought": "Starting ReAct loop",
            "system_prompt": self.get_system_prompt()[:100] + "...",
        })

        current_message = message

        for i in range(max_iterations):
            step = i + 1

            thought = Thought(thought=f"Step {step}: Analyzing request")
            thought_history.append(thought)

            trace.append({
                "step": step,
                "thought": thought.thought,
            })

            relevant_tools = self._identify_relevant_tools(
                current_message,
                self.get_available_tools()
            )

            if relevant_tools:
                thought.action = "execute_tool"
                thought.action_input = {"tools": relevant_tools}
                trace[-1]["action"] = relevant_tools

                tool_results = []
                for tool in relevant_tools[:2]:
                    result = await self.execute_tool(tool, {"path": "."})
                    tool_results.append({"tool": tool, "result": result})

                trace[-1]["observation"] = f"Executed {len(tool_results)} tools"
                thought.observation = trace[-1]["observation"]

                if tool_results:
                    current_message = f"Based on tool results: {json.dumps(tool_results)}\n\nOriginal request: {message}"
            else:
                trace[-1]["observation"] = "No tools needed"
                thought.observation = trace[-1]["observation"]
                break

        response = await self._generate_response(
            current_message,
            self.get_system_prompt()
        )

        return {
            "response": response,
            "trace": trace,
            "thoughts": thought_history,
            "skill_used": self.current_skill.name if self.current_skill else None,
            "iterations": len(trace),
        }

    def get_skill_stats(self) -> dict[str, Any]:
        """Get statistics about loaded skills."""
        return self.registry.get_skill_stats()


class ProjectAgent(SkillAwareAgent):
    """Agent specialized for project-specific tasks."""

    def __init__(
        self,
        project_dir: str | None = None,
        skills_dir: str | None = None,
    ):
        super().__init__(project_dir, skills_dir)
        self.project_plan = self._load_project_plan()

    def _load_project_plan(self) -> dict[str, Any] | None:
        """Load project-plan.md if it exists."""
        plan_path = self.project_dir / "project-plan.md"
        if plan_path.exists():
            return {
                "path": str(plan_path),
                "content": plan_path.read_text(encoding="utf-8"),
            }
        return None

    def get_project_context(self) -> dict[str, Any]:
        """Get project context for the agent."""
        context = {
            "project_dir": str(self.project_dir),
            "skills_loaded": len(self.registry.list_skills()),
            "current_skill": self.current_skill.name if self.current_skill else None,
        }

        if self.project_plan:
            context["project_plan"] = True

        return context

    def suggest_skills_for_project_phase(self, phase: str) -> list[dict[str, Any]]:
        """Suggest skills based on project phase."""
        phase_keywords = {
            "Phase 1": ["foundation", "setup", "structure", "core"],
            "Phase 2": ["features", "implementation", "api", "backend"],
            "Phase 3": ["testing", "polish", "performance", "security", "documentation"],
        }

        keywords = phase_keywords.get(phase, [])
        task = " ".join(keywords)

        recommendations = self.suggest_skills(task)

        return [
            {"name": s.name, "score": score, "description": s.description}
            for s, score in recommendations[:5]
        ]

