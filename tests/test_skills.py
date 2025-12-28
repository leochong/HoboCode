"""Tests for skill management modules."""

import tempfile
from pathlib import Path

import pytest

from hobo_code.skills.registry import SkillRegistry, AnthropicSkill, SkillMetadata
from hobo_code.skills.init import ProjectInitializer
from hobo_code.skills.downloader import SkillDownloader, SkillDownloadError


class TestSkillMetadata:
    """Tests for SkillMetadata class."""

    def test_create_metadata(self):
        """Test creating skill metadata."""
        metadata = SkillMetadata(
            name="Test Skill",
            description="A test skill",
            version="1.0.0",
            author="Test Author",
            tags=["test", "example"],
        )
        assert metadata.name == "Test Skill"
        assert metadata.description == "A test skill"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.tags == ["test", "example"]

    def test_default_values(self):
        """Test default values for metadata."""
        metadata = SkillMetadata(name="Test", description="Test description")
        assert metadata.version == "1.0.0"
        assert metadata.author == "Hobo Code"
        assert metadata.tags == []


class TestSkillRegistry:
    """Tests for SkillRegistry class."""

    def test_load_skills_from_directory(self, tmp_path):
        """Test loading skills from a directory."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_file = skills_dir / "test_skill" / "SKILL.md"
        skill_file.parent.mkdir()
        skill_file.write_text('''---
name: "Test Skill"
description: "A test skill"
version: "1.0.0"
tags: ["test"]
---

# Test Skill

This is a test skill.
''')

        registry = SkillRegistry(project_dir=str(tmp_path))
        registry.load_project_skills()

        assert "test_skill" in registry.list_skills()

    def test_get_skill(self, tmp_path):
        """Test getting a skill by name."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_file = skills_dir / "python_expert" / "SKILL.md"
        skill_file.parent.mkdir()
        skill_file.write_text('''---
name: "Python Expert"
description: "Python development"
tags: ["python"]
---

# Python Expert

You are a Python expert.
''')

        registry = SkillRegistry(project_dir=str(tmp_path))
        registry.load_project_skills()

        skill = registry.get_skill("python_expert")
        assert skill is not None
        assert isinstance(skill, AnthropicSkill)
        assert skill.metadata is not None
        assert skill.metadata.name == "Python Expert"

    def test_get_recommended_skills(self, tmp_path):
        """Test skill recommendation based on task."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_file = skills_dir / "python_expert" / "SKILL.md"
        skill_file.parent.mkdir()
        skill_file.write_text('''---
name: "Python Expert"
description: "Python development"
tags: ["python", "async"]
---

# Python Expert
''')

        registry = SkillRegistry(project_dir=str(tmp_path))
        registry.load_project_skills()

        recommendations = registry.get_recommended_skills("fix async bug in Python")
        assert len(recommendations) > 0

    def test_project_aware_loading(self, tmp_path):
        """Test that project directory takes precedence."""
        repo_skills = Path(__file__).parent.parent.parent / "skills"
        if repo_skills.exists():
            project_skills_dir = tmp_path / "skills"
            project_skills_dir.mkdir()

            project_skill = project_skills_dir / "custom" / "SKILL.md"
            project_skill.parent.mkdir()
            project_skill.write_text('''---
name: "Custom Skill"
description: "A custom skill"
tags: ["custom"]
---

# Custom Skill
''')

            registry = SkillRegistry(project_dir=str(tmp_path))
            registry.load_project_skills()

            assert "custom" in registry.list_skills()


class TestProjectInitializer:
    """Tests for ProjectInitializer class."""

    def test_create_project(self, tmp_path):
        """Test creating a new project."""
        initializer = ProjectInitializer()
        result = initializer.create_project(
            "test-project",
            tmp_path,
            description="A test project",
        )

        assert result["project_path"] == str(tmp_path / "test-project")
        assert (Path(result["project_path"]) / "project-plan.md").exists()
        assert (Path(result["project_path"]) / ".hobo-code" / "config").exists()
        assert (Path(result["project_path"]) / "skills").exists()

    def test_create_project_plan(self):
        """Test creating project-plan.md content."""
        initializer = ProjectInitializer()
        plan = initializer.create_project_plan("Test Project", "A test description")

        assert "# Project: Test Project" in plan
        assert "A test description" in plan
        assert "Phase 1: Foundation" in plan
        assert "Security Requirements" in plan
        assert "Test Strategy" in plan
        assert "security_audit" in plan
        assert "test_driven_development" in plan

    def test_create_config(self):
        """Test creating project config."""
        initializer = ProjectInitializer()
        config = initializer.create_config("my-project")

        assert 'name = "my-project"' in config
        assert 'primary_source = "leochong/HoboCode"' in config
        assert 'auto_download = true' in config


class TestSkillDownloader:
    """Tests for SkillDownloader class."""

    def test_list_remote_skills(self):
        """Test listing skills from GitHub repo."""
        downloader = SkillDownloader()
        skills = downloader.list_remote_skills("leochong/HoboCode")

        if skills:
            assert isinstance(skills, list)
            assert all(isinstance(s, str) for s in skills)

    def test_search_anthropic_repos(self):
        """Test searching Anthropic repos for a skill."""
        downloader = SkillDownloader()
        results = downloader.search_anthropic_repos("python_expert")

        assert isinstance(results, list)
        for result in results:
            assert "owner" in result
            assert "repo" in result
            assert "skill" in result


class TestSkillDiscovery:
    """Tests for SkillDiscovery class."""

    def test_find_skill_local(self, tmp_path):
        """Test finding a skill that exists locally."""
        from hobo_code.skills.discovery import SkillDiscovery

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_file = skills_dir / "test_skill" / "SKILL.md"
        skill_file.parent.mkdir()
        skill_file.write_text('''---
name: "Test Skill"
description: "A test skill"
tags: ["test"]
---

# Test Skill
''')

        discovery = SkillDiscovery()
        found = discovery.find_skill("test_skill", skills_dir)

        assert found is not None
        assert found.parent.name == "test_skill"
        assert found.name == "SKILL.md"
        assert (skills_dir / "test_skill" / "SKILL.md").exists()

    def test_suggest_skills_for_task(self):
        """Test skill suggestions for a task description."""
        from hobo_code.skills.discovery import SkillDiscovery

        discovery = SkillDiscovery()
        suggestions = discovery.suggest_skills_for_task(
            "Build a REST API with Python and database"
        )

        assert isinstance(suggestions, list)
        for suggestion in suggestions:
            assert "name" in suggestion
            assert "relevance_score" in suggestion


class TestAnthropicSkill:
    """Tests for AnthropicSkill class."""

    def test_parse_frontmatter(self, tmp_path):
        """Test YAML frontmatter parsing."""
        skill_file = tmp_path / "test_skill" / "SKILL.md"
        skill_file.parent.mkdir()
        skill_file.write_text('''---
name: "Test Skill"
description: "A test skill"
version: "1.0.0"
author: "Test Author"
tags: ["test", "example"]
---

# Test Skill

This is the content.
''')

        skill = AnthropicSkill("test_skill", skill_file)
        assert skill.metadata is not None
        assert skill.metadata.name == "Test Skill"
        assert skill.metadata.description == "A test skill"
        assert skill.metadata.tags == ["test", "example"]

    def test_full_content(self, tmp_path):
        """Test getting full content with linked files."""
        skill_file = tmp_path / "test_skill" / "SKILL.md"
        skill_file.parent.mkdir()

        linked_file = tmp_path / "test_skill" / "guidelines.md"
        linked_file.write_text("# Guidelines\n\nSome guidelines.")

        skill_file.write_text('''---
name: "Test Skill"
description: "A test skill"
tags: ["test"]
---

# Test Skill

Some content.

[link: guidelines.md]
''')

        skill = AnthropicSkill("test_skill", skill_file)
        full_content = skill.full_content

        assert "# Test Skill" in full_content
        assert "Some content." in full_content
        assert "guidelines" in full_content


class TestIntegration:
    """Integration tests for skill management."""

    def test_full_project_initialization_workflow(self, tmp_path):
        """Test the complete project initialization workflow."""
        from hobo_code.skills.init import init_project, ProjectInitializer
        from hobo_code.skills.registry import SkillRegistry
        from hobo_code.skills.discovery import suggest_skills_for_project

        result = init_project(
            "my-api",
            tmp_path,
            description="REST API for user management",
        )

        assert (Path(result["project_path"]) / "project-plan.md").exists()

        project_plan = (Path(result["project_path"]) / "project-plan.md").read_text()
        assert "REST API for user management" in project_plan

        skills_dir = Path(result["project_path"]) / "skills"
        skills_dir.mkdir(exist_ok=True)

        for skill_name in ["security_audit", "test_driven_development"]:
            skill_file = skills_dir / skill_name / "SKILL.md"
            skill_file.parent.mkdir(exist_ok=True)
            skill_file.write_text(f'''---
name: "{skill_name.replace("_", " ").title()}"
description: "A {skill_name} skill"
tags: ["{skill_name}"]
---

# {skill_name.replace("_", " ").title()}
''')

        registry = SkillRegistry(project_dir=result["project_path"])
        registry.load_project_skills()

        assert "security_audit" in registry.list_skills()
        assert "test_driven_development" in registry.list_skills()

        suggestions = suggest_skills_for_project(
            "Build a REST API with Python",
            Path(result["project_path"]),
        )

        assert isinstance(suggestions, list)
