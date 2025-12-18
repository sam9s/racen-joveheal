# JoveHeal Client Deployment Guide

This guide explains how to deploy the JoveHeal application on your own infrastructure.

## What You're Getting

The JoveHeal application is an AI-powered coaching assistant that includes:

- **Main Chat Interface** - Website visitors can chat with the AI assistant
- **SOMERA Coaching Assistant** - Empathetic coaching support
- **Embeddable Widget** - Add chat to any website with one line of code
- **Admin Dashboard** - Manage conversations and knowledge base

## What You Need to Provide

### 1. Server Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| RAM | 2 GB | 4 GB |
| Storage | 20 GB | 50 GB |
| OS | Ubuntu 20.04+ | Ubuntu 22.04 |
| Docker | v20+ | Latest |
| Docker Compose | v2+ | Latest |

### 2. Your Own API Keys

You must create accounts and get your own API keys:

| Service | Purpose | Where to Get |
|---------|---------|--------------|
| **OpenAI** | AI chat responses | https://platform.openai.com |
| **Google OAuth** | User sign-in | https://console.cloud.google.com |

#### Getting OpenAI API Key
1. Go to https://platform.openai.com
2. Sign up or log in
3. Go to API Keys section
4. Create new secret key
5. Copy and save it securely

#### Getting Google OAuth Credentials
1. Go to https://console.cloud.google.com
2. Create a new project
3. Go to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: Web application
6. Add authorized redirect URI: `https://yourdomain.com/api/auth/callback/google`
7. Copy Client ID and Client Secret

### 3. A Domain Name

You need a domain pointing to your server. Example:
- Main app: `chat.yourdomain.com`
- Admin panel: `admin.chat.yourdomain.com`

## Deployment Steps

### Step 1: Prepare Your Server

Install Docker on your server:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify
docker --version
docker compose version
```

### Step 2: Get the Application Files

You will receive either:
- **Option A**: Access to a private Docker registry (recommended)
- **Option B**: Access to the source code repository

#### Option A: Using Pre-Built Images (Recommended)

Create a file called `docker-compose.yml`:

```yaml
# You will receive this file from the developer
# It references pre-built images that don't expose source code
```

#### Option B: Using Source Code

```bash
git clone [repository-url-provided-to-you]
cd joveheal
```

### Step 3: Configure Environment Variables

Create a file called `.env` in the application folder:

```env
# Your domain (change this!)
DOMAIN=chat.yourdomain.com

# Database (make up a secure password)
POSTGRES_USER=joveheal
POSTGRES_PASSWORD=CHANGE_THIS_TO_SOMETHING_SECURE
POSTGRES_DB=joveheal

# OpenAI (your key from Step 2)
OPENAI_API_KEY=sk-your-key-here

# Security keys (generate random strings)
# Use this command: openssl rand -base64 32
SESSION_SECRET=paste_random_string_here
INTERNAL_API_KEY=paste_another_random_string
NEXTAUTH_SECRET=paste_another_random_string

# Your domain with https
NEXTAUTH_URL=https://chat.yourdomain.com

# Google OAuth (your credentials from Step 2)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Admin login (optional)
DASHBOARD_EMAIL=your@email.com
DASHBOARD_PASSWORD=your_admin_password
```

### Step 4: Point Your Domain to Your Server

In your domain registrar (GoDaddy, Cloudflare, etc.):

1. Find DNS settings
2. Add these records:

| Type | Name | Value |
|------|------|-------|
| A | chat | Your_Server_IP_Address |
| A | admin | Your_Server_IP_Address |

Wait 5-30 minutes for DNS to update.

### Step 5: Start the Application

```bash
docker compose up -d
```

This will:
1. Download all necessary components
2. Set up the database
3. Start all services
4. Get SSL certificates automatically

Wait 1-2 minutes for everything to start.

### Step 6: Verify It's Working

Open your browser and go to:
- `https://chat.yourdomain.com` - You should see the chat interface
- `https://admin.chat.yourdomain.com` - Admin dashboard

## Using the Widget on Your Website

To add the chat widget to any website (like Kajabi), add this code:

```html
<script src="https://chat.yourdomain.com/widget.js"></script>
```

That's it! A chat bubble will appear on your website.

## Common Issues

### "Site can't be reached"
- DNS hasn't updated yet (wait 30 minutes)
- Check if domain points to your server: `ping chat.yourdomain.com`

### "502 Bad Gateway"
- Application is still starting (wait 2 minutes)
- Check status: `docker compose ps`

### "Google sign-in doesn't work"
- Verify the redirect URI in Google Console matches exactly
- Must be: `https://chat.yourdomain.com/api/auth/callback/google`

## Getting Help

For technical support, contact:
- Email: [your support email]
- Response time: [your SLA]

## Monthly Costs (Approximate)

| Service | Cost |
|---------|------|
| OpenAI API | ~$5-50/month (usage-based) |
| VPS Hosting | $10-40/month |
| Domain | $10-15/year |

---

*Document Version: 1.0*
*Last Updated: December 2024*
