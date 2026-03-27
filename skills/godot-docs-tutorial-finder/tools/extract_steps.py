#!/usr/bin/env python3
"""
Extract step-by-step content from a tutorial RST file.
"""

import sys
import json
import re
from pathlib import Path


def extract_steps(file_path: str) -> dict:
    """
    Extract structured steps from a tutorial RST file.

    Args:
        file_path: Path to the RST file

    Returns:
        Dictionary with tutorial structure
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    result = {
        'title': lines[0].strip() if lines else 'Untitled',
        'sections': [],
        'code_examples': [],
        'class_references': []
    }

    current_section = None
    current_content = []

    # Pattern for section headers
    section_pattern = re.compile(r'^[=\-~]+$')

    for i, line in enumerate(lines):
        # Check for section header
        if i > 0 and section_pattern.match(lines[i-1]):
            # Save previous section
            if current_section:
                result['sections'].append({
                    'name': current_section,
                    'content': '\n'.join(current_content)
                })
                current_content = []

            current_section = lines[i-1].strip()
            continue

        # Skip empty lines between sections
        if not line.strip() and not current_section:
            continue

        # Skip RST directives
        if line.strip().startswith('.. '):
            continue

        # Skip role definitions
        if line.strip().startswith('.. role::'):
            continue

        if line.strip():
            current_content.append(line.strip())

    # Save last section
    if current_section:
        result['sections'].append({
            'name': current_section,
            'content': '\n'.join(current_content)
        })

    # Extract code examples
    result['code_examples'] = extract_code_blocks(content)

    # Extract class references
    result['class_references'] = find_class_refs(content)

    return result


def extract_code_blocks(content: str) -> list:
    """
    Extract code blocks from RST content.

    Args:
        content: RST content

    Returns:
        List of code block dictionaries
    """
    code_blocks = []

    # Pattern for .. code-block:: directives
    pattern = r'\.\. code-block::\s*(\w+)\s*\n(?:\s*:\w+:.*\n)*\n(.+?)(?=\n\s*\n|\.\. |\Z)'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    for lang, code in matches:
        cleaned_code = clean_code(code)
        if cleaned_code.strip():
            code_blocks.append({
                'language': lang.lower(),
                'code': cleaned_code
            })

    return code_blocks


def clean_code(code: str) -> str:
    """Clean up code block content."""
    code = code.strip()
    lines = code.split('\n')

    # Remove RST continuation markers
    cleaned_lines = []
    for line in lines:
        line = re.sub(r'^\s*\.\.\s*', '', line)
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def find_class_refs(content: str) -> list:
    """
    Find class references in content.

    Args:
        content: RST content

    Returns:
        List of class names mentioned
    """
    class_refs = []

    # Match :class:`ClassName` syntax
    class_pattern = r':class:`(\w+)`'
    matches = re.findall(class_pattern, content)
    class_refs.extend(matches)

    # Match .. class:: ClassName
    class_directive = r'..\s+class::\s*(\w+)'
    matches = re.findall(class_directive, content)
    class_refs.extend(matches)

    # Remove duplicates while preserving order
    seen = set()
    unique_refs = []
    for ref in class_refs:
        if ref not in seen:
            seen.add(ref)
            unique_refs.append(ref)

    return unique_refs


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_steps.py <tutorial_file> [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    is_json = '--json' in sys.argv

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    tutorial = extract_steps(file_path)

    if is_json:
        print(json.dumps(tutorial, indent=2))
    else:
        print(f"# {tutorial['title']}")
        print()

        if tutorial['sections']:
            print("## Structure")
            for i, section in enumerate(tutorial['sections'], 1):
                preview = section['content'][:100]
                if len(section['content']) > 100:
                    preview += "..."
                print(f"{i}. {section['name']}: {preview}")
            print()

        if tutorial['code_examples']:
            print(f"## Code Examples ({len(tutorial['code_examples'])})")
            for i, example in enumerate(tutorial['code_examples'], 1):
                print(f"\n{i}. {example['language'].upper()} ({len(example['code'])} chars)")
                print(example['code'][:200])
                if len(example['code']) > 200:
                    print("... (truncated)")
            print()

        if tutorial['class_references']:
            print(f"## Class References ({len(tutorial['class_references'])})")
            print(", ".join(tutorial['class_references'][:20]))
            if len(tutorial['class_references']) > 20:
                print(f"... and {len(tutorial['class_references']) - 20} more")


if __name__ == '__main__':
    main()
