#!/bin/bash
# Pre-deployment verification script for Render
# Run this before pushing to ensure everything is ready

set -e  # Exit on error

echo "🔍 Running Hermes Backend Deployment Verification..."
echo ""

cd "$(dirname "$0")/.."

# 1. Check requirements.txt syntax
echo "✓ Checking requirements.txt..."
if grep -q "^[^#].*[^=<>].*:" backend/requirements.txt; then
    echo "❌ ERROR: requirements.txt has invalid syntax (colons or plain text)"
    exit 1
fi
if head -1 backend/requirements.txt | grep -qv "^#"; then
    echo "❌ ERROR: requirements.txt first line must be a comment"
    exit 1
fi
echo "  ✅ requirements.txt is valid"

# 2. Check Dockerfile exists and is valid
echo "✓ Checking Dockerfile..."
if [ ! -f "backend/Dockerfile" ]; then
    echo "❌ ERROR: backend/Dockerfile not found"
    exit 1
fi
if ! grep -q "CMD.*backend/run_app.py" backend/Dockerfile; then
    echo "❌ ERROR: Dockerfile CMD doesn't reference run_app.py"
    exit 1
fi
echo "  ✅ Dockerfile is valid"

# 3. Check render.yaml exists and has correct settings
echo "✓ Checking render.yaml..."
if [ ! -f "render.yaml" ]; then
    echo "❌ ERROR: render.yaml not found"
    exit 1
fi
if ! grep -q "dockerfilePath:.*backend/Dockerfile" render.yaml; then
    echo "❌ ERROR: render.yaml doesn't point to backend/Dockerfile"
    exit 1
fi
if ! grep -q "healthCheckPath: /health" render.yaml; then
    echo "⚠️  WARNING: render.yaml health check path may not match /health endpoint"
fi
echo "  ✅ render.yaml is valid"

# 4. Check run_app.py exists and is executable
echo "✓ Checking run_app.py..."
if [ ! -f "backend/run_app.py" ]; then
    echo "❌ ERROR: backend/run_app.py not found"
    exit 1
fi
if ! grep -q "backend.simple_main" backend/run_app.py; then
    echo "❌ ERROR: run_app.py doesn't import backend.simple_main"
    exit 1
fi
echo "  ✅ run_app.py is valid"

# 5. Check simple_main.py exists and has health endpoint
echo "✓ Checking simple_main.py..."
if [ ! -f "backend/simple_main.py" ]; then
    echo "❌ ERROR: backend/simple_main.py not found"
    exit 1
fi
if ! grep -q '@app.get("/health")' backend/simple_main.py; then
    echo "❌ ERROR: simple_main.py missing /health endpoint"
    exit 1
fi
echo "  ✅ simple_main.py is valid"

# 6. Check .dockerignore to ensure .env is excluded
echo "✓ Checking .dockerignore..."
if [ -f "backend/.dockerignore" ]; then
    if ! grep -q "\.env" backend/.dockerignore; then
        echo "⚠️  WARNING: .dockerignore should exclude .env files"
    fi
    echo "  ✅ .dockerignore is valid"
else
    echo "⚠️  WARNING: backend/.dockerignore not found"
fi

# 7. Test Python syntax of key files
echo "✓ Testing Python syntax..."
if ! python3 -m py_compile backend/run_app.py 2>/dev/null; then
    echo "❌ ERROR: run_app.py has syntax errors"
    exit 1
fi
if ! python3 -m py_compile backend/simple_main.py 2>/dev/null; then
    echo "❌ ERROR: simple_main.py has syntax errors"
    exit 1
fi
echo "  ✅ Python files have valid syntax"

# 8. Check for common issues
echo "✓ Checking for common issues..."

# Check for hardcoded ports
if grep -rn "localhost:800" backend/*.py 2>/dev/null | grep -v "^Binary" | grep -v ".pyc" | grep -v "#"; then
    echo "⚠️  WARNING: Found hardcoded localhost ports in backend code"
fi

# Check for print statements in production code (should use logging)
if grep -rn "^print(" backend/*.py 2>/dev/null | grep -v "^Binary" | grep -v ".pyc" | grep -v "run_app.py"; then
    echo "⚠️  INFO: Found print statements (consider using logging)"
fi

echo "  ✅ Common checks passed"

# 9. Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All deployment checks passed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Pre-Deployment Checklist:"
echo "  ✅ requirements.txt is valid"
echo "  ✅ Dockerfile is configured correctly"
echo "  ✅ render.yaml points to correct files"
echo "  ✅ run_app.py exists and imports backend.simple_main"
echo "  ✅ simple_main.py has /health endpoint"
echo "  ✅ Python syntax is valid"
echo ""
echo "🚀 Ready to deploy to Render!"
echo ""
echo "Next steps:"
echo "  1. git add -A"
echo "  2. git commit -m \"Fix deployment configuration\""
echo "  3. git push origin master"
echo ""
echo "🔗 Remember to set environment variables in Render dashboard:"
echo "  - OPENAI_API_KEY"
echo "  - OPENAI_MODEL=gpt-5"
echo "  - NEWS_API_KEY"
echo "  - ALPHAVANTAGE_API_KEY"
echo "  - BINANCE_API_KEY (optional)"
echo "  - BINANCE_API_SECRET (optional)"
echo "  - DATABASE_URL (Render can provision Postgres)"
echo "  - REDIS_URL (optional)"
echo ""
