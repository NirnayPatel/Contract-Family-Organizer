#!/bin/bash
set -euo pipefail

# Only run in Claude Code remote (claude.ai/code) sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Install Python dependencies from pyproject.toml
# --no-deps on cryptography avoids conflicts with debian-managed system packages
pip install -e . --quiet || pip install -e . --quiet --upgrade-strategy only-if-needed

# Attempt to install Tesseract OCR for scanned PDF support (optional)
# The tool degrades gracefully if Tesseract is unavailable
if ! command -v tesseract &>/dev/null; then
  apt-get install -y -q tesseract-ocr 2>/dev/null || true
fi

# Make the organizer module importable from any working directory
echo "export PYTHONPATH=\"$CLAUDE_PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"
