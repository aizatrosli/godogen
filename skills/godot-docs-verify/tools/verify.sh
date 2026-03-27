#!/bin/bash
# godot-docs-verify - Pre-task documentation validation
# Usage: bash tools/verify.sh "<task description>"
#        bash tools/verify.sh --classes "Class1,Class2" "<task description>"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR"/../..)"
DOCS_LOOKUP_SKILL="$ROOT_DIR/skills/godot-docs-lookup"

# Parse arguments
CLASSES=""
TASK_ARG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --classes)
            CLASSES="$2"
            shift 2
            ;;
        *)
            TASK_ARG="$1"
            shift
            ;;
    esac
done

# Extract task number from task argument
TASK_NUMBER=""
if [[ "$TASK_ARG" =~ ^##\ ([0-9]+)\..* ]]; then
    TASK_NUMBER="${BASH_REMATCH[1]}"
elif [[ "$TASK_ARG" =~ Task\ ([0-9]+) ]]; then
    TASK_NUMBER="${BASH_REMATCH[1]}"
else
    echo "ERROR: Could not extract task number from task description"
    exit 1
fi

# Extract "Classes to use" from task argument if not provided
if [[ -z "$CLASSES" ]]; then
    CLASSES=$(echo "$TASK_ARG" | grep -oP 'Classes to use:\s*\K[^-]+' | head -1 | tr -d ' ')
fi

if [[ -z "$CLASSES" ]]; then
    echo "ERROR: No 'Classes to use' field found in task description"
    echo "Task must include: **Classes to use:** ClassName1, ClassName2, ..."
    exit 1
fi

# Create temp directory
TEMP_DIR="$ROOT_DIR/temp"
mkdir -p "$TEMP_DIR"
OUTPUT_FILE="$TEMP_DIR/docs_lookups_task_$TASK_NUMBER.md"

echo "=== Godot Documentation Verification ==="
echo "Task: $TASK_NUMBER"
echo "Classes to verify: $CLASSES"
echo ""

# Initialize output file
cat > "$OUTPUT_FILE" << EOF
# Task $TASK_NUMBER Documentation Lookup

## Classes Verified

EOF

# Convert comma-separated list to array
IFS=',' read -ra CLASS_ARRAY <<< "$CLASSES"

SUCCESS_COUNT=0
FAILURE_COUNT=0

for CLASS in "${CLASS_ARRAY[@]}"; do
    CLASS=$(echo "$CLASS" | xargs)  # Trim whitespace
    [[ -z "$CLASS" ]] && continue

    echo "Checking: $CLASS"

    # Call godot-docs-lookup for each class
    LOOKUP_RESULT=""
    if bash "$DOCS_LOOKUP_SKILL/tools/search.sh" "class $CLASS" 2>/dev/null; then
        LOOKUP_STATUS="Found"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

        # Find the documentation URL
        DOCS_URL="https://docs.godotengine.org/en/stable/classes/class_${CLASS,,}.html"

        echo "- Status: $LOOKUP_STATUS" >> "$OUTPUT_FILE"
        echo "- Source: $DOCS_URL" >> "$OUTPUT_FILE"
    else
        LOOKUP_STATUS="Not Found"
        FAILURE_COUNT=$((FAILURE_COUNT + 1))

        echo "- Status: $LOOKUP_STATUS" >> "$OUTPUT_FILE"
        echo "- ERROR: Class not found in official documentation" >> "$OUTPUT_FILE"
    fi

    echo "" >> "$OUTPUT_FILE"
done

# Write summary
cat >> "$OUTPUT_FILE" << EOF
## Lookup Summary
- Total classes: ${#CLASS_ARRAY[@]}
- Found: $SUCCESS_COUNT
- Not found: $FAILURE_COUNT

## Verification Status
EOF

if [[ $FAILURE_COUNT -eq 0 ]]; then
    echo "[✓] All $SUCCESS_COUNT classes found in official documentation" >> "$OUTPUT_FILE"
    echo ""
    echo "SUCCESS: All classes verified!"
    echo "Lookup cache saved to: $OUTPUT_FILE"
    exit 0
else
    echo "[✗] $FAILURE_COUNT of ${#CLASS_ARRAY[@]} classes NOT found" >> "$OUTPUT_FILE"
    echo ""
    echo "FAILED: $FAILURE_COUNT class(es) not found in documentation"
    echo "Review $OUTPUT_FILE for details"
    exit 1
fi
