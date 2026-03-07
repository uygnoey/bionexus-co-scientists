# Installation Guide

## Option 1: Podman (Recommended - Free & Open Source)

### Install Podman

```bash
brew install podman podman-compose
```

### Initialize Podman

```bash
podman machine init
podman machine start
```

### Run the Stack

```bash
cd infra/docker
podman-compose up -d
```

### Check Status

```bash
podman ps
```

---

## Option 2: Docker Desktop (Personal Use Free)

### Install Docker Desktop

```bash
brew install --cask docker
```

### Run Docker Desktop App

Open Docker Desktop from Applications.

### Run the Stack

```bash
cd infra/docker
docker-compose up -d
```

---

## Option 3: Backend Only (No Containers)

If you don't want to use containers, you can run Backend directly:

```bash
cd backend
poetry install
cp .env.example .env
# Edit .env with your API keys

poetry run uvicorn app.main:app --reload
```

**Note:** This runs Backend only. Neo4j, Qdrant, and Redis features will not work.

---

## Services

After starting the stack, access:

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Frontend**: http://localhost:3000 (if enabled)

---

## Troubleshooting

### Podman: "machine not running"

```bash
podman machine start
```

### Port already in use

```bash
# Stop existing containers
podman stop --all
# or
docker stop $(docker ps -aq)
```

### Permission denied

```bash
# Podman is rootless, but if issues persist:
podman system reset
podman machine init
podman machine start
```
