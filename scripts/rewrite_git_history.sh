#!/bin/bash
# Rewrite git history to remove secrets from commit 4ef9a16

set -e

echo "🔄 Rewriting git history to remove secrets..."

# Create a backup branch
git branch -D backup-before-history-rewrite 2>/dev/null || true
git branch backup-before-history-rewrite
echo "✅ Created backup branch: backup-before-history-rewrite"

# Save the current HEAD
CURRENT_HEAD=$(git rev-parse HEAD)
echo "📍 Current HEAD: $CURRENT_HEAD"

# Reset to the remote HEAD (d4a48ec)
echo "⏪ Resetting to origin/main (d4a48ec)..."
git reset --hard origin/main

# Now all the files from both commits are in the working directory but not committed
# Let's get all the changes from both commits
git checkout backup-before-history-rewrite -- .

echo "✅ All changes from local commits restored to working directory"

# Sanitize any remaining secrets in the files
echo "🧹 Sanitizing files..."
find docs -name "*.md" -type f -exec sed -i 's/pat9wRDiRC8Fen7CO\.3413cf6bfc7026d2d2001d531a7f64cf91a3aacd760746d6ac8263bd929455ff/YOUR_AIRTABLE_API_KEY/g' {} \;

echo "✅ Files sanitized"

# Show status
git status --short | head -20

echo ""
echo "✅ History rewrite preparation complete!"
echo "📝 Next: Review changes and create clean commit"
