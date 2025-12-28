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

    def get_session_stats(self) -> dict[str, Any]:
        """Get server session statistics."""
        return {
            "active_sessions": len(self.sessions),
            "sessions": list(self.sessions.values()),
        }
