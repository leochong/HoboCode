"""Skill panel component for the TUI."""

from typing import Generator
from rich.text import Text
from textual.containers import Container
from textual.widgets import Label, Static, ListView, ListItem
from textual.widget import Widget


class SkillListItem(ListItem):
    """List item for displaying a skill."""

    def __init__(self, name: str, description: str = "", active: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.active = active

    def compose(self) -> Generator[Widget, None, None]:
        style = "bold green" if self.active else ""
        indicator = "[*] " if self.active else "    "
        yield Label(f"{indicator}{self.name}", style=style)


class SkillPanel(Container):
    """Panel showing available skills and skill management controls."""

    CSS = """
    SkillPanel {
        width: 30;
        border: solid $accent;
        background: $surface;
        padding: 1;
    }
    #skill-header {
        height: 3;
        background: $accent;
        color: $text;
        text-align: center;
        content-align: center;
    }
    #skill-list {
        height: 1fr;
        overflow: auto;
    }
    #skill-info {
        height: auto;
        border-top: solid $accent;
        padding-top: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.skills: list[dict[str, str]] = []
        self.active_skill: str | None = None
        self._skill_list: ListView | None = None
        self._on_skill_select_callback = None

    def compose(self) -> Generator[Widget, None, None]:
        yield Label("SKILLS", id="skill-header")
        yield ListView(id="skill-list")
        yield Static("No skill selected\nUse /skill <name>\nto activate", id="skill-info")

    def on_mount(self) -> None:
        """Load skills on mount."""
        self._skill_list = self.query_one("#skill-list", ListView)
        self.refresh_skills()

    def refresh_skills(self) -> None:
        """Refresh the skill list from registry."""
        from hobo_code.skills.registry import SkillRegistry

        registry = SkillRegistry()
        skill_names = registry.list_skills()

        self.skills = []
        for name in skill_names:
            skill = registry.get_skill(name)
            if skill:
                self.skills.append({
                    "name": name,
                    "description": skill.description[:30] if skill.description else "",
                })

        self._update_skill_list()

    def _update_skill_list(self) -> None:
        """Update the skill list widget."""
        if not self._skill_list:
            return

        self._skill_list.clear()

        for skill in self.skills:
            if skill["name"] != self.active_skill:
                item = SkillListItem(
                    name=skill["name"],
                    description=skill.get("description", ""),
                    active=False
                )
                self._skill_list.append(item)

        if self.active_skill:
            active_skill = next((s for s in self.skills if s["name"] == self.active_skill), None)
            if active_skill:
                item = SkillListItem(
                    name=active_skill["name"],
                    description=active_skill.get("description", ""),
                    active=True
                )
                self._skill_list.append(item)

        self._update_skill_info()

    def _update_skill_info(self) -> None:
        """Update the skill info display."""
        info_widget = self.query_one("#skill-info", Static)

        if self.active_skill:
            skill = next((s for s in self.skills if s["name"] == self.active_skill), None)
            if skill:
                info_widget.update(
                    f"Active: [bold green]{self.active_skill}[/]\n{skill.get('description', '')}"
                )
            else:
                info_widget.update(f"Active: [bold green]{self.active_skill}[/]")
        else:
            info_widget.update("No skill selected\nUse /skill <name>\nto activate")

    def set_active_skill(self, skill_name: str | None) -> None:
        """Set the active skill."""
        self.active_skill = skill_name
        self._update_skill_list()

    def get_active_skill(self) -> str | None:
        """Get the currently active skill."""
        return self.active_skill

    def on_skill_select(self, callback) -> None:
        """Set callback for skill selection."""
        self._on_skill_select_callback = callback

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle skill selection from list."""
        if isinstance(event.item, SkillListItem):
            self.set_active_skill(event.item.name)
            if self._on_skill_select_callback:
                self._on_skill_select_callback(event.item.name)


class SkillIndicator(Static):
    """Small indicator showing the currently active skill."""

    CSS = """
    SkillIndicator {
        color: $success;
        bold;
    }
    """

    def __init__(self, skill_name: str | None = None, auto_mode: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._skill_name = skill_name
        self._auto_mode = auto_mode
        self.update_display()

    def update_display(self) -> None:
        """Update the display based on current skill."""
        if self._skill_name:
            mode = "[Auto] " if self._auto_mode else ""
            self.update(f"{mode}[Skill: {self._skill_name}]")
        else:
            mode = "[Auto] " if self._auto_mode else ""
            self.update(f"{mode}[No skill]")

    @property
    def skill_name(self) -> str | None:
        return self._skill_name

    @skill_name.setter
    def skill_name(self, value: str | None) -> None:
        self._skill_name = value
        self.update_display()

    @property
    def auto_mode(self) -> bool:
        return self._auto_mode

    @auto_mode.setter
    def auto_mode(self, value: bool) -> None:
        self._auto_mode = value
        self.update_display()


class SkillCommandHelp(Static):
    """Help panel showing skill-related commands."""

    CSS = """
    SkillCommandHelp {
        height: 5;
        border: solid $accent;
        padding: 1;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_content()

    def update_content(self) -> None:
        content = Text()
        content.append("Skill Commands:\n", style="bold")
        content.append("  /skill list    ", style="dim")
        content.append("- Show available skills\n", style="dim")
        content.append("  /skill <name>  ", style="dim")
        content.append("- Activate a skill\n", style="dim")
        content.append("  /skill clear   ", style="dim")
        content.append("- Deactivate current skill\n", style="dim")
        content.append("  /skill info    ", style="dim")
        content.append("- Show skill details\n", style="dim")
        self.update(content)


class SkillNotification(Container):
    """Toast notification for skill auto-switch."""

    CSS = """
    SkillNotification {
        width: 50;
        height: auto;
        border: solid $accent;
        background: $surface-darken-1;
        padding: 1;
        dock: top;
        offset-y: -1;
    }
    #notification-text {
        text-align: center;
        color: $text;
    }
    #notification-confidence {
        color: $success;
        italic;
    }
    """

    def __init__(
        self,
        skill_name: str,
        confidence: float,
        is_auto: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.skill_name = skill_name
        self.confidence = confidence
        self.is_auto = is_auto

    def compose(self) -> Generator[Widget, None, None]:
        mode = "[Auto] " if self.is_auto else ""
        yield Label(
            f"{mode}Switched to: {self.skill_name}",
            id="notification-text"
        )
        yield Label(
            f"Confidence: {self.confidence:.0%}",
            id="notification-confidence"
        )

    async def on_click(self) -> None:
        """Dismiss on click."""
        self.remove()
