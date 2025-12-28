"""Tests for ACP protocol implementation."""

import pytest
from hobo_code.server.acp import (
    ACPServer,
    ACPMessage,
    ACPRequest,
    ACPResponse,
    MessageType,
)


class TestACPMessage:
    """Tests for ACPMessage class."""

    def test_create_handshake_message(self):
        """Test creating a handshake message."""
        message = ACPMessage(type=MessageType.HANDSHAKE)
        assert message.type == MessageType.HANDSHAKE
        assert message.version == "1.0"
        assert message.message_id is not None
        assert message.payload == {}

    def test_message_to_dict(self):
        """Test message serialization to dictionary."""
        message = ACPMessage(
            type=MessageType.REQUEST,
            payload={"method": "test", "params": {"key": "value"}},
        )
        data = message.to_dict()
        assert data["type"] == "request"
        assert data["version"] == "1.0"
        assert data["payload"]["method"] == "test"

    def test_message_from_dict(self):
        """Test message deserialization from dictionary."""
        data = {
            "type": "response",
            "version": "1.0",
            "message_id": "test-id",
            "timestamp": "2024-01-01T00:00:00",
            "payload": {"status": "success", "result": "ok"},
        }
        message = ACPMessage.from_dict(data)
        assert message.type == MessageType.RESPONSE
        assert message.message_id == "test-id"
        assert message.payload["status"] == "success"

    def test_message_json_serialization(self):
        """Test JSON serialization roundtrip."""
        original = ACPMessage(
            type=MessageType.REQUEST,
            payload={"test": "value"},
        )
        json_str = original.to_json()
        restored = ACPMessage.from_json(json_str)
        assert restored.type == original.type
        assert restored.payload == original.payload


class TestACPRequest:
    """Tests for ACPRequest class."""

    def test_request_creation(self):
        """Test creating an ACP request."""
        request = ACPRequest(
            request_id="req-123",
            method="ping",
            params={"key": "value"},
        )
        assert request.request_id == "req-123"
        assert request.method == "ping"
        assert request.params["key"] == "value"

    def test_request_to_message(self):
        """Test converting request to message."""
        request = ACPRequest(
            request_id="req-456",
            method="echo",
            params={"message": "hello"},
        )
        message = request.to_message()
        assert message.type == MessageType.REQUEST
        assert message.payload["request_id"] == "req-456"
        assert message.payload["method"] == "echo"

    def test_request_from_message(self):
        """Test creating request from message."""
        message = ACPMessage(
            type=MessageType.REQUEST,
            payload={
                "request_id": "req-789",
                "method": "test",
                "params": {"data": 123},
            },
        )
        request = ACPRequest.from_message(message)
        assert request.request_id == "req-789"
        assert request.method == "test"
        assert request.params["data"] == 123


class TestACPResponse:
    """Tests for ACPResponse class."""

    def test_success_response(self):
        """Test creating a success response."""
        response = ACPResponse.success("req-123", {"result": "value"})
        assert response.request_id == "req-123"
        assert response.status == "success"
        assert response.result == {"result": "value"}
        assert response.error is None
        assert response.is_success is True

    def test_error_response(self):
        """Test creating an error response."""
        response = ACPResponse.err("req-123", "Something went wrong")
        assert response.request_id == "req-123"
        assert response.status == "error"
        assert response.result is None
        assert response.error == "Something went wrong"
        assert response.is_success is False

    def test_response_to_message(self):
        """Test converting response to message."""
        response = ACPResponse.success("req-123", {"data": "test"})
        message = response.to_message()
        assert message.type == MessageType.RESPONSE
        assert message.payload["status"] == "success"

    def test_response_from_message(self):
        """Test creating response from message."""
        message = ACPMessage(
            type=MessageType.RESPONSE,
            payload={
                "request_id": "req-123",
                "status": "success",
                "result": {"key": "value"},
            },
        )
        response = ACPResponse.from_message(message)
        assert response.request_id == "req-123"
        assert response.status == "success"


class TestACPServer:
    """Tests for ACPServer class."""

    def test_server_initialization(self):
        """Test server initialization with default values."""
        server = ACPServer()
        assert server.host == "127.0.0.1"
        assert server.port == 8765
        assert server.sessions == {}

    def test_server_custom_address(self):
        """Test server initialization with custom address."""
        server = ACPServer(host="0.0.0.0", port=9000)
        assert server.host == "0.0.0.0"
        assert server.port == 9000

    def test_session_stats_empty(self):
        """Test getting stats when no sessions exist."""
        server = ACPServer()
        stats = server.get_session_stats()
        assert stats["active_sessions"] == 0
        assert stats["sessions"] == []

    @pytest.mark.asyncio
    async def test_server_start_and_stop(self):
        """Test starting and stopping the server."""
        server = ACPServer(host="127.0.0.1", port=18765)
        await server.start()
        assert server._server is not None
        assert server.socket_address[1] == 18765
        await server.stop()
        assert server._server is None

    @pytest.mark.asyncio
    async def test_handle_ping_request(self):
        """Test handling ping request."""
        server = ACPServer()
        request = ACPRequest(
            request_id="test-req",
            method="ping",
            params={},
        )
        response = await server._handle_ping(request.request_id, {}, "test-session")
        assert response.is_success
        assert response.result["pong"] is True
        assert response.result["session_id"] == "test-session"

    @pytest.mark.asyncio
    async def test_handle_echo_request(self):
        """Test handling echo request."""
        server = ACPServer()
        request = ACPRequest(
            request_id="test-req",
            method="echo",
            params={"message": "Hello, ACP!"},
        )
        response = await server._handle_echo(request.request_id, {"message": "Hello, ACP!"}, "session-1")
        assert response.is_success
        assert response.result["echo"] == "Hello, ACP!"

    @pytest.mark.asyncio
    async def test_handle_unknown_method(self):
        """Test handling unknown method."""
        server = ACPServer()
        response = await server._handle_request(
            ACPRequest(request_id="test", method="unknown", params={}),
            "session-1",
        )
        assert response.is_success is False
        assert "Unknown method" in response.error

    @pytest.mark.asyncio
    async def test_process_handshake_message(self):
        """Test processing handshake message."""
        server = ACPServer()
        message = ACPMessage(type=MessageType.HANDSHAKE)
        response = await server._process_message(message, "test-session")
        assert response.request_id == ""
        assert response.status == "connected"
        assert response.result["session_id"] == "test-session"
