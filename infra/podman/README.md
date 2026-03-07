# Podman Setup (Docker-free Alternative)

Podman is a free, open-source, Docker-compatible container runtime.

## Installation

```bash
# Install Podman
brew install podman

# Initialize Podman machine
podman machine init
podman machine start
```

## Usage

### Using docker-compose.yml with Podman

```bash
# Install podman-compose
brew install podman-compose

# Run the stack
cd infra/docker
podman-compose up -d
```

### Direct Podman Commands (Docker-compatible)

```bash
# Run Neo4j
podman run -d \
  --name bionexus-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.16

# Run Qdrant
podman run -d \
  --name bionexus-qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant:v1.7.0

# Run Redis
podman run -d \
  --name bionexus-redis \
  -p 6379:6379 \
  redis:7-alpine
```

## Check Status

```bash
podman ps
podman logs bionexus-neo4j
```

## Cleanup

```bash
podman-compose down
# or
podman stop bionexus-neo4j bionexus-qdrant bionexus-redis
podman rm bionexus-neo4j bionexus-qdrant bionexus-redis
```

## Notes

- Podman is rootless and daemonless (more secure)
- 100% Docker CLI compatible
- Free and open-source (Apache 2.0 license)
- No need for Docker Desktop subscription
