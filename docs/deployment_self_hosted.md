# JoveHeal Self-Hosted Deployment Guide

This guide is for deploying the JoveHeal application on your own infrastructure (VPS, dedicated server, or cloud VM).

## Prerequisites

Before starting, ensure you have:

- [ ] A VPS or server with Docker and Docker Compose installed
- [ ] A domain name you control
- [ ] Access to the GitHub repository
- [ ] Your own API keys (OpenAI, Google OAuth)

## Deployment Options

You have three reverse proxy options:

| File | Proxy | SSL | Complexity |
|------|-------|-----|------------|
| `docker-compose.caddy.yml` | Caddy | Automatic | Simplest |
| `docker-compose.dokploy.yml` | Traefik | Automatic | For Dokploy users |
| `docker-compose.yml` | Nginx | Manual | Most control |

**Recommended**: Use `docker-compose.caddy.yml` for the easiest setup.

## Step-by-Step Deployment

### Step 1: Prepare Your Server

```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/sam9s/racen-joveheal.git
cd racen-joveheal
```

### Step 3: Create Environment File

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Fill in all required values:

```env
# Domain Configuration
DOMAIN=chat.yourdomain.com

# Database
POSTGRES_USER=joveheal
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=joveheal

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Session Security (generate with: openssl rand -base64 32)
SESSION_SECRET=random_string_here
INTERNAL_API_KEY=another_random_string

# NextAuth (for Google Sign-in)
NEXTAUTH_URL=https://chat.yourdomain.com
NEXTAUTH_SECRET=another_random_string

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Admin Panel (optional)
DASHBOARD_EMAIL=admin@yourdomain.com
DASHBOARD_PASSWORD=secure_password
```

### Step 4: Point DNS to Your Server

In your domain registrar's DNS settings:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | chat | Your_Server_IP | 3600 |
| A | admin | Your_Server_IP | 3600 |

Wait 5-30 minutes for DNS propagation.

### Step 5: Deploy

```bash
# Using Caddy (recommended)
docker compose -f docker-compose.caddy.yml up -d

# OR using Dokploy's Traefik
docker compose -f docker-compose.dokploy.yml up -d

# OR using Nginx
docker compose up -d
```

### Step 6: Verify Deployment

```bash
# Check all containers are running
docker compose ps

# Check logs if something is wrong
docker compose logs -f

# Test the health endpoint
curl https://chat.yourdomain.com/health
```

## Post-Deployment

### Accessing the Application

| URL | Purpose |
|-----|---------|
| `https://chat.yourdomain.com` | Main chat interface |
| `https://chat.yourdomain.com/somera` | SOMERA coaching assistant |
| `https://chat.yourdomain.com/widget.js` | Embeddable widget |
| `https://admin.chat.yourdomain.com` | Admin dashboard |

### Updating the Application

```bash
cd racen-joveheal
git pull origin main
docker compose -f docker-compose.caddy.yml down
docker compose -f docker-compose.caddy.yml up -d --build
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f flask
docker compose logs -f nextjs
```

### Backing Up Data

```bash
# Database backup
docker exec joveheal-postgres pg_dump -U joveheal joveheal > backup.sql

# Copy volumes (if needed)
docker cp joveheal-flask:/app/vector_db ./backup_vector_db
docker cp joveheal-flask:/app/knowledge_base ./backup_knowledge_base
```

## Troubleshooting

### SSL Certificate Not Working
- Ensure DNS is pointing to your server: `nslookup chat.yourdomain.com`
- Wait 30-60 seconds after first start for Caddy to get certificates
- Check Caddy logs: `docker compose logs caddy`

### Database Connection Failed
- Verify POSTGRES_PASSWORD matches in .env
- Check if postgres container is healthy: `docker compose ps`
- View postgres logs: `docker compose logs postgres`

### 502 Bad Gateway
- Services might still be starting (wait 1-2 minutes)
- Check if Flask is healthy: `docker compose logs flask`
- Verify healthchecks: `docker compose ps`

## Security Recommendations

1. **Firewall**: Only open ports 80 and 443
2. **Updates**: Regularly update Docker images
3. **Secrets**: Never commit .env file to Git
4. **Backups**: Schedule regular database backups
5. **Monitoring**: Set up uptime monitoring (UptimeRobot, etc.)
