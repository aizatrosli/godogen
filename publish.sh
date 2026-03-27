#!/usr/bin/env bash
# Publish godogen skills into a target project directory.
# Creates .claude/skills/ and copies a CLAUDE.md.
#
# Usage: ./publish.sh <target_dir> [claude_md]
#   claude_md  Path to CLAUDE.md to use (default: game.md)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <target_dir> [claude_md]"
    exit 1
fi

TARGET="$(cd "$1" 2>/dev/null && pwd || (mkdir -p "$1" && cd "$1" && pwd))"
CLAUDE_MD="${2:-$REPO_ROOT/game.md}"

echo "Publishing to: $TARGET"

mkdir -p "$TARGET/.claude/skills"
rsync -a --delete --exclude='doc_source/' --exclude='__pycache__/' \
    "$REPO_ROOT/skills/" "$TARGET/.claude/skills/"

# Create docs_source symlink to godot-docs for godot-docs-* skills
GODOT_DOCS_SRC="$REPO_ROOT/godot-docs"
if [ -d "$GODOT_DOCS_SRC" ]; then
    TARGET_DOCS_SOURCE="$TARGET/.claude/skills/godot-docs-core/docs_source"
    # Create relative symlink
    ln -sfn "$(cd "$GODOT_DOCS_SRC" && pwd)" "$TARGET_DOCS_SOURCE"
    echo "Created docs_source symlink pointing to godot-docs"
fi

cp "$CLAUDE_MD" "$TARGET/CLAUDE.md"
echo "Created CLAUDE.md (from $CLAUDE_MD)"

if [ ! -f "$TARGET/.gitignore" ]; then
    cat > "$TARGET/.gitignore" << 'GI_EOF'
.claude
CLAUDE.md
assets
screenshots
.godot
*.import
GI_EOF
    echo "Created .gitignore"
fi

git -C "$TARGET" init -q 2>/dev/null || true

echo "Done. skills: $(ls "$TARGET/.claude/skills/" | wc -l)"
