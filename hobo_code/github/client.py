"""GitHub client for repository operations."""

import os
import subprocess
from pathlib import Path
from typing import Any


class GitHubClient:
    """Client for GitHub repository operations using git and GitHub API."""

    def __init__(self, token: str | None = None, repo_path: str | None = None):
        self.token = token or self._load_token()
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self._repo = None

    def _load_token(self) -> str | None:
        """Load GitHub token from credential store."""
        try:
            from hobo_code.auth.credentials import CredentialStore
            store = CredentialStore()
            return store.get_github_token()
        except Exception:
            return os.environ.get("GITHUB_TOKEN")

    def _run_git(self, *args, cwd: Path | None = None) -> subprocess.CompletedProcess:
        """Run a git command."""
        env = os.environ.copy()
        if self.token:
            env["GITHUB_TOKEN"] = self.token
        return subprocess.run(
            ["git"] + list(args),
            cwd=cwd or self.repo_path,
            capture_output=True,
            text=True,
            env=env,
        )

    def _run_gh(self, *args, cwd: Path | None = None) -> subprocess.CompletedProcess:
        """Run a gh (GitHub CLI) command."""
        env = os.environ.copy()
        if self.token:
            env["GITHUB_TOKEN"] = self.token
        return subprocess.run(
            ["gh"] + list(args),
            cwd=cwd or self.repo_path,
            capture_output=True,
            text=True,
            env=env,
        )

    def clone(self, repo_url: str, local_path: str | None = None) -> Path:
        """Clone a repository."""
        target = local_path or repo_url.split("/")[-1].replace(".git", "")
        result = self._run_git("clone", repo_url, target)
        if result.returncode != 0:
            raise RuntimeError(f"Clone failed: {result.stderr}")
        return Path(target)

    def get_repo_info(self) -> dict[str, Any]:
        """Get repository information."""
        result = self._run_git("remote", "get-url", "origin")
        branch_result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        commit_result = self._run_git("rev-parse", "HEAD")

        return {
            "url": result.stdout.strip() if result.returncode == 0 else None,
            "branch": branch_result.stdout.strip() if branch_result.returncode == 0 else "main",
            "commit": commit_result.stdout.strip() if commit_result.returncode == 0 else None,
            "path": str(self.repo_path),
        }

    def list_branches(self) -> list[str]:
        """List all branches."""
        result = self._run_git("branch", "-a")
        if result.returncode != 0:
            return []
        branches = [b.strip().replace("* ", "") for b in result.stdout.strip().split("\n") if b.strip()]
        return branches

    def current_branch(self) -> str:
        """Get current branch name."""
        result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip() if result.returncode == 0 else "main"

    def create_branch(self, name: str, checkout: bool = True) -> bool:
        """Create a new branch."""
        result = self._run_git("branch", name)
        if result.returncode != 0:
            return False
        if checkout:
            return self.switch_branch(name)
        return True

    def switch_branch(self, name: str) -> bool:
        """Switch to a branch."""
        result = self._run_git("checkout", name)
        return result.returncode == 0

    def list_files(self, path: str = ".") -> list[str]:
        """List files in a directory."""
        result = self._run_git("ls-files", path)
        if result.returncode != 0:
            return []
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

    def get_file_content(self, path: str) -> str | None:
        """Get content of a file."""
        result = self._run_git("show", f"HEAD:{path}")
        return result.stdout if result.returncode == 0 else None

    def commit(self, paths: list[str], message: str) -> bool:
        """Commit changes."""
        self._run_git("add", *paths)
        result = self._run_git("commit", "-m", message)
        return result.returncode == 0

    def push(self, remote: str = "origin", branch: str | None = None) -> bool:
        """Push to remote."""
        current = branch or self.current_branch()
        result = self._run_git("push", remote, current)
        return result.returncode == 0

    def pull(self, remote: str = "origin", branch: str | None = None) -> bool:
        """Pull from remote."""
        current = branch or self.current_branch()
        result = self._run_git("pull", remote, current)
        return result.returncode == 0

    def status(self) -> dict[str, Any]:
        """Get repository status."""
        result = self._run_git("status", "--porcelain")
        changes = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                changes.append({"status": line[:2], "file": line[3:].strip()})

        return {
            "clean": len(changes) == 0,
            "changes": changes,
            "branch": self.current_branch(),
        }

    def diff(self, target: str = "HEAD") -> str:
        """Get diff against a target."""
        result = self._run_git("diff", target)
        return result.stdout if result.returncode == 0 else ""

    def get_stashed_changes(self) -> list[dict[str, Any]]:
        """Get list of stashed changes."""
        result = self._run_git("stash", "list")
        stashes = []
        for i, line in enumerate(result.stdout.strip().split("\n")):
            if line.strip():
                stashes.append({"index": i, "message": line})
        return stashes
