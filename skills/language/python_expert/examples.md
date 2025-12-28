# Python Examples

## FastAPI with Authentication

### Creating a REST API with FastAPI

```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt

app = FastAPI(
    title="Task Manager API",
    description="API for managing tasks",
    version="1.0.0"
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

# Database simulation
users_db = {}
user_counter = 0

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Endpoints
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    global user_counter
    if any(u["email"] == user.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = user_counter + 1
    hashed = get_password_hash(user.password)
    users_db[user_id] = {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed,
        "is_active": True
    }
    return UserResponse(**users_db[user_id])

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    for u in users_db.values():
        if u["email"] == form_data.username and verify_password(form_data.password, u["hashed_password"]):
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
```

### Running the API
```bash
pip install fastapi uvicorn pydantic[email]
uvicorn main:app --reload
```

## Refactoring to Use Dataclasses

### Before (Regular Classes)
```python
class User:
    def __init__(self, id: int, name: str, email: str, active: bool = True):
        self.id = id
        self.name = name
        self.email = email
        self.active = active

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "active": self.active
        }

    def __repr__(self):
        return f"User({self.id}, {self.name!r})"
```

### After (Dataclasses)
```python
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: str
    active: bool = True
    roles: list[str] = field(default_factory=list)
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def __post_init__(self):
        if not self.email:
            raise ValueError("Email cannot be empty")
```

### With Frozen Immutable Data
```python
@dataclass(frozen=True)
class ImmutableUser:
    id: int
    name: str
    email: str

# Attempting to modify raises FrozenInstanceError
user = ImmutableUser(1, "Alice", "alice@example.com")
user.name = "Bob"  # Error!
```

## Debugging Async Code

### Common Async Patterns and Debugging

```python
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def async_timer(name: str) -> AsyncGenerator[None, None]:
    """Context manager to time async operations."""
    start = asyncio.get_event_loop().time()
    logger.info(f"[{name}] Started")
    try:
        yield
    finally:
        elapsed = asyncio.get_event_loop().time() - start
        logger.info(f"[{name}] Completed in {elapsed:.3f}s")

async def process_items(items: list[int]) -> list[int]:
    """Process items with timing."""
    async with async_timer("process_items"):
        results = []
        for item in items:
            await asyncio.sleep(0.1)  # Simulate work
            results.append(item * 2)
        return results

async def main():
    """Main entry point."""
    logger.info("Starting async processing")
    
    # Process with error handling
    try:
        items = [1, 2, 3, 4, 5]
        results = await process_items(items)
        logger.info(f"Results: {results}")
    except asyncio.CancelledError:
        logger.warning("Processing was cancelled")
        raise
    except Exception as e:
        logger.exception(f"Processing failed: {e}")
        raise

# Run with proper cleanup
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
```

## Pytest Tests

### Fixtures and Parametrization
```python
import pytest
from typing import Generator
from pathlib import Path

@pytest.fixture
def temp_project(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary project structure."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    yield tmp_path

@pytest.fixture
def sample_users():
    """Sample user data."""
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ]

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (10, 20),
    (0, 0),
    (-5, -10),
])
def test_double(input: int, expected: int):
    """Test doubling function."""
    from mymodule import double
    assert double(input) == expected

class TestUserService:
    """Test suite for UserService."""
    
    def test_create_user(self, sample_users):
        from mymodule import UserService
        service = UserService()
        user = service.create_user(**sample_users[0])
        assert user.id == sample_users[0]["id"]
        assert user.name == sample_users[0]["name"]
    
    def test_list_users(self, sample_users, temp_project):
        from mymodule import UserService
        service = UserService(base_path=temp_project)
        users = service.list_users()
        assert len(users) == len(sample_users)

@pytest.mark.asyncio
async def test_async_operation():
    """Test async function."""
    from mymodule import async_fetch
    result = await async_fetch("https://example.com")
    assert result is not None
```

## Using Pathlib

### File Operations with Pathlib
```python
from pathlib import Path
from typing import Generator
import shutil

class ProjectManager:
    def __init__(self, root: str | Path):
        self.root = Path(root)
    
    @property
    def src_dir(self) -> Path:
        """Get source directory."""
        return self.root / "src"
    
    @property
    def tests_dir(self) -> Path:
        """Get tests directory."""
        return self.root / "tests"
    
    def create_module(self, name: str) -> Path:
        """Create a new Python module."""
        module_path = self.src_dir / name
        module_path.mkdir(exist_ok=True)
        (module_path / "__init__.py").write_text("")
        return module_path
    
    def find_python_files(self, pattern: str = "**/*.py") -> Generator[Path, None, None]:
        """Find all Python files matching pattern."""
        yield from self.root.glob(pattern)
    
    def get_file_stats(self) -> dict[str, dict]:
        """Get statistics about Python files."""
        stats = {}
        for py_file in self.find_python_files():
            stats[str(py_file)] = {
                "size": py_file.stat().st_size,
                "lines": len(py_file.read_text().splitlines()),
            }
        return stats
    
    def backup_project(self, backup_dir: Path) -> None:
        """Create a backup of the project."""
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(self.root, backup_dir)

# Usage
manager = ProjectManager("/path/to/project")
manager.create_module("new_feature")
stats = manager.get_file_stats()
```

## Logging Configuration

### Structured Logging
```python
import logging
import json
from datetime import datetime
from typing import Any

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging(name: str = "app") -> logging.Logger:
    """Set up structured logging."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger

# Usage
logger = setup_logging()
logger.info("User logged in", extra={"user_id": 123, "action": "login"})
```

## Environment Variables

### Using pydantic-settings
```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional


class DatabaseSettings(BaseModel):
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "app"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 5
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "My App"
    debug: bool = False
    database: DatabaseSettings = DatabaseSettings()
    api_keys: dict[str, str] = {}
    
    class Config:
        env_prefix = "APP_"
        env_nested_delimiter = "__"


# Usage
settings = Settings()
print(f"Database URL: {settings.database.url}")
```
