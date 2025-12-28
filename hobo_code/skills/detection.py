"""Skill detection engine for automatic skill activation."""

import re
from pathlib import Path
from typing import Any

from hobo_code.skills.registry import SkillRegistry, Skill, AnthropicSkill


class SkillDetectionEngine:
    """Detects which skill matches a user request based on keyword matching."""

    DEFAULT_THRESHOLD = 0.7

    SKILL_CATEGORY_KEYWORDS = {
        "api": ["api", "rest", "http", "endpoint", "crud", "route", "request", "response"],
        "database": ["database", "sql", "query", "schema", "table", "migration", "orm"],
        "testing": ["test", "pytest", "unit", "integration", "tdd", "coverage", "assert"],
        "security": ["security", "auth", "password", "encrypt", "vulnerability", "audit"],
        "frontend": ["react", "vue", "html", "css", "frontend", "ui", "component"],
        "backend": ["backend", "server", "python", "node", "java", "go", "rust"],
        "docker": ["docker", "container", "kubernetes", "k8s", "deployment", "pod"],
        "git": ["git", "commit", "branch", "merge", "pr", "pull request"],
        "documentation": ["documentation", "readme", "doc", "comment", "docstring"],
        "performance": ["performance", "optimize", "speed", "cache", "profiling"],
        "debugging": ["debug", "bug", "error", "issue", "traceback", "stack"],
        "refactoring": ["refactor", "cleanup", "improve", "restructure", "technical debt"],
    }

    def __init__(self, project_dir: str | None = None):
        self.project_dir = Path(project_dir) if project_dir else None
        self.registry = SkillRegistry(
            project_dir=str(self.project_dir) if self.project_dir else None
        )
        self._keyword_cache: dict[str, set[str]] = {}

    def load_skills(self) -> None:
        """Load skills from registry."""
        self.registry.load_project_skills()
        self._build_keyword_cache()

    def _build_keyword_cache(self) -> None:
        """Build keyword cache for faster matching."""
        self._keyword_cache.clear()

        for skill in self.registry.get_all_skills():
            keywords = set()

            if skill.keywords:
                for kw in skill.keywords:
                    keywords.add(kw.lower())

            if skill.when_to_use:
                for pattern in skill.when_to_use:
                    words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", pattern.lower())
                    keywords.update(words)

            if hasattr(skill, "description"):
                words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", skill.description.lower())
                keywords.update([w for w in words if len(w) > 2])

            self._keyword_cache[skill.name] = keywords

    def detect_skill(
        self,
        user_message: str,
        threshold: float | None = None,
        exclude_skill: str | None = None,
    ) -> tuple[str | None, float]:
        """Detect which skill matches the user message.

        Args:
            user_message: The user's message to analyze
            threshold: Minimum confidence to return a match (default: 0.7)
            exclude_skill: Skill name to exclude from matching

        Returns:
            Tuple of (skill_name, confidence) or (None, 0.0) if no match
        """
        if threshold is None:
            threshold = self.DEFAULT_THRESHOLD

        if not self._keyword_cache:
            self.load_skills()

        message_lower = user_message.lower()
        words = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", message_lower))

        best_match: str | None = None
        best_score = 0.0

        for skill_name in self.registry.list_skills():
            if skill_name == exclude_skill:
                continue

            skill = self.registry.get_skill(skill_name)
            if not skill:
                continue

            score = self._calculate_confidence(words, message_lower, skill_name)

            if score > best_score:
                best_score = score
                best_match = skill_name

        if best_score >= threshold:
            return best_match, best_score

        return None, 0.0

    def _calculate_confidence(
        self,
        words: set[str],
        message_lower: str,
        skill_name: str,
    ) -> float:
        """Calculate confidence score for a skill match."""
        score = 0.0
        keywords = self._keyword_cache.get(skill_name, set())

        direct_matches = words & keywords
        score += len(direct_matches) * 0.15

        for kw in keywords:
            if len(kw) > 3 and kw in message_lower:
                score += 0.1

        category_boost = self._get_category_boost(message_lower)
        score += category_boost * 0.2

        skill_parts = skill_name.lower().split("/")
        for part in skill_parts:
            if part in words:
                score += 0.25

        return min(score, 1.0)

    def _get_category_boost(self, message_lower: str) -> float:
        """Get boost based on detected category keywords."""
        boost = 0.0

        for category, category_kw in self.SKILL_CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in category_kw if kw in message_lower)
            if matches > 0:
                boost = max(boost, matches * 0.1)

        return boost

    def detect_skills_ranked(
        self,
        user_message: str,
        top_n: int = 5,
    ) -> list[tuple[str, float]]:
        """Get top N skills ranked by confidence for a user message.

        Args:
            user_message: The user's message to analyze
            top_n: Number of top skills to return

        Returns:
            List of (skill_name, confidence) tuples sorted by confidence
        """
        if not self._keyword_cache:
            self.load_skills()

        message_lower = user_message.lower()
        words = set(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", message_lower))

        scored: list[tuple[str, float]] = []

        for skill_name in self.registry.list_skills():
            skill = self.registry.get_skill(skill_name)
            if not skill:
                continue

            score = self._calculate_confidence(words, message_lower, skill_name)
            if score > 0:
                scored.append((skill_name, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def get_skill_keywords(self, skill_name: str) -> set[str]:
        """Get all keywords for a skill."""
        if not self._keyword_cache:
            self._build_keyword_cache()
        return self._keyword_cache.get(skill_name, set())

    def should_auto_switch(
        self,
        current_skill: str | None,
        new_skill: str,
        confidence: float,
        threshold: float,
    ) -> bool:
        """Determine if auto-switch should occur.

        Args:
            current_skill: Currently active skill
            new_skill: Skill to potentially switch to
            confidence: Confidence score for the new skill
            threshold: Minimum confidence threshold

        Returns:
            True if should switch, False otherwise
        """
        if not new_skill:
            return False

        if current_skill == new_skill:
            return False

        if confidence < threshold:
            return False

        return True


def detect_skill_from_message(
    message: str,
    project_dir: str | None = None,
    threshold: float = 0.7,
) -> tuple[str | None, float]:
    """Convenience function to detect skill from a message.

    Args:
        message: User message to analyze
        project_dir: Optional project directory
        threshold: Minimum confidence threshold

    Returns:
        Tuple of (skill_name, confidence)
    """
    engine = SkillDetectionEngine(project_dir)
    return engine.detect_skill(message, threshold)


def get_skill_recommendations(
    message: str,
    project_dir: str | None = None,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """Get skill recommendations for a message.

    Args:
        message: User message to analyze
        project_dir: Optional project directory
        top_n: Number of recommendations to return

    Returns:
        List of dicts with 'name', 'confidence', 'description'
    """
    engine = SkillDetectionEngine(project_dir)
    recommendations = engine.detect_skills_ranked(message, top_n)

    registry = SkillRegistry(
        project_dir=project_dir
    )

    result = []
    for skill_name, confidence in recommendations:
        skill = registry.get_skill(skill_name)
        if skill:
            result.append({
                "name": skill_name,
                "confidence": confidence,
                "description": skill.description,
            })

    return result
