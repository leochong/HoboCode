"""ACP Protocol implementation for agent-client communication."""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageType(str, Enum):
    """ACP message types."""

    HANDSHAKE = "handshake"
    REQUEST = "request"
    RESPONSE = "response"
    HEARTBEAT = "heartbeat"
    DISCONNECT = "disconnect"


@dataclass
class ACPMessage:
    """Base ACP message structure."""

    type: MessageType
    version: str = "1.0"
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "type": self.type.value,
            "version": self.version,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ACPMessage":
        """Create message from dictionary."""
        return cls(
            type=MessageType(data["type"]),
            version=data.get("version", "1.0"),
            message_id=data.get("message_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            payload=data.get("payload", {}),
        )

    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> "ACPMessage":
        """Deserialize message from JSON string."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class ACPRequest:
    """ACP request message."""

    request_id: str
    method: str
    params: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)

    def to_message(self) -> ACPMessage:
        """Convert to ACP message."""
        return ACPMessage(
            type=MessageType.REQUEST,
            payload={
                "request_id": self.request_id,
                "method": self.method,
                "params": self.params,
                "context": self.context,
            },
        )

    @classmethod
    def from_message(cls, message: ACPMessage) -> "ACPRequest":
        """Create from ACP message."""
        payload = message.payload
        return cls(
            request_id=payload.get("request_id", str(uuid.uuid4())),
            method=payload["method"],
            params=payload.get("params", {}),
            context=payload.get("context", {}),
        )


@dataclass
class ACPResponse:
    """ACP response message."""

    request_id: str
    status: str
    result: Any | None = None
    error: str | None = None

    @property
    def is_success(self) -> bool:
        """Check if response is successful."""
        return self.status == "success"

    def to_message(self) -> ACPMessage:
        """Convert to ACP message."""
        return ACPMessage(
            type=MessageType.RESPONSE,
            payload={
                "request_id": self.request_id,
                "status": self.status,
                "result": self.result,
                "error": self.error,
            },
        )

    @classmethod
    def from_message(cls, message: ACPMessage) -> "ACPResponse":
        """Create from ACP message."""
        payload = message.payload
        return cls(
            request_id=payload.get("request_id", ""),
            status=payload.get("status", "error"),
            result=payload.get("result"),
            error=payload.get("error"),
        )

    @staticmethod
    def success(request_id: str, result: Any | None = None) -> "ACPResponse":
        """Create success response."""
        return ACPResponse(request_id=request_id, status="success", result=result)

    @staticmethod
    def err(request_id: str, err_msg: str) -> "ACPResponse":
        """Create error response."""
        return ACPResponse(request_id=request_id, status="error", error=err_msg)


class ACPServer:
    """ACP server for handling client connections and routing messages."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.sessions: dict[str, dict[str, Any]] = {}
        self._server: asyncio.Server | None = None

    async def start(self) -> None:
        """Start the ACP server."""
        self._server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port,
        )
        addr = self.socket_address
        print(f"ACP server started on {addr[0]}:{addr[1]}")

    @property
    def socket_address(self) -> tuple[str, int]:
        """Get server socket address."""
        if self._server:
            sock = self._server.sockets[0]
            return sock.getsockname()
        return (self.host, self.port)

    async def stop(self) -> None:
        """Stop the ACP server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
            print("ACP server stopped")

    async def _handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        client_id = str(uuid.uuid4())[:8]
        session_id = str(uuid.uuid4())
        addr = writer.get_extra_info("peername")
        print(f"Client {client_id} connected from {addr}")
        self.sessions[session_id] = {
            "client_id": client_id,
            "addr": addr,
            "connected_at": datetime.utcnow().isoformat(),
        }

        try:
            while True:
                data = await reader.read(65536)
                if not data:
                    break

                message = ACPMessage.from_json(data.decode())
                response = await self._process_message(message, session_id)

                response_data = response.to_json().encode()
                writer.write(response_data)
                await writer.drain()
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            print(f"Client {client_id} disconnected")
            if session_id in self.sessions:
                del self.sessions[session_id]
            writer.close()
            await writer.wait_closed()

    async def _process_message(
        self,
        message: ACPMessage,
        session_id: str,
    ) -> ACPResponse:
        request_id = ""
        try:
            if message.type == MessageType.HANDSHAKE:
                return ACPResponse(
                    request_id="",
                    status="connected",
                    result={"session_id": session_id},
                )

            if message.type == MessageType.REQUEST:
                request = ACPRequest.from_message(message)
                request_id = request.request_id
                return await self._handle_request(request, session_id)

            if message.type == MessageType.DISCONNECT:
                return ACPResponse.success(request_id)

            return ACPResponse.err(request_id, f"Unknown message type: {message.type}")
        except Exception as e:
            return ACPResponse.err(request_id, str(e))

    async def _handle_request(
        self,
        request: ACPRequest,
        session_id: str,
    ) -> ACPResponse:
        request_id = request.request_id
        method = request.method
        params = request.params

        handlers = {
            "ping": self._handle_ping,
            "echo": self._handle_echo,
            "completion": self._handle_completion,
            "skills.list": self._handle_skills_list,
            "skills.get": self._handle_skills_get,
            "skills.search": self._handle_skills_search,
            "skills.recommend": self._handle_skills_recommend,
            "skills.add": self._handle_skills_add,
            "session.create": self._handle_session_create,
            "session.send": self._handle_session_send,
            "session.history": self._handle_session_history,
        }

        handler = handlers.get(method)
        if handler:
            return await handler(request_id, params, session_id)

        return ACPResponse.err(request_id, f"Unknown method: {method}")

    async def _handle_ping(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        return ACPResponse.success(request_id, {"pong": True, "session_id": session_id})

    async def _handle_echo(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        return ACPResponse.success(request_id, {"echo": params.get("message", "")})

    async def _handle_completion(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.auth.credentials import CredentialStore
        from hobo_code.skills.registry import SkillRegistry
        from hobo_code.models.provider import ModelProvider

        message = params.get("message")
        skill_name = params.get("skill")

        if not message:
            return ACPResponse.err(request_id, "message is required")

        registry = SkillRegistry()
        skill = registry.get_skill(skill_name) if skill_name else None
        system_prompt = skill.system_prompt if skill else "You are a helpful coding assistant."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        store = CredentialStore()
        provider = store.get_provider()
        api_key = store.get_key(provider) if provider else None

        if not provider or not api_key:
            return ACPResponse.err(request_id, "No API key configured. Run 'hobo auth' first.")

        model = f"{provider}/default"
        if provider == "openrouter":
            model = "openrouter/meta-llama/llama-3-8b-instruct"

        mp = ModelProvider()
        result = mp.get_completion(model, messages, api_key)

        if "error" in result:
            return ACPResponse.err(request_id, result["error"])

        content = result["choices"][0]["message"]["content"]
        return ACPResponse.success(request_id, {"response": content})

    async def _handle_skills_list(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.skills.registry import SkillRegistry

        registry = SkillRegistry()
        skills = registry.list_skills()
        skill_list = []
        for s in skills:
            skill = registry.get_skill(s)
            if skill:
                skill_list.append(
                    {
                        "name": skill.name,
                        "description": skill.description,
                        "keywords": skill.keywords,
                    }
                )
        return ACPResponse.success(request_id, {"skills": skill_list})

    async def _handle_skills_get(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.skills.registry import SkillRegistry

        skill_name = params.get("name")
        if not skill_name:
            return ACPResponse.err(request_id, "Skill name is required")

        registry = SkillRegistry()
        skill = registry.get_skill(skill_name)

        if not skill:
            return ACPResponse.err(request_id, f"Skill '{skill_name}' not found")

        return ACPResponse.success(request_id, {"skill": skill.to_dict()})

    async def _handle_skills_search(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.skills.discovery import SkillDiscovery

        query = params.get("query", "")
        repo = params.get("repo", "leochong/HoboCode")

        discovery = SkillDiscovery()
        results = discovery.search_skills(query, repo)

        return ACPResponse.success(request_id, {"results": results})

    async def _handle_skills_recommend(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.skills.registry import SkillRegistry

        task = params.get("task", "")
        if not task:
            return ACPResponse.err(request_id, "Task description is required")

        registry = SkillRegistry()
        recommendations = registry.get_recommended_skills(task)

        result = [{"name": s.name, "score": score} for s, score in recommendations[:5]]
        return ACPResponse.success(request_id, {"recommendations": result})

    async def _handle_skills_add(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.skills.discovery import SkillDiscovery
        from hobo_code.skills.registry import SkillRegistry
        from pathlib import Path

        skill_name = params.get("name")
        if not skill_name:
            return ACPResponse.err(request_id, "Skill name is required")

        repo = params.get("repo", "leochong/HoboCode")
        project_dir = params.get("project_dir", str(Path.cwd()))

        discovery = SkillDiscovery()
        skills_dir = Path(project_dir) / "skills"

        skill_path = discovery.find_skill(skill_name, skills_dir, repo)

        if skill_path and skill_path.exists():
            registry = SkillRegistry(project_dir=project_dir)
            if registry.add_skill(skill_path):
                return ACPResponse.success(request_id, {"message": f"Skill '{skill_name}' added"})
            return ACPResponse.err(request_id, f"Failed to add skill '{skill_name}'")

        return ACPResponse.err(request_id, f"Skill '{skill_name}' not found in {repo}")

    async def _handle_session_create(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.session.manager import SessionManager
        from hobo_code.skills.registry import SkillRegistry

        title = params.get("title", "New Chat")
        skill = params.get("skill")

        registry = SkillRegistry()
        system_prompt = registry.get_system_prompt(skill) if skill else None

        manager = SessionManager()
        session = manager.create_session(
            title=title,
            system_prompt=system_prompt or "",
            model=skill or None,
        )

        return ACPResponse.success(request_id, {"session_id": session.id})

    async def _handle_session_send(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.session.manager import SessionManager
        from hobo_code.skills.registry import SkillRegistry
        from hobo_code.auth.credentials import CredentialStore
        from hobo_code.models.provider import ModelProvider

        session_id_param = params.get("session_id")
        message = params.get("message")

        if not session_id_param or not message:
            return ACPResponse.err(request_id, "session_id and message are required")

        manager = SessionManager()
        session = manager.get_session(session_id_param)

        if not session:
            return ACPResponse.err(request_id, "Session not found")

        registry = SkillRegistry()
        skill = registry.get_skill(session.model) if session.model else None
        system_prompt = skill.system_prompt if skill else "You are a helpful coding assistant."

        manager.add_message(session_id_param, "user", message)
        manager.add_message(session_id_param, "assistant", assistant_content)

        return ACPResponse.success(request_id, {"response": assistant_content})

    async def _handle_session_history(
        self,
        request_id: str,
        params: dict[str, Any],
        session_id: str,
    ) -> ACPResponse:
        from hobo_code.session.manager import SessionManager

        session_id_param = params.get("session_id")
        if not session_id_param:
            return ACPResponse.err(request_id, "session_id is required")

        manager = SessionManager()
        session = manager.get_session(session_id_param)

        if not session:
            return ACPResponse.err(request_id, "Session not found")

        return ACPResponse.success(
            request_id,
            {
                "session": {
                    "id": session.id,
                    "title": session.title,
                    "model": session.model,
                    "messages": len(session.messages),
                }
            },
        )

    def get_session_stats(self) -> dict[str, Any]:
        """Get server session statistics."""
        return {
            "active_sessions": len(self.sessions),
            "sessions": list(self.sessions.values()),
        }
