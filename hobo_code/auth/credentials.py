"""Credential store with AES encryption for API keys."""

import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Any


class CredentialStore:
    """Secure credential storage with AES encryption."""

    def __init__(self):
        self.config_dir = Path.home() / ".hobo-code"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.config_dir / "credentials.json.enc"
        self.github_token_file = self.config_dir / "github_token"
        self._key_file = self.config_dir / ".encryption_key"
        self._fernet = self._get_fernet()

    def _get_fernet(self) -> Fernet:
        """Get or create encryption key."""
        if self._key_file.exists():
            key = self._key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self._key_file.write_bytes(key)
        return Fernet(key)

    def _load_credentials(self) -> dict[str, str]:
        """Load and decrypt credentials."""
        if not self.credentials_file.exists():
            return {}
        try:
            encrypted = self.credentials_file.read_bytes()
            decrypted = self._fernet.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception:
            return {}

    def _save_credentials(self, credentials: dict[str, str]) -> None:
        """Encrypt and save credentials."""
        data = json.dumps(credentials).encode()
        encrypted = self._fernet.encrypt(data)
        self.credentials_file.write_bytes(encrypted)

    def save_key(self, provider: str, key: str) -> bool:
        """Save an API key for a provider."""
        if not provider or not key:
            return False
        credentials = self._load_credentials()
        credentials[provider] = key
        self._save_credentials(credentials)
        return True

    def get_key(self, provider: str) -> str | None:
        """Get an API key for a provider."""
        credentials = self._load_credentials()
        return credentials.get(provider)

    def delete_key(self, provider: str) -> bool:
        """Delete an API key for a provider."""
        credentials = self._load_credentials()
        if provider in credentials:
            del credentials[provider]
            self._save_credentials(credentials)
            return True
        return False

    def list_providers(self) -> list[str]:
        """List all configured providers."""
        credentials = self._load_credentials()
        return sorted(credentials.keys())

    def save_github_token(self, token: str) -> bool:
        """Save GitHub token."""
        if not token:
            return False
        self.github_token_file.write_text(token, encoding="utf-8")
        return True

    def get_github_token(self) -> str | None:
        """Get GitHub token."""
        if self.github_token_file.exists():
            return self.github_token_file.read_text(encoding="utf-8").strip()
        return None

    def delete_github_token(self) -> bool:
        """Delete GitHub token."""
        if self.github_token_file.exists():
            self.github_token_file.unlink()
            return True
        return False

    def has_credentials(self) -> bool:
        """Check if any credentials are stored."""
        return bool(self._load_credentials())

    def clear_all(self) -> None:
        """Clear all credentials."""
        if self.credentials_file.exists():
            self.credentials_file.unlink()
        self.delete_github_token()
