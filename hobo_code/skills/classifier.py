"""LLM-based skill classifier for intelligent skill detection."""

import json
from typing import Any

from hobo_code.skills.registry import SkillRegistry


class SkillClassifier:
    """Uses LLM to classify user intent and suggest appropriate skills."""

    DEFAULT_PROMPT = """You are a skill classifier for Hobo Code, an AI coding assistant.

Given a user's message, classify their intent and recommend the best matching skill.

Available skills:
{skills_list}

Your task:
1. Analyze the user's message
2. Identify their intent (coding task, debugging, testing, etc.)
3. Recommend the best matching skill from the available skills
4. Provide a confidence score (0.0 to 1.0)

Respond with JSON in this format:
{{
    "intent": "brief description of user intent",
    "recommended_skill": "skill name or null if none matches",
    "confidence": 0.0-1.0,
    "reasoning": "why this skill was recommended",
    "alternatives": ["skill1", "skill2"]  # optional
}}

User's message: "{message}"
"""

    def __init__(self, project_dir: str | None = None):
        self.project_dir = project_dir
        self.registry = SkillRegistry(
            project_dir=project_dir
        )
        self._model_provider = None

    def _get_model_provider(self):
        """Lazy load model provider."""
        if self._model_provider is None:
            try:
                from hobo_code.models.provider import ModelProvider
                self._model_provider = ModelProvider()
            except Exception:
                pass
        return self._model_provider

    def _get_skills_list(self) -> str:
        """Get formatted list of available skills."""
        skills = self.registry.list_skills()
        skill_descriptions = []

        for skill_name in skills:
            skill = self.registry.get_skill(skill_name)
            if skill:
                desc = f"  - {skill_name}: {skill.description}"
                if skill.keywords:
                    desc += f" (keywords: {', '.join(skill.keywords[:5])})"
                skill_descriptions.append(desc)

        return "\n".join(skill_descriptions)

    def classify_with_llm(
        self,
        message: str,
        model: str | None = None,
    ) -> dict[str, Any] | None:
        """Classify user intent using LLM.

        Args:
            message: User's message to classify
            model: Optional model to use (default: from config)

        Returns:
            Dict with classification results or None if failed
        """
        model_provider = self._get_model_provider()
        if not model_provider:
            return None

        skills_list = self._get_skills_list()
        prompt = self.DEFAULT_PROMPT.format(
            skills_list=skills_list,
            message=message,
        )

        try:
            if model is None:
                model = "claude-3-5-sonnet-20241002"

            response = model_provider.call(model, prompt, max_tokens=500)

            if response and response.get("content"):
                content = response["content"]
                return self._parse_response(content)
        except Exception:
            pass

        return None

    def _parse_response(self, content: str) -> dict[str, Any]:
        """Parse LLM response to extract classification."""
        try:
            content = content.strip()

            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]

            content = content.strip()

            result = json.loads(content)

            return {
                "intent": result.get("intent", ""),
                "recommended_skill": result.get("recommended_skill"),
                "confidence": float(result.get("confidence", 0.0)),
                "reasoning": result.get("reasoning", ""),
                "alternatives": result.get("alternatives", []),
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

        return None

    def classify(
        self,
        message: str,
        use_llm_fallback: bool = True,
        min_llm_confidence: float = 0.6,
    ) -> dict[str, Any]:
        """Classify user intent using best available method.

        This first tries keyword-based detection, then falls back to LLM
        if confidence is low or explicitly requested.

        Args:
            message: User's message to classify
            use_llm_fallback: Use LLM when keyword detection is uncertain
            min_llm_confidence: Minimum confidence to accept LLM result

        Returns:
            Dict with classification results
        """
        from hobo_code.skills.detection import SkillDetectionEngine

        detection_engine = SkillDetectionEngine(self.project_dir)
        skill_name, keyword_confidence = detection_engine.detect_skill(message)

        result = {
            "method": "keyword",
            "skill": skill_name,
            "confidence": keyword_confidence,
            "intent": "",
            "reasoning": "",
            "source": "detection",
        }

        if skill_name:
            skill = self.registry.get_skill(skill_name)
            if skill:
                result["intent"] = f"{skill_name.split('/')[-1]} task"
                result["reasoning"] = f"Matched {skill_name} via keywords"

        if use_llm_fallback and (
            skill_name is None or
            keyword_confidence < min_llm_confidence
        ):
            llm_result = self.classify_with_llm(message)

            if llm_result:
                should_use_llm = (
                    llm_result.get("confidence", 0) >= min_llm_confidence and
                    llm_result.get("recommended_skill")
                )

                if should_use_llm or keyword_confidence < 0.3:
                    result = {
                        "method": "llm",
                        "skill": llm_result.get("recommended_skill"),
                        "confidence": llm_result.get("confidence", 0),
                        "intent": llm_result.get("intent", ""),
                        "reasoning": llm_result.get("reasoning", ""),
                        "alternatives": llm_result.get("alternatives", []),
                        "source": "llm",
                    }

        return result

    def get_recommendations(
        self,
        message: str,
        top_n: int = 3,
    ) -> list[dict[str, Any]]:
        """Get top skill recommendations for a message.

        Args:
            message: User's message
            top_n: Number of recommendations to return

        Returns:
            List of skill recommendations with scores
        """
        from hobo_code.skills.detection import SkillDetectionEngine

        detection_engine = SkillDetectionEngine(self.project_dir)
        keyword_recommendations = detection_engine.detect_skills_ranked(message, top_n)

        recommendations = []
        seen = set()

        for skill_name, score in keyword_recommendations:
            if skill_name not in seen and score > 0:
                recommendations.append({
                    "skill": skill_name,
                    "confidence": score,
                    "method": "keyword",
                })
                seen.add(skill_name)

        llm_result = self.classify_with_llm(message)
        if llm_result:
            skill = llm_result.get("recommended_skill")
            if skill and skill not in seen:
                recommendations.append({
                    "skill": skill,
                    "confidence": llm_result.get("confidence", 0),
                    "method": "llm",
                    "reasoning": llm_result.get("reasoning", ""),
                })

        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        return recommendations[:top_n]


def classify_skill(
    message: str,
    project_dir: str | None = None,
    use_llm: bool = True,
) -> dict[str, Any]:
    """Convenience function to classify skill from message.

    Args:
        message: User's message
        project_dir: Optional project directory
        use_llm: Whether to use LLM fallback

    Returns:
        Classification result dict
    """
    classifier = SkillClassifier(project_dir)
    return classifier.classify(message, use_llm_fallback=use_llm)


def get_skill_recommendations(
    message: str,
    project_dir: str | None = None,
    top_n: int = 3,
) -> list[dict[str, Any]]:
    """Get skill recommendations for a message.

    Args:
        message: User's message
        project_dir: Optional project directory
        top_n: Number of recommendations

    Returns:
        List of recommendations
    """
    classifier = SkillClassifier(project_dir)
    return classifier.get_recommendations(message, top_n)
