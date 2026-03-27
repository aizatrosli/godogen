#!/usr/bin/env bash
# Godogen Plan Converter
# Converts a generic PLAN.md into godogen-compatible format

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/convert.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: convert.py not found at $PYTHON_SCRIPT"
    exit 1
fi

if [ $# -lt 1 ]; then
    echo "Usage: convert.sh <input_plan.md> [output_plan.md]"
    echo ""
    echo "Converts a generic PLAN.md into godogen-compatible format."
    echo "Adds: **Status:**, **Targets:**, **Depends on:** fields"
    echo "Preserves: **Goal:**, **Requirements:**, **Verify:**"
    exit 1
fi

python3 "$PYTHON_SCRIPT" "$@"
