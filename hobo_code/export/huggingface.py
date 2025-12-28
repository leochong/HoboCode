"""HuggingFace integration for dataset publishing."""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DatasetMetadata:
    """Metadata for a dataset."""

    name: str
    description: str
    license: str = "mit"
    version: str = "1.0.0"
    author: str = "Hobo Code"
    contributors: list[str] = field(default_factory=list)
    task_types: list[str] = field(default_factory=list)
    skills_used: list[str] = field(default_factory=list)
    total_examples: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class HuggingFaceExporter:
    """Exporter for pushing datasets to Hugging Face."""

    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("HF_TOKEN")
        self._datasets_imported = False

    def _import_datasets(self):
        """Lazy import datasets library."""
        if not self._datasets_imported:
            try:
                from datasets import Dataset, DatasetDict
                self.Dataset = Dataset
                self.DatasetDict = DatasetDict
                self._datasets_imported = True
            except ImportError:
                raise ImportError("Please install datasets: pip install datasets")

    def prepare_dataset(
        self,
        jsonl_lines: list[str],
        metadata: DatasetMetadata,
    ) -> Any:
        """Prepare a dataset from JSONL lines.

        Args:
            jsonl_lines: List of JSONL strings
            metadata: Dataset metadata

        Returns:
            Prepared dataset
        """
        self._import_datasets()

        import json

        data = {"text": []}
        for line in jsonl_lines:
            try:
                data["text"].append(json.loads(line))
            except Exception:
                continue

        dataset = self.Dataset.from_dict(data)

        dataset.info.description = metadata.description
        dataset.info.license = metadata.license
        dataset.info.version = metadata.version
        dataset.info.author = metadata.author

        if metadata.contributors:
            dataset.info.contributors = metadata.contributors

        return dataset

    def push_to_hub(
        self,
        dataset: Any,
        repo_id: str,
        commit_message: str | None = None,
        private: bool = False,
    ) -> dict[str, Any]:
        """Push dataset to Hugging Face Hub.

        Args:
            dataset: Prepared dataset
            repo_id: Repository ID (e.g., "username/dataset-name")
            commit_message: Optional commit message
            private: Whether to make dataset private

        Returns:
            Result dictionary
        """
        self._import_datasets()

        if not self.token:
            return {"success": False, "error": "No HuggingFace token provided"}

        commit_msg = commit_message or f"Upload dataset from Hobo Code - {datetime.utcnow().isoformat()}"

        try:
            dataset.push_to_hub(
                repo_id,
                token=self.token,
                commit_message=commit_msg,
                private=private,
            )
            return {
                "success": True,
                "repo_id": repo_id,
                "url": f"https://huggingface.co/datasets/{repo_id}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_dataset_card(
        self,
        metadata: DatasetMetadata,
    ) -> str:
        """Create a README.md for the dataset.

        Args:
            metadata: Dataset metadata

        Returns:
            Markdown content for dataset card
        """
        card = f"""---
license: {metadata.license}
language:
- en
size_categories:
- nSamples: {metadata.total_examples}
task_categories:
- {'- ' + '\n- '.join(metadata.task_types) if metadata.task_types else 'text-generation'}
task_ids:
- {'- ' + '\n- '.join(metadata.task_types) if metadata.task_types else 'dialogue-modeling'}
---

# {metadata.name}

{metadata.description}

## Dataset Information

- **Version**: {metadata.version}
- **Created**: {metadata.created_at}
- **Author**: {metadata.author}
- **Total Examples**: {metadata.total_examples}

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{metadata.name}")
```

## Skills Used

{'- ' + '\n- '.join(metadata.skills_used) if metadata.skills_used else 'General coding assistance'}

## Example Format

Each example is a JSON object with:
- `system`: System prompt
- `messages`: Conversation messages
- `reasoning`: Chain of thought traces
- `tool_calls`: Tool execution records
- `model`: Model used
- `task`: Task type
- `success`: Whether the task was completed successfully
"""

        return card

    def export_with_metadata(
        self,
        jsonl_lines: list[str],
        dataset_name: str,
        description: str,
        license: str = "mit",
        private: bool = False,
    ) -> dict[str, Any]:
        """Export dataset with metadata to HuggingFace.

        Args:
            jsonl_lines: JSONL data
            dataset_name: Name for the dataset
            description: Dataset description
            license: License type
            private: Whether to make private

        Returns:
            Export result
        """
        from hobo_code.export.formatter import JSONLFormatter

        formatter = JSONLFormatter()
        stats = formatter.get_stats(jsonl_lines)

        metadata = DatasetMetadata(
            name=dataset_name,
            description=description,
            license=license,
            total_examples=stats["total_examples"],
            task_types=list(stats.get("task_types", {}).keys()),
            skills_used=stats.get("skills_used", []),
        )

        dataset = self.prepare_dataset(jsonl_lines, metadata)
        repo_id = f"{self._get_username()}/{dataset_name}" if self.token else dataset_name

        return self.push_to_hub(dataset, repo_id, private=private)

    def _get_username(self) -> str:
        """Get HuggingFace username from token."""
        if not self.token:
            return "user"

        try:
            import base64
            payload = self.token.split('.')[0]
            decoded = base64.urlsafe_b64decode(payload + '==')
            import json
            data = json.loads(decoded)
            return data.get("name", "user")
        except Exception:
            return "user"

    def authenticate(self, token: str) -> bool:
        """Test authentication with a token.

        Args:
            token: HuggingFace token

        Returns:
            True if authentication successful
        """
        try:
            from huggingface_hub import whoami
            whoami(token=token)
            self.token = token
            return True
        except Exception:
            return False

    def list_datasets(self, username: str | None = None) -> list[dict[str, Any]]:
        """List user's datasets on HuggingFace.

        Args:
            username: Username (uses token owner if None)

        Returns:
            List of dataset info dictionaries
        """
        if not self.token:
            return []

        try:
            from huggingface_hub import list_datasets
            owner = username or self._get_username()
            datasets = list(list_datasets(author=owner))
            return [{"name": d.id, "url": f"https://huggingface.co/{d.id}"} for d in datasets]
        except Exception:
            return []
