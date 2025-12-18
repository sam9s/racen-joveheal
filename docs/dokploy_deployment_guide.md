# JoveHeal Dokploy Deployment Guide

This guide explains how to deploy your JoveHeal application on a Hostinger VPS using Dokploy.

## Overview

**What is Dokploy?**
Dokploy is a self-hosted deployment platform (like Vercel/Heroku but on your own server). It runs Docker Compose files and automatically handles:
- SSL certificates (HTTPS)
- Domain routing
- Container management
- Auto-deploy on Git push

## How Your Application Works

```
┌──────────────────────────────────────────────────────────────┐
│                     DOKPLOY (on your VPS)                    │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                     TRAEFIK                              │ │
│  │  (handles domains, SSL, routing - provided by Dokploy)   │ │
│  └──────────────────────────┬──────────────────────────────┘ │
│                             │                                 │
│        ┌────────────────────┼────────────────────┐           │
│        │                    │                    │           │
│        ▼                    ▼                    ▼           │
│  ┌──────────┐         ┌──────────┐        ┌──────────┐      │
│  │ NEXT.JS  │         │  FLASK   │        │STREAMLIT │      │
│  │ Frontend │ ◄──────►│  Backend │        │  Admin   │      │
│  │(website) │         │ (AI/API) │        │ (panel)  │      │
│  └──────────┘         └────┬─────┘        └──────────┘      │
│                            │                                 │
│                            ▼                                 │
│                     ┌──────────────┐                        │
│                     │  POSTGRESQL  │                        │
│                     │  (database)  │                        │
│                     └──────────────┘                        │
└──────────────────────────────────────────────────────────────┘
```

### Service Roles

| Service | Port | Purpose |
|---------|------|---------|
| **Next.js** | 5000 | The website visitors see (chat widget, pages) |
| **Flask** | 8080 | AI chatbot brain (OpenAI, RAG, knowledge base) |
| **PostgreSQL** | 5432 | Stores conversations, users, feedback |
| **Streamlit** | 5001 | Admin dashboard (you access this) |
| **Traefik** | 80/443 | Routes traffic (Dokploy provides this) |

## Prerequisites

Before deploying, ensure you have:

1. **Hostinger VPS** with Dokploy installed
2. **Domain** pointed to your VPS IP (A record)
3. **GitHub repository** connected to Dokploy
4. **Environment secrets** ready (see below)

## Step-by-Step Deployment

### Step 1: Push Code to GitHub

Run the backup script on Replit:
```bash
bash backup.sh "Ready for Dokploy deployment"
```

### Step 2: Create Project in Dokploy

1. Log into Dokploy dashboard
2. Click **Create Project**
3. Name it: `joveheal` (or similar)

### Step 3: Add Docker Compose Service

1. In your project, click **Add Service → Docker Compose**
2. Select **GitHub** as source
3. Choose repository: `sam9s/racen-joveheal`
4. Branch: `main`
5. Compose file path: `./docker-compose.dokploy.yml`

### Step 4: Configure Environment Variables

In the **Environment** tab, add these secrets:

#### Required Secrets

| Variable | Description | Example |
|----------|-------------|---------|
| `DOMAIN` | Your domain | `chat.joveheal.com` |
| `POSTGRES_PASSWORD` | Database password | (generate random) |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `SESSION_SECRET` | Flask session secret | (generate random) |
| `INTERNAL_API_KEY` | Internal API auth | (generate random) |
| `NEXTAUTH_URL` | Full URL with https | `https://chat.joveheal.com` |
| `NEXTAUTH_SECRET` | NextAuth encryption | (generate random) |
| `GOOGLE_CLIENT_ID` | Google OAuth | (from Google Console) |
| `GOOGLE_CLIENT_SECRET` | Google OAuth | (from Google Console) |

#### Optional Secrets

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database user | `joveheal` |
| `POSTGRES_DB` | Database name | `joveheal` |
| `DASHBOARD_EMAIL` | Admin login email | (none) |
| `DASHBOARD_PASSWORD` | Admin login password | (none) |
| `ADMIN_EMAILS` | Comma-separated admin emails | (none) |

**Generating Random Secrets:**
```bash
openssl rand -base64 32
```

### Step 5: Configure DNS

Point these domains to your VPS IP:

| Record Type | Name | Value |
|-------------|------|-------|
| A | `chat` | Your VPS IP |
| A | `admin` (optional) | Your VPS IP |

Wait for DNS propagation (5-30 minutes).

### Step 6: Deploy

1. Click **Deploy** in Dokploy
2. Watch the logs - first build takes 5-10 minutes
3. Once healthy, visit `https://chat.joveheal.com`

## Domain Routing (How Traefik Works)

The `docker-compose.dokploy.yml` file includes Traefik labels that tell Dokploy:

```yaml
labels:
  - "traefik.http.routers.joveheal-web.rule=Host(`${DOMAIN}`)"
```

This means:
- `chat.joveheal.com` → Next.js (main website)
- `chat.joveheal.com/api/*` → Flask (API endpoints)
- `admin.chat.joveheal.com` → Streamlit (admin panel)

Traefik automatically gets SSL certificates from Let's Encrypt.

## File Differences: Original vs Dokploy

| File | Purpose |
|------|---------|
| `docker-compose.yml` | For manual VPS with Nginx |
| `docker-compose.dokploy.yml` | For Dokploy with Traefik |

**Key differences:**
1. Dokploy version has no Nginx (Traefik replaces it)
2. Dokploy version connects to `dokploy-network`
3. Dokploy version uses Traefik labels for routing

## Troubleshooting

### Build Fails
- Check logs in Dokploy dashboard
- Ensure all required env vars are set
- Verify Dockerfiles exist in repo

### SSL Certificate Not Working
- Check DNS propagation: `nslookup chat.joveheal.com`
- Wait 10-30 seconds after first deploy
- Check Traefik logs in Dokploy

### Database Connection Failed
- PostgreSQL starts first (healthcheck ensures this)
- Verify `POSTGRES_PASSWORD` is set correctly
- Check Flask logs for connection errors

### Site Shows 502 Error
- Services might still be starting (wait 1-2 minutes)
- Check if healthchecks are passing in Dokploy
- Review service logs for crashes

## Updating Your App

After making changes on Replit:

1. Run: `bash backup.sh "Description of changes"`
2. In Dokploy: Click **Redeploy** (or enable auto-deploy)
3. Dokploy pulls latest code and rebuilds

## Data Persistence

Your data is stored in Docker volumes:
- `postgres_data` - Database (conversations, users)
- `vector_db_data` - ChromaDB embeddings
- `knowledge_base_data` - Uploaded documents
- `logs_data` - Application logs

These volumes persist across container restarts and redeployments.

## Backup Strategy

Even on your own VPS, you should backup:

1. **Database**: Use Dokploy's backup feature or schedule pg_dump
2. **Git**: Your code is already on GitHub
3. **Volumes**: Optional - backup `/var/lib/docker/volumes/`

## Cost Comparison

| Platform | Monthly Cost | Notes |
|----------|-------------|-------|
| Replit Autoscale | ~$50+/week | Current, managed |
| Hostinger VPS | $10-20/month | Self-managed |
| Dokploy | Free | Runs on your VPS |

Moving to Dokploy significantly reduces costs but requires you to manage the server.
