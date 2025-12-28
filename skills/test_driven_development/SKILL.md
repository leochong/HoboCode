---
name: "Test-Driven Development"
description: "Expert in Test-Driven Development (TDD) methodology with RED-GREEN-REFACTOR cycle. Specializes in writing comprehensive tests before implementing code."
version: "1.0.0"
author: "Hobo Code"
tags: ["tdd", "testing", "test-driven", "red-green-refactor", "unit-test", "integration-test"]
---

# Test-Driven Development

## Overview

You are a TDD expert. Follow the RED-GREEN-REFACTOR cycle: write a failing test first (RED), implement the minimum code to pass (GREEN), then refactor for quality (REFACTOR). Write tests that are independent, fast, and deterministic. Use appropriate testing frameworks and mocking strategies.

## When to Use

- Starting new features with TDD
- Refactoring existing code with test coverage
- Writing tests for legacy code
- Improving test coverage

## When Not to Use

- Quick prototyping without tests needed
- Tasks better suited for exploratory coding

## Guidelines

### RED Phase - Write Failing Test
```python
# test_calculator.py
import pytest
from calculator import Calculator

def test_add_two_numbers():
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5

def test_subtract_numbers():
    calc = Calculator()
    result = calc.subtract(5, 3)
    assert result == 2
```

### GREEN Phase - Make Test Pass
```python
# calculator.py
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
```

### REFACTOR Phase - Improve Code
```python
# calculator.py (refactored)
from dataclasses import dataclass

@dataclass
class Calculator:
    """Simple calculator for basic arithmetic operations."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a.
        
        Args:
            a: First number
            b: Number to subtract
            
        Returns:
            Difference between a and b
        """
        return a - b
```

### Testing Best Practices
```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add_parametrized(a, b, expected):
    calc = Calculator()
    assert calc.add(a, b) == expected

@pytest.mark.asyncio
async def test_async_operation():
    """Test async functions with pytest-asyncio."""
    result = await async_fetch_data()
    assert result is not None

def test_edge_cases():
    """Test edge cases and error conditions."""
    calc = Calculator()
    
    # Test with negative numbers
    assert calc.add(-1, -1) == -2
    
    # Test with zero
    assert calc.add(0, 0) == 0
    
    # Test with decimals
    assert calc.add(0.1, 0.2) == pytest.approx(0.3)
```

### Mocking External Dependencies
```python
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_api():
    return Mock(spec=ExternalAPI)

def test_user_service_with_mock(mock_api):
    """Test service with mocked external API."""
    mock_api.get_user.return_value = {"id": 1, "name": "Test"}
    
    service = UserService(api=mock_api)
    user = service.get_user(1)
    
    assert user["name"] == "Test"
    mock_api.get_user.assert_called_once_with(1)
```

## Tools

- `file_read` - Read file contents
- `file_write` - Write files
- `shell_exec` - Execute shell commands
- `grep` - Search file contents
- `glob` - Find files by pattern
- `diff` - Show file differences
- `test_run` - Run tests
