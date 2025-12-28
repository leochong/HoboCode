"""Pull request management."""

import subprocess
from typing import Any


class PRManager:
    """Manager for GitHub pull requests using gh CLI."""

    def __init__(self, token: str | None = None, repo_path: str | None = None):
        self.token = token
        self.repo_path = repo_path

    def _run_gh(self, *args) -> subprocess.CompletedProcess:
        """Run a gh command."""
        env = {}
        if self.token:
            env["GITHUB_TOKEN"] = self.token
        return subprocess.run(
            ["gh"] + list(args),
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            env=env,
        )

    def list_prs(self, state: str = "open") -> list[dict[str, Any]]:
        """List pull requests."""
        result = self._run_gh("pr", "list", "--state", state, "--json", "number,title,author,state,url")
        if result.returncode != 0:
            return []
        try:
            import json
            prs = json.loads(result.stdout)
            return [{"number": p["number"], "title": p["title"], "author": p["author"]["login"], "state": p["state"], "url": p["url"]} for p in prs]
        except Exception:
            return []

    def get_pr(self, pr_number: int) -> dict[str, Any] | None:
        """Get a specific PR."""
        result = self._run_gh("pr", "view", str(pr_number), "--json", "number,title,body,author,state,url,files")
        if result.returncode != 0:
            return None
        try:
            import json
            pr = json.loads(result.stdout)
            return {
                "number": pr["number"],
                "title": pr["title"],
                "body": pr["body"],
                "author": pr["author"]["login"],
                "state": pr["state"],
                "url": pr["url"],
                "files": [f["name"] for f in pr.get("files", [])],
            }
        except Exception:
            return None

    def checkout_pr(self, pr_number: int) -> bool:
        """Checkout a PR locally."""
        result = self._run_gh("pr", "checkout", str(pr_number))
        return result.returncode == 0

    def get_pr_diff(self, pr_number: int) -> str:
        """Get the diff for a PR."""
        result = self._run_gh("pr", "diff", str(pr_number))
        return result.stdout if result.returncode == 0 else ""

    def merge_pr(self, pr_number: int, method: str = "merge") -> bool:
        """Merge a PR."""
        result = self._run_gh("pr", "merge", str(pr_number), "--admin", "--method", method)
        return result.returncode == 0

    def close_pr(self, pr_number: int) -> bool:
        """Close a PR."""
        result = self._run_gh("pr", "close", str(pr_number))
        return result.returncode == 0

    def create_pr(self, title: str, body: str, base: str = "main", head: str | None = None) -> dict[str, Any] | None:
        """Create a new PR."""
        cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]
        if head:
            cmd.extend(["--head", head])
        result = self._run_gh(*cmd[1:])
        if result.returncode != 0:
            return None
        return {"url": result.stdout.strip()}

    def get_pr_files(self, pr_number: int) -> list[str]:
        """Get list of files changed in a PR."""
        pr = self.get_pr(pr_number)
        return pr.get("files", []) if pr else []
