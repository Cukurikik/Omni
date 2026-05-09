#!/bin/bash

# OMNI Framework Publisher Script
# Updates repository navigation links and package release information

echo "🚀 OMNI Framework Publisher v2.1.0"
echo "===================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository. Initializing..."
    git init
else
    echo "✅ Git repository detected"
fi

# Fetch the latest changes from remote
echo "🔄 Fetching latest changes..."
git fetch origin

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    # If we're in detached HEAD state or no branch, default to main
    CURRENT_BRANCH="main"
fi

echo "📋 Current branch: $CURRENT_BRANCH"

# Update the repository
echo "📥 Pulling latest changes..."
git pull origin "$CURRENT_BRANCH" || echo "⚠️  No remote to pull from, continuing..."

# Show status
echo "📊 Repository status:"
git status

# Add all changes
echo "📝 Adding all changes..."
git add .

# Create commit if there are changes
if git diff-index --quiet HEAD --; then
    echo "✅ Repository is already up to date"
else
    echo "📦 Creating new commit with updates..."
    
    # Get timestamp for commit message
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    COMMIT_MSG="Publish: Update repository navigation links and package release info
    
- Update version to 2.1.0
- Update repository URLs
- Update package release information
- Update documentation links
- Update registry information

Timestamp: $TIMESTAMP"
    
    git commit -m "$COMMIT_MSG"
    
    # Push to remote
    echo "📤 Pushing changes to remote repository..."
    git push origin "$CURRENT_BRANCH"
    
    if [ $? -eq 0 ]; then
        echo "🎉 Successfully published updates!"
        echo "🔗 Main Repository: https://github.com/omni-framework/omni"
        echo "📦 Package Registry: https://nexus.omniframework.dev"
        echo "📚 Documentation: https://docs.omniframework.dev"
    else
        echo "❌ Failed to push changes"
        exit 1
    fi
fi

echo "✨ Publishing process completed!"