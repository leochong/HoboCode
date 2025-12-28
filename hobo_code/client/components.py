"""TUI components for the chat interface."""

import re
from rich.markdown import Markdown
from rich.text import Text
from rich.panel import Panel
from textual.widget import Widget
from textual.widgets import Label, Input, Static


class MessageBubble(Static):
    """Message bubble component for chat messages."""

    def __init__(self, content: str, role: str = "user", **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.role = role

    def compose(self):
        if self.role == "user":
            yield Panel(
                Text(self.content),
                style="blue on dark_blue",
                subtitle=f"[{self.role}]",
                subtitle_align="right",
            )
        else:
            yield Panel(
                Markdown(self.content),
                style="green on dark_green",
                subtitle=f"[{self.role}]",
                subtitle_align="left",
            )


class MessageList(Static):
    """Widget displaying a list of messages."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages: list[tuple[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a message bubble to the list."""
        self.messages.append((role, content))
        bubble = MessageBubble(content, role=role)
        self.mount(bubble)
        self.scroll_bottom = True

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()
        for child in self.query(MessageBubble):
            child.remove()

    def get_messages(self) -> list[tuple[str, str]]:
        """Get all messages."""
        return self.messages.copy()


class ChatInput(Input):
    """Input widget for chat messages with skill command support."""

    BINDINGS = [
        ("ctrl+s", "activate_skill", "Activate Skill"),
    ]

    SKILL_PATTERN = re.compile(r"^/skill\s+(\S+)$")
    SKILL_LIST_PATTERN = re.compile(r"^/skill\s+list$")
    SKILL_CLEAR_PATTERN = re.compile(r"^/skill\s+clear$")
    SKILL_INFO_PATTERN = re.compile(r"^/skill\s+info(?:\s+(\S+))?$")

    def __init__(
        self,
        placeholder: str = "Type a message... (Enter to send, /skill <name> to activate)",
        **kwargs,
    ):
        super().__init__(placeholder=placeholder, **kwargs)
        self.on_skill_command_callback = None
        self.on_regular_message_callback = None

    def on_skill_command(self, callback) -> None:
        """Set callback for skill commands."""
        self.on_skill_command_callback = callback

    def on_regular_message(self, callback) -> None:
        """Set callback for regular messages."""
        self.on_regular_message_callback = callback

    async def on_submit(self) -> None:
        """Handle Enter key submission."""
        value = self.value.strip()
        if not value:
            return

        skill_match = self.SKILL_PATTERN.match(value)
        skill_list_match = self.SKILL_LIST_PATTERN.match(value)
        skill_clear_match = self.SKILL_CLEAR_PATTERN.match(value)
        skill_info_match = self.SKILL_INFO_PATTERN.match(value)

        if skill_list_match:
            if self.on_skill_command_callback:
                await self.on_skill_command_callback("list", None)
            self.value = ""
            return

        if skill_clear_match:
            if self.on_skill_command_callback:
                await self.on_skill_command_callback("clear", None)
            self.value = ""
            return

        if skill_info_match:
            skill_name = skill_info_match.group(1)
            if self.on_skill_command_callback:
                await self.on_skill_command_callback("info", skill_name)
            self.value = ""
            return

        if skill_match:
            skill_name = skill_match.group(1)
            if self.on_skill_command_callback:
                await self.on_skill_command_callback("activate", skill_name)
            self.value = ""
            return

        if self.on_regular_message_callback:
            await self.on_regular_message_callback(value)
        else:
            await self.post_message_no_wait(self.Submitted(self, value, None))
        self.value = ""

    class Submitted(Input.Submitted):
        """Event emitted when Enter is pressed."""

        def __init__(self, input_widget: Input, value: str, validation_result):
            super().__init__(input_widget, value, validation_result)
            self.value = value
