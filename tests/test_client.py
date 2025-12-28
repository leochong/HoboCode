"""Tests for client TUI components."""

import pytest
from textual.app import App

from hobo_code.client.components import MessageBubble, MessageList, ChatInput


class TestMessageBubble:
    """Tests for MessageBubble component."""

    def test_user_bubble_creation(self):
        """Test creating a user message bubble."""
        bubble = MessageBubble("Hello", role="user")
        assert bubble.content == "Hello"
        assert bubble.role == "user"

    def test_assistant_bubble_creation(self):
        """Test creating an assistant message bubble."""
        bubble = MessageBubble("I can help", role="assistant")
        assert bubble.content == "I can help"
        assert bubble.role == "assistant"


class TestMessageList:
    """Tests for MessageList component."""

    def test_empty_message_list(self):
        """Test initializing an empty message list."""
        message_list = MessageList()
        assert message_list.messages == []

    def test_add_message(self):
        """Test adding a message to the list."""
        message_list = MessageList()
        message_list.add_message("user", "Hello")
        assert len(message_list.messages) == 1
        assert message_list.messages[0] == ("user", "Hello")

    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        message_list = MessageList()
        message_list.add_message("user", "Hello")
        message_list.add_message("assistant", "Hi!")
        message_list.add_message("user", "How are you?")

        assert len(message_list.messages) == 3

    def test_clear_messages(self):
        """Test clearing all messages."""
        message_list = MessageList()
        message_list.add_message("user", "Hello")
        message_list.add_message("assistant", "Hi!")
        message_list.clear()

        assert len(message_list.messages) == 0


class TestChatInput:
    """Tests for ChatInput component."""

    def test_input_creation(self):
        """Test creating a chat input."""
        chat_input = ChatInput(placeholder="Type here...")
        assert chat_input.placeholder == "Type here..."

    def test_input_creation_default_placeholder(self):
        """Test default placeholder."""
        chat_input = ChatInput()
        assert chat_input.placeholder == "Type a message..."
