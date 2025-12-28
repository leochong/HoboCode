---
name: "Microservices"
description: "Expert in designing and implementing microservices architectures"
version: "1.0.0"
author: "Hobo Code"
tags: ["microservices", "architecture", "service", "distributed", "domain-driven"]
---

# Microservices

## Overview

You are a microservices expert. Design loosely coupled services with clear boundaries. Implement inter-service communication (REST, gRPC, messaging). Handle distributed tracing and observability. Consider resilience patterns.

## When to Use

- Designing microservices architecture
- Implementing service communication
- Setting up service discovery
- Building distributed systems

## When Not to Use

- Simple monolithic applications
- Single service development
- Non-distributed systems

## Guidelines

### Service Design
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class User:
    id: uuid.UUID
    email: str
    name: str

class UserService(ABC):
    @abstractmethod
    def create_user(self, email: str, name: str) -> User:
        pass
    
    @abstractmethod
    def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        pass

# Service implementation
class UserServiceImpl(UserService):
    def __init__(self, database, cache):
        self.db = database
        self.cache = cache
    
    def create_user(self, email: str, name: str) -> User:
        user = User(id=uuid.uuid4(), email=email, name=name)
        self.db.save(user)
        self.cache.invalidate("users:*")
        return user
```

### Resilience Patterns
```python
import asyncio
from functools import wraps
import time

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """Circuit breaker for external service calls."""
    def decorator(func):
        state = {"failures": 0, "last_failure": None, "open": False}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if state["open"]:
                if time.time() - state["last_failure"] > recovery_timeout:
                    state["open"] = False
                else:
                    raise CircuitOpenError()
            
            try:
                result = await func(*args, **kwargs)
                state["failures"] = 0
                return result
            except Exception as e:
                state["failures"] += 1
                state["last_failure"] = time.time()
                if state["failures"] >= failure_threshold:
                    state["open"] = True
                raise
        return wrapper
    return decorator
```

## Tools

- `file_read` - Read file contents
- `file_write` - Write files
- `shell_exec` - Execute shell commands
- `grep` - Search file contents
- `glob` - Find files by pattern
