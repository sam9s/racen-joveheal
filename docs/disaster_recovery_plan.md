# JoveHeal Disaster Recovery Plan

## Overview

This document provides step-by-step instructions to rebuild the entire JoveHeal application from scratch in the event of a catastrophic failure. The goal is to have the application fully operational within **30 minutes** on any platform.

---

## Prerequisites

Before recovery, ensure you have:

1. **Access to Git repository** (all code is version controlled)
2. **Backup archive** (`joveheal_complete_*.tar.gz`) - download from Replit or use latest Git state
3. **Secret values** (stored securely outside the application):
   - `DATABASE_URL` - PostgreSQL connection string
   - `OPENAI_API_KEY` - OpenAI API key
   - `NEXTAUTH_SECRET` - Session encryption key
   - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` - OAuth credentials
   - `SESSION_SECRET` - Flask session secret

---

## Recovery Options

### Option 1: New Replit Instance (Fastest - ~15 minutes)

**Step 1: Create new Repl from Git**
1. Go to [replit.com](https://replit.com) and click "Create Repl"
2. Select "Import from GitHub"
3. Paste repository URL: `https://github.com/YOUR_USERNAME/jove-heal-chatbot`
4. Click "Import from GitHub"

**Step 2: Set up Secrets**
In the Secrets tab, add:
```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
NEXTAUTH_SECRET=...
NEXTAUTH_URL=https://your-new-repl.replit.app
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SESSION_SECRET=...
INTERNAL_API_KEY=... (generate new: openssl rand -base64 32)
```

**Step 3: Create PostgreSQL Database**
1. In the Replit Tools panel, click "Database"
2. Create a new PostgreSQL database
3. Copy the new `DATABASE_URL` to Secrets

**Step 4: Install Dependencies**
```bash
npm install
pip install -r requirements.txt
```

**Step 5: Restore Data from Backup**
```bash
# Extract backup
tar -xzf joveheal_complete_YYYY-MM-DD_*.tar.gz
cd joveheal_backup_*

# Restore PostgreSQL
psql "$DATABASE_URL" < postgresql.sql

# Restore ChromaDB
cp -r vector_db ../

# Restore knowledge base
cp -r knowledge_base ../
```

**Step 6: Build and Deploy**
```bash
npm run build
```
Then click "Publish" → "Autoscale" to deploy.

---

### Option 2: External VPS with Docker (Recommended for independence)

See `docker-compose.yml` for complete deployment configuration.

**Step 1: Prepare Server**
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com | sh
sudo apt install docker-compose -y
```

**Step 2: Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/jove-heal-chatbot.git
cd jove-heal-chatbot
```

**Step 3: Create Environment File**
```bash
cp .env.example .env
# Edit .env with your secret values
nano .env
```

**Step 4: Start Services**
```bash
docker-compose up -d
```

**Step 5: Restore Data (if using backup)**
```bash
# Extract backup
tar -xzf joveheal_complete_*.tar.gz
cd joveheal_backup_*

# Create data directories for host-mounted volumes
mkdir -p ../data/vector_db ../data/knowledge_base

# Restore PostgreSQL
docker-compose exec -T postgres psql -U joveheal joveheal < postgresql.sql

# Restore ChromaDB and knowledge base to host-mounted paths
cp -r vector_db/* ../data/vector_db/
cp -r knowledge_base/* ../data/knowledge_base/
```

**Step 6: Verify Deployment**
```bash
curl http://localhost:5000/health
curl http://localhost:8080/health
```

---

### Option 3: Manual Rebuild (No backup available)

If no backup is available, the application can still be rebuilt from Git:

**Step 1: Clone and Install**
```bash
git clone https://github.com/YOUR_USERNAME/jove-heal-chatbot.git
cd jove-heal-chatbot
npm install
pip install -r requirements.txt
```

**Step 2: Set Environment Variables**
Set all required secrets (see Prerequisites section).

**Step 3: Initialize Empty Database**
```bash
python -c "from database import init_database; init_database()"
```

**Step 4: Rebuild Knowledge Base**
The knowledge base will be empty. You'll need to:
1. Go to Admin Panel (http://localhost:5001)
2. Upload documents or ingest website content
3. ChromaDB will rebuild automatically

**Step 5: Build and Start**
```bash
npm run build
bash start_production.sh
```

---

## Data Recovery Details

### PostgreSQL Tables

| Table | Purpose | Can Rebuild? |
|-------|---------|--------------|
| `user_accounts` | User profiles | No - user data is lost |
| `chat_sessions` | Session tracking | No - history is lost |
| `conversations` | Chat history | No - history is lost |
| `response_feedback` | User feedback | No - feedback is lost |
| `analytics_daily` | Pre-computed analytics | Yes - recalculates |
| `conversation_summaries` | Personalization data | Yes - regenerates |

### ChromaDB Collections

| Collection | Purpose | Can Rebuild? |
|------------|---------|--------------|
| `jovee_knowledge_base` | Website content + docs | Yes - re-ingest from sources |
| `somera_coaching` | SOMERA video transcripts | Partial - need original transcripts |

### Critical Files

| File/Directory | Purpose | In Git? |
|----------------|---------|---------|
| `vector_db/` | ChromaDB data | No - backup separately |
| `knowledge_base/` | Uploaded documents | No - backup separately |
| `somera_content/` | SOMERA transcripts | Yes - in Git |
| `.next/` | Build output | No - regenerate with `npm run build` |

---

## Backup Schedule

**Recommended backup frequency:**

| Data Type | Frequency | Retention |
|-----------|-----------|-----------|
| Full backup (all data) | Daily | 7 days |
| PostgreSQL only | Every 6 hours | 3 days |
| Before major changes | Manual | 30 days |

**Automated backup command:**
```bash
python disaster_recovery/backup.py
```

---

## Recovery Verification Checklist

After recovery, verify each component:

- [ ] Homepage loads: `curl https://your-domain.com/`
- [ ] Health endpoint: `curl https://your-domain.com/health`
- [ ] Flask backend: `curl https://your-domain.com/api/chat -X POST`
- [ ] Widget loads: `curl https://your-domain.com/widget.js`
- [ ] SOMERA page: `curl https://your-domain.com/somera`
- [ ] Admin panel: Access port 5001 or `/admin`
- [ ] Database connection: Check conversation logging works
- [ ] ChromaDB: Test a chat query returns relevant results

---

## Emergency Contacts

| Role | Contact | Purpose |
|------|---------|---------|
| Replit Support | support@replit.com | Platform issues |
| OpenAI Status | status.openai.com | API issues |
| Google Cloud Console | console.cloud.google.com | OAuth issues |

---

## Document History

| Date | Change | Author |
|------|--------|--------|
| 2024-12-18 | Initial creation after production incident | Agent |
