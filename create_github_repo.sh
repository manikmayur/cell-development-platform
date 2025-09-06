#!/bin/bash

# Cell Development Platform - GitHub Repository Setup Script
# This script helps you create and push to a new GitHub repository

echo "🔋 Cell Development Platform - GitHub Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "cell_development_app.py" ]; then
    echo "❌ Error: Please run this script from the cell-development-platform directory"
    exit 1
fi

echo "✅ Found Cell Development Platform files"

# Test the app first
echo ""
echo "🧪 Testing the application..."
python -c "import cell_development_app; print('✅ App imports successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Application test passed"
else
    echo "❌ Application test failed - please check dependencies"
    echo "Run: pip install -r cell_development_requirements.txt"
    exit 1
fi

echo ""
echo "📋 GitHub Repository Setup Instructions:"
echo "========================================"
echo ""
echo "1. Go to https://github.com/new"
echo "2. Repository name: cell-development-platform"
echo "3. Description: 🔋 Cell Development Platform - A comprehensive Streamlit web application for battery cell development, material analysis, and design optimization"
echo "4. Set to PUBLIC"
echo "5. DO NOT initialize with README, .gitignore, or license (we already have these)"
echo "6. Click 'Create repository'"
echo ""
echo "7. After creating the repository, run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/cell-development-platform.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "8. Replace YOUR_USERNAME with your actual GitHub username"
echo ""

# Check git status
echo "📊 Current Git Status:"
echo "====================="
git status --short
echo ""

# Show recent commits
echo "📝 Recent Commits:"
echo "================="
git log --oneline -5
echo ""

echo "🎉 Setup Complete!"
echo "=================="
echo "Your Cell Development Platform is ready for GitHub deployment."
echo "Follow the instructions above to create and push to your repository."
echo ""
echo "To run the app locally:"
echo "  streamlit run cell_development_app.py"
echo ""
echo "To run the demo:"
echo "  python demo.py"
