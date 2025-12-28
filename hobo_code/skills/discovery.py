"""Skill discovery for searching skills across multiple sources."""

import re
from pathlib import Path
from typing import Any

from .downloader import SkillDownloader, SkillDownloadError


class SkillNotFoundError(Exception):
    """Exception raised when skill cannot be found."""
    pass


class SkillDiscovery:
    """Discovers skills across multiple sources with fallback chain."""

    def __init__(self, token: str | None = None):
        self.downloader = SkillDownloader(token)

    def find_skill(
        self,
        skill_name: str,
        skills_dir: Path,
        primary_repo: str = "leochong/HoboCode",
    ) -> Path | None:
        """Find or download a skill.

        Searches in order:
        1. Local skills/ directory
        2. Primary GitHub repo (leochong/HoboCode)
        3. Anthropic-compatible skill repos

        Args:
            skill_name: Name of the skill to find
            skills_dir: Local skills directory
            primary_repo: Primary GitHub repository

        Returns:
            Path to skill file if found, None otherwise
        """
        local_path = skills_dir / skill_name / "SKILL.md"
        if local_path.exists():
            return local_path

        try:
            self.downloader.download_skill(skill_name, skills_dir, primary_repo)
            if local_path.exists():
                return local_path
        except SkillDownloadError:
            pass

        sources = self.downloader.search_all_sources(skill_name, primary_repo)

        for source in sources:
            source_type = source.get("source_type", "")
            if source_type == "anthropic":
                try:
                    repo = f"{source.get('owner', '')}/{source.get('repo', '')}"
                    self.downloader.download_skill(skill_name, skills_dir, repo)
                    if local_path.exists():
                        return local_path
                except SkillDownloadError:
                    continue

        return None

    def ensure_skill(
        self,
        skill_name: str,
        skills_dir: Path,
        primary_repo: str = "leochong/HoboCode",
    ) -> Path:
        """Ensure a skill exists, downloading if necessary.

        Args:
            skill_name: Name of the skill
            skills_dir: Local skills directory
            primary_repo: Primary GitHub repository

        Returns:
            Path to the skill file

        Raises:
            SkillNotFoundError: If skill cannot be found or downloaded
        """
        skill_path = self.find_skill(skill_name, skills_dir, primary_repo)
        if skill_path is None:
            raise SkillNotFoundError(
                f"Skill '{skill_name}' not found in any source"
            )
        return skill_path

    def search_all_sources(
        self,
        skill_name: str,
        primary_repo: str = "leochong/HoboCode",
    ) -> list[dict[str, str]]:
        """Search for a skill across all known sources.

        Args:
            skill_name: Name of the skill to search for
            primary_repo: Primary GitHub repository

        Returns:
            List of dicts with 'owner', 'repo', 'skill', 'source_type' keys
        """
        return self.downloader.search_all_sources(skill_name, primary_repo)

    def list_all_available_skills(
        self,
        primary_repo: str = "leochong/HoboCode",
    ) -> list[dict[str, str]]:
        """List all skills available across all sources.

        Args:
            primary_repo: Primary GitHub repository

        Returns:
            List of skill names with source information
        """
        skills = []

        primary_skills = self.downloader.list_remote_skills(primary_repo)
        for skill in primary_skills:
            skills.append({
                "name": skill,
                "source": primary_repo,
                "source_type": "primary",
            })

        for owner, repo in self.downloader.ANTHROPIC_REPOS:
            repo_name = f"{owner}/{repo}"
            repo_skills = self.downloader.list_remote_skills(repo_name)
            for skill in repo_skills:
                if skill not in primary_skills:
                    skills.append({
                        "name": skill,
                        "source": repo_name,
                        "source_type": "anthropic",
                    })

        return sorted(skills, key=lambda x: str(x.get("name", "")))

    def search_skills(
        self,
        query: str,
        primary_repo: str = "leochong/HoboCode",
    ) -> list[dict[str, str]]:
        """Search for skills matching a query.

        Uses case-insensitive substring matching on skill names.

        Args:
            query: Search query
            primary_repo: Primary GitHub repository

        Returns:
            List of matching skills with source information
        """
        query_lower = query.lower()
        all_skills = self.list_all_available_skills(primary_repo)

        matching = []
        for skill in all_skills:
            skill_name = skill.get("name", "")
            if isinstance(skill_name, str) and query_lower in skill_name.lower():
                matching.append(skill)

        return matching

    def get_skill_metadata(
        self, skill_path: Path
    ) -> dict[str, Any] | None:
        """Extract metadata from a skill file.

        Args:
            skill_path: Path to SKILL.md file

        Returns:
            Dict with 'name', 'description', 'tags', etc. or None
        """
        if not skill_path.exists():
            return None

        content = skill_path.read_text(encoding="utf-8")

        match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if match:
            try:
                import yaml
                return yaml.safe_load(match.group(1))
            except Exception:
                pass

        return None

    def suggest_skills_for_task(
        self,
        task_description: str,
        primary_repo: str = "leochong/HoboCode",
    ) -> list[dict[str, str]]:
        """Suggest skills that might be useful for a task.

        This is a simple keyword-based matching. For better results,
        this could integrate with an LLM.

        Args:
            task_description: Description of the task
            primary_repo: Primary GitHub repository

        Returns:
            List of suggested skills with relevance scores
        """
        keywords = self._extract_keywords(task_description)
        all_skills = self.list_all_available_skills(primary_repo)

        suggestions = []
        for skill in all_skills:
            skill_name = str(skill.get("name", ""))
            score = self._calculate_relevance(skill_name, keywords)
            if score > 0:
                new_skill: dict[str, Any] = {
                    "name": skill.get("name", ""),
                    "source": skill.get("source", ""),
                    "source_type": skill.get("source_type", ""),
                    "relevance_score": score,
                }
                suggestions.append(new_skill)

        suggestions.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return suggestions

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract potential keywords from text."""
        words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", text.lower())
        stop_words = {
            "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
            "be", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "shall", "can", "need",
            "i", "me", "my", "we", "our", "you", "your", "it", "its", "this",
            "that", "these", "those", "build", "create", "make", "develop",
            "write", "code", "implement", "add", "fix", "debug", "test",
        }
        return [w for w in words if w not in stop_words and len(w) > 2]

    def _calculate_relevance(
        self, skill_name: str, keywords: list[str]
    ) -> float:
        """Calculate relevance score for a skill given keywords."""
        score = 0.0
        skill_name_lower = skill_name.lower()

        for keyword in keywords:
            if keyword in skill_name_lower:
                score += 0.3

            if keyword in ["api", "rest", "http", "backend", "server"]:
                if "api" in skill_name_lower or "backend" in skill_name_lower:
                    score += 0.2

            if keyword in ["frontend", "ui", "web", "react", "vue"]:
                if "react" in skill_name_lower or "frontend" in skill_name_lower:
                    score += 0.2

            if keyword in ["database", "sql", "query", "data"]:
                if "database" in skill_name_lower or "data" in skill_name_lower:
                    score += 0.2

            if keyword in ["test", "testing", "tdd", "pytest"]:
                if "test" in skill_name_lower:
                    score += 0.2

            if keyword in ["security", "auth", "password", "encrypt"]:
                if "security" in skill_name_lower or "audit" in skill_name_lower:
                    score += 0.2

            if keyword in ["docker", "kubernetes", "deploy", "ci", "cd"]:
                if "devops" in skill_name_lower or "docker" in skill_name_lower:
                    score += 0.2

        return min(score, 1.0)


def find_or_download_skill(
    skill_name: str,
    project_path: Path,
    token: str | None = None,
) -> Path | None:
    """Convenience function to find or download a skill.

    Args:
        skill_name: Name of the skill
        project_path: Path to project directory
        token: Optional GitHub token

    Returns:
        Path to skill file if found, None otherwise
    """
    discovery = SkillDiscovery(token)
    skills_dir = project_path / "skills"
    return discovery.find_skill(skill_name, skills_dir)


def ensure_skill_exists(
    skill_name: str,
    project_path: Path,
    token: str | None = None,
) -> Path:
    """Ensure a skill exists, downloading if necessary.

    Args:
        skill_name: Name of the skill
        project_path: Path to project directory
        token: Optional GitHub token

    Returns:
        Path to the skill file

    Raises:
        SkillNotFoundError: If skill cannot be found
    """
    discovery = SkillDiscovery(token)
    skills_dir = project_path / "skills"
    return discovery.ensure_skill(skill_name, skills_dir)


def suggest_skills_for_project(
    task_description: str,
    project_path: Path | None = None,
    token: str | None = None,
) -> list[dict[str, str]]:
    """Suggest skills that might be useful for a project task.

    Args:
        task_description: Description of the task
        project_path: Optional project path to check existing skills
        token: Optional GitHub token

    Returns:
        List of suggested skills with relevance scores
    """
    discovery = SkillDiscovery(token)
    suggestions = discovery.suggest_skills_for_task(task_description)

    if project_path:
        skills_dir = project_path / "skills"
        if skills_dir.exists():
            existing = set()
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    existing.add(skill_dir.name)
            suggestions = [
                s for s in suggestions if s.get("name", "") not in existing
            ]

    return suggestions
