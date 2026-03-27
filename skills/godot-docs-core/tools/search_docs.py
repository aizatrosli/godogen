#!/usr/bin/env python3
"""
Core search functionality for godot-docs.
Searches across RST files for keywords, class names, and topics.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def get_docs_source() -> Path:
    """Get the docs source directory, supporting symlink or direct path."""
    skill_dir = Path(__file__).parent.parent
    docs_source = skill_dir / 'docs_source'

    if not docs_source.exists():
        # Try through godot-docs-core parent
        potential = skill_dir.parent / 'godot-docs'
        if potential.exists():
            return potential
        # Try repo root level
        repo_root = skill_dir.parent.parent / 'godot-docs'
        if repo_root.exists():
            return repo_root

    return docs_source


def search(content: str, query: str, case_sensitive: bool = False) -> List[Dict]:
    """
    Search for a query in content.

    Args:
        content: RST content to search
        query: Search query
        case_sensitive: Whether search is case sensitive

    Returns:
        List of matches with position and context
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    matches = []

    for match in re.finditer(re.escape(query), content, flags):
        start = max(0, match.start() - 50)
        end = min(len(content), match.end() + 50)
        context = content[start:end]

        matches.append({
            'position': match.start(),
            'context': context,
            'matched_text': match.group()
        })

    return matches


def search_files(pattern: str, directory: Optional[Path] = None) -> List[Path]:
    """
    Find files matching a glob pattern.

    Args:
        pattern: Glob pattern (e.g., '*.rst', '*movement*')
        directory: Directory to search in

    Returns:
        List of matching file paths
    """
    if directory is None:
        directory = get_docs_source()

    return list(directory.rglob(pattern))


def find_files_by_keyword(keyword: str, case_sensitive: bool = False) -> List[Tuple[Path, int]]:
    """
    Find all RST files containing a keyword.

    Args:
        keyword: Text to search for
        case_sensitive: Whether search is case sensitive

    Returns:
        List of (file_path, line_number) tuples
    """
    docs_source = get_docs_source()
    results = []

    for rst_file in docs_source.rglob('*.rst'):
        try:
            content = rst_file.read_text(encoding='utf-8')
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                if case_sensitive:
                    if keyword in line:
                        results.append((rst_file, line_num))
                else:
                    if keyword.lower() in line.lower():
                        results.append((rst_file, line_num))
        except (UnicodeDecodeError, PermissionError):
            continue

    return results


def find_class(class_name: str) -> Optional[Path]:
    """
    Find a class reference file by class name.

    Args:
        class_name: Godot class name (e.g., 'Node2D', 'Area2D')

    Returns:
        Path to the class RST file, or None if not found
    """
    docs_source = get_docs_source()

    # Try common naming patterns
    patterns = [
        f'classes/{class_name.lower()}.rst',
        f'classes/{class_name}.rst',
        f'classes/{class_name.lower().replace("2d", "_2d")}.rst',
        f'classes/{class_name.lower().replace("3d", "_3d")}.rst',
    ]

    for pattern in patterns:
        file_path = docs_source / pattern
        if file_path.exists():
            return file_path

    # Fallback: search by content
    for rst_file in docs_source.glob('classes/*.rst'):
        try:
            content = rst_file.read_text(encoding='utf-8')
            # Match class definition line
            if re.search(rf'.. class::\s*{re.escape(class_name)}', content, re.IGNORECASE):
                return rst_file
        except (UnicodeDecodeError, PermissionError):
            continue

    return None


def find_tutorial_by_topic(topic: str) -> List[Path]:
    """
    Find tutorial files related to a topic.

    Args:
        topic: Topic keyword (e.g., 'movement', 'animation', 'ui')

    Returns:
        List of tutorial RST file paths
    """
    docs_source = get_docs_source()
    results = []

    # Search tutorial directories
    tutorial_dir = docs_source / 'tutorials'
    if tutorial_dir.exists():
        for rst_file in tutorial_dir.rglob('*.rst'):
            try:
                content = rst_file.read_text(encoding='utf-8')
                # Check if topic appears in content
                if re.search(rf'\b{re.escape(topic)}\b', content, re.IGNORECASE):
                    results.append(rst_file)
            except (UnicodeDecodeError, PermissionError):
                continue

    # Also check getting_started
    getting_started = docs_source / 'getting_started'
    if getting_started.exists():
        for rst_file in getting_started.rglob('*.rst'):
            try:
                content = rst_file.read_text(encoding='utf-8')
                if re.search(rf'\b{re.escape(topic)}\b', content, re.IGNORECASE):
                    results.append(rst_file)
            except (UnicodeDecodeError, PermissionError):
                continue

    return results


def search_by_category(category: str) -> List[Path]:
    """
    Find all files in a documentation category.

    Args:
        category: Category name (e.g., 'tutorials/2d', 'classes', 'getting_started')

    Returns:
        List of file paths in the category
    """
    docs_source = get_docs_source()
    category_path = docs_source / category

    if not category_path.exists():
        return []

    results = []
    for rst_file in category_path.rglob('*.rst'):
        results.append(rst_file)

    return results


def get_file_info(file_path: Path) -> Dict:
    """
    Get metadata about a documentation file.

    Args:
        file_path: Path to the RST file

    Returns:
        Dictionary with file metadata
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Extract title from first line
        title = None
        if lines and lines[0].strip():
            title = lines[0].strip()

        # Check for metadata directives
        allow_comments = False
        orphan = False
        github_url = None

        for line in lines:
            if ':allow_comments:' in line and 'False' not in line:
                allow_comments = True
            if ':orphan:' in line:
                orphan = True
            match = re.search(r':github_url:\s*(\S+)', line)
            if match:
                github_url = match.group(1)

        return {
            'path': str(file_path),
            'relative_path': str(file_path.relative_to(get_docs_source())),
            'title': title,
            'line_count': len(lines),
            'allow_comments': allow_comments,
            'orphan': orphan,
            'github_url': github_url
        }
    except (UnicodeDecodeError, PermissionError):
        return {
            'path': str(file_path),
            'relative_path': str(file_path.relative_to(get_docs_source())),
            'error': 'Could not read file'
        }


if __name__ == '__main__':
    # Simple CLI for testing
    if len(sys.argv) < 2:
        print("Usage: search_docs.py <search_term> [class|tutorial|file]")
        print("  search_term: Text to search for")
        print("  type: 'class', 'tutorial', 'file' (default: file)")
        sys.exit(1)

    query = sys.argv[1]
    search_type = sys.argv[2] if len(sys.argv) > 2 else 'file'

    if search_type == 'class':
        result = find_class(query)
        if result:
            print(f"Found: {result}")
        else:
            print(f"Class '{query}' not found")
    elif search_type == 'tutorial':
        results = find_tutorial_by_topic(query)
        if results:
            print(f"Found {len(results)} tutorial(s):")
            for r in results[:10]:
                print(f"  - {r.relative_to(get_docs_source())}")
        else:
            print(f"No tutorials found for '{query}'")
    else:
        results = find_files_by_keyword(query)
        if results:
            print(f"Found '{query}' in {len(results)} location(s):")
            for path, line_num in results[:20]:
                print(f"  - {path.relative_to(get_docs_source())}:{line_num}")
        else:
            print(f"'{query}' not found")
