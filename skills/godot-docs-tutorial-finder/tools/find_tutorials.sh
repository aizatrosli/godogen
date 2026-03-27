#!/usr/bin/env bash
# Find tutorials matching a topic
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=../godot-docs-core/tools/find_docs_root.sh
source "$SKILL_DIR/../../godot-docs-core/tools/find_docs_root.sh"

# Parse arguments
TOPIC="${1:-movement}"
OUTPUT_FORMAT="${2:-text}"

if [ -z "$TOPIC" ]; then
    echo "Usage: find_tutorials.sh <topic> [text|json]"
    echo ""
    echo "Searches tutorials for the given topic"
    exit 1
fi

echo "Finding tutorials for: '$TOPIC'"
echo "Output: $OUTPUT_FORMAT"
echo ""

# Search for matching tutorials
FOUND_TUTORIALS=""

# Search in tutorials directory
TUTORIAL_RESULTS=$(find "${DOCS_SOURCE}/tutorials" -name "*.rst" -type f 2>/dev/null | while read -r file; do
    if grep -qi "$TOPIC" "$file" 2>/dev/null; then
        echo "$file"
    fi
done)

if [ -n "$TUTORIAL_RESULTS" ]; then
    FOUND_TUTORIALS="$TUTORIAL_RESULTS"
fi

# Also search in getting_started
START_RESULTS=$(find "${DOCS_SOURCE}/getting_started" -name "*.rst" -type f 2>/dev/null | while read -r file; do
    if grep -qi "$TOPIC" "$file" 2>/dev/null; then
        echo "$file"
    fi
done)

if [ -n "$START_RESULTS" ]; then
    if [ -n "$FOUND_TUTORIALS" ]; then
        FOUND_TUTORIALS="$FOUND_TUTORIALS"$'\n'"$START_RESULTS"
    else
        FOUND_TUTORIALS="$START_RESULTS"
    fi
fi

# Output results
if [ "$OUTPUT_FORMAT" = "json" ]; then
    # JSON output — use Python to safely serialize strings
    if [ -n "$FOUND_TUTORIALS" ]; then
        echo "$FOUND_TUTORIALS" | python3 - <<PYEOF
import sys, json

docs_source = """${DOCS_SOURCE}"""
topic = """${TOPIC}"""
tutorials = []
for line in sys.stdin:
    path = line.strip()
    if not path:
        continue
    rel = path.replace(docs_source + "/", "", 1).replace(docs_source + "\\\\", "", 1)
    try:
        with open(path, encoding="utf-8") as f:
            title = f.readline().strip()
    except Exception:
        title = ""
    tutorials.append({"path": rel, "title": title})
print(json.dumps({"topic": topic, "tutorials": tutorials}, ensure_ascii=False, indent=2))
PYEOF
    else
        python3 -c "import json; print(json.dumps({'topic': '${TOPIC}', 'tutorials': []}))"
    fi
else
    # Text output
    if [ -n "$FOUND_TUTORIALS" ]; then
        COUNT=$(echo "$FOUND_TUTORIALS" | wc -l)
        echo "Found $COUNT tutorial(s) for '$TOPIC':"
        echo ""
        echo "$FOUND_TUTORIALS" | while read -r file; do
            if [ -n "$file" ]; then
                REL_PATH=$(echo "$file" | sed "s|^${DOCS_SOURCE}/||")
                # Show first few lines as context
                echo "  $REL_PATH"
                head -3 "$file" | tail -2 | sed 's/^/    /'
                echo ""
            fi
        done
    else
        echo "No tutorials found for '$TOPIC'"
        echo ""
        echo "=== Available Tutorial Categories ==="
        ls -1 "${DOCS_SOURCE}/tutorials" 2>/dev/null
    fi
fi
