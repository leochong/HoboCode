"""Auto-switch manager for automatic skill activation with debounce."""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from hobo_code.skills.detection import SkillDetectionEngine, detect_skill_from_message


class AutoSwitchConfig:
    """Configuration for auto-switch behavior."""

    DEFAULT_CONFIG = {
        "enabled": True,
        "use_llm": True,
        "min_keyword_confidence": 0.7,
        "min_llm_confidence": 0.6,
        "debounce_seconds": 3.0,
        "show_notifications": True,
        "notification_sound": True,
        "locked_skill": None,
        "exclude_skills": [],
    }

    def __init__(self, config_path: str | None = None):
        self.config_path = Path(config_path) if config_path else self._get_default_path()
        self.config = self._load_config()

    def _get_default_path(self) -> Path:
        """Get default config path."""
        return Path.home() / ".hobo-code" / "auto_switch.json"

    def _load_config(self) -> dict[str, Any]:
        """Load config from file or use defaults."""
        if self.config_path and self.config_path.exists():
            try:
                content = self.config_path.read_text(encoding="utf-8")
                loaded = json.loads(content)
                return {**self.DEFAULT_CONFIG, **loaded}
            except (json.JSONDecodeError, OSError):
                pass
        return self.DEFAULT_CONFIG.copy()

    def save(self) -> None:
        """Save config to file."""
        if self.config_path:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(
                json.dumps(self.config, indent=2),
                encoding="utf-8"
            )

    @property
    def enabled(self) -> bool:
        return self.config.get("enabled", True)

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self.config["enabled"] = value

    @property
    def use_llm(self) -> bool:
        return self.config.get("use_llm", True)

    @use_llm.setter
    def use_llm(self, value: bool) -> None:
        self.config["use_llm"] = value

    @property
    def min_keyword_confidence(self) -> float:
        return self.config.get("min_keyword_confidence", 0.7)

    @min_keyword_confidence.setter
    def min_keyword_confidence(self, value: float) -> None:
        self.config["min_keyword_confidence"] = max(0.0, min(1.0, value))

    @property
    def min_llm_confidence(self) -> float:
        return self.config.get("min_llm_confidence", 0.6)

    @min_llm_confidence.setter
    def min_llm_confidence(self, value: float) -> None:
        self.config["min_llm_confidence"] = max(0.0, min(1.0, value))

    @property
    def debounce_seconds(self) -> float:
        return self.config.get("debounce_seconds", 3.0)

    @debounce_seconds.setter
    def debounce_seconds(self, value: float) -> None:
        self.config["debounce_seconds"] = max(0.5, value)

    @property
    def show_notifications(self) -> bool:
        return self.config.get("show_notifications", True)

    @show_notifications.setter
    def show_notifications(self, value: bool) -> None:
        self.config["show_notifications"] = value

    @property
    def notification_sound(self) -> bool:
        return self.config.get("notification_sound", True)

    @notification_sound.setter
    def notification_sound(self, value: bool) -> None:
        self.config["notification_sound"] = value

    @property
    def locked_skill(self) -> str | None:
        return self.config.get("locked_skill")

    @locked_skill.setter
    def locked_skill(self, value: str | None) -> None:
        self.config["locked_skill"] = value

    def to_dict(self) -> dict[str, Any]:
        return self.config.copy()


class AutoSwitchEvent:
    """Event emitted when skill auto-switches."""

    def __init__(
        self,
        previous_skill: str | None,
        new_skill: str,
        confidence: float,
        triggered_by: str = "message",
    ):
        self.previous_skill = previous_skill
        self.new_skill = new_skill
        self.confidence = confidence
        self.triggered_by = triggered_by
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "previous_skill": self.previous_skill,
            "new_skill": self.new_skill,
            "confidence": self.confidence,
            "triggered_by": self.triggered_by,
            "timestamp": self.timestamp,
        }


