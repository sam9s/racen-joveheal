#!/bin/bash
# ==============================================
# Full Backup Script for JoveHeal
# ==============================================
# This script performs a complete backup:
#   1. Database & data backup (PostgreSQL, ChromaDB, docs)
#   2. Git push to GitHub
# ==============================================
# Usage: bash backup_full.sh "Your commit message"
# Force: bash backup_full.sh "Your message" --force
# ==============================================

echo ""
echo "=============================================="
echo "  JoveHeal FULL BACKUP"
echo "=============================================="
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================================="
echo ""

# Get commit message
if [[ "$1" == "--force" ]]; then
    MESSAGE="Full backup $(date '+%Y-%m-%d %H:%M')"
    FORCE_FLAG="--force"
elif [[ "$2" == "--force" ]]; then
    MESSAGE="${1:-Full backup $(date '+%Y-%m-%d %H:%M')}"
    FORCE_FLAG="--force"
else
    MESSAGE="${1:-Full backup $(date '+%Y-%m-%d %H:%M')}"
    FORCE_FLAG=""
fi

echo "Commit message: $MESSAGE"
echo ""

# ============================
# STEP 1: Database & Data Backup
# ============================
echo "=============================================="
echo "  STEP 1: Database & Data Backup"
echo "=============================================="
echo ""

bash backup_db.sh
if [ $? -ne 0 ]; then
    echo "WARNING: Database backup had issues, but continuing..."
fi

echo ""

# ============================
# STEP 2: Git Push to GitHub
# ============================
echo "=============================================="
echo "  STEP 2: Git Push to GitHub"
echo "=============================================="
echo ""

if [ -n "$FORCE_FLAG" ]; then
    bash backup.sh "$MESSAGE" --force
else
    bash backup.sh "$MESSAGE"
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Git backup failed!"
    echo "The database backup was saved locally."
    exit 1
fi

echo ""
echo "=============================================="
echo "  FULL BACKUP COMPLETE!"
echo "=============================================="
echo ""
echo "  Database backup: backups/joveheal_complete_*.tar.gz"
echo "  Git repository: https://github.com/sam9s/racen-joveheal"
echo ""
echo "=============================================="
