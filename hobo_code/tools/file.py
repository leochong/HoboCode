"""File tool implementation with safe path validation."""

import os
from pathlib import Path
from typing import Any


class PathSecurityError(Exception):
    """Raised when path validation fails."""

    pass


class FileTool:
    """Tool for file operations with safe path validation."""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def _validate_path(self, file_path: str) -> Path:
        requested = Path(file_path)
        if requested.is_absolute():
            resolved = requested
        else:
            resolved = (self.base_path / requested).resolve()
        try:
            resolved.relative_to(self.base_path.resolve())
        except ValueError:
            raise PathSecurityError(
                f"Path '{file_path}' is outside the allowed base path '{self.base_path}'"
            )
        return resolved

    def read(self, file_path: str) -> dict[str, Any]:
        """Read file contents.

        Args:
            file_path: Path to the file to read.

        Returns:
            Dictionary with file contents and metadata.
        """
        try:
            path = self._validate_path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found", "path": file_path}
            if not path.is_file():
                return {"success": False, "error": "Not a file", "path": file_path}

            content = path.read_text(encoding="utf-8")
            return {
                "success": True,
                "content": content,
                "path": str(path),
                "size": len(content),
                "lines": content.count("\n") + 1 if content else 0,
            }
        except PathSecurityError as e:
            return {"success": False, "error": str(e), "path": file_path}
        except Exception as e:
            return {"success": False, "error": str(e), "path": file_path}

    def write(self, file_path: str, content: str) -> dict[str, Any]:
        """Write content to a file.

        Args:
            file_path: Path to the file to write.
            content: Content to write.

        Returns:
            Dictionary with operation result.
        """
        try:
            path = self._validate_path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {
                "success": True,
                "path": str(path),
                "size": len(content),
            }
        except PathSecurityError as e:
            return {"success": False, "error": str(e), "path": file_path}
        except Exception as e:
            return {"success": False, "error": str(e), "path": file_path}

    def list(self, directory: str = ".") -> dict[str, Any]:
        """List directory contents.

        Args:
            directory: Path to the directory to list.

        Returns:
            Dictionary with directory contents.
        """
        try:
            path = self._validate_path(directory)
            if not path.exists():
                return {"success": False, "error": "Directory not found", "path": directory}
            if not path.is_dir():
                return {"success": False, "error": "Not a directory", "path": directory}

            items = []
            for item in path.iterdir():
                items.append(
                    {
                        "name": item.name,
                        "is_dir": item.is_dir(),
                        "is_file": item.is_file(),
                        "size": item.stat().st_size if item.is_file() else None,
                    }
                )
            return {
                "success": True,
                "path": str(path),
                "items": items,
                "count": len(items),
            }
        except PathSecurityError as e:
            return {"success": False, "error": str(e), "path": directory}
        except Exception as e:
            return {"success": False, "error": str(e), "path": directory}

    def exists(self, path: str) -> dict[str, Any]:
        """Check if a path exists.

        Args:
            path: Path to check.

        Returns:
            Dictionary with existence status.
        """
        try:
            resolved = self._validate_path(path)
            exists = resolved.exists()
            return {
                "success": True,
                "path": str(resolved),
                "exists": exists,
                "is_file": resolved.is_file() if exists else False,
                "is_dir": resolved.is_dir() if exists else False,
            }
        except PathSecurityError as e:
            return {"success": False, "error": str(e), "path": path}

    def mkdir(self, directory: str, parents: bool = True) -> dict[str, Any]:
        """Create a directory.

        Args:
            directory: Path to the directory to create.
            parents: Create parent directories if they don't exist.

        Returns:
            Dictionary with operation result.
        """
        try:
            path = self._validate_path(directory)
            if parents:
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.mkdir(exist_ok=True)
            return {
                "success": True,
                "path": str(path),
            }
        except PathSecurityError as e:
            return {"success": False, "error": str(e), "path": directory}
        except Exception as e:
            return {"success": False, "error": str(e), "path": directory}

    def remove(self, path: str) -> dict[str, Any]:
        """Remove a file or directory.

        Args:
            path: Path to remove.

        Returns:
            Dictionary with operation result.
        """
        try:
            resolved = self._validate_path(path)
            if not resolved.exists():
                return {"success": False, "error": "Path does not exist", "path": path}

            if resolved.is_dir():
                resolved.rmdir()
            else:
                resolved.unlink()
            return {
                "success": True,
                "path": str(resolved),
            }
        except PathSecurityError as e:
            return {"success": False, "error": str(e), "path": path}
        except Exception as e:
            return {"success": False, "error": str(e), "path": path}

    def search(
        self,
        pattern: str,
        directory: str = ".",
        recursive: bool = True,
    ) -> dict[str, Any]:
        """Search for files matching a pattern.

        Args:
            pattern: Glob pattern to match.
            directory: Directory to search in.
            recursive: Search recursively.

        Returns:
            Dictionary with matching files.
        """
        try:
            base = self._validate_path(directory)
            matches = list(base.glob(pattern)) if recursive else list(base.glob(pattern))
            files = [str(m) for m in matches if m.is_file()]
            return {
                "success": True,
                "pattern": pattern,
                "directory": str(base),
                "files": files,
                "count": len(files),
            }
        except PathSecurityError as e:
            return {"success": False, "error": str(e), "pattern": pattern}
        except Exception as e:
            return {"success": False, "error": str(e), "pattern": pattern}
