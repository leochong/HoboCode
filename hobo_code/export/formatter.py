"""JSONL formatter for SFT training data with Chain of Thought traces."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ToolCall:
    """Record of a tool execution during reasoning."""

    name: str
    params: dict[str, Any]
    result: str | None = None
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: str | None = None


@dataclass
class Message:
    """A message in the conversation with reasoning trace."""

    role: str
    content: str
    reasoning: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class TrainingExample:
    """A single training example for SFT."""

    system: str
    messages: list[dict[str, Any]]
    model: str | None = None
    tokens: dict[str, int] = field(default_factory=dict)
    task_type: str = "general"
    success: bool = True
    skill: str | None = None
    session_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_time_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "system": self.system,
            "messages": self.messages,
            "model": self.model,
            "tokens": self.tokens,
            "task": self.task_type,
            "success": self.success,
            "skill": self.skill,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "execution_time_ms": self.execution_time_ms,
        }

    def to_jsonl(self) -> str:
        """Convert to JSONL line."""
        return json.dumps(self.to_dict())


class JSONLFormatter:
    """Formatter for creating SFT-ready JSONL training data."""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def format_session(
        self,
        session: Any,
        system_prompt: str,
        skill_name: str | None = None,
    ) -> list[str]:
        """Format a session as JSONL lines.

        Args:
            session: Session object with messages
            system_prompt: System prompt to use
            skill_name: Name of active skill

        Returns:
            List of JSONL strings
        """
        lines = []
        current_reasoning = ""
        current_tool_calls: list[ToolCall] = []

        for msg in session.messages:
            if msg.role == "assistant" and current_reasoning:
                message_data = {
                    "role": "user",
                    "content": self._get_previous_user_message(session.messages, msg),
                }
                assistant_data = {
                    "role": "assistant",
                    "content": msg.content,
                    "reasoning": current_reasoning,
                    "tool_calls": [
                        {"name": tc.name, "params": tc.params}
                        for tc in current_tool_calls
                    ],
                }

                example = TrainingExample(
                    system=system_prompt,
                    messages=[message_data, assistant_data],
                    model=session.model,
                    tokens={"input": self._estimate_tokens(message_data["content"]), "output": self._estimate_tokens(msg.content)},
                    task_type=self._infer_task_type(msg.content),
                    success=True,
                    skill=skill_name,
                    session_id=session.id,
                    execution_time_ms=self._estimate_execution_time(session),
                )
                lines.append(example.to_jsonl())

                current_reasoning = ""
                current_tool_calls = []
            elif msg.role == "assistant":
                message_data = {
                    "role": "user",
                    "content": self._get_previous_user_message(session.messages, msg),
                }
                assistant_data = {
                    "role": "assistant",
                    "content": msg.content,
                }

                example = TrainingExample(
                    system=system_prompt,
                    messages=[message_data, assistant_data],
                    model=session.model,
                    tokens={"input": self._estimate_tokens(message_data["content"]), "output": self._estimate_tokens(msg.content)},
                    task_type=self._infer_task_type(msg.content),
                    success=True,
                    skill=skill_name,
                    session_id=session.id,
                )
                lines.append(example.to_jsonl())

        return lines

    def _get_previous_user_message(self, messages: list, current_msg: Any) -> str:
        """Get the user message that preceded this assistant message."""
        for i, msg in enumerate(messages):
            if msg is current_msg and i > 0:
                return messages[i - 1].content
        return ""

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        return len(text) // 4

    def _infer_task_type(self, content: str) -> str:
        """Infer the type of task from the content."""
        content_lower = content.lower()

        if "fix" in content_lower or "bug" in content_lower or "error" in content_lower:
            return "bug_fix"
        if "refactor" in content_lower or "restructur" in content_lower:
            return "refactor"
        if "test" in content_lower or "spec" in content_lower:
            return "testing"
        if "document" in content_lower or "docstring" in content_lower:
            return "documentation"
        if "create" in content_lower or "implement" in content_lower or "add" in content_lower:
            return "feature"
        if "explain" in content_lower or "what is" in content_lower or "how to" in content_lower:
            return "explanation"
        if "review" in content_lower or "check" in content_lower:
            return "code_review"
        return "general"

    def _estimate_execution_time(self, session: Any) -> int:
        """Estimate execution time in milliseconds."""
        return len(session.messages) * 500

    def format_conversation(
        self,
        messages: list[dict[str, Any]],
        system_prompt: str,
        metadata: dict[str, Any] | None = None,
    ) -> list[str]:
        """Format a raw conversation as JSONL lines.

        Args:
            messages: List of message dictionaries
            system_prompt: System prompt
            metadata: Optional metadata

        Returns:
            List of JSONL strings
        """
        lines = []
        pairs = []

        for i in range(len(messages) - 1):
            if messages[i].get("role") == "user" and messages[i + 1].get("role") == "assistant":
                pairs.append((messages[i], messages[i + 1]))

        for user_msg, assistant_msg in pairs:
            example = TrainingExample(
                system=system_prompt,
                messages=[user_msg, assistant_msg],
                model=metadata.get("model"),
                tokens=metadata.get("tokens", {}),
                task_type=metadata.get("task_type", "general"),
                success=metadata.get("success", True),
                skill=metadata.get("skill"),
                session_id=metadata.get("session_id"),
            )
            lines.append(example.to_jsonl())

        return lines

    def export_to_file(
        self,
        lines: list[str],
        output_path: str,
        append: bool = False,
    ) -> int:
        """Export JSONL lines to a file.

        Args:
            lines: List of JSONL strings
            output_path: Path to output file
            append: If True, append to existing file

        Returns:
            Number of lines written
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if append else "w"
        with open(path, mode, encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

        return len(lines)

    def create_sample_export(self, output_path: str) -> int:
        """Create a sample JSONL export file.

        Args:
            output_path: Path for the sample file

        Returns:
            Number of lines written
        """
        sample_lines = [
            json.dumps({
                "system": "You are an expert Python coding assistant specialized in bug fixes and code optimization.",
                "messages": [
                    {"role": "user", "content": "Fix the bug in user authentication where login fails with valid credentials"},
                    {"role": "assistant", "content": "Let me analyze the authentication flow to identify the issue.", "reasoning": "First, I'll check the login module to understand the authentication flow and identify where the validation is failing.", "tool_calls": [{"name": "read", "params": {"path": "auth.py"}}]},
                ],
                "model": "gpt-4",
                "tokens": {"input": 450, "output": 380},
                "task": "bug_fix",
                "success": True,
                "skill": "python_expert",
                "session_id": "sess-123-abc",
                "timestamp": "2024-12-28T10:30:00Z",
                "execution_time_ms": 2500
            }),
            json.dumps({
                "system": "You are a full-stack developer skilled in React, Node.js, and database design.",
                "messages": [
                    {"role": "user", "content": "Create a REST API for a todo list application with CRUD operations"},
                    {"role": "assistant", "content": "I'll create a complete REST API with Express.js and MongoDB.", "reasoning": "The user needs a todo API. I'll create models, routes, and controllers for full CRUD functionality."},
                ],
                "model": "gpt-4",
                "tokens": {"input": 320, "output": 890},
                "task": "feature",
                "success": True,
                "skill": "fullstack",
                "session_id": "sess-456-def",
                "timestamp": "2024-12-28T11:00:00Z",
                "execution_time_ms": 4200
            }),
            json.dumps({
                "system": "You are a code review expert focused on security and performance best practices.",
                "messages": [
                    {"role": "user", "content": "Review this code for security vulnerabilities and suggest improvements"},
                    {"role": "assistant", "content": "I've reviewed the code and found several security concerns.", "reasoning": "Looking for common vulnerabilities: SQL injection, XSS, hardcoded secrets, and improper error handling."},
                ],
                "model": "gpt-4",
                "tokens": {"input": 520, "output": 650},
                "task": "code_review",
                "success": True,
                "skill": "security_audit",
                "session_id": "sess-789-ghi",
                "timestamp": "2024-12-28T12:00:00Z",
                "execution_time_ms": 3100
            }),
        ]

        return self.export_to_file(sample_lines, output_path)

    def get_stats(self, lines: list[str]) -> dict[str, Any]:
        """Get statistics about the exported data.

        Args:
            lines: List of JSONL strings

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_examples": len(lines),
            "task_types": {},
            "success_rate": 0.0,
            "avg_tokens_input": 0,
            "avg_tokens_output": 0,
            "skills_used": set(),
        }

        total_input = 0
        total_output = 0
        success_count = 0

        for line in lines:
            try:
                data = json.loads(line)
                task = data.get("task", "unknown")
                stats["task_types"][task] = stats["task_types"].get(task, 0) + 1

                if data.get("success"):
                    success_count += 1

                tokens = data.get("tokens", {})
                total_input += tokens.get("input", 0)
                total_output += tokens.get("output", 0)

                skill = data.get("skill")
                if skill:
                    stats["skills_used"].add(skill)
            except Exception:
                continue

        if lines:
            stats["success_rate"] = success_count / len(lines)
            stats["avg_tokens_input"] = total_input // len(lines)
            stats["avg_tokens_output"] = total_output // len(lines)
            stats["skills_used"] = list(stats["skills_used"])

        return stats
