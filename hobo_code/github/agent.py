"""GitHub agent for AI-powered repository operations."""

from typing import Any


class GitHubAgent:
    """AI-powered GitHub operations agent."""

    def __init__(self, token: str | None = None, repo_path: str | None = None):
        from hobo_code.github.client import GitHubClient
        from hobo_code.github.pr import PRManager
        from hobo_code.github.issues import IssueManager

        self.client = GitHubClient(token=token, repo_path=repo_path)
        self.pr_manager = PRManager(token=token, repo_path=repo_path)
        self.issue_manager = IssueManager(token=token, repo_path=repo_path)

    def analyze_repository(self) -> dict[str, Any]:
        """Analyze repository structure and provide insights."""
        info = self.client.get_repo_info()
        branches = self.client.list_branches()
        status = self.client.status()

        return {
            "repository": info,
            "branches": branches,
            "working_tree_status": status,
            "language_stats": self._detect_languages(),
        }

    def _detect_languages(self) -> dict[str, int]:
        """Detect programming languages in the repository."""
        files = self.client.list_files()
        extensions = {}
        for f in files:
            ext = f.split(".")[-1] if "." in f else "unknown"
            extensions[ext] = extensions.get(ext, 0) + 1
        return extensions

    def generate_code_review(self, pr_number: int) -> dict[str, Any]:
        """Generate an AI-powered code review for a PR."""
        pr = self.pr_manager.get_pr(pr_number)
        if not pr:
            return {"error": "PR not found"}

        files = self.pr_manager.get_pr_files(pr_number)
        diff = self.pr_manager.get_pr_diff(pr_number)

        return {
            "pr": pr,
            "files_changed": len(files),
            "diff_length": len(diff),
            "review_summary": self._summarize_changes(diff),
            "suggestions": self._generate_suggestions(files, diff),
        }

    def _summarize_changes(self, diff: str) -> str:
        """Summarize changes from a diff."""
        additions = diff.count("\n+")
        deletions = diff.count("\n-")
        files_changed = diff.count("diff --git")
        return f"Changed {files_changed} files (+{additions} lines, -{deletions} lines)"

    def _generate_suggestions(self, files: list[str], diff: str) -> list[str]:
        """Generate improvement suggestions."""
        suggestions = []
        for f in files:
            if f.endswith(".py"):
                if "print(" in diff:
                    suggestions.append(f"Consider using logging instead of print() in {f}")
            if f.endswith(".js") or f.endswith(".ts"):
                if "var " in diff:
                    suggestions.append(f"Consider using let/const instead of var in {f}")
        return suggestions[:5]

    def generate_pr_description(self, pr_number: int) -> str:
        """Generate a PR description based on changes."""
        pr = self.pr_manager.get_pr(pr_number)
        if not pr:
            return "PR not found"

        files = self.pr_manager.get_pr_files(pr_number)
        return f"## Summary\n\nThis PR modifies {len(files)} files.\n\n## Changes\n\n" + "\n".join(f"- {f}" for f in files[:10])

    def generate_issue_report(self, issue_number: int) -> dict[str, Any]:
        """Generate a report for an issue."""
        issue = self.issue_manager.get_issue(issue_number)
        if not issue:
            return {"error": "Issue not found"}

        return {
            "issue": issue,
            "related_prs": [],
            "activity_summary": f"Issue created by {issue['author']} with {issue['comments']} comments",
        }

    def suggest_branches(self, task: str) -> list[str]:
        """Suggest branch names based on a task."""
        task_lower = task.lower()
        prefixes = []
        if "fix" in task_lower:
            prefixes.append("fix/")
        elif "feature" in task_lower or "add" in task_lower:
            prefixes.append("feature/")
        elif "docs" in task_lower or "documentation" in task_lower:
            prefixes.append("docs/")
        elif "refactor" in task_lower:
            prefixes.append("refactor/")
        else:
            prefixes.append("task/")

        suggested = []
        words = task_lower.replace("_", "-").replace(" ", "-")[:30]
        for prefix in prefixes:
            suggested.append(f"{prefix}{words}")
        return suggested

    def get_repository_stats(self) -> dict[str, Any]:
        """Get repository statistics."""
        info = self.client.get_repo_info()
        branches = self.client.list_branches()
        open_prs = self.pr_manager.list_prs("open")
        open_issues = self.issue_manager.list_issues("open")

        return {
            "repository": info["url"],
            "branch_count": len(branches),
            "open_prs": len(open_prs),
            "open_issues": len(open_issues),
            "contributors": 1,
        }
