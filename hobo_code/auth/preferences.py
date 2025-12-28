"""User preferences storage for Hobo Code."""

import json
from pathlib import Path
from typing import Any

from hobo_code.skills.auto_switch import AutoSwitchConfig


class UserPreferences:
    """Centralized user preferences storage."""

    DEFAULT_PREFS = {
        "auto_switch": {
            "enabled": True,
            "min_confidence": 0.7,
            "debounce_seconds": 3.0,
            "show_notifications": True,
            "notification_sound": True,
            "locked_skill": None,
        },
        "ui": {
            "theme": "default",
            "font_size": 14,
            "sidebar_visible": True,
            "compact_mode": False,
        },
        "chat": {
            "auto_scroll": True,
            "show_timestamps": False,
            "max_messages": 1000,
        },
        "telemetry": {
            "enabled": False,
            "share_errors": False,
        },
    }

    def __init__(self, config_dir: str | None = None):
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".hobo-code"

        self.prefs_file = self.config_dir / "preferences.json"
        self.auto_switch_config = AutoSwitchConfig(
            str(self.config_dir / "auto_switch.json")
        )
        self._prefs = self._load_prefs()

    def _load_prefs(self) -> dict[str, Any]:
        """Load preferences from file."""
        if self.prefs_file.exists():
            try:
                content = self.prefs_file.read_text(encoding="utf-8")
                loaded = json.loads(content)
                return {**self.DEFAULT_PREFS, **loaded}
            except (json.JSONDecodeError, OSError):
                pass
        return self.DEFAULT_PREFS.copy()

    def save(self) -> None:
        """Save preferences to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.prefs_file.write_text(
            json.dumps(self._prefs, indent=2),
            encoding="utf-8"
        )
        self.auto_switch_config.save()

    def get(self, *keys: str, default: Any = None) -> Any:
        """Get a nested preference value."""
        current = self._prefs
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def set(self, value: Any, *keys: str) -> None:
        """Set a nested preference value."""
        if len(keys) == 0:
            return

        current = self._prefs
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value
        self.save()

    @property
    def auto_switch_enabled(self) -> bool:
        return self.auto_switch_config.enabled

    @auto_switch_enabled.setter
    def auto_switch_enabled(self, value: bool) -> None:
        self.auto_switch_config.enabled = value
        self.auto_switch_config.save()

    @property
    def min_confidence(self) -> float:
        return self.auto_switch_config.min_confidence

    @min_confidence.setter
    def min_confidence(self, value: float) -> None:
        self.auto_switch_config.min_confidence = value
        self.auto_switch_config.save()

    @property
    def debounce_seconds(self) -> float:
        return self.auto_switch_config.debounce_seconds

    @debounce_seconds.setter
    def debounce_seconds(self, value: float) -> None:
        self.auto_switch_config.debounce_seconds = value
        self.auto_switch_config.save()

    @property
    def show_notifications(self) -> bool:
        return self.auto_switch_config.show_notifications

    @show_notifications.setter
    def show_notifications(self, value: bool) -> None:
        self.auto_switch_config.show_notifications = value
        self.auto_switch_config.save()

    @property
    def locked_skill(self) -> str | None:
        return self.auto_switch_config.locked_skill

    @locked_skill.setter
    def locked_skill(self, value: str | None) -> None:
        self.auto_switch_config.locked_skill = value
        self.auto_switch_config.save()

    def reset(self) -> None:
        """Reset all preferences to defaults."""
        self._prefs = self.DEFAULT_PREFS.copy()
        self.auto_switch_config = AutoSwitchConfig()
        self.save()

    def to_dict(self) -> dict[str, Any]:
        """Export all preferences as dict."""
        return {
            "auto_switch": self.auto_switch_config.to_dict(),
            "ui": self._prefs.get("ui", {}),
            "chat": self._prefs.get("chat", {}),
            "telemetry": self._prefs.get("telemetry", {}),
        }


def get_user_preferences(config_dir: str | None = None) -> UserPreferences:
    """Factory function to get user preferences."""
    return UserPreferences(config_dir)


def reset_user_preferences(config_dir: str | None = None) -> None:
    """Reset user preferences to defaults."""
    prefs = UserPreferences(config_dir)
    prefs.reset()
