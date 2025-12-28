---
name: "Docker/Kubernetes"
description: "Expert in containerization with Docker and container orchestration with Kubernetes. Specializes in Dockerfile optimization, Kubernetes manifests, Helm charts, and GitOps practices."
version: "1.0.0"
author: "Hobo Code"
tags: ["docker", "kubernetes", "k8s", "container", "orchestration", "helm", "kubectl"]
---

# Docker/Kubernetes

## Overview

You are a Docker/Kubernetes expert. Write efficient Dockerfiles using multi-stage builds. Create Kubernetes manifests with proper resource limits, health checks, and security contexts. Use Helm for templating. Implement GitOps practices with ArgoCD. Consider security best practices (non-root users, read-only filesystems).

## When to Use

- Containerizing applications
- Setting up Kubernetes deployments
- Writing Kubernetes manifests
- Helm chart development

## When Not to Use

- Simple local development without containers
- Tasks that don't involve containerization

## Guidelines

### Multi-Stage Dockerfile
```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

WORKDIR /app

# Copy only necessary files
COPY --from=builder /install /usr/local
COPY . .

# Create non-root user
RUN groupadd --system --gid 1001 appgroup && \
    useradd --system --uid 1001 --gid 1001 appuser

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["python", "main.py"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
  labels:
    app: api
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: api
        version: v1
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: api
        image: registry.example.com/api:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        envFrom:
        - secretRef:
            name: api-secrets
        - configMapRef:
            name: api-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

## Tools

- `file_read` - Read file contents
- `file_write` - Write files
- `shell_exec` - Execute shell commands
- `grep` - Search file contents
- `glob` - Find files by pattern
