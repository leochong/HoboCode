"""TUI components for the chat interface."""

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
        """Add a message to the list (without auto-update)."""
        self.messages.append((role, content))

    def clear(self) -> None:
        """Clear all messages."""
        self.messages.clear()

    def get_messages(self) -> list[tuple[str, str]]:
        """Get all messages."""
        return self.messages.copy()


class ChatInput(Input):
    """Input widget for chat messages."""

    def __init__(self, placeholder: str = "Type a message...", **kwargs):
        super().__init__(placeholder=placeholder, **kwargs)

    async def on_submit(self) -> None:
        """Handle Enter key submission."""
        if self.value.strip():
            await self.post_message_no_wait(self.Submitted(self.value))
            self.value = ""

    class Submitted(Input.Submitted):
        """Event emitted when Enter is pressed."""
