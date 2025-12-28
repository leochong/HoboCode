"""Skill registry for managing AI personas and expertise."""

import json
import re
from pathlib import Path
from typing import Any

import yaml


class SkillMetadata:
    """Represents skill metadata from YAML frontmatter."""

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        author: str = "Hobo Code",
        tags: list[str] | None = None,
    ):
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.tags = tags or []


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
        self._full_content: str | None = None
        self._metadata: SkillMetadata | None = None
        self._linked_files: dict[str, str] = {}
        self._skill_dir: Path | None = None

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


class AnthropicSkill(Skill):
    """Represents a skill in Anthropic V1.0 format (Markdown + YAML)."""

    def __init__(self, name: str, skill_path: Path):
        self._skill_path = skill_path
        self._skill_dir = skill_path.parent
        self._is_loaded = False
        self._linked_files = {}

        content = skill_path.read_text(encoding="utf-8")
        frontmatter = self._parse_frontmatter(content)

        if frontmatter:
            metadata = SkillMetadata(
                name=frontmatter.get("name", name),
                description=frontmatter.get("description", ""),
                version=frontmatter.get("version", "1.0.0"),
                author=frontmatter.get("author", "Hobo Code"),
                tags=frontmatter.get("tags", []),
            )
            super().__init__(name, {
                "description": metadata.description,
                "keywords": metadata.tags,
            })
            self._metadata = metadata
        else:
            super().__init__(name, {"description": ""})
            self._metadata = None

    def _parse_frontmatter(self, content: str) -> dict[str, Any] | None:
        """Parse YAML frontmatter from skill content."""
        match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except Exception:
                return None
        return None

    def _load_full_content(self) -> None:
        """Load full skill content and linked files."""
        if self._is_loaded:
            return

        content = self._skill_path.read_text(encoding="utf-8")
        match = re.match(r"^---\n.*?\n---\n(.*)$", content, re.DOTALL)
        self._full_content = match.group(1) if match else content

        link_pattern = r"\[link:\s*([^\]]+)\]"
        for link_match in re.finditer(link_pattern, content):
            link_name = link_match.group(1).strip()
            if self._skill_dir:
                link_path = self._skill_dir / link_name
                if link_path.exists():
                    self._linked_files[link_name] = link_path.read_text(encoding="utf-8")

        self._is_loaded = True

    @property
    def full_content(self) -> str:
        """Get full skill content including linked files."""
        self._load_full_content()

        linked_content = ""
        for link_name, link_text in self._linked_files.items():
            linked_content += f"\n\n## Linked: {link_name}\n\n{link_text}"

        return (self._full_content or "") + linked_content

    @property
    def metadata(self) -> SkillMetadata | None:
        """Get skill metadata."""
        return self._metadata

    def get_linked_file(self, filename: str) -> str | None:
        """Get content of a linked file."""
        self._load_full_content()
        return self._linked_files.get(filename)

    def get_linked_files_list(self) -> list[str]:
        """Get list of linked file names."""
        self._load_full_content()
        return list(self._linked_files.keys())

    def get_scripts(self) -> list[Path]:
        """Get executable scripts in the skill's scripts directory."""
        if not self._skill_dir:
            return []
        scripts_dir = self._skill_dir / "scripts"
        if not scripts_dir.exists():
            return []

        scripts = []
        for script_path in scripts_dir.iterdir():
            if script_path.is_file() and script_path.suffix == ".py":
                scripts.append(script_path)
        return scripts


