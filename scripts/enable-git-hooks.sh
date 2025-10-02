#!/bin/sh
# Enable the repository-local git hooks by setting core.hooksPath
set -e

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
HOOKS_DIR="$REPO_ROOT/.githooks"

if [ ! -d "$HOOKS_DIR" ]; then
  echo "No .githooks directory found at $HOOKS_DIR"
  exit 1
fi

echo "Making hooks executable..."
chmod +x "$HOOKS_DIR"/* || true

echo "Configuring git to use .githooks for this repo..."
git config core.hooksPath "$HOOKS_DIR"

echo "Done. Git hooks enabled."
echo "Note: This is a local config. Other clones will need to run this script too."
