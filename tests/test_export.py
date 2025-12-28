"""Tests for export module."""

import pytest
import json
import tempfile
from pathlib import Path

from hobo_code.export.formatter import JSONLFormatter, TrainingExample
from hobo_code.export.privacy import PrivacyFilter, FilterConfig, FilterResult


class TestJSONLFormatter:
    """Tests for JSONLFormatter class."""

    def test_training_example_to_dict(self):
        """Test TrainingExample serialization."""
        example = TrainingExample(
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-4",
            task_type="general",
        )
        data = example.to_dict()

        assert data["system"] == "You are a helpful assistant."
        assert data["model"] == "gpt-4"
        assert data["task"] == "general"
        assert len(data["messages"]) == 1

    def test_training_example_to_jsonl(self):
        """Test TrainingExample JSONL output."""
        example = TrainingExample(
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": "Hello"}],
        )
        line = example.to_jsonl()

        data = json.loads(line)
        assert data["system"] == "You are a helpful assistant."

    def test_export_to_file(self):
        """Test exporting to a file."""
        formatter = JSONLFormatter()
        lines = [
            json.dumps({"system": "Test", "messages": []}),
            json.dumps({"system": "Test2", "messages": []}),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.jsonl"
            count = formatter.export_to_file(lines, str(output_path))

            assert count == 2
            assert output_path.exists()
            with open(output_path) as f:
                file_lines = f.readlines()
            assert len(file_lines) == 2

    def test_create_sample_export(self):
        """Test creating sample export."""
        formatter = JSONLFormatter()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "sample.jsonl"
            count = formatter.create_sample_export(str(output_path))

            assert count == 3
            with open(output_path) as f:
                lines = f.readlines()
            assert len(lines) == 3

    def test_get_stats(self):
        """Test getting export statistics."""
        formatter = JSONLFormatter()
        lines = [
            json.dumps({"task": "bug_fix", "success": True, "tokens": {"input": 100, "output": 50}, "skill": "python"}),
            json.dumps({"task": "feature", "success": True, "tokens": {"input": 200, "output": 100}, "skill": "javascript"}),
        ]

        stats = formatter.get_stats(lines)

        assert stats["total_examples"] == 2
        assert stats["success_rate"] == 1.0
        assert "bug_fix" in stats["task_types"]
        assert "feature" in stats["task_types"]

    def test_infer_task_type(self):
        """Test task type inference."""
        formatter = JSONLFormatter()

        assert formatter._infer_task_type("Fix the bug") == "bug_fix"
        assert formatter._infer_task_type("Refactor this code") == "refactor"
        assert formatter._infer_task_type("Add tests") == "testing"
        assert formatter._infer_task_type("Explain this function") == "explanation"

    def test_estimate_tokens(self):
        """Test token estimation."""
        formatter = JSONLFormatter()
        count = formatter._estimate_tokens("Hello world this is a test")
        assert count > 0


class TestPrivacyFilter:
    """Tests for PrivacyFilter class."""

    def test_remove_email(self):
        """Test email removal."""
        filter = PrivacyFilter()
        result = filter.filter_text("Contact me at test@example.com for more info")

        assert "[EMAIL_REMOVED]" in result.filtered_text
        assert len(result.matches_found) == 1
        assert result.matches_found[0]["type"] == "email"

    def test_remove_api_key(self):
        """Test API key removal."""
        filter = PrivacyFilter()
        result = filter.filter_text("Use sk-abcdefghijklmnopqrstuvwxyz for auth")

        assert "[API_KEY_REMOVED]" in result.filtered_text
        assert len(result.matches_found) == 1

    def test_remove_api_key_short(self):
        """Test short API key removal."""
        filter = PrivacyFilter()
        result = filter.filter_text("Key: sk-abcdefghijklmnopqrstuvwxyz12345")

        assert result.filtered is True
        assert "[API_KEY_REMOVED]" in result.filtered_text

    def test_filter_dict(self):
        """Test filtering a dictionary."""
        filter = PrivacyFilter()
        data = {
            "email": "test@example.com",
            "content": "Hello world",
            "nested": {"api_key": "sk-abcdefghijklmnopqrstuvwxyz"},
        }

        filtered, matches = filter.filter_dict(data)

        assert "[EMAIL_REMOVED]" in filtered["email"]
        assert "[API_KEY_REMOVED]" in filtered["nested"]["api_key"]
        assert filtered["content"] == "Hello world"

    def test_filter_jsonl_lines(self):
        """Test filtering JSONL lines."""
        filter = PrivacyFilter()
        lines = [
            json.dumps({"email": "test@example.com", "content": "Hello"}),
            json.dumps({"content": "World"}),
        ]

        filtered_lines, stats = filter.filter_jsonl_lines(lines)

        assert stats["total_lines"] == 2
        assert stats["filtered_lines"] == 1
        assert stats["total_matches"] == 1

    def test_dry_run(self):
        """Test dry run mode."""
        filter = PrivacyFilter()
        lines = [
            json.dumps({"email": "test@example.com"}),
            json.dumps({"content": "Clean"}),
        ]

        stats = filter.dry_run(lines)

        assert stats["total_lines"] == 2
        assert stats["filtered_lines"] == 1
        assert stats["matches_by_type"]["email"] == 1

    def test_custom_config(self):
        """Test custom filter configuration."""
        config = FilterConfig(
            remove_emails=False,
            remove_api_keys=True,
            base_path="/home/user",
        )
        filter = PrivacyFilter(config)

        result = filter.filter_text("Email: test@example.com")
        assert "test@example.com" in result.filtered_text

    def test_no_matches(self):
        """Test filtering text with no PII."""
        filter = PrivacyFilter()
        result = filter.filter_text("This is clean content without any PII.")

        assert result.filtered is False
        assert result.filtered_text == "This is clean content without any PII."
        assert len(result.matches_found) == 0

    def test_multiple_pii_types(self):
        """Test filtering multiple PII types."""
        filter = PrivacyFilter()
        result = filter.filter_text(
            "Email: test@example.com, Phone: 555-123-4567, IP: 192.168.1.1"
        )

        assert result.filtered is True
        assert "[EMAIL_REMOVED]" in result.filtered_text
        assert "[PHONE_REMOVED]" in result.filtered_text
        assert "[IP_REMOVED]" in result.filtered_text
        assert len(result.matches_found) == 3
