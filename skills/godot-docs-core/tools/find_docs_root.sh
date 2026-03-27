#!/usr/bin/env bash
# Source this file after setting SKILL_DIR to get DOCS_SOURCE.
# Usage: source "$(cd "$(dirname "$0")/../godot-docs-core/tools" && pwd)/find_docs_root.sh"
DOCS_SOURCE=""
if [ -d "$SKILL_DIR/../../godot-docs-core/docs_source" ]; then
    DOCS_SOURCE="$(cd "$SKILL_DIR/../../godot-docs-core/docs_source" && pwd)"
else
    _FIND_DOCS_REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
    if [ -d "$_FIND_DOCS_REPO_ROOT/godot-docs" ]; then
        DOCS_SOURCE="$(cd "$_FIND_DOCS_REPO_ROOT/godot-docs" && pwd)"
    elif [ -d "$SKILL_DIR/../godot-docs" ]; then
        DOCS_SOURCE="$(cd "$SKILL_DIR/../godot-docs" && pwd)"
    fi
    unset _FIND_DOCS_REPO_ROOT
fi
if [ -z "$DOCS_SOURCE" ]; then
    echo "Error: Could not find godot-docs directory" >&2
    echo "  Checked: \$SKILL_DIR/../../godot-docs-core/docs_source" >&2
    echo "  Checked: \$SKILL_DIR/../../../godot-docs" >&2
    echo "  Checked: \$SKILL_DIR/../godot-docs" >&2
    exit 1
fi
