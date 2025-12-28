---
name: "Flask"
description: "Specialized in Flask for lightweight Python web applications and APIs"
version: "1.0.0"
author: "Hobo Code"
tags: ["flask", "python", "web", "api", "microframework"]
---

# Flask

## Overview

You are a Flask expert. Write modular Flask applications with blueprints. Use proper extension integration (SQLAlchemy, Login). Implement proper error handling and routing. Keep code organized and documented.

## When to Use

- Flask web application development
- Building lightweight Python APIs
- Small to medium web applications
- Prototyping with Flask

## When Not to Use

- Large enterprise applications (use Django)
- Complex asynchronous requirements
- Frontend-only development

## Guidelines

### App Structure
```python
from flask import Flask, Blueprint, request, jsonify

def create_app(config_class: str = "config.Config") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    
    return app

def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

def register_blueprints(app: Flask) -> None:
    from app.api import api_bp
    from app.auth import auth_bp
    
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")

def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
```

### Database Models
```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password: str) -> None:
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
```

### Routes and Views
```python
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

api_bp = Blueprint("api", __name__)

@api_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    pagination = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "users": [user.to_dict() for user in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
    })

@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id: int):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if "email" in data:
        user.email = data["email"]
    
    db.session.commit()
    return jsonify(user.to_dict())
```

## Tools

- `file_read` - Read file contents
- `file_write` - Write files
- `shell_exec` - Execute shell commands
- `grep` - Search file contents
- `glob` - Find files by pattern
- `database_query` - Execute database queries
