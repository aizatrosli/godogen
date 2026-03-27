#!/usr/bin/env bash
# Search tool for godot-docs lookup agent
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../godot-docs-core/tools/find_docs_root.sh
source "$SKILL_DIR/../../godot-docs-core/tools/find_docs_root.sh"

# Parse arguments
QUERY="${1:-}"
SEARCH_TYPE="${2:-file}"

if [ -z "$QUERY" ]; then
    echo "Usage: search.sh <search_term> [class|tutorial|file|best_practices]"
    echo ""
    echo "Search types:"
    echo "  class        - Find a specific Godot class"
    echo "  tutorial     - Find tutorials by topic"
    echo "  file         - Search file content (default)"
    echo "  best_practices - Search best_practices directory"
    exit 1
fi

echo "Searching for: '$QUERY'"
echo "Type: $SEARCH_TYPE"
echo "Docs source: $DOCS_SOURCE"
echo ""

case "$SEARCH_TYPE" in
    class)
        # Find class reference
        echo "=== Class Reference ==="

        # Try direct file lookup - check actual file patterns
        FOUND=""
        # Check class_node2d.rst pattern
        if [ -f "${DOCS_SOURCE}/classes/class_${QUERY,,}.rst" ]; then
            FOUND="${DOCS_SOURCE}/classes/class_${QUERY,,}.rst"
        # Check class_node_2d.rst pattern
        elif [ -f "${DOCS_SOURCE}/classes/class_${QUERY,,_2d}.rst" ]; then
            FOUND="${DOCS_SOURCE}/classes/class_${QUERY,,_2d}.rst"
        # Check class_node_3d.rst pattern
        elif [ -f "${DOCS_SOURCE}/classes/class_${QUERY,,_3d}.rst" ]; then
            FOUND="${DOCS_SOURCE}/classes/class_${QUERY,,_3d}.rst"
        # Fallback: no prefix
        elif [ -f "${DOCS_SOURCE}/classes/${QUERY,,}.rst" ]; then
            FOUND="${DOCS_SOURCE}/classes/${QUERY,,}.rst"
        elif [ -f "${DOCS_SOURCE}/classes/${QUERY,,_2d}.rst" ]; then
            FOUND="${DOCS_SOURCE}/classes/${QUERY,,_2d}.rst"
        elif [ -f "${DOCS_SOURCE}/classes/${QUERY,,_3d}.rst" ]; then
            FOUND="${DOCS_SOURCE}/classes/${QUERY,,_3d}.rst"
        fi

        if [ -n "$FOUND" ]; then
            echo "Found: $FOUND"
            echo ""
            head -30 "$FOUND"
            exit 0
        fi

        # Search by content - look for class name at start of file
        echo "Searching by content..."
        CLASS_FILE=$(find "${DOCS_SOURCE}/classes" -name "*.rst" -type f -exec grep -l "^${QUERY}$" {} \; 2>/dev/null | head -1)

        if [ -n "$CLASS_FILE" ]; then
            echo "Found: $CLASS_FILE"
            echo ""
            head -30 "$CLASS_FILE"
        else
            echo "Class '$QUERY' not found in classes/"
            echo ""
            echo "Did you mean one of these?"
            # Show similar class names
            find "${DOCS_SOURCE}/classes" -name "*.rst" -type f -exec basename {} .rst \; 2>/dev/null | \
                grep -i "${QUERY:0:3}" | head -10
        fi
        ;;

    tutorial)
        # Find tutorials by topic
        echo "=== Tutorials ==="

        TUTORIAL_FILES=$(cd "${DOCS_SOURCE}" && find ./tutorials -name "*.rst" -type f -exec grep -l -i "$QUERY" {} \; 2>/dev/null | head -20)

        if [ -n "$TUTORIAL_FILES" ]; then
            COUNT=$(echo "$TUTORIAL_FILES" | wc -l)
            echo "Found $COUNT tutorial(s):"
            echo ""
            echo "$TUTORIAL_FILES" | sed 's|^\./||'
        else
            echo "No tutorials found for '$QUERY'"
            echo ""
            echo "=== Available Tutorial Categories ==="
            ls -1 "${DOCS_SOURCE}/tutorials" 2>/dev/null | head -20
        fi
        ;;

    best_practices)
        # Search best practices directory
        echo "=== Best Practices ==="

        BP_DIR="${DOCS_SOURCE}/tutorials/best_practices"
        if [ ! -d "$BP_DIR" ]; then
            echo "Best practices directory not found"
            exit 1
        fi

        BP_FILES=$(cd "${DOCS_SOURCE}" && find ./tutorials/best_practices -name "*.rst" -type f -exec grep -l -i "$QUERY" {} \; 2>/dev/null)

        if [ -n "$BP_FILES" ]; then
            COUNT=$(echo "$BP_FILES" | wc -l)
            echo "Found $COUNT best practice(s):"
            echo ""
            echo "$BP_FILES" | sed 's|^\./||'
        else
            echo "No best practices found for '$QUERY'"
            echo ""
            find "$BP_DIR" -name "*.rst" -type f 2>/dev/null | head -10
        fi
        ;;

    *)
        # Default: search all files
        echo "=== File Search ==="

        RESULTS=$(cd "${DOCS_SOURCE}" && find . -name "*.rst" -type f -exec grep -l -i "$QUERY" {} \; 2>/dev/null | head -20)

        if [ -n "$RESULTS" ]; then
            COUNT=$(echo "$RESULTS" | wc -l)
            echo "Found '$QUERY' in $COUNT file(s):"
            echo ""
            echo "$RESULTS" | sed 's|^\./||' | while IFS= read -r file; do
                LINE_NUM=$(grep -n "$QUERY" "${DOCS_SOURCE}/$file" 2>/dev/null | head -1 | cut -d: -f1)
                if [ -n "$LINE_NUM" ]; then
                    echo "$file:$LINE_NUM"
                else
                    echo "$file"
                fi
            done
        else
            echo "No files found containing '$QUERY'"
            echo ""
            echo "=== Searchable Areas ==="
            echo "  - classes/     : Godot class API reference"
            echo "  - tutorials/   : Topic tutorials"
            echo "  - getting_started/ : Beginner guides"
            echo "  - engine_details/ : Engine internals"
        fi
        ;;
esac
