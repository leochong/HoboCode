"""Tests for authentication module."""

import pytest
import tempfile
from pathlib import Path

from hobo_code.auth.credentials import CredentialStore


class TestCredentialStore:
    """Tests for CredentialStore class."""

    def test_save_and_get_key(self, tmp_path):
        """Test saving and retrieving a key."""
        store = CredentialStore()
        store.credentials_file = tmp_path / "credentials.json.enc"
        store._key_file = tmp_path / ".encryption_key"
        store._fernet = store._get_fernet()

        store.save_key("openai", "sk-test123")
        retrieved = store.get_key("openai")

        assert retrieved == "sk-test123"

    def test_get_nonexistent_key(self, tmp_path):
        """Test getting a nonexistent key returns None."""
        store = CredentialStore()
        store.credentials_file = tmp_path / "credentials.json.enc"
        store._key_file = tmp_path / ".encryption_key"
        store._fernet = store._get_fernet()

        result = store.get_key("nonexistent")
        assert result is None

    def test_delete_key(self, tmp_path):
        """Test deleting a key."""
        store = CredentialStore()
        store.credentials_file = tmp_path / "credentials.json.enc"
        store._key_file = tmp_path / ".encryption_key"
        store._fernet = store._get_fernet()

        store.save_key("anthropic", "sk-ant123")
        assert store.delete_key("anthropic") is True
        assert store.get_key("anthropic") is None

    def test_delete_nonexistent_key(self, tmp_path):
        """Test deleting a nonexistent key returns False."""
        store = CredentialStore()
        store.credentials_file = tmp_path / "credentials.json.enc"
        store._key_file = tmp_path / ".encryption_key"
        store._fernet = store._get_fernet()

        result = store.delete_key("nonexistent")
        assert result is False

    def test_list_providers(self, tmp_path):
        """Test listing providers."""
        store = CredentialStore()
        store.credentials_file = tmp_path / "credentials.json.enc"
        store._key_file = tmp_path / ".encryption_key"
        store._fernet = store._get_fernet()

        store.save_key("openai", "sk-oai")
        store.save_key("anthropic", "sk-ant")

        providers = store.list_providers()
        assert "openai" in providers
        assert "anthropic" in providers

    def test_save_github_token(self, tmp_path):
        """Test saving GitHub token."""
        store = CredentialStore()
        store.github_token_file = tmp_path / "github_token"

        store.save_github_token("ghp_token123")
        token = store.get_github_token()

        assert token == "ghp_token123"

    def test_delete_github_token(self, tmp_path):
        """Test deleting GitHub token."""
        store = CredentialStore()
        store.github_token_file = tmp_path / "github_token"
        store.save_github_token("ghp_token123")

        assert store.delete_github_token() is True
        assert store.get_github_token() is None

    def test_clear_all(self, tmp_path):
        """Test clearing all credentials."""
        store = CredentialStore()
        store.credentials_file = tmp_path / "credentials.json.enc"
        store.github_token_file = tmp_path / "github_token"
        store._key_file = tmp_path / ".encryption_key"
        store._fernet = store._get_fernet()

        store.save_key("openai", "sk-test")
        store.save_github_token("ghp_token")

        store.clear_all()

        assert store.get_key("openai") is None
        assert store.get_github_token() is None

    def test_invalid_key_does_not_save(self, tmp_path):
        """Test that empty key is not saved."""
        store = CredentialStore()
        store.credentials_file = tmp_path / "credentials.json.enc"
        store._key_file = tmp_path / ".encryption_key"
        store._fernet = store._get_fernet()

        result = store.save_key("", "sk-test")
        assert result is False

        result = store.save_key("openai", "")
        assert result is False
