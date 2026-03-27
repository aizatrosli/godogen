#!/usr/bin/env bash
# Helper script for finding tutorials in godot-docs
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=find_docs_root.sh
source "$SKILL_DIR/find_docs_root.sh"

# Default search
TOPIC="${1:-movement}"

echo "Searching tutorials for: $TOPIC"
echo "Docs source: $DOCS_SOURCE"
echo ""

# Search in tutorials directory
echo "=== Tutorials ==="
find "$DOCS_SOURCE/tutorials" -name "*.rst" -type f 2>/dev/null | while read -r file; do
    if grep -qi "$TOPIC" "$file" 2>/dev/null; then
        echo "  $file"
    fi
done

# Search in getting_started
echo ""
echo "=== Getting Started ==="
find "$DOCS_SOURCE/getting_started" -name "*.rst" -type f 2>/dev/null | while read -r file; do
    if grep -qi "$TOPIC" "$file" 2>/dev/null; then
        echo "  $file"
    fi
done

# List available tutorial categories
echo ""
echo "=== Available Tutorial Categories ==="
ls -1 "$DOCS_SOURCE/tutorials" 2>/dev/null | head -20
