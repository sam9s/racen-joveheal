#!/bin/bash
# Simple backup script for pushing to GitHub
# Usage: bash backup.sh "Your commit message"
# Force push: bash backup.sh "Your message" --force

echo "=========================================="
echo "  JoveHeal Git Backup"
echo "=========================================="

# Check if token exists
if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN not found in secrets!"
    exit 1
fi

# Check for --force flag
FORCE_PUSH=""
if [[ "$2" == "--force" ]] || [[ "$1" == "--force" ]]; then
    FORCE_PUSH="--force"
    echo "Force push enabled"
fi

# Remove existing github remote if exists, then add fresh
git remote remove github 2>/dev/null
git remote add github "https://sam9s:${GITHUB_TOKEN}@github.com/sam9s/racen-joveheal.git"

# Get commit message (use default if not provided)
if [[ "$1" == "--force" ]]; then
    MESSAGE="Backup $(date '+%Y-%m-%d %H:%M')"
else
    MESSAGE="${1:-Backup $(date '+%Y-%m-%d %H:%M')}"
fi

# Stage all changes
echo ""
echo "Staging changes..."
git add -A

# Commit
echo "Committing..."
git commit -m "$MESSAGE" || echo "Nothing new to commit"

# Push (force if requested, otherwise normal push)
echo ""
echo "Pushing to GitHub..."
if [ -n "$FORCE_PUSH" ]; then
    git push github main --force
else
    git push github main || {
        echo ""
        echo "=========================================="
        echo "  Push failed - remote has different changes"
        echo "=========================================="
        echo ""
        echo "Your local version is the production version."
        echo "To overwrite GitHub with your local version, run:"
        echo ""
        echo "  bash backup.sh \"Your message\" --force"
        echo ""
        exit 1
    }
fi

echo ""
echo "=========================================="
echo "  Backup complete!"
echo "=========================================="
echo "  Check: https://github.com/sam9s/racen-joveheal"
echo ""
