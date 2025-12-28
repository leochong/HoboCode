"""Session manager for persisting chat sessions."""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Message:
    """Chat message."""

    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Chat session."""

    id: str
    title: str
    messages: list[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model: str | None = None
    token_count: int = 0
    cost_estimate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [
                {"role": m.role, "content": m.content, "timestamp": m.timestamp, "metadata": m.metadata}
                for m in self.messages
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "model": self.model,
            "token_count": self.token_count,
            "cost_estimate": self.cost_estimate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        """Create session from dictionary."""
        messages = [
            Message(role=m["role"], content=m["content"], timestamp=m.get("timestamp", ""), metadata=m.get("metadata", {}))
            for m in data.get("messages", [])
        ]
        return cls(
            id=data["id"],
            title=data["title"],
            messages=messages,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            model=data.get("model"),
            token_count=data.get("token_count", 0),
            cost_estimate=data.get("cost_estimate", 0.0),
        )


class SessionManager:
    """Manages chat sessions with JSON persistence."""

    def __init__(self, sessions_dir: str | None = None):
        if sessions_dir is None:
            self.sessions_dir = Path.home() / ".hobo-code" / "sessions"
        else:
            self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def list_sessions(self) -> list[Session]:
        """List all sessions sorted by updated_at."""
        sessions = []
        for path in self.sessions_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                sessions.append(Session.from_dict(data))
            except Exception:
                continue
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)

    def get_session(self, session_id: str) -> Session | None:
        """Load a session by ID."""
        path = self.sessions_dir / f"{session_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return Session.from_dict(data)
        except Exception:
            return None

    def save_session(self, session: Session) -> None:
        """Save a session to disk."""
        session.updated_at = datetime.utcnow().isoformat()
        path = self.sessions_dir / f"{session.id}.json"
        path.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")

    def create_session(self, title: str = "New Session") -> Session:
        """Create a new session."""
        session = Session(
            id=str(uuid.uuid4()),
            title=title,
        )
        self.save_session(session)
        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID."""
        path = self.sessions_dir / f"{session_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Session | None:
        """Add a message to a session."""
        session = self.get_session(session_id)
        if session is None:
            return None
        session.messages.append(Message(role=role, content=content, metadata=metadata or {}))
        self.save_session(session)
        return session

    def update_stats(self, session_id: str, token_count: int, cost_estimate: float) -> Session | None:
        """Update session statistics."""
        session = self.get_session(session_id)
        if session is None:
            return None
        session.token_count = token_count
        session.cost_estimate = cost_estimate
        self.save_session(session)
        return session

    def get_stats(self) -> dict[str, Any]:
        """Get aggregate statistics across all sessions."""
        sessions = self.list_sessions()
        total_tokens = sum(s.token_count for s in sessions)
        total_cost = sum(s.cost_estimate for s in sessions)
        total_messages = sum(len(s.messages) for s in sessions)
        return {
            "total_sessions": len(sessions),
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "total_cost_estimate": total_cost,
        }
