#!/usr/bin/env python3
"""
Extract GDScript examples from RST files.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "godot-docs-core" / "tools"))
from extract_code import (
    extract_code_blocks as _extract_code_blocks,
    extract_gdscript_examples as _extract_gdscript,
    clean_code_block,
)

def extract_gdscript_examples(content: str) -> list:
    return _extract_gdscript(content)


def extract_all_code(content: str) -> list:
    return _extract_code_blocks(content)


def find_context(code_start: int, content: str, context_chars: int = 200) -> str:
    """
    Find context before a code block.

    Args:
        code_start: Position where code block starts
        content: Full RST content
        context_chars: Number of characters of context to include

    Returns:
        Context string
    """
    start = max(0, code_start - context_chars)
    context = content[start:code_start].strip()

    # Get last non-empty line
    lines = context.split('\n')
    while lines and not lines[-1].strip():
        lines.pop()

    if lines:
        return lines[-1]
    return ''


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_examples.py <file> [--gdscript | --json]")
        sys.exit(1)

    file_path = sys.argv[1]
    is_gdscript = '--gdscript' in sys.argv
    is_json = '--json' in sys.argv

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if is_gdscript:
        examples = extract_gdscript_examples(content)
    else:
        examples = extract_all_code(content)

    if is_json:
        print(json.dumps(examples, indent=2))
    else:
        print(f"Found {len(examples)} code block(s)")
        print()

        for i, example in enumerate(examples, 1):
            print(f"--- Example {i} ({example['language']}) ---")
            print(example['code'][:500])
            if len(example['code']) > 500:
                print("... (truncated)")
            print()


if __name__ == '__main__':
    main()
