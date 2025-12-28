"""Skill registry for managing AI personas and expertise."""

import json
from pathlib import Path
from typing import Any


class Skill:
    """Represents a skill/persona definition."""

    def __init__(self, name: str, data: dict[str, Any]):
        self.name = name
        self.description = data.get("description", "")
        self.system_prompt = data.get("system_prompt", "")
        self.keywords = data.get("keywords", [])
        self.when_to_use = data.get("when_to_use", [])
        self.when_not_to_use = data.get("when_not_to_use", [])
        self.examples = data.get("examples", [])
        self.tools = data.get("tools", [])

    def matches_context(self, query: str) -> float:
        """Calculate how well this skill matches a query."""
        query_lower = query.lower()
        score = 0.0

        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                score += 0.3

        for pattern in self.when_to_use:
            if pattern.lower() in query_lower:
                score += 0.2

        return min(score, 1.0)

    def to_dict(self) -> dict[str, Any]:
        """Convert skill to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "keywords": self.keywords,
            "when_to_use": self.when_to_use,
            "when_not_to_use": self.when_not_to_use,
            "examples": self.examples,
            "tools": self.tools,
        }


class SkillRegistry:
    """Registry for managing skills and personas."""

    def __init__(self, skills_dir: str | None = None):
        if skills_dir is None:
            self.skills_dir = Path(__file__).parent.parent.parent / "skills"
        else:
            self.skills_dir = Path(skills_dir)
        self._skills: dict[str, Skill] = {}

    def load_skills(self) -> None:
        """Load all skills from the skills directory."""
        if not self.skills_dir.exists():
            return

        for json_file in self.skills_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                name = json_file.stem
                self._skills[name] = Skill(name, data)
            except Exception:
                continue

    def list_skills(self) -> list[str]:
        """List all available skills."""
        if not self._skills:
            self.load_skills()
        return sorted(self._skills.keys())

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        if not self._skills:
            self.load_skills()
        return self._skills.get(name)

    def get_all_skills(self) -> list[Skill]:
        """Get all loaded skills."""
        if not self._skills:
            self.load_skills()
        return list(self._skills.values())

    def get_recommended_skills(self, task: str) -> list[tuple[Skill, float]]:
        """Get skills recommended for a task."""
        if not self._skills:
            self.load_skills()

        scored = []
        for skill in self._skills.values():
            score = skill.matches_context(task)
            if score > 0:
                scored.append((skill, score))

        return sorted(scored, key=lambda x: x[1], reverse=True)

    def activate_skill(self, name: str, context: str) -> Skill | None:
        """Activate a skill with context."""
        skill = self.get_skill(name)
        if skill and skill.matches_context(context) > 0:
            return skill
        return None

    def get_system_prompt(self, skill_name: str | None = None, task: str | None = None) -> str:
        """Get the system prompt for a skill or task."""
        if skill_name:
            skill = self.get_skill(skill_name)
            if skill:
                return skill.system_prompt

        if task:
            recommendations = self.get_recommended_skills(task)
            if recommendations:
                best_skill, _ = recommendations[0]
                return best_skill.system_prompt

        return "You are Hobo Code, a helpful AI coding assistant."

    def get_skill_stats(self) -> dict[str, Any]:
        """Get statistics about loaded skills."""
        if not self._skills:
            self.load_skills()

        categories = {}
        for skill in self._skills.values():
            category = skill.name.split("/")[0] if "/" in skill.name else "general"
            if category not in categories:
                categories[category] = []
            categories[category].append(skill.name)

        return {
            "total_skills": len(self._skills),
            "categories": categories,
        }
