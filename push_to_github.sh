#!/bin/bash

# GitHub Push Setup Guide
# Run this script to push your repository to GitHub

echo "🚀 GitHub Push Setup for SportyBet AI Predictor"
echo "================================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository. Run 'git init' first."
    exit 1
fi

echo "✅ Git repository detected"
echo ""

# Prompt for GitHub repository URL
echo "📝 Please create a new repository on GitHub first:"
echo "   1. Go to https://github.com/new"
echo "   2. Name: sportybet-ai-predictor"
echo "   3. Set to Public or Private"
echo "   4. DO NOT initialize with README, .gitignore, or license"
echo ""

read -p "Enter your GitHub repository URL (e.g., https://github.com/BlueS-3e/sportybet-ai-predictor.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Error: Repository URL cannot be empty"
    exit 1
fi

echo ""
echo "🔗 Setting up remote repository..."

# Remove existing remote if it exists
git remote remove origin 2>/dev/null

# Add new remote
git remote add origin "$REPO_URL"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to add remote repository"
    exit 1
fi

echo "✅ Remote repository added: $REPO_URL"
echo ""

# Check if there are commits
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")

if [ "$COMMIT_COUNT" = "0" ]; then
    echo "⚠️  No commits found. Creating initial commit..."
    git add -A
    git commit -m "Initial commit: Production-ready SportyBet AI Predictor"
fi

echo "📊 Repository Status:"
git log --oneline -1
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
echo "   Branch: main"
echo "   Remote: origin"
echo ""

read -p "Ready to push? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Push cancelled"
    exit 0
fi

# Push with upstream tracking
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🎉 Your repository is now available at:"
    echo "   ${REPO_URL%.git}"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Add repository description and topics on GitHub"
    echo "   2. Configure GitHub Actions for CI/CD (optional)"
    echo "   3. Add collaborators if needed"
    echo "   4. Enable GitHub Pages for documentation (optional)"
    echo ""
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   - Check if you have the correct permissions"
    echo "   - Verify the repository URL is correct"
    echo "   - Ensure you're authenticated (use SSH key or GitHub CLI)"
    echo ""
    echo "💡 Try these commands:"
    echo "   git remote -v  # Verify remote URL"
    echo "   git push -u origin main --force  # Force push (use with caution)"
    echo ""
fi
