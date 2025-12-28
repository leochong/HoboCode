"""Issue management."""

import subprocess
from typing import Any


class IssueManager:
    """Manager for GitHub issues using gh CLI."""

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

    def list_issues(self, state: str = "open") -> list[dict[str, Any]]:
        """List issues."""
        result = self._run_gh("issue", "list", "--state", state, "--json", "number,title,author,state,url,labels")
        if result.returncode != 0:
            return []
        try:
            import json
            issues = json.loads(result.stdout)
            return [
                {
                    "number": i["number"],
                    "title": i["title"],
                    "author": i["author"]["login"],
                    "state": i["state"],
                    "url": i["url"],
                    "labels": [l["name"] for l in i.get("labels", [])],
                }
                for i in issues
            ]
        except Exception:
            return []

    def get_issue(self, issue_number: int) -> dict[str, Any] | None:
        """Get a specific issue."""
        result = self._run_gh("issue", "view", str(issue_number), "--json", "number,title,body,author,state,url,labels,comments")
        if result.returncode != 0:
            return None
        try:
            import json
            issue = json.loads(result.stdout)
            return {
                "number": issue["number"],
                "title": issue["title"],
                "body": issue["body"],
                "author": issue["author"]["login"],
                "state": issue["state"],
                "url": issue["url"],
                "labels": [l["name"] for l in issue.get("labels", [])],
                "comments": issue.get("comments", 0),
            }
        except Exception:
            return None

    def create_issue(self, title: str, body: str, labels: list[str] | None = None) -> dict[str, Any] | None:
        """Create a new issue."""
        cmd = ["gh", "issue", "create", "--title", title, "--body", body]
        if labels:
            for label in labels:
                cmd.extend(["--label", label])
        result = self._run_gh(*cmd[1:])
        if result.returncode != 0:
            return None
        return {"url": result.stdout.strip()}

    def close_issue(self, issue_number: int) -> bool:
        """Close an issue."""
        result = self._run_gh("issue", "close", str(issue_number))
        return result.returncode == 0

    def reopen_issue(self, issue_number: int) -> bool:
        """Reopen an issue."""
        result = self._run_gh("issue", "reopen", str(issue_number))
        return result.returncode == 0

    def add_comment(self, issue_number: int, comment: str) -> bool:
        """Add a comment to an issue."""
        result = self._run_gh("issue", "comment", str(issue_number), "--body", comment)
        return result.returncode == 0

    def add_label(self, issue_number: int, label: str) -> bool:
        """Add a label to an issue."""
        result = self._run_gh("issue", "edit", str(issue_number), "--add-label", label)
        return result.returncode == 0

    def remove_label(self, issue_number: int, label: str) -> bool:
        """Remove a label from an issue."""
        result = self._run_gh("issue", "edit", str(issue_number), "--remove-label", label)
        return result.returncode == 0
