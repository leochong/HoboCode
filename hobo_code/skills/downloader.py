"""Skill downloader for fetching skills from GitHub repositories."""

import json
import os
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import yaml


class SkillDownloadError(Exception):
    """Exception raised when skill download fails."""
    pass


class SkillDownloader:
    """Downloads and manages skills from GitHub repositories."""

    DEFAULT_REPO = "leochong/HoboCode"
    RAW_CONTENT_URL = "https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    API_URL = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    DEFAULT_BRANCH = "main"

    ANTHROPIC_REPOS = [
        ("anthropics", "skills"),
        ("abubakarsiddik31", "claude-skills-collection"),
        ("hesreallyhim", "awesome-claude-code"),
        ("brightdata", "awesome-claude-skills"),
    ]

    def __init__(self, token: str | None = None):
        self.token = token
        self._cache: dict[str, dict[str, Any]] = {}

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for GitHub API requests."""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def _api_request(self, url: str) -> dict[str, Any]:
        """Make API request to GitHub."""
        if url in self._cache:
            return self._cache[url]

        req = Request(url, headers=self._get_headers())
        try:
            with urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
                self._cache[url] = data
                return data
        except HTTPError as e:
            if e.code == 403:
                raise SkillDownloadError(
                    f"Rate limit exceeded or unauthorized access to {url}"
                )
            raise SkillDownloadError(f"GitHub API error: {e.code} {e.reason}")
        except (URLError, json.JSONDecodeError) as e:
            raise SkillDownloadError(f"Request failed: {e}")

    def _raw_request(self, url: str) -> str:
        """Fetch raw content from GitHub."""
        req = Request(url, headers={"Accept": "application/vnd.github.v3.raw+json"})
        try:
            with urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8")
        except HTTPError as e:
            if e.code == 404:
                return ""
            raise SkillDownloadError(f"Failed to fetch raw content: {e}")

    def list_remote_skills(self, repo: str | None = None) -> list[str]:
        """List all skills available in a remote repository."""
        if repo is None:
            repo = self.DEFAULT_REPO

        owner, repo_name = repo.split("/", 1)
        url = self.API_URL.format(owner=owner, repo=repo_name, path="skills")
        url += "?ref=" + self.DEFAULT_BRANCH

        try:
            data = self._api_request(url)
            if not isinstance(data, list):
                return []

            skills = []
            for item in data:
                if isinstance(item, dict):
                    item_type = item.get("type")
                    item_name = item.get("name")
                    if item_type == "dir" and isinstance(item_name, str):
                        skills.append(item_name)
            return sorted(skills)
        except SkillDownloadError:
            return []

    def get_skill_content(self, skill_path: str, repo: str | None = None) -> str | None:
        """Get the content of a skill file from GitHub."""
        if repo is None:
            repo = self.DEFAULT_REPO

        owner, repo_name = repo.split("/", 1)
        skill_file = f"skills/{skill_path}/SKILL.md"
        url = self.API_URL.format(
            owner=owner, repo=repo_name, path=skill_file
        )
        url += "?ref=" + self.DEFAULT_BRANCH

        try:
            data = self._api_request(url)
            if "download_url" in data:
                return self._raw_request(data["download_url"])
        except SkillDownloadError:
            pass

        return None

    def download_skill(
        self,
        skill_name: str,
        target_dir: Path,
        repo: str | None = None,
        overwrite: bool = False,
    ) -> bool:
        """Download a skill from GitHub to the target directory.

        Args:
            skill_name: Name of the skill (e.g., "python_expert")
            target_dir: Directory to download skill to
            repo: GitHub repository in format "owner/repo"
            overwrite: Whether to overwrite existing skills

        Returns:
            True if skill was downloaded successfully, False if already exists
        """
        if repo is None:
            repo = self.DEFAULT_REPO

        skill_dir = target_dir / skill_name
        skill_file = skill_dir / "SKILL.md"

        if skill_file.exists() and not overwrite:
            return False

        content = self.get_skill_content(skill_name, repo)
        if content is None:
            raise SkillDownloadError(
                f"Skill '{skill_name}' not found in {repo}"
            )

        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(content, encoding="utf-8")

        return True

    def download_default_skills(
        self,
        skills_dir: Path,
        default_skills: list[str] | None = None,
    ) -> list[str]:
        """Download the default skills for a new project.

        Args:
            skills_dir: Directory to download skills to
            default_skills: List of skill names to download

        Returns:
            List of successfully downloaded skill names
        """
        if default_skills is None:
            default_skills = ["security_audit", "test_driven_development"]

        downloaded = []
        for skill_name in default_skills:
            try:
                if self.download_skill(skill_name, skills_dir):
                    downloaded.append(skill_name)
            except SkillDownloadError as e:
                print(f"Warning: Could not download {skill_name}: {e}")

        return downloaded

    def download_all_skills(self, target_dir: Path, repo: str | None = None) -> int:
        """Download all skills from a repository.

        Args:
            target_dir: Directory to download skills to
            repo: GitHub repository to download from

        Returns:
            Number of skills downloaded
        """
        skills = self.list_remote_skills(repo)
        downloaded = 0

        for skill_name in skills:
            try:
                if self.download_skill(skill_name, target_dir, repo):
                    downloaded += 1
            except SkillDownloadError as e:
                print(f"Warning: Could not download {skill_name}: {e}")

        return downloaded

    def search_remote_skill(
        self, skill_name: str, repo: str | None = None
    ) -> bool:
        """Check if a skill exists in a remote repository."""
        content = self.get_skill_content(skill_name, repo)
        return content is not None

    def search_anthropic_repos(
        self, skill_name: str
    ) -> list[tuple[str, str, str]]:
        """Search for a skill across Anthropic-compatible repositories.

        Args:
            skill_name: Name of the skill to search for

        Returns:
            List of tuples (owner, repo, skill_name) where skill was found
        """
        found = []
        for owner, repo in self.ANTHROPIC_REPOS:
            if self.search_remote_skill(skill_name, f"{owner}/{repo}"):
                found.append((owner, repo, skill_name))
        return found

    def search_all_sources(
        self, skill_name: str, primary_repo: str | None = None
    ) -> list[dict[str, str]]:
        """Search for a skill across all known sources.

        Args:
            skill_name: Name of the skill to search for

        Returns:
            List of dicts with 'owner', 'repo', 'source_type' keys
        """
        results = []

        if primary_repo is None:
            primary_repo = self.DEFAULT_REPO

        if self.search_remote_skill(skill_name, primary_repo):
            results.append({
                "owner": primary_repo.split("/")[0],
                "repo": primary_repo.split("/")[1],
                "skill": skill_name,
                "source_type": "primary",
            })

        for owner, repo in self.ANTHROPIC_REPOS:
            if self.search_remote_skill(skill_name, f"{owner}/{repo}"):
                results.append({
                    "owner": owner,
                    "repo": repo,
                    "skill": skill_name,
                    "source_type": "anthropic",
                })

        return results

    def clear_cache(self) -> None:
        """Clear the API request cache."""
        self._cache.clear()


def download_skill_to_project(
    skill_name: str,
    project_path: Path,
    token: str | None = None,
) -> Path | None:
    """Convenience function to download a skill to a project.

    Args:
        skill_name: Name of the skill
        project_path: Path to project directory
        token: Optional GitHub token

    Returns:
        Path to downloaded skill file, or None if failed
    """
    downloader = SkillDownloader(token)
    skills_dir = project_path / "skills"

    try:
        if downloader.download_skill(skill_name, skills_dir):
            return skills_dir / skill_name / "SKILL.md"
    except SkillDownloadError:
        pass

    return None


def ensure_skill(
    skill_name: str,
    project_path: Path,
    token: str | None = None,
) -> Path | None:
    """Ensure a skill exists, searching all sources.

    Args:
        skill_name: Name of the skill
        project_path: Path to project directory
        token: Optional GitHub token

    Returns:
        Path to skill file if found/created, None if not found
    """
    skills_dir = project_path / "skills"
    skill_path = skills_dir / skill_name / "SKILL.md"

    if skill_path.exists():
        return skill_path

    downloader = SkillDownloader(token)

    sources = downloader.search_all_sources(skill_name)

    for source in sources:
        try:
            if downloader.download_skill(
                source["skill"],
                skills_dir,
                repo=f"{source['owner']}/{source['repo']}",
            ):
                return skill_path
        except SkillDownloadError:
            continue

    return None