class SkillRegistry:
    """Registry for managing skills and personas."""

    def __init__(self, skills_dir: str | None = None, project_dir: str | None = None):
        self.repo_skills_dir = Path(__file__).parent.parent.parent / "skills"

        if project_dir:
            self.project_dir = Path(project_dir)
            self.skills_dir = self.project_dir / "skills"
        else:
            self.project_dir = None
            self.skills_dir = Path(skills_dir) if skills_dir else self.repo_skills_dir

        self._skills: dict[str, Skill] = {}
        self._anthropic_skills: dict[str, AnthropicSkill] = {}
        self._loaded = False

    def load_skills(self) -> None:
        """Load all skills from the skills directory."""
        if self._loaded:
            return

        if not self.skills_dir.exists():
            return

        for json_file in self.skills_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                name = json_file.stem
                self._skills[name] = Skill(name, data)
            except Exception:
                continue

        for skill_md in self.skills_dir.rglob("*/SKILL.md"):
            try:
                rel_path = skill_md.parent.relative_to(self.skills_dir)
                skill_name = str(rel_path).replace("\\", "/")
                self._anthropic_skills[skill_name] = AnthropicSkill(skill_name, skill_md)
            except Exception:
                continue

        self._loaded = True

    def load_project_skills(self) -> None:
        """Load skills from project directory, falling back to repo skills."""
        if self.project_dir and self.skills_dir.exists():
            self.load_skills()
        elif self.repo_skills_dir.exists():
            self.skills_dir = self.repo_skills_dir
            self.load_skills()

    def list_skills(self) -> list[str]:
        """List all available skills."""
        if not self._loaded:
            self.load_project_skills()

        json_skills = set(self._skills.keys())
        anthropic_skills = set(self._anthropic_skills.keys())

        json_only = json_skills - anthropic_skills
        combined = list(anthropic_skills) + list(json_only)
        return sorted(combined)

    def get_skill(self, name: str) -> Skill | None:
        """Get a skill by name."""
        if not self._loaded:
            self.load_project_skills()

        if name in self._anthropic_skills:
            return self._anthropic_skills[name]
        return self._skills.get(name)

    def get_all_skills(self) -> list[Skill]:
        """Get all loaded skills."""
        if not self._loaded:
            self.load_project_skills()

        all_skills = list(self._anthropic_skills.values()) + list(self._skills.values())
        return all_skills

    def get_recommended_skills(self, task: str) -> list[tuple[Skill, float]]:
        """Get skills recommended for a task."""
        if not self._loaded:
            self.load_project_skills()

        scored = []
        for skill in self.get_all_skills():
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
                if isinstance(skill, AnthropicSkill):
                    return skill.full_content
                return skill.system_prompt

        if task:
            recommendations = self.get_recommended_skills(task)
            if recommendations:
                best_skill, _ = recommendations[0]
                if isinstance(best_skill, AnthropicSkill):
                    return best_skill.full_content
                return best_skill.system_prompt

        return "You are Hobo Code, a helpful AI coding assistant."

    def get_skill_stats(self) -> dict[str, Any]:
        """Get statistics about loaded skills."""
        if not self._loaded:
            self.load_project_skills()

        categories = {}
        for skill in self.get_all_skills():
            category = skill.name.split("/")[0] if "/" in skill.name else "general"
            if category not in categories:
                categories[category] = []
            categories[category].append(skill.name)

        return {
            "total_skills": len(self._skills) + len(self._anthropic_skills),
            "anthropic_format": len(self._anthropic_skills),
            "json_format": len(self._skills),
            "categories": categories,
        }

    def is_anthropic_format(self, skill_name: str) -> bool:
        """Check if a skill is in Anthropic format."""
        if not self._loaded:
            self.load_project_skills()
        return skill_name in self._anthropic_skills

    def get_skill_path(self, skill_name: str) -> Path | None:
        """Get the file path for a skill."""
        if not self._loaded:
            self.load_project_skills()

        if skill_name in self._anthropic_skills:
            return self._anthropic_skills[skill_name]._skill_path
        return None

    def add_skill(self, skill_path: Path) -> bool:
        """Add a skill from a file path.

        Args:
            skill_path: Path to the SKILL.md file

        Returns:
            True if skill was added successfully
        """
        try:
            if skill_path.is_file():
                skill_name = skill_path.parent.name
                anthropic_skill = AnthropicSkill(skill_name, skill_path)
                self._anthropic_skills[skill_name] = anthropic_skill
                return True
        except Exception:
            pass
        return False
