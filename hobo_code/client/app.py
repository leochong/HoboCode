"""Main TUI application for Hobo Code."""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Label

from hobo_code.client.components import MessageList, ChatInput
from hobo_code.session.manager import SessionManager


class HoboApp(App):
    """Main TUI application for Hobo Code."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #chat-container {
        height: 1fr;
        overflow: hidden;
    }
    #status-bar {
        height: 1;
        background: $accent;
        color: $text;
    }
    """

    BINDINGS = [
        ("Ctrl+C", "quit", "Quit"),
        ("Ctrl+L", "clear", "Clear Chat"),
    ]

    def __init__(self, session_id: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.session_manager = SessionManager()
        self.current_session = None
        if session_id:
            self.current_session = self.session_manager.get_session(session_id)
        if not self.current_session:
            self.current_session = self.session_manager.create_session("New Chat")

    def compose(self) -> ComposeResult:
        yield Label("Hobo Code | Connected", id="status-bar")
        with Container(id="chat-container"):
            yield MessageList(id="message-list")
        yield ChatInput(id="chat-input", placeholder="Type a message... (Enter to send)")
        yield Footer()

    async def on_mount(self) -> None:
        """Handle app mount."""
        if self.current_session:
            for msg in self.current_session.messages:
                self.query_one("#message-list", MessageList).add_message(msg.role, msg.content)

    async def on_chat_input_submitted(self, event: ChatInput.Submitted) -> None:
        """Handle message submission."""
        user_message = event.value.strip()
        if not user_message:
            return

        message_list = self.query_one("#message-list", MessageList)
        message_list.add_message("user", user_message)

        await self.process_assistant_response(user_message)

    async def process_assistant_response(self, user_message: str) -> None:
        """Process user message and generate assistant response."""
        await asyncio.sleep(0.5)

        assistant_response = f"I received: {user_message}\n\nThis is a placeholder response. In production, this would connect to the ACP server."

        message_list = self.query_one("#message-list", MessageList)
        message_list.add_message("assistant", assistant_response)

        if self.current_session:
            self.session_manager.add_message(self.current_session.id, "user", user_message)
            self.session_manager.add_message(self.current_session.id, "assistant", assistant_response)

    def action_clear(self) -> None:
        """Clear the chat."""
        message_list = self.query_one("#message-list", MessageList)
        message_list.clear()

    async def action_quit(self) -> None:
        """Quit the application."""
        if self.current_session:
            self.session_manager.save_session(self.current_session)
        await self.shutdown()
