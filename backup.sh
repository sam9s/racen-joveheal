#!/bin/bash
# Simple backup script for pushing to GitHub

echo "Starting backup to GitHub..."

# Check if token exists
if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN not found in secrets!"
    exit 1
fi

# Remove existing github remote if exists, then add fresh
git remote remove github 2>/dev/null
git remote add github "https://sam9s:${GITHUB_TOKEN}@github.com/sam9s/racen-joveheal.git"

# Get commit message (use default if not provided)
MESSAGE="${1:-Backup $(date '+%Y-%m-%d %H:%M')}"

# Stage all changes
git add -A

# Commit
git commit -m "$MESSAGE" || echo "Nothing new to commit"

# Pull remote changes first (merge strategy to avoid conflicts)
echo "Pulling remote changes..."
git pull github main --no-rebase --no-edit || {
    echo "Pull failed - attempting to resolve..."
    git pull github main --rebase || {
        echo "ERROR: Could not sync with remote. Manual intervention needed."
        exit 1
    }
}

# Push
git push -u github main

echo ""
echo "Backup complete! Check: https://github.com/sam9s/racen-joveheal"
