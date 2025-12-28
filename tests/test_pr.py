"""Tests for PR functionality."""

import pytest
from unittest.mock import patch, MagicMock

from hobo_code.github.pr import PRManager


class TestPRManagerUnit:
    """Unit tests for PRManager."""

    @patch("subprocess.run")
    def test_list_prs_empty(self, mock_run):
        """Test listing PRs when none exist."""
        mock_run.return_value = MagicMock(returncode=1, stdout="[]")

        manager = PRManager()
        prs = manager.list_prs()

        assert prs == []

    @patch("subprocess.run")
    def test_get_pr_diff(self, mock_run):
        """Test getting PR diff."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="diff --git a/file.py b/file.py\n+print('hello')",
        )

        manager = PRManager()
        diff = manager.get_pr_diff(1)

        assert "diff --git" in diff
        assert "print('hello')" in diff

    @patch("subprocess.run")
    def test_merge_pr_success(self, mock_run):
        """Test successful PR merge."""
        mock_run.return_value = MagicMock(returncode=0)

        manager = PRManager()
        result = manager.merge_pr(1, "merge")

        assert result is True

    @patch("subprocess.run")
    def test_close_pr_success(self, mock_run):
        """Test successful PR close."""
        mock_run.return_value = MagicMock(returncode=0)

        manager = PRManager()
        result = manager.close_pr(1)

        assert result is True

    @patch("subprocess.run")
    def test_create_pr_success(self, mock_run):
        """Test successful PR creation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="https://github.com/user/repo/pull/1")

        manager = PRManager()
        result = manager.create_pr("Test PR", "Description", "main", "feature-branch")

        assert result is not None
        assert "url" in result

    @patch("hobo_code.github.pr.PRManager._run_gh")
    def test_get_pr_files(self, mock_run_gh):
        """Test getting PR files."""
        mock_run_gh.return_value = MagicMock(
            returncode=0,
            stdout='{"number": 1, "title": "Test", "body": "", "author": {"login": "user"}, "state": "OPEN", "url": "https://github.com/user/repo/pull/1", "files": [{"name": "file1.py"}, {"name": "file2.py"}]}',
        )

        manager = PRManager()
        files = manager.get_pr_files(1)

        assert len(files) == 2
        assert "file1.py" in files

    @patch("subprocess.run")
    def test_merge_pr_squash(self, mock_run):
        """Test PR merge with squash."""
        mock_run.return_value = MagicMock(returncode=0)

        manager = PRManager()
        result = manager.merge_pr(1, "squash")

        assert result is True

    @patch("subprocess.run")
    def test_merge_pr_rebase(self, mock_run):
        """Test PR merge with rebase."""
        mock_run.return_value = MagicMock(returncode=0)

        manager = PRManager()
        result = manager.merge_pr(1, "rebase")

        assert result is True


class TestPRManagerIntegration:
    """Integration tests for PRManager."""

    def test_pr_manager_init(self):
        """Test PRManager initialization."""
        manager = PRManager(token="test-token", repo_path="/tmp/repo")
        assert manager.token == "test-token"
        assert manager.repo_path == "/tmp/repo"

    def test_pr_manager_default_init(self):
        """Test PRManager with default values."""
        manager = PRManager()
        assert manager.token is None
        assert manager.repo_path is None

    @patch("subprocess.run")
    def test_list_prs_with_state(self, mock_run):
        """Test listing PRs with different states."""
        mock_run.return_value = MagicMock(returncode=0, stdout="[]")

        manager = PRManager()
        manager.list_prs("closed")
        manager.list_prs("all")

        assert mock_run.call_count == 2