class AutoSwitchManager:
    """Manages automatic skill switching with debounce and notifications."""

    def __init__(
        self,
        config: AutoSwitchConfig | None = None,
        project_dir: str | None = None,
    ):
        self.config = config or AutoSwitchConfig()
        self.detection_engine = SkillDetectionEngine(project_dir)
        self._last_switch_time: datetime | None = None
        self._pending_switch: tuple[str, float] | None = None
        self._debounce_task: asyncio.Task | None = None
        self._callbacks: list[Callable[[AutoSwitchEvent], None]] = []

    def on_switch(self, callback: Callable[[AutoSwitchEvent], None]) -> None:
        """Register callback for skill switch events."""
        self._callbacks.append(callback)

    def _emit_switch_event(self, event: AutoSwitchEvent) -> None:
        """Emit switch event to all callbacks."""
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception:
                pass

    def should_auto_switch(
        self,
        current_skill: str | None,
        new_skill: str | None,
        confidence: float,
    ) -> tuple[bool, str]:
        """Check if auto-switch should occur.

        Returns:
            Tuple of (should_switch, reason)
        """
        if not self.config.enabled:
            return False, "auto_switch_disabled"

        if not new_skill:
            return False, "no_skill_detected"

        if current_skill == new_skill:
            return False, "same_skill"

        locked_skill = self.config.locked_skill
        if locked_skill and current_skill == locked_skill:
            return False, "skill_locked"

        if confidence < self.config.min_keyword_confidence:
            return False, "below_threshold"

        if self._is_in_debounce():
            return False, "in_debounce"

        return True, "ok"

    def _is_in_debounce(self) -> bool:
        """Check if we're in the debounce period."""
        if self._last_switch_time is None:
            return False

        elapsed = datetime.utcnow() - self._last_switch_time
        return elapsed.total_seconds() < self.config.debounce_seconds

    async def _do_switch_after_debounce(
        self,
        new_skill: str,
        confidence: float,
        current_skill: str,
    ) -> None:
        """Perform the switch after debounce period."""
        await asyncio.sleep(self.config.debounce_seconds)

        if self._pending_switch != (new_skill, confidence):
            return

        self._last_switch_time = datetime.utcnow()
        self._pending_switch = None

        event = AutoSwitchEvent(
            previous_skill=current_skill,
            new_skill=new_skill,
            confidence=confidence,
            triggered_by="debounce",
        )
        self._emit_switch_event(event)

    async def process_message(
        self,
        message: str,
        current_skill: str | None,
    ) -> tuple[str | None, float, bool]:
        """Process a message and potentially auto-switch skills.

        Uses both keyword detection and LLM classification for best results.

        Args:
            message: The user's message
            current_skill: Currently active skill

        Returns:
            Tuple of (suggested_skill, confidence, did_switch)
        """
        if not self.config.enabled:
            return None, 0.0, False

        detected_skill, confidence, method = self._detect_skill_with_fallback(message)

        should_switch, reason = self.should_auto_switch(
            current_skill, detected_skill, confidence
        )

        if should_switch and detected_skill:
            self._last_switch_time = datetime.utcnow()

            event = AutoSwitchEvent(
                previous_skill=current_skill,
                new_skill=detected_skill,
                confidence=confidence,
                triggered_by=f"message_{method}",
            )
            self._emit_switch_event(event)

            return detected_skill, confidence, True

        return detected_skill, confidence, False

    def _detect_skill_with_fallback(
        self,
        message: str,
    ) -> tuple[str | None, float, str]:
        """Detect skill with keyword -> LLM fallback.

        Returns:
            Tuple of (skill, confidence, method)
        """
        from hobo_code.skills.detection import SkillDetectionEngine

        detection_engine = SkillDetectionEngine()
        keyword_skill, keyword_confidence = detection_engine.detect_skill(message)

        if keyword_skill and keyword_confidence >= self.config.min_keyword_confidence:
            return keyword_skill, keyword_confidence, "keyword"

        if self.config.use_llm:
            try:
                from hobo_code.skills.classifier import SkillClassifier
                classifier = SkillClassifier()
                llm_result = classifier.classify_with_llm(message)

                if llm_result:
                    llm_skill = llm_result.get("recommended_skill")
                    llm_confidence = llm_result.get("confidence", 0)

                    if llm_skill and llm_confidence >= self.config.min_llm_confidence:
                        return llm_skill, llm_confidence, "llm"

                    if not keyword_skill or llm_confidence > keyword_confidence:
                        return llm_skill, llm_confidence, "llm"
            except Exception:
                pass

        if keyword_skill:
            return keyword_skill, keyword_confidence, "keyword"

        return None, 0.0, "none"

    def get_status(self) -> dict[str, Any]:
        """Get current auto-switch status."""
        return {
            "enabled": self.config.enabled,
            "min_keyword_confidence": self.config.min_keyword_confidence,
            "debounce_seconds": self.config.debounce_seconds,
            "locked_skill": self.config.locked_skill,
            "in_debounce": self._is_in_debounce(),
            "time_since_last_switch": (
                (datetime.utcnow() - self._last_switch_time).total_seconds()
                if self._last_switch_time else None
            ),
        }

    def toggle(self) -> bool:
        """Toggle auto-switch on/off. Returns new state."""
        self.config.enabled = not self.config.enabled
        self.config.save()
        return self.config.enabled

    def set_locked_skill(self, skill_name: str | None) -> None:
        """Set the locked skill (None to unlock)."""
        self.config.locked_skill = skill_name
        self.config.save()

    def reset_debounce(self) -> None:
        """Reset the debounce timer."""
        self._last_switch_time = None
        self._pending_switch = None
        if self._debounce_task:
            self._debounce_task.cancel()
            self._debounce_task = None


def create_auto_switch_manager(
    project_dir: str | None = None,
) -> AutoSwitchManager:
    """Factory function to create auto-switch manager."""
    config = AutoSwitchConfig()
    return AutoSwitchManager(config, project_dir)
