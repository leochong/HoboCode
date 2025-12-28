"""Tests for session management."""

import pytest
import json
import tempfile
from pathlib import Path

from hobo_code.session.manager import SessionManager, Session, Message


class TestSessionManager:
    """Tests for SessionManager class."""

    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates the sessions directory."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        assert (tmp_path / "sessions").exists()

    def test_create_session(self, tmp_path):
        """Test creating a new session."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        session = manager.create_session("Test Session")

        assert session.id is not None
        assert session.title == "Test Session"
        assert session.messages == []
        assert (tmp_path / "sessions" / f"{session.id}.json").exists()

    def test_list_sessions(self, tmp_path):
        """Test listing sessions."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        s1 = manager.create_session("First")
        s2 = manager.create_session("Second")

        sessions = manager.list_sessions()
        assert len(sessions) == 2

    def test_get_session(self, tmp_path):
        """Test getting a session by ID."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        created = manager.create_session("Test")

        retrieved = manager.get_session(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test"

    def test_get_nonexistent_session(self, tmp_path):
        """Test getting a nonexistent session returns None."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        result = manager.get_session("nonexistent-id")
        assert result is None

    def test_delete_session(self, tmp_path):
        """Test deleting a session."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        session = manager.create_session("To Delete")

        assert manager.delete_session(session.id) is True
        assert manager.get_session(session.id) is None

    def test_delete_nonexistent_session(self, tmp_path):
        """Test deleting a nonexistent session returns False."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        result = manager.delete_session("nonexistent")
        assert result is False

    def test_add_message(self, tmp_path):
        """Test adding a message to a session."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        session = manager.create_session("Test")
        updated = manager.add_message(session.id, "user", "Hello!")

        assert len(updated.messages) == 1
        assert updated.messages[0].role == "user"
        assert updated.messages[0].content == "Hello!"

    def test_add_multiple_messages(self, tmp_path):
        """Test adding multiple messages."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        session = manager.create_session("Test")
        manager.add_message(session.id, "user", "Hello")
        manager.add_message(session.id, "assistant", "Hi there!")
        manager.add_message(session.id, "user", "How are you?")

        retrieved = manager.get_session(session.id)
        assert len(retrieved.messages) == 3

    def test_update_stats(self, tmp_path):
        """Test updating session statistics."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        session = manager.create_session("Test")
        manager.update_stats(session.id, token_count=100, cost_estimate=0.05)

        updated = manager.get_session(session.id)
        assert updated.token_count == 100
        assert updated.cost_estimate == 0.05

    def test_get_stats(self, tmp_path):
        """Test getting aggregate statistics."""
        manager = SessionManager(sessions_dir=str(tmp_path / "sessions"))
        s1 = manager.create_session("First")
        s2 = manager.create_session("Second")
        manager.add_message(s1.id, "user", "msg1")
        manager.add_message(s1.id, "assistant", "resp1")
        manager.update_stats(s1.id, token_count=50, cost_estimate=0.02)

        stats = manager.get_stats()
        assert stats["total_sessions"] == 2
        assert stats["total_messages"] == 2
        assert stats["total_tokens"] == 50
        assert stats["total_cost_estimate"] == 0.02


class TestSession:
    """Tests for Session dataclass."""

    def test_session_to_dict(self):
        """Test session serialization."""
        session = Session(id="test-id", title="Test", messages=[Message(role="user", content="Hi")])
        data = session.to_dict()

        assert data["id"] == "test-id"
        assert data["title"] == "Test"
        assert len(data["messages"]) == 1

    def test_session_from_dict(self):
        """Test session deserialization."""
        data = {
            "id": "test-id",
            "title": "Test",
            "messages": [{"role": "user", "content": "Hi", "timestamp": "2024-01-01", "metadata": {}}],
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01",
            "model": "gpt-4",
            "token_count": 10,
            "cost_estimate": 0.01,
        }
        session = Session.from_dict(data)

        assert session.id == "test-id"
        assert session.model == "gpt-4"
        assert len(session.messages) == 1
