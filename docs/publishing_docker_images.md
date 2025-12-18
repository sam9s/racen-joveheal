# Publishing Docker Images for Client Distribution

This guide explains how to build and publish Docker images so clients can deploy without accessing your source code.

## Overview

```
YOUR WORKFLOW:
Source Code → Build Images → Push to Docker Hub → Give client docker-compose

CLIENT WORKFLOW:
docker-compose up → Pulls YOUR images → Runs application (no source code visible)
```

## Step 1: Create Docker Hub Account

1. Go to https://hub.docker.com
2. Sign up (free tier is fine)
3. Note your username (e.g., `sameer9s`)

## Step 2: Build Images Locally

On your development machine (or Replit):

```bash
# Log in to Docker Hub
docker login

# Build each image with your Docker Hub username
docker build -f Dockerfile.flask -t sameer9s/joveheal-flask:v1.0 .
docker build -f Dockerfile.nextjs -t sameer9s/joveheal-nextjs:v1.0 .
docker build -f Dockerfile.streamlit -t sameer9s/joveheal-admin:v1.0 .
```

## Step 3: Push to Docker Hub

```bash
docker push sameer9s/joveheal-flask:v1.0
docker push sameer9s/joveheal-nextjs:v1.0
docker push sameer9s/joveheal-admin:v1.0
```

## Step 4: Create Client Docker Compose

Create a docker-compose file that uses YOUR pre-built images instead of building from source:

```yaml
# docker-compose.client.yml
# This file uses pre-built images - client cannot see source code

services:
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-joveheal}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-joveheal}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-joveheal}"]
      interval: 10s
      timeout: 5s
      retries: 5

  flask:
    image: sameer9s/joveheal-flask:v1.0  # Pre-built image
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-joveheal}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-joveheal}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SESSION_SECRET=${SESSION_SECRET}
      - INTERNAL_API_KEY=${INTERNAL_API_KEY}
    volumes:
      - vector_db:/app/vector_db
      - knowledge_base:/app/knowledge_base

  nextjs:
    image: sameer9s/joveheal-nextjs:v1.0  # Pre-built image
    restart: unless-stopped
    depends_on:
      - flask
    environment:
      - NEXTAUTH_URL=${NEXTAUTH_URL}
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - INTERNAL_API_KEY=${INTERNAL_API_KEY}
      - FLASK_BACKEND_URL=http://flask:8080

  admin:
    image: sameer9s/joveheal-admin:v1.0  # Pre-built image
    restart: unless-stopped
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-joveheal}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-joveheal}
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
    environment:
      - DOMAIN=${DOMAIN}

volumes:
  postgres_data:
  vector_db:
  knowledge_base:
  caddy_data:
```

## What to Give the Client

1. `docker-compose.client.yml` (uses your pre-built images)
2. `Caddyfile` (routing configuration)
3. `.env.example` (template for their secrets)
4. `docs/deployment_client_handoff.md` (instructions)

## Version Management

When you update the application:

```bash
# Build new version
docker build -f Dockerfile.flask -t sameer9s/joveheal-flask:v1.1 .
docker push sameer9s/joveheal-flask:v1.1

# Also update "latest" tag
docker tag sameer9s/joveheal-flask:v1.1 sameer9s/joveheal-flask:latest
docker push sameer9s/joveheal-flask:latest
```

Tell client to update:
```bash
docker compose pull
docker compose up -d
```

## Private vs Public Images

| Type | Visibility | Client Setup |
|------|-----------|--------------|
| **Public** | Anyone can pull | Just `docker compose up` |
| **Private** | Only authorized users | Client needs `docker login` with access token |

For private images, you give client a read-only access token for Docker Hub.

## Pricing Considerations

- **Docker Hub Free**: 1 private repository, unlimited public
- **Docker Hub Pro ($5/mo)**: Unlimited private repositories

For client distribution, public images are usually fine (code is compiled, not readable).

## Security Notes

1. **Source code is NOT visible** in Docker images (it's compiled/bundled)
2. **Secrets are NOT in images** (client provides via .env)
3. Client can inspect image layers, but not read your actual code
4. For maximum protection, use obfuscation in your build process
