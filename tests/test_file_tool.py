"""Tests for FileTool implementation."""

import pytest
from pathlib import Path

from hobo_code.tools.file import FileTool, PathSecurityError


class TestFileTool:
    """Tests for FileTool class."""

    def test_initialization_with_default_path(self, tmp_path):
        """Test FileTool initialization with default path."""
        tool = FileTool()
        assert tool.base_path == Path.cwd()

    def test_initialization_with_custom_path(self, tmp_path):
        """Test FileTool initialization with custom base path."""
        tool = FileTool(str(tmp_path))
        assert tool.base_path == tmp_path

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading a nonexistent file."""
        tool = FileTool(str(tmp_path))
        result = tool.read("nonexistent.txt")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_read_file(self, tmp_path):
        """Test reading a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        tool = FileTool(str(tmp_path))
        result = tool.read("test.txt")

        assert result["success"] is True
        assert result["content"] == "Hello, World!"
        assert result["path"] == str(test_file)
        assert result["size"] == 13

    def test_read_file_with_special_chars(self, tmp_path):
        """Test reading a file with special characters in content."""
        test_file = tmp_path / "special.txt"
        content = "Line 1\nLine 2\n\tIndented\n"
        test_file.write_text(content)

        tool = FileTool(str(tmp_path))
        result = tool.read("special.txt")

        assert result["success"] is True
        assert result["content"] == content

    def test_write_new_file(self, tmp_path):
        """Test writing a new file."""
        tool = FileTool(str(tmp_path))
        result = tool.write("new_file.txt", "Test content")

        assert result["success"] is True
        assert result["path"] == str(tmp_path / "new_file.txt")
        assert result["size"] == 12

    def test_write_creates_directories(self, tmp_path):
        """Test writing creates nested directories."""
        tool = FileTool(str(tmp_path))
        result = tool.write("nested/dir/new_file.txt", "Nested content")

        assert result["success"] is True
        assert (tmp_path / "nested" / "dir" / "new_file.txt").exists()

    def test_write_overwrites_file(self, tmp_path):
        """Test overwriting an existing file."""
        test_file = tmp_path / "existing.txt"
        test_file.write_text("Original")

        tool = FileTool(str(tmp_path))
        result = tool.write("existing.txt", "Updated")

        assert result["success"] is True
        assert test_file.read_text() == "Updated"

    def test_list_directory(self, tmp_path):
        """Test listing directory contents."""
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "subdir").mkdir()

        tool = FileTool(str(tmp_path))
        result = tool.list(".")

        assert result["success"] is True
        assert result["count"] == 3
        names = {item["name"] for item in result["items"]}
        assert names == {"file1.txt", "file2.txt", "subdir"}

    def test_list_nonexistent_directory(self, tmp_path):
        """Test listing a nonexistent directory."""
        tool = FileTool(str(tmp_path))
        result = tool.list("nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_exists_true_for_file(self, tmp_path):
        """Test exists returns True for existing file."""
        (tmp_path / "exists.txt").write_text("test")
        tool = FileTool(str(tmp_path))
        result = tool.exists("exists.txt")

        assert result["success"] is True
        assert result["exists"] is True
        assert result["is_file"] is True
        assert result["is_dir"] is False

    def test_exists_true_for_directory(self, tmp_path):
        """Test exists returns True for existing directory."""
        (tmp_path / "testdir").mkdir()
        tool = FileTool(str(tmp_path))
        result = tool.exists("testdir")

        assert result["success"] is True
        assert result["exists"] is True
        assert result["is_dir"] is True

    def test_exists_false_for_nonexistent(self, tmp_path):
        """Test exists returns False for nonexistent path."""
        tool = FileTool(str(tmp_path))
        result = tool.exists("nonexistent.txt")

        assert result["success"] is True
        assert result["exists"] is False

    def test_mkdir_creates_directory(self, tmp_path):
        """Test creating a directory."""
        tool = FileTool(str(tmp_path))
        result = tool.mkdir("new_dir")

        assert result["success"] is True
        assert (tmp_path / "new_dir").is_dir()

    def test_mkdir_creates_nested_directories(self, tmp_path):
        """Test creating nested directories."""
        tool = FileTool(str(tmp_path))
        result = tool.mkdir("a/b/c/d")

        assert result["success"] is True
        assert (tmp_path / "a" / "b" / "c" / "d").is_dir()

    def test_remove_file(self, tmp_path):
        """Test removing a file."""
        test_file = tmp_path / "to_remove.txt"
        test_file.write_text("remove me")
        assert test_file.exists()

        tool = FileTool(str(tmp_path))
        result = tool.remove("to_remove.txt")

        assert result["success"] is True
        assert not test_file.exists()

    def test_remove_directory(self, tmp_path):
        """Test removing an empty directory."""
        test_dir = tmp_path / "empty_dir"
        test_dir.mkdir()
        assert test_dir.exists()

        tool = FileTool(str(tmp_path))
        result = tool.remove("empty_dir")

        assert result["success"] is True
        assert not test_dir.exists()

    def test_remove_nonexistent(self, tmp_path):
        """Test removing a nonexistent path."""
        tool = FileTool(str(tmp_path))
        result = tool.remove("nonexistent")

        assert result["success"] is False
        assert "does not exist" in result["error"].lower()

    def test_search_files(self, tmp_path):
        """Test searching for files with glob pattern."""
        (tmp_path / "file1.py").write_text("# Python")
        (tmp_path / "file2.py").write_text("# Python")
        (tmp_path / "file1.txt").write_text("Text")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file3.py").write_text("# Python")

        tool = FileTool(str(tmp_path))
        result = tool.search("*.py")

        assert result["success"] is True
        assert result["count"] == 2
        filenames = [str(Path(f).name) for f in result["files"]]
        assert "file1.py" in filenames
        assert "file2.py" in filenames

    def test_search_recursive(self, tmp_path):
        """Test recursive file search."""
        (tmp_path / "root.py").write_text("# Python")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.py").write_text("# Python")

        tool = FileTool(str(tmp_path))
        result = tool.search("**/*.py")

        assert result["success"] is True
        assert result["count"] == 2

    def test_path_security_prevents_escape(self, tmp_path):
        """Test that path validation prevents directory traversal."""
        tool = FileTool(str(tmp_path))
        result = tool.read("../etc/passwd")

        assert result["success"] is False
        assert "outside the allowed base path" in result["error"]

    def test_path_security_allows_subdirectory(self, tmp_path):
        """Test that subdirectory access is allowed."""
        (tmp_path / "allowed.txt").write_text("allowed content")

        tool = FileTool(str(tmp_path))
        result = tool.read("allowed.txt")

        assert result["success"] is True
        assert result["content"] == "allowed content"
