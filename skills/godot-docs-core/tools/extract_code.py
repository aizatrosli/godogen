#!/usr/bin/env python3
"""
Code block extraction utilities for godot-docs.
Extract GDScript, C#, and C++ examples from RST files.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional


def get_docs_source() -> Path:
    """Get the docs source directory."""
    skill_dir = Path(__file__).parent.parent
    docs_source = skill_dir / 'docs_source'

    if not docs_source.exists():
        parent_docs = skill_dir.parent / 'godot-docs'
        if parent_docs.exists():
            return parent_docs

    return docs_source


def extract_code_blocks(content: str) -> List[Dict]:
    """
    Extract all code blocks from RST content.

    Args:
        content: RST content to extract from

    Returns:
        List of code block dictionaries
    """
    code_blocks = []

    # Pattern for .. code-block:: directives
    code_block_pattern = r'\.\. code-block::\s*(\w+)\s*\n(?:\s*:\w+:.*\n)*\n(.+?)(?=\n\s*\n|\.\. |\Z)'

    matches = re.findall(code_block_pattern, content, re.DOTALL | re.IGNORECASE)

    for lang, code in matches:
        # Clean up the code
        cleaned_code = clean_code_block(code)

        if cleaned_code.strip():
            code_blocks.append({
                'language': lang.lower(),
                'code': cleaned_code
            })

    # Also try inline code blocks (triple backticks in newer RST)
    inline_pattern = r'```(\w+)?\n(.*?)```'
    inline_matches = re.findall(inline_pattern, content, re.DOTALL)

    for lang, code in inline_matches:
        cleaned_code = clean_code_block(code)

        if cleaned_code.strip():
            code_blocks.append({
                'language': lang.lower() if lang else 'text',
                'code': cleaned_code
            })

    return code_blocks


def extract_gdscript_examples(content: str) -> List[Dict]:
    """
    Extract GDScript examples specifically.

    Args:
        content: RST content to extract from

    Returns:
        List of GDScript code blocks
    """
    all_blocks = extract_code_blocks(content)
    return [b for b in all_blocks if b['language'] == 'gdscript']


def extract_csharp_examples(content: str) -> List[Dict]:
    """
    Extract C# examples specifically.

    Args:
        content: RST content to extract from

    Returns:
        List of C# code blocks
    """
    all_blocks = extract_code_blocks(content)
    return [b for b in all_blocks if b['language'] == 'csharp']


def extract_all_scripting_examples(content: str) -> Dict[str, List[Dict]]:
    """
    Extract all scripting language examples.

    Args:
        content: RST content to extract from

    Returns:
        Dictionary mapping language names to code blocks
    """
    all_blocks = extract_code_blocks(content)

    by_language = {}
    for block in all_blocks:
        lang = block['language']
        if lang not in by_language:
            by_language[lang] = []
        by_language[lang].append(block)

    return by_language


def clean_code_block(code: str) -> str:
    """
    Clean up code block content.

    Args:
        code: Raw code block content

    Returns:
        Cleaned code string
    """
    # Remove leading/trailing whitespace
    code = code.strip()

    # Normalize whitespace within the code
    lines = code.split('\n')
    cleaned_lines = []

    for line in lines:
        # Remove RST continuation markers
        line = re.sub(r'^\s*\.\.\s*', '', line)
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def extract_class_methods(content: str, class_name: str) -> List[Dict]:
    """
    Extract method examples for a specific class.

    Args:
        content: RST content (class reference)
        class_name: Name of the class

    Returns:
        List of method examples
    """
    methods = []

    # Find methods section
    methods_pattern = r'(?<=Methods)\n+(?:[=\-~]+\n+)?([\s\S]*?)(?=\n\n[A-Z]|\n\n[A-Z][a-z]+:|\Z)'
    methods_match = re.search(methods_pattern, content)

    if not methods_match:
        return methods

    methods_section = methods_match.group(1)

    # Extract method examples
    method_pattern = r'\.\. method::\s*(\w+).*?\n(?:\s+:\w+:.*\n)*\n(.*?)(?=\n\n|\n\.\. |\Z)'
    matches = re.findall(method_pattern, methods_section, re.DOTALL | re.IGNORECASE)

    for method_name, code in matches:
        cleaned_code = clean_code_block(code)

        methods.append({
            'name': method_name,
            'class': class_name,
            'code': cleaned_code
        })

    return methods


def extract_signal_examples(content: str, class_name: str) -> List[Dict]:
    """
    Extract signal examples for a specific class.

    Args:
        content: RST content (class reference)
        class_name: Name of the class

    Returns:
        List of signal examples
    """
    signals = []

    # Find signals section
    signals_pattern = r'(?<=Signals)\n+(?:[=\-~]+\n+)?([\s\S]*?)(?=\n\n[A-Z]|\n\n[A-Z][a-z]+:|\Z)'
    signals_match = re.search(signals_pattern, content)

    if not signals_match:
        return signals

    signals_section = signals_match.group(1)

    # Extract signal usages
    signal_pattern = r'\.\. signal::\s*(\w+).*?\n(?:\s+:\w+:.*\n)*\n(.*?)(?=\n\n|\n\.\. |\Z)'
    matches = re.findall(signal_pattern, signals_section, re.DOTALL | re.IGNORECASE)

    for signal_name, code in matches:
        cleaned_code = clean_code_block(code)

        signals.append({
            'name': signal_name,
            'class': class_name,
            'code': cleaned_code
        })

    return signals


def extract_usage_patterns(content: str) -> List[Dict]:
    """
    Extract usage patterns and examples from a tutorial.

    Args:
        content: RST tutorial content

    Returns:
        List of usage patterns
    """
    patterns = []

    # Look for code examples with context
    pattern_pattern = r'(\.\.? [^\n]*?)\n(?:\n|.. code-block::.*?)'

    # Find all code blocks with surrounding context
    code_blocks = extract_code_blocks(content)

    for i, block in enumerate(code_blocks):
        # Try to find surrounding text
        code_start = content.find(f'.. code-block:: {block["language"]}')
        if code_start > 0:
            # Get context before (up to 200 chars)
            context_start = max(0, code_start - 200)
            context = content[context_start:code_start].strip()
            # Get last non-empty line
            context_lines = context.split('\n')
            while context_lines and not context_lines[-1].strip():
                context_lines.pop()

            patterns.append({
                'language': block['language'],
                'code': block['code'],
                'context': context_lines[-1].strip() if context_lines else ''
            })
        else:
            patterns.append({
                'language': block['language'],
                'code': block['code'],
                'context': ''
            })

    return patterns


def search_for_class_usage(class_name: str, search_content: str) -> List[Dict]:
    """
    Search for usage of a class in content.

    Args:
        class_name: Name of the class to search for
        search_content: Content to search in

    Returns:
        List of usage occurrences with context
    """
    usages = []

    # Match class references (as ClassName, $ClassName, or get_node("ClassName"))
    patterns = [
        rf'\b{re.escape(class_name)}\b',
        rf'\$[^\s]*{re.escape(class_name)}',
        rf'get_node\(["\'].*{re.escape(class_name)}',
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, search_content):
            start = max(0, match.start() - 50)
            end = min(len(search_content), match.end() + 100)
            context = search_content[start:end]

            usages.append({
                'position': match.start(),
                'context': context,
                'matched_text': match.group()
            })

    return usages


def extract_from_directory(directory: Path) -> Dict[str, List[Dict]]:
    """
    Extract code blocks from all RST files in a directory.

    Args:
        directory: Directory containing RST files

    Returns:
        Dictionary mapping file paths to extracted code blocks
    """
    results = {}

    for rst_file in directory.rglob('*.rst'):
        try:
            content = rst_file.read_text(encoding='utf-8')
            code_blocks = extract_code_blocks(content)

            if code_blocks:
                relative_path = rst_file.relative_to(directory)
                results[str(relative_path)] = code_blocks
        except (UnicodeDecodeError, PermissionError):
            continue

    return results


def format_code_for_gdscript(code: str) -> str:
    """
    Format extracted GDScript code for use in game development.

    Args:
        code: Raw GDScript code

    Returns:
        Formatted GDScript code
    """
    # Remove GDScript-specific RST markers
    code = re.sub(r':[a-z]+:`([^`]+)`', r'\1', code)

    # Clean up function signatures
    code = re.sub(r'func\s+(\w+)\s*\([^)]*\)\s*->\s*void:', r'func \1(...):', code)

    return code.strip()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: extract_code.py <file_or_directory>")
        print("  file: Extract code blocks from a single RST file")
        print("  directory: Extract code blocks from all RST files in directory")
        sys.exit(1)

    arg = sys.argv[1]
    path = Path(arg)

    if path.is_file():
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        code_blocks = extract_code_blocks(content)
        print(f"Found {len(code_blocks)} code blocks in {path.name}")
        print()

        for i, block in enumerate(code_blocks, 1):
            print(f"--- Code block {i} ({block['language']}) ---")
            print(block['code'][:500])  # First 500 chars
            if len(block['code']) > 500:
                print("... (truncated)")
            print()
    else:
        results = extract_from_directory(path)
        print(f"Found {len(results)} files with code blocks")
        print()

        for file_path, blocks in list(results.items())[:10]:
            print(f"--- {file_path} ({len(blocks)} blocks) ---")
            for block in blocks[:2]:
                print(f"  {block['language']}: {len(block['code'])} chars")
            print()
