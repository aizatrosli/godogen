#!/usr/bin/env bash
# Search best practices in godot-docs
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../godot-docs-core/tools/find_docs_root.sh
source "$SKILL_DIR/../../godot-docs-core/tools/find_docs_root.sh"

# Parse arguments
TOPIC="${1:-best_practices}"

if [ -z "$TOPIC" ]; then
    echo "Usage: search.sh <topic>"
    echo ""
    echo "Search best practices, performance tips, and patterns"
    exit 1
fi

echo "Searching best practices for: '$TOPIC'"
echo ""

# Search best_practices directory
echo "=== Best Practices ==="
BP_DIR="${DOCS_SOURCE}/tutorials/best_practices"

if [ -d "$BP_DIR" ]; then
    BP_FILES=$(find "$BP_DIR" -name "*.rst" -type f 2>/dev/null | while read -r file; do
        if grep -qi "$TOPIC" "$file" 2>/dev/null; then
            echo "$file"
        fi
    done)

    if [ -n "$BP_FILES" ]; then
        echo "Found $(echo "$BP_FILES" | wc -l) best practice(s):"
        echo ""
        echo "$BP_FILES" | while read -r file; do
            REL_PATH=$(echo "$file" | sed "s|^${DOCS_SOURCE}/||")
            echo "  - $REL_PATH"
            head -5 "$file" | tail -4 | sed 's/^/      /'
            echo ""
        done
    else
        echo "No best practices found for '$TOPIC'"
        echo ""
        echo "Available best practice files:"
        find "$BP_DIR" -name "*.rst" -type f 2>/dev/null | head -10
    fi
else
    echo "Best practices directory not found"
fi

# Also search performance
echo ""
echo "=== Performance Tips ==="
PERF_DIR="${DOCS_SOURCE}/tutorials/performance"

if [ -d "$PERF_DIR" ]; then
    PERF_FILES=$(find "$PERF_DIR" -name "*.rst" -type f 2>/dev/null | while read -r file; do
        if grep -qi "$TOPIC" "$file" 2>/dev/null; then
            echo "$file"
        fi
    done)

    if [ -n "$PERF_FILES" ]; then
        echo "Found $(echo "$PERF_FILES" | wc -l) performance tip(s):"
        echo ""
        echo "$PERF_FILES" | while read -r file; do
            REL_PATH=$(echo "$file" | sed "s|^${DOCS_SOURCE}/||")
            echo "  - $REL_PATH"
        done
    fi
fi

# Search troubleshooting
echo ""
echo "=== Troubleshooting ==="
TROUBLE_DIR="${DOCS_SOURCE}/tutorials/troubleshooting"

if [ -d "$TROUBLE_DIR" ]; then
    TROUBLE_FILES=$(find "$TROUBLE_DIR" -name "*.rst" -type f 2>/dev/null | while read -r file; do
        if grep -qi "$TOPIC" "$file" 2>/dev/null; then
            echo "$file"
        fi
    done)

    if [ -n "$TROUBLE_FILES" ]; then
        echo "Found $(echo "$TROUBLE_FILES" | wc -l) troubleshooting tip(s):"
        echo ""
        echo "$TROUBLE_FILES" | while read -r file; do
            REL_PATH=$(echo "$file" | sed "s|^${DOCS_SOURCE}/||")
            echo "  - $REL_PATH"
        done
    fi
fi
