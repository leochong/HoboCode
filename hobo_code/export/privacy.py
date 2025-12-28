"""Privacy filter for scrubbing PII and secrets from exported data."""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FilterResult:
    """Result of privacy filtering."""

    filtered: bool
    original_text: str
    filtered_text: str
    matches_found: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class FilterConfig:
    """Configuration for privacy filtering."""

    remove_emails: bool = True
    remove_phone_numbers: bool = True
    remove_api_keys: bool = True
    remove_file_paths: bool = True
    remove_ip_addresses: bool = True
    sanitize_absolute_paths: bool = True
    base_path: str = ""
    allowlist_patterns: list[str] = field(default_factory=list)
    blocklist_patterns: list[str] = field(default_factory=list)


class PrivacyFilter:
    """Filter for detecting and removing PII from text."""

    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_PATTERN = re.compile(r"(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")
    API_KEY_PATTERNS = [
        re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),
        re.compile(r"sk-ant-[a-zA-Z0-9-]{20,}", re.IGNORECASE),
        re.compile(r"ghp_[a-zA-Z0-9]{36}", re.IGNORECASE),
        re.compile(r"gho_[a-zA-Z0-9]{36}", re.IGNORECASE),
        re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"),
        re.compile(r"AIza[0-9A-Za-z-_]{35}"),
        re.compile(r"xox[baprs]-([0-9a-zA-Z]{10,48})"),
    ]
    IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
    IPV6_PATTERN = re.compile(r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}")

    def __init__(self, config: FilterConfig | None = None):
        self.config = config or FilterConfig()

    def filter_text(self, text: str) -> FilterResult:
        """Filter PII from text.

        Args:
            text: Text to filter

        Returns:
            FilterResult with filtered content
        """
        filtered_text = text
        matches: list[dict[str, Any]] = []

        if self.config.remove_emails:
            filtered_text, email_matches = self._remove_emails(filtered_text)
            matches.extend(email_matches)

        if self.config.remove_phone_numbers:
            filtered_text, phone_matches = self._remove_phone_numbers(filtered_text)
            matches.extend(phone_matches)

        if self.config.remove_api_keys:
            filtered_text, api_matches = self._remove_api_keys(filtered_text)
            matches.extend(api_matches)

        if self.config.remove_ip_addresses:
            filtered_text, ip_matches = self._remove_ip_addresses(filtered_text)
            matches.extend(ip_matches)

        if self.config.sanitize_absolute_paths and self.config.base_path:
            filtered_text, path_matches = self._sanitize_paths(filtered_text)
            matches.extend(path_matches)

        return FilterResult(
            filtered=len(matches) > 0,
            original_text=text,
            filtered_text=filtered_text,
            matches_found=matches,
        )

    def _remove_emails(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        """Remove email addresses."""
        matches = []
        for match in self.EMAIL_PATTERN.finditer(text):
            matches.append({"type": "email", "value": match.group(), "position": match.span()})

        filtered = self.EMAIL_PATTERN.sub("[EMAIL_REMOVED]", text)
        return filtered, matches

    def _remove_phone_numbers(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        """Remove phone numbers."""
        matches = []
        for match in self.PHONE_PATTERN.finditer(text):
            matches.append({"type": "phone", "value": match.group(), "position": match.span()})

        filtered = self.PHONE_PATTERN.sub("[PHONE_REMOVED]", text)
        return filtered, matches

    def _remove_api_keys(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        """Remove API keys and secrets."""
        matches = []
        for pattern in self.API_KEY_PATTERNS:
            for match in pattern.finditer(text):
                matches.append({"type": "api_key", "value": match.group()[:10] + "...", "position": match.span()})

        for pattern in self.API_KEY_PATTERNS:
            text = pattern.sub("[API_KEY_REMOVED]", text)

        return text, matches

    def _remove_ip_addresses(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        """Remove IP addresses."""
        matches = []
        for match in self.IPV4_PATTERN.finditer(text):
            matches.append({"type": "ipv4", "value": match.group(), "position": match.span()})

        filtered = self.IPV4_PATTERN.sub("[IP_REMOVED]", text)
        return filtered, matches

    def _sanitize_paths(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        """Sanitize absolute file paths."""
        matches = []
        base = self.config.base_path.rstrip("/")

        path_pattern = re.compile(re.escape(base) + r"(/[^\s\"')>\]]+)")
        for match in path_pattern.finditer(text):
            matches.append({"type": "path", "value": match.group(), "position": match.span()})

        filtered = path_pattern.sub("./relative/path", text)
        return filtered, matches

    def filter_dict(self, data: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Recursively filter PII from a dictionary.

        Args:
            data: Dictionary to filter

        Returns:
            Tuple of (filtered_dict, all_matches)
        """
        all_matches = []
        filtered_data = {}

        for key, value in data.items():
            if isinstance(value, str):
                result = self.filter_text(value)
                filtered_data[key] = result.filtered_text
                all_matches.extend(result.matches_found)
            elif isinstance(value, dict):
                sub_filtered, sub_matches = self.filter_dict(value)
                filtered_data[key] = sub_filtered
                all_matches.extend(sub_matches)
            elif isinstance(value, list):
                filtered_list = []
                for item in value:
                    if isinstance(item, str):
                        result = self.filter_text(item)
                        filtered_list.append(result.filtered_text)
                        all_matches.extend(result.matches_found)
                    elif isinstance(item, dict):
                        sub_filtered, sub_matches = self.filter_dict(item)
                        filtered_list.append(sub_filtered)
                        all_matches.extend(sub_matches)
                    else:
                        filtered_list.append(item)
                filtered_data[key] = filtered_list
            else:
                filtered_data[key] = value

        return filtered_data, all_matches

    def filter_jsonl_lines(self, lines: list[str]) -> tuple[list[str], dict[str, Any]]:
        """Filter PII from JSONL lines.

        Args:
            lines: List of JSONL strings

        Returns:
            Tuple of (filtered_lines, stats)
        """
        import json

        filtered_lines = []
        stats = {
            "total_lines": len(lines),
            "filtered_lines": 0,
            "total_matches": 0,
            "matches_by_type": {},
        }

        for line in lines:
            try:
                data = json.loads(line)
                filtered_data, matches = self.filter_dict(data)

                if matches:
                    stats["filtered_lines"] += 1
                    stats["total_matches"] += len(matches)
                    for match in matches:
                        match_type = match.get("type", "unknown")
                        stats["matches_by_type"][match_type] = stats["matches_by_type"].get(match_type, 0) + 1

                    filtered_lines.append(json.dumps(filtered_data))
                else:
                    filtered_lines.append(line)
            except Exception:
                filtered_lines.append(line)

        return filtered_lines, stats

    def dry_run(self, lines: list[str]) -> dict[str, Any]:
        """Preview filtering without modifying data.

        Args:
            lines: List of JSONL strings

        Returns:
            Statistics about what would be filtered
        """
        _, stats = self.filter_jsonl_lines(lines)
        return stats

    def create_config(
        self,
        remove_emails: bool = True,
        remove_phone_numbers: bool = True,
        remove_api_keys: bool = True,
        remove_file_paths: bool = True,
        base_path: str = "",
    ) -> FilterConfig:
        """Create a custom filter configuration.

        Args:
            remove_emails: Whether to remove emails
            remove_phone_numbers: Whether to remove phone numbers
            remove_api_keys: Whether to remove API keys
            remove_file_paths: Whether to remove file paths
            base_path: Base path for path sanitization

        Returns:
            FilterConfig instance
        """
        return FilterConfig(
            remove_emails=remove_emails,
            remove_phone_numbers=remove_phone_numbers,
            remove_api_keys=remove_api_keys,
            remove_file_paths=remove_file_paths,
            sanitize_absolute_paths=bool(base_path),
            base_path=base_path,
        )
