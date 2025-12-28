"""Main TUI application for Hobo Code."""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Label

from hobo_code.client.components import MessageList, ChatInput
from hobo_code.client.skills import SkillPanel, SkillIndicator, SkillNotification
from hobo_code.session.manager import SessionManager
from hobo_code.skills.registry import SkillRegistry
from hobo_code.skills.auto_switch import AutoSwitchManager, AutoSwitchEvent
from hobo_code.auth.preferences import UserPreferences


class HoboApp(App):
    """Main TUI application for Hobo Code."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #main-content {
        layout: horizontal;
        height: 1fr;
    }
    #chat-area {
        width: 1fr;
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
    #input-area {
        height: auto;
    }
    """

    BINDINGS = [
        ("Ctrl+C", "quit", "Quit"),
        ("Ctrl+L", "clear", "Clear Chat"),
        ("Ctrl+S", "toggle_skills", "Toggle Skills Panel"),
        ("Ctrl+A", "toggle_auto_switch", "Toggle Auto-Switch"),
    ]

    def __init__(self, session_id: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.session_manager = SessionManager()
        self.preferences = UserPreferences()
        self.auto_switch_manager = AutoSwitchManager(
            config=None,
            project_dir=None,
        )
        self.auto_switch_manager.on_switch(self._on_skill_switch)
        self.current_session = None
        self.active_skill: str | None = None
        self.skills_panel_visible = True
        self.auto_mode = self.preferences.auto_switch_enabled

        if session_id:
            self.current_session = self.session_manager.get_session(session_id)
        if not self.current_session:
            self.current_session = self.session_manager.create_session("New Chat")

        if self.current_session and self.current_session.model:
            self.active_skill = self.current_session.model

    def compose(self) -> ComposeResult:
        yield Label("Hobo Code | Connected", id="status-bar")
        with Horizontal(id="main-content"):
            with Container(id="chat-area"):
                with Container(id="chat-container"):
                    yield MessageList(id="message-list")
                with Container(id="input-area"):
                    yield SkillIndicator(id="skill-indicator")
                    yield ChatInput(
                        id="chat-input",
                        placeholder="Type a message... (Enter to send, /skill <name> to activate)",
                    )
            yield SkillPanel(id="skills-panel")

        yield Footer()

    def on_mount(self) -> None:
        """Handle app mount."""
        if self.current_session:
            for msg in self.current_session.messages:
                self.query_one("#message-list", MessageList).add_message(msg.role, msg.content)

        self.query_one("#chat-input", ChatInput).on_skill_command(self.handle_skill_command)
        self.query_one("#chat-input", ChatInput).on_regular_message(self.handle_regular_message)

        self.update_skill_indicator()
        self.refresh_skills_panel()

    def update_skill_indicator(self) -> None:
        """Update the skill indicator."""
        indicator = self.query_one("#skill-indicator", SkillIndicator)
        indicator.skill_name = self.active_skill
        indicator.auto_mode = self.auto_mode

    def refresh_skills_panel(self) -> None:
        """Refresh the skills panel."""
        panel = self.query_one("#skills-panel", SkillPanel)
        panel.set_active_skill(self.active_skill)
        panel.on_skill_select(self.handle_skill_panel_select)

    def _on_skill_switch(self, event: AutoSwitchEvent) -> None:
        """Handle skill switch event from auto-switch manager."""
        self.active_skill = event.new_skill
        self.update_skill_indicator()
        self.refresh_skills_panel()

        if self.current_session:
            self.current_session.model = event.new_skill

        if self.preferences.show_notifications:
            self._show_switch_notification(event.new_skill, event.confidence, is_auto=True)

        message_list = self.query_one("#message-list", MessageList)
        message_list.add_message(
            "system", f"[Auto] Switched to {event.new_skill} ({event.confidence:.0%} confidence)"
        )

    def _show_switch_notification(
        self,
        skill_name: str,
        confidence: float,
        is_auto: bool = True,
    ) -> None:
        """Show a notification for skill switch."""
        notification = SkillNotification(
            skill_name=skill_name,
            confidence=confidence,
            is_auto=is_auto,
        )
        self.mount(notification)

        async def dismiss():
            await asyncio.sleep(3)
            if notification.parent:
                notification.remove()

        asyncio.create_task(dismiss())

    async def handle_skill_command(self, command: str, argument: str | None) -> None:
        """Handle skill commands from chat input."""
        message_list = self.query_one("#message-list", MessageList)

        if command == "list":
            registry = SkillRegistry()
            skills = registry.list_skills()
            skill_list = "\n".join([f"  - {s}" for s in skills])
            response = f"Available skills:\n{skill_list}"
            message_list.add_message("assistant", response)

        elif command == "clear":
            self.active_skill = None
            self.auto_mode = False
            self.update_skill_indicator()
            self.refresh_skills_panel()
            if self.current_session:
                self.current_session.model = None
            message_list.add_message("assistant", "Skill deactivated. Auto-switch disabled.")

        elif command == "activate":
            skill_name = argument
            if skill_name:
                registry = SkillRegistry()
                skill = registry.get_skill(skill_name)
                if skill:
                    self.active_skill = skill_name
                    self.auto_mode = False
                    self.update_skill_indicator()
                    self.refresh_skills_panel()
                    if self.current_session:
                        self.current_session.model = skill_name
                    message_list.add_message(
                        "assistant", f"Skill '{skill_name}' activated (manual). {skill.description}"
                    )
                else:
                    message_list.add_message(
                        "assistant",
                        f"Skill '{skill_name}' not found. Use /skill list to see available skills.",
                    )

        elif command == "info":
            skill_name = argument or self.active_skill
            if skill_name:
                registry = SkillRegistry()
                skill = registry.get_skill(skill_name)
                if skill:
                    info = f"**{skill_name}**\n\n{skill.description}"
                    if skill.keywords:
                        info += f"\n\nKeywords: {', '.join(skill.keywords)}"
                    message_list.add_message("assistant", info)
                else:
                    message_list.add_message("assistant", f"Skill '{skill_name}' not found.")
            else:
                message_list.add_message(
                    "assistant", "No skill active. Use /skill <name> to activate a skill first."
                )

    async def handle_skill_panel_select(self, skill_name: str) -> None:
        """Handle skill selection from the panel."""
        self.active_skill = skill_name
        self.auto_mode = False
        self.update_skill_indicator()

        if self.current_session:
            self.current_session.model = skill_name

        registry = SkillRegistry()
        skill = registry.get_skill(skill_name)
        message_list = self.query_one("#message-list", MessageList)

        if skill:
            message_list.add_message(
                "assistant", f"Skill '{skill_name}' activated (manual). {skill.description}"
            )

    async def handle_regular_message(self, message: str) -> None:
        """Handle regular chat messages."""
        import sys
        print("", file=sys.stderr)
        print(f"[DEBUG] handle_regular_message: {message}", file=sys.stderr, flush=True)
        
        message_list = self.query_one("#message-list", MessageList)
        message_list.add_message("user", message)
        print(f"[DEBUG] User message added", file=sys.stderr, flush=True)

        detected_skill, confidence, did_switch = await self.auto_switch_manager.process_message(
            message,
            self.active_skill,
        )
        print(f"[DEBUG] Skill: {detected_skill}, conf: {confidence}, switched: {did_switch}", file=sys.stderr, flush=True)

        if did_switch and detected_skill:
            self.active_skill = detected_skill
            self.update_skill_indicator()
            self.refresh_skills_panel()

            if self.current_session:
                self.current_session.model = detected_skill

        await self.process_assistant_response(message)

    async def process_assistant_response(self, user_message: str) -> None:
        """Process user message and generate assistant response via ACP server."""
        import asyncio
        import json

        message_list = self.query_one("#message-list", MessageList)

        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", 8765)

            request = {
                "type": "request",
                "version": "1.0",
                "payload": {
                    "request_id": "req-1",
                    "method": "completion",
                    "params": {
                        "message": user_message,
                        "skill": self.active_skill,
                    },
                    "context": {},
                },
            }

            writer.write(json.dumps(request).encode())
            await writer.drain()

            response_data = await reader.read(65536)
            writer.close()
            await writer.wait_closed()

            response = json.loads(response_data.decode())
            payload = response.get("payload", {})
            status = payload.get("status")

            if status == "success":
                assistant_response = payload.get("result", {}).get("response", "No response")
            else:
                assistant_response = f"Error: {payload.get('error', 'Unknown error')}"

        except ConnectionRefusedError:
            assistant_response = "Error: Could not connect to ACP server. Make sure the server is running with 'hobo --server'"
        except Exception as e:
            assistant_response = f"Error: {str(e)}"

        mode_indicator = "[Auto] " if self.auto_mode else ""
        assistant_response = (
            f"{assistant_response}\n\n{mode_indicator}(Skill: {self.active_skill or 'none'})"
        )

        message_list.add_message("assistant", assistant_response)

        if self.current_session:
            self.session_manager.add_message(self.current_session.id, "user", user_message)
            self.session_manager.add_message(
                self.current_session.id, "assistant", assistant_response
            )

    def action_clear(self) -> None:
        """Clear the chat."""
        message_list = self.query_one("#message-list", MessageList)
        message_list.clear()

    def action_toggle_skills(self) -> None:
        """Toggle the skills panel visibility."""
        self.skills_panel_visible = not self.skills_panel_visible
        panel = self.query_one("#skills-panel", SkillPanel)
        panel.display = self.skills_panel_visible

    def action_toggle_auto_switch(self) -> None:
        """Toggle auto-switch on/off."""
        self.auto_mode = not self.auto_mode
        self.preferences.auto_switch_enabled = self.auto_mode
        self.update_skill_indicator()

        message_list = self.query_one("#message-list", MessageList)
        if self.auto_mode:
            message_list.add_message("system", "[Auto] Auto-switch enabled")
        else:
            message_list.add_message("system", "[Manual] Auto-switch disabled")

    async def action_quit(self) -> None:
        """Quit the application."""
        if self.current_session:
            self.session_manager.save_session(self.current_session)
        await self.shutdown()
