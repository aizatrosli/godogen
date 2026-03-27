#!/usr/bin/env bash
# Parse a Godot class from the documentation
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../godot-docs-core/tools/find_docs_root.sh
source "$SKILL_DIR/../../godot-docs-core/tools/find_docs_root.sh"

# Parse arguments
CLASS_NAME="${1:-}"
OUTPUT_FORMAT="${2:-text}"

if [ -z "$CLASS_NAME" ]; then
    echo "Usage: parse_class.sh <class_name> [text|json]"
    echo ""
    echo "Output formats:"
    echo "  text  - Human readable format (default)"
    echo "  json  - JSON format for programmatic use"
    exit 1
fi

# Find the class file - check file patterns (class_node2d.rst, class_node_2d.rst, etc.)
CLASS_FILE=""
for pattern in "${DOCS_SOURCE}/classes/class_${CLASS_NAME,,}.rst" \
               "${DOCS_SOURCE}/classes/class_${CLASS_NAME,,_2d}.rst" \
               "${DOCS_SOURCE}/classes/class_${CLASS_NAME,,_3d}.rst" \
               "${DOCS_SOURCE}/classes/${CLASS_NAME,,}.rst" \
               "${DOCS_SOURCE}/classes/${CLASS_NAME,,_2d}.rst" \
               "${DOCS_SOURCE}/classes/${CLASS_NAME,,_3d}.rst"; do
    if [ -f "$pattern" ]; then
        CLASS_FILE="$pattern"
        break
    fi
done

# Fallback: search by content (class name at start of file)
if [ -z "$CLASS_FILE" ]; then
    CLASS_FILE=$(find "${DOCS_SOURCE}/classes" -name "*.rst" -type f -exec grep -l "^${CLASS_NAME}$" {} \; 2>/dev/null | head -1)
fi

if [ -z "$CLASS_FILE" ]; then
    echo "Error: Class '$CLASS_NAME' not found"
    echo ""
    echo "Searching for similar classes..."
    SIMILAR=$(find "${DOCS_SOURCE}/classes" -name "*.rst" -type f -exec basename {} .rst \; 2>/dev/null | \
        grep -i "${CLASS_NAME:0:3}" | head -10)
    if [ -n "$SIMILAR" ]; then
        echo "$SIMILAR"
    fi
    exit 1
fi

echo "Class: $CLASS_NAME"
echo "File: $CLASS_FILE"
echo ""

if [ "$OUTPUT_FORMAT" = "json" ]; then
    # Use Python for JSON output
    python3 "${SKILL_DIR}/../tools/parse_class.py" --json "$CLASS_FILE"
else
    # Human readable format
    python3 "${SKILL_DIR}/../tools/parse_class.py" "$CLASS_FILE"
fi
