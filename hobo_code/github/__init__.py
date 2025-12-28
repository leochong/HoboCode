"""GitHub integration module."""

from hobo_code.github.client import GitHubClient
from hobo_code.github.pr import PRManager
from hobo_code.github.issues import IssueManager
from hobo_code.github.agent import GitHubAgent

__all__ = ["GitHubClient", "PRManager", "IssueManager", "GitHubAgent"]
