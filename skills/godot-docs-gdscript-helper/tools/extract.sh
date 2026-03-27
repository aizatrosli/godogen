#!/usr/bin/env bash
# Extract GDScript examples from godot-docs
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../godot-docs-core/tools/find_docs_root.sh
source "$SKILL_DIR/../../godot-docs-core/tools/find_docs_root.sh"

# Parse arguments
SEARCH_TERM="${1:-}"
SEARCH_TYPE="${2:-file}"

if [ -z "$SEARCH_TERM" ]; then
    echo "Usage: extract.sh <search_term> [class|tutorial|file]"
    echo ""
    echo "Search types:"
    echo "  class    - Extract examples from a specific class reference"
    echo "  tutorial - Extract examples from tutorials matching topic"
    echo "  file     - Extract examples from all RST files (default)"
    exit 1
fi

echo "Extracting GDScript examples for: '$SEARCH_TERM'"
echo "Type: $SEARCH_TYPE"
echo ""

case "$SEARCH_TYPE" in
    class)
        # Find class file and extract GDScript examples
        CLASS_FILE=""
        for pattern in "${DOCS_SOURCE}/classes/${SEARCH_TERM,,}.rst" \
                       "${DOCS_SOURCE}/classes/${SEARCH_TERM,,_2d}.rst" \
                       "${DOCS_SOURCE}/classes/${SEARCH_TERM,,_3d}.rst"; do
            if [ -f "$pattern" ]; then
                CLASS_FILE="$pattern"
                break
            fi
        done

        if [ -z "$CLASS_FILE" ]; then
            echo "Class '$SEARCH_TERM' not found"
            exit 1
        fi

        echo "Class: $CLASS_FILE"
        echo ""
        echo "=== GDScript Examples ==="

        # Use Python to extract code blocks
        python3 "${SKILL_DIR}/../tools/extract_examples.py" --gdscript "$CLASS_FILE"
        ;;

    tutorial)
        # Find tutorials and extract examples
        echo "Searching tutorials for: '$SEARCH_TERM'"
        echo ""

        # Find matching tutorial files
        TUTORIAL_FILES=$(find "${DOCS_SOURCE}/tutorials" -name "*.rst" -type f 2>/dev/null | while read -r file; do
            if grep -qi "$SEARCH_TERM" "$file" 2>/dev/null; then
                echo "$file"
            fi
        done)

        if [ -z "$TUTORIAL_FILES" ]; then
            echo "No tutorials found for '$SEARCH_TERM'"
            exit 1
        fi

        echo "Found $(echo "$TUTORIAL_FILES" | wc -l) tutorial(s)"
        echo ""

        echo "$TUTORIAL_FILES" | while read -r file; do
            REL_PATH=$(echo "$file" | sed "s|^${DOCS_SOURCE}/||")
            echo "--- $REL_PATH ---"

            # Extract GDScript examples
            python3 "${SKILL_DIR}/../tools/extract_examples.py" --gdscript "$file" 2>/dev/null | head -30

            echo ""
        done
        ;;

    *)
        # Extract from all files containing the search term
        echo "Searching all files for: '$SEARCH_TERM'"
        echo ""

        # Find files with the search term
        MATCHING_FILES=$(cd "${DOCS_SOURCE}" && find . -name "*.rst" -type f -exec grep -l -i "$SEARCH_TERM" {} \; 2>/dev/null | head -10)

        if [ -z "$MATCHING_FILES" ]; then
            echo "No files found containing '$SEARCH_TERM'"
            exit 1
        fi

        echo "Found $(echo "$MATCHING_FILES" | wc -l) matching file(s)"
        echo ""

        while IFS= read -r file; do
            [ -z "$file" ] && continue
            REL_PATH=$(echo "$file" | sed 's|^\./||')
            FILEPATH="${DOCS_SOURCE}/${file}"
            echo "--- $REL_PATH ---"

            # Extract GDScript examples
            python3 "${SKILL_DIR}/../tools/extract_examples.py" --gdscript "$FILEPATH" 2>/dev/null | head -30

            echo ""
        done <<< "$MATCHING_FILES"
        ;;
esac
