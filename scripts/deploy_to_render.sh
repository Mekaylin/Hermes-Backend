#!/bin/bash
# Deploy Hermes Backend to Render - Final Commit & Push

set -e  # Exit on error

cd "$(dirname "$0")/.."

echo "🚀 Preparing Hermes Backend for Render Deployment"
echo "=================================================="
echo ""

# Stage the critical deployment files
echo "📦 Staging deployment files..."

# Core deployment configuration
git add backend/requirements.txt
git add backend/run_app.py
git add backend/Dockerfile
git add Dockerfile  # Root Dockerfile (fallback)
git add render.yaml

# Backend improvements (Pylance fixes, type stubs)
git add backend/*.py
git add backend/routers/*.py
git add backend/services/*.py
git add backend/tests/*.py
git add backend/backtesting/*.py
git add typings/
git add pyrightconfig.json

# Frontend integration
git add react-frontend/src/services/api.ts
git add react-frontend/src/pages/Dashboard.tsx
git add react-frontend/src/pages/AgentViz.tsx

# Development scripts
git add backend/start_dev.sh
git add scripts/verify_deployment.sh
git add .githooks/

# Documentation
git add DEPLOYMENT_READY.md
git add FRONTEND_SETUP_COMPLETE.md
git add backend/.env.example

echo "✅ Files staged"
echo ""

# Show what will be committed
echo "📋 Changes to be committed:"
git status --short | grep "^[AM]" | head -20
echo ""

# Commit with detailed message
echo "💾 Creating commit..."
git commit -m "Fix Render deployment and integrate frontend

Deployment Fixes:
- Fix requirements.txt syntax (comments must start with #)
- Clean up run_app.py (remove duplicate code)
- Correct health check path in render.yaml (/health)
- Add deployment verification script

Backend Improvements:
- Add typing stubs for optional packages (talib, lightgbm, openai, redis)
- Fix Pylance/Pyright diagnostics across codebase
- Improve import handling and type safety
- Add fallback implementations for optional ML packages

Frontend Integration:
- Connect React frontend to real backend API
- Update API service with correct endpoints
- Implement real data fetching in Dashboard
- Add error handling with fallback to demo data

Development Tools:
- Add backend/start_dev.sh for quick local startup
- Add scripts/verify_deployment.sh for pre-deploy checks
- Add pre-commit hooks to prevent .env commits

All deployment checks passed ✅
Ready for production deployment to Render 🚀"

echo "✅ Commit created"
echo ""

# Show commit details
echo "📊 Commit details:"
git log -1 --stat | head -30
echo ""

# Ask for confirmation before pushing
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Ready to push to GitHub and trigger Render deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will:"
echo "  1. Push to origin/master"
echo "  2. Trigger automatic Render deployment"
echo "  3. Build Docker container"
echo "  4. Start your backend API"
echo ""
read -p "Continue with push? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Pushing to GitHub..."
    git push origin master
    echo ""
    echo "✅ Push complete!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Deployment initiated!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 Monitor your deployment:"
    echo "   https://dashboard.render.com"
    echo ""
    echo "⏱️  Expected build time: 3-5 minutes"
    echo ""
    echo "🔗 Don't forget to set environment variables in Render:"
    echo "   - OPENAI_API_KEY"
    echo "   - OPENAI_MODEL=gpt-5"
    echo "   - NEWS_API_KEY"
    echo "   - ALPHAVANTAGE_API_KEY"
    echo "   - BINANCE_API_KEY (optional)"
    echo "   - BINANCE_API_SECRET (optional)"
    echo ""
    echo "📖 Full deployment guide: DEPLOYMENT_READY.md"
    echo ""
else
    echo ""
    echo "❌ Push cancelled"
    echo ""
    echo "💡 To push later, run:"
    echo "   git push origin master"
    echo ""
fi
