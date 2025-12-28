"""Project initialization for Hobo Code."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .downloader import SkillDownloader


class ProjectInitializer:
    """Initializes Hobo Code projects with project-plan.md and default skills."""

    DEFAULT_SKILLS = ["security_audit", "test_driven_development"]

    def create_project(
        self,
        project_name: str,
        base_path: Path,
        description: str = "",
        github_token: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Hobo Code project.

        Args:
            project_name: Name of the project
            base_path: Base directory to create project in
            description: Optional project description
            github_token: Optional GitHub token for skill downloads

        Returns:
            Dict with project creation details
        """
        project_path = base_path / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        skills_dir = project_path / "skills"
        skills_dir.mkdir(exist_ok=True)

        hobo_dir = project_path / ".hobo-code"
        hobo_dir.mkdir(exist_ok=True)

        project_plan = self.create_project_plan(project_name, description)
        project_plan_path = project_path / "project-plan.md"
        project_plan_path.write_text(project_plan, encoding="utf-8")

        config = self.create_config(project_name)
        config_path = hobo_dir / "config"
        config_path.write_text(config, encoding="utf-8")

        downloader = SkillDownloader(github_token)
        downloaded = downloader.download_default_skills(skills_dir, self.DEFAULT_SKILLS)

        return {
            "project_path": str(project_path),
            "project_plan": str(project_plan_path),
            "skills_dir": str(skills_dir),
            "downloaded_skills": downloaded,
        }

    def create_project_plan(
        self, project_name: str, description: str = ""
    ) -> str:
        """Generate project-plan.md content.

        Args:
            project_name: Name of the project
            description: Optional project description

        Returns:
            Markdown content for project-plan.md
        """
        created_at = datetime.now().strftime("%Y-%m-%d")

        template = f'''# Project: {project_name}

## Overview
{description if description else "_Add project description here_"}

Created: {created_at}

## Phases

### Phase 1: Foundation
- [ ] Set up project structure
- [ ] Implement core functionality
- [ ] Security review (apply security_audit skill)

### Phase 2: Features
- [ ] Feature implementation
- [ ] Security review

### Phase 3: Testing & Polish
- [ ] Comprehensive test coverage (apply test_driven_development skill)
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation

## Security Requirements
- [ ] Input validation
- [ ] Authentication/Authorization
- [ ] Data encryption
- [ ] Audit logging
- [ ] Dependency vulnerability scanning

## Test Strategy
- [ ] Unit tests (pytest)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Security tests
- [ ] Performance benchmarks

## Skills Installed
These skills are available for this project:

| Skill | Description |
|-------|-------------|
| security_audit | Security-first design patterns and vulnerability checking |
| test_driven_development | TDD methodology and testing best practices |

## Additional Skills
Add more skills as needed using `hobo skills add <skill-name>`:

- language/python_expert - Python development
- language/javascript_typescript - JavaScript/TypeScript development
- framework/react_nextjs - React/Next.js development
- task/api_design - REST API design
- task/database_schema - Database design
- devops/docker_kubernetes - Container orchestration

## Progress Tracking
- [ ] Initialize project
- [ ] Define requirements
- [ ] Implement Phase 1
- [ ] Implement Phase 2
- [ ] Complete Phase 3 (Testing & Polish)

## Notes
_Add project-specific notes here_
'''
        return template

    def create_config(self, project_name: str) -> str:
        """Generate .hobo-code/config content.

        Args:
            project_name: Name of the project

        Returns:
            Config file content
        """
        created_at = datetime.now().isoformat()

        config = f'''[project]
name = "{project_name}"
created_at = "{created_at}"

[skills]
primary_source = "leochong/HoboCode"
auto_download = true
'''
        return config

    def update_project_plan(
        self, project_path: Path, phase: str, tasks: list[str]
    ) -> None:
        """Update project-plan.md with completed phase.

        Args:
            project_path: Path to project directory
            phase: Phase name (e.g., "Phase 1")
            tasks: List of tasks completed in this phase
        """
        plan_path = project_path / "project-plan.md"
        if not plan_path.exists():
            return

        content = plan_path.read_text(encoding="utf-8")

        for task in tasks:
            checkbox = f"- [ ] {task}"
            replacement = f"- [x] {task}"
            content = content.replace(checkbox, replacement)

        plan_path.write_text(content, encoding="utf-8")

    def add_skills_section(
        self, project_path: Path, skills: list[dict[str, str]]
    ) -> None:
        """Add skills to project-plan.md skills table.

        Args:
            project_path: Path to project directory
            skills: List of skill dicts with 'name' and 'description'
        """
        plan_path = project_path / "project-plan.md"
        if not plan_path.exists():
            return

        content = plan_path.read_text(encoding="utf-8")

        table_rows = []
        for skill in skills:
            name = skill.get("name", "")
            desc = skill.get("description", "")
            table_rows.append(f"| {name} | {desc} |")

        table = "\n".join(table_rows)

        insert_marker = "## Skills Installed"
        if insert_marker in content:
            existing_table_start = content.find("| Skill | Description |")
            if existing_table_start == -1:
                new_table = f'''{insert_marker}
These skills are available for this project:

| Skill | Description |
|-------|-------------|
{table}

'''
                content = content.replace(insert_marker, new_table)

        plan_path.write_text(content, encoding="utf-8")


def init_project(
    project_name: str,
    base_path: Path,
    description: str = "",
    github_token: str | None = None,
) -> dict[str, Any]:
    """Convenience function to initialize a project.

    Args:
        project_name: Name of the project
        base_path: Base directory to create project in
        description: Optional project description
        github_token: Optional GitHub token for skill downloads

    Returns:
        Dict with project creation details
    """
    initializer = ProjectInitializer()
    return initializer.create_project(project_name, base_path, description, github_token)
