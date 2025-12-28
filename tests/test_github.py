"""Tests for GitHub module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from hobo_code.github.client import GitHubClient
from hobo_code.github.pr import PRManager
from hobo_code.github.issues import IssueManager
from hobo_code.github.agent import GitHubAgent


class TestGitHubClient:
    """Tests for GitHubClient class."""

    @patch("subprocess.run")
    def test_get_repo_info(self, mock_run):
        """Test getting repository info."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="https://github.com/user/repo.git"),
            MagicMock(returncode=0, stdout="main"),
            MagicMock(returncode=0, stdout="abc123"),
        ]

        client = GitHubClient(repo_path="/tmp")
        info = client.get_repo_info()

        assert info["url"] == "https://github.com/user/repo.git"
        assert info["branch"] == "main"
        assert info["commit"] == "abc123"

    @patch("subprocess.run")
    def test_list_branches(self, mock_run):
        """Test listing branches."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="  main\n* develop\n  feature/test",
        )

        client = GitHubClient(repo_path="/tmp")
        branches = client.list_branches()

        assert "main" in branches
        assert "develop" in branches
        assert "feature/test" in branches

    @patch("subprocess.run")
    def test_current_branch(self, mock_run):
        """Test getting current branch."""
        mock_run.return_value = MagicMock(returncode=0, stdout="feature/new\n")

        client = GitHubClient(repo_path="/tmp")
        branch = client.current_branch()

        assert branch == "feature/new"

    @patch("subprocess.run")
    def test_status_clean(self, mock_run):
        """Test clean repository status."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        client = GitHubClient(repo_path="/tmp")
        status = client.status()

        assert status["clean"] is True

    @patch("subprocess.run")
    def test_status_dirty(self, mock_run):
        """Test dirty repository status."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=" M file1.py\n?? file2.py",
        )

        client = GitHubClient(repo_path="/tmp")
        status = client.status()

        assert status["clean"] is False
        assert len(status["changes"]) == 2

    @patch("subprocess.run")
    def test_list_files(self, mock_run):
        """Test listing files."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="file1.py\nfile2.py\ndir/file3.py",
        )

        client = GitHubClient(repo_path="/tmp")
        files = client.list_files(".")

        assert len(files) == 3
        assert "file1.py" in files


class TestPRManager:
    """Tests for PRManager class."""

    @patch("subprocess.run")
    def test_list_prs(self, mock_run):
        """Test listing PRs."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"number": 1, "title": "Test PR", "author": {"login": "user"}, "state": "OPEN", "url": "https://github.com/user/repo/pull/1"}]',
        )

        manager = PRManager()
        prs = manager.list_prs()

        assert len(prs) == 1
        assert prs[0]["number"] == 1
        assert prs[0]["title"] == "Test PR"

    @patch("subprocess.run")
    def test_get_pr(self, mock_run):
        """Test getting a specific PR."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"number": 1, "title": "Test PR", "body": "Description", "author": {"login": "user"}, "state": "OPEN", "url": "https://github.com/user/repo/pull/1", "files": [{"name": "file1.py"}]}',
        )

        manager = PRManager()
        pr = manager.get_pr(1)

        assert pr is not None
        assert pr["number"] == 1
        assert pr["title"] == "Test PR"

    @patch("subprocess.run")
    def test_get_pr_not_found(self, mock_run):
        """Test getting non-existent PR."""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Not Found")

        manager = PRManager()
        pr = manager.get_pr(999)

        assert pr is None

    @patch("subprocess.run")
    def test_checkout_pr(self, mock_run):
        """Test checking out a PR."""
        mock_run.return_value = MagicMock(returncode=0)

        manager = PRManager()
        result = manager.checkout_pr(1)

        assert result is True


class TestIssueManager:
    """Tests for IssueManager class."""

    @patch("subprocess.run")
    def test_list_issues(self, mock_run):
        """Test listing issues."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='[{"number": 1, "title": "Bug Report", "author": {"login": "user"}, "state": "OPEN", "url": "https://github.com/user/repo/issues/1", "labels": []}]',
        )

        manager = IssueManager()
        issues = manager.list_issues()

        assert len(issues) == 1
        assert issues[0]["number"] == 1

    @patch("subprocess.run")
    def test_create_issue(self, mock_run):
        """Test creating an issue."""
        mock_run.return_value = MagicMock(returncode=0, stdout="https://github.com/user/repo/issues/1")

        manager = IssueManager()
        result = manager.create_issue("Test Issue", "This is a test")

        assert result is not None
        assert "url" in result

    @patch("subprocess.run")
    def test_close_issue(self, mock_run):
        """Test closing an issue."""
        mock_run.return_value = MagicMock(returncode=0)

        manager = IssueManager()
        result = manager.close_issue(1)

        assert result is True


class TestGitHubAgent:
    """Tests for GitHubAgent class."""

    @patch("hobo_code.github.client.GitHubClient")
    def test_analyze_repository(self, MockClient):
        """Test repository analysis."""
        mock_client = MagicMock()
        mock_client.get_repo_info.return_value = {"url": "https://github.com/user/repo", "branch": "main", "commit": "abc123"}
        mock_client.list_branches.return_value = ["main", "develop"]
        mock_client.status.return_value = {"clean": True, "changes": []}
        mock_client.list_files.return_value = ["file1.py", "file2.py"]
        MockClient.return_value = mock_client

        agent = GitHubAgent()
        analysis = agent.analyze_repository()

        assert "repository" in analysis
        assert "branches" in analysis
        assert "working_tree_status" in analysis

    @patch("hobo_code.github.pr.PRManager")
    def test_generate_code_review(self, MockPRManager):
        """Test code review generation."""
        mock_pr = MagicMock()
        mock_pr.get_pr.return_value = {"number": 1, "title": "Test", "files": ["file1.py"]}
        mock_pr.get_pr_files.return_value = ["file1.py"]
        mock_pr.get_pr_diff.return_value = "+print('hello')\n-world"
        MockPRManager.return_value = mock_pr

        agent = GitHubAgent()
        review = agent.generate_code_review(1)

        assert "pr" in review
        assert "files_changed" in review
        assert "review_summary" in review

    def test_suggest_branches_fix(self):
        """Test branch name suggestions for fix task."""
        agent = GitHubAgent()
        suggestions = agent.suggest_branches("fix login bug")

        assert len(suggestions) > 0
        assert any("fix/" in s for s in suggestions)

    def test_suggest_branches_feature(self):
        """Test branch name suggestions for feature task."""
        agent = GitHubAgent()
        suggestions = agent.suggest_branches("add new feature")

        assert len(suggestions) > 0
        assert any("feature/" in s for s in suggestions)
