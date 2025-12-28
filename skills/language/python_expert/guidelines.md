# Python Guidelines

## Code Style and Formatting

### PEP 8 Compliance
- Use 4 spaces for indentation (no tabs)
- Limit lines to 100 characters
- Use blank lines to separate functions and classes
- Use `snake_case` for functions and variables
- Use `PascalCase` for class names
- Use `UPPER_SNAKE_CASE` for constants

### Import Organization
```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Any, Protocol

# Third-party imports
import requests
import pytest
from fastapi import FastAPI

# Local application imports
from app.models import User
from app.utils import format_date
```

### Docstring Formats

**Google Style:**
```python
def func(arg1: int, arg2: str) -> bool:
    """Short description.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: If arguments are invalid
    """
```

**NumPy Style:**
```python
def func(arg1: int, arg2: str) -> bool:
    """Short description.

    Extended description of function.

    Parameters
    ----------
    arg1 : int
        Description of arg1
    arg2 : str
        Description of arg2

    Returns
    -------
    bool
        Description of return value
    """
```

## Type Hints Best Practices

### Basic Types
```python
def process_items(items: list[str]) -> dict[str, int]:
    """Process a list of strings."""
    return {item: len(item) for item in items}
```

### Union and Optional
```python
from typing import Union, Optional

def find_user(name: str) -> Optional[User]:
    """Find user by name, or None if not found."""
    ...

def parse_value(value: str | int) -> float:
    """Parse value to float."""
    return float(value)
```

### Generics
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
```

### Protocols
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str:
        ...

def render_all(items: list[Renderable]) -> list[str]:
    return [item.render() for item in items]
```

## Async/Await Patterns

### Basic Async
```python
import asyncio
import aiohttp

async def fetch_all(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Semaphore for Rate Limiting
```python
import asyncio

async def rate_limited_fetch(urls: list[str], limit: int = 5) -> list[dict]:
    """Fetch URLs with rate limiting."""
    semaphore = asyncio.Semaphore(limit)

    async def fetch_with_limit(url: str) -> dict:
        async with semaphore:
            return await fetch(url)

    return await asyncio.gather(*[fetch_with_limit(url) for url in urls])
```

### Timeout Handling
```python
import asyncio
from async_timeout import timeout

async def fetch_with_timeout(url: str, timeout_sec: float = 10.0) -> dict:
    """Fetch with explicit timeout."""
    try:
        async with timeout(timeout_sec):
            return await fetch(url)
    except asyncio.TimeoutError:
        logger.error(f"Request timeout: {url}")
        raise
```

## Object-Oriented Patterns

### Data Classes
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str
    active: bool = True
    roles: list[str] = field(default_factory=list)

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles
```

### Slots for Memory Optimization
```python
class MemoryEfficientPoint:
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
```

### ABC and Protocols
```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> None:
        ...

    @abstractmethod
    def load(self, key: str) -> bytes:
        ...
```

## Error Handling Patterns

### Custom Exceptions
```python
class AppError(Exception):
    """Base application error."""
    pass

class ValidationError(AppError):
    """Raised when validation fails."""
    pass

class NotFoundError(AppError):
    """Raised when resource is not found."""
    pass
```

### Context Managers
```python
from contextlib import contextmanager
import logging

@contextmanager
def log_operation(name: str):
    """Log before and after operation."""
    logger.info(f"Starting: {name}")
    try:
        yield
        logger.info(f"Completed: {name}")
    except Exception as e:
        logger.error(f"Failed: {name} - {e}")
        raise

# Usage
with log_operation("backup"):
    create_backup()
```

## Performance Patterns

### Caching
```python
from functools import lru_cache, cache
import time

@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """Expensive computation with caching."""
    time.sleep(1)  # Simulate work
    return n * 2

@cache
def cached_expensive(n: int) -> int:
    """Permanent cache (until process ends)."""
    time.sleep(1)
    return n * 2
```

### Generators for Large Data
```python
def process_large_file(filepath: str):
    """Process file line by line without loading all into memory."""
    with open(filepath) as f:
        for line in f:
            yield process_line(line)

# Usage
for result in process_large_file("big_file.txt"):
    handle_result(result)
```

### itertools for Efficiency
```python
import itertools

# Chained operations
results = itertools.chain(list1, list2, list3)

# Grouping
groups = itertools.groupby(data, key=lambda x: x.category)

# Infinite sequences
evens = itertools.count(0, 2)
```

## Testing Best Practices

### Fixtures
```python
import pytest
from typing import Generator

@pytest.fixture
def sample_data() -> list[dict]:
    """Sample test data."""
    return [{"id": i, "name": f"item_{i}"} for i in range(5)]

@pytest.fixture
def temp_file(tmp_path) -> Generator[Path, None, None]:
    """Temporary file for testing."""
    path = tmp_path / "test.txt"
    path.write_text("test content")
    yield path
```

### Mocking
```python
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_api():
    """Mock API response."""
    with patch('app.api.client') as mock:
        mock.get.return_value.json.return_value = {"status": "ok"}
        yield mock

def test_with_mock(mock_api):
    result = call_api()
    assert result["status"] == "ok"
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("2+2", 4),
    ("3*3", 9),
    ("10/2", 5),
])
def test_calculator(input: str, expected: int):
    assert eval(input) == expected
```
