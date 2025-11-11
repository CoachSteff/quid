# Docker Files for Quid MCP

This directory contains Docker-related files (currently in project root for standard Docker conventions).

## Files

- `../Dockerfile` - Main Docker image definition
- `../docker-compose.yml` - Docker Compose orchestration
- `../.dockerignore` - Files excluded from Docker build

## Quick Start

```bash
# From project root
docker-compose up -d
```

See [Docker Setup Guide](../docs/guides/DOCKER_SETUP.md) for full documentation.

## Why Files Are in Root

Docker conventions expect these files in the project root:
- `Dockerfile` - Build context starts from root
- `docker-compose.yml` - References root paths
- `.dockerignore` - Applies to root context

This is standard practice for Dockerized projects.
