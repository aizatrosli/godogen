#!/usr/bin/env python3
"""
RST parsing utilities for godot-docs.
Parse class references, tutorials, and extract structured data.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def get_docs_source() -> Path:
    """Get the docs source directory."""
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


class ClassInfo:
    """Parsed information about a Godot class."""

    def __init__(self, name: str):
        self.name = name
        self.parent_class: Optional[str] = None
        self.description: str = ""
        self.methods: List[Dict] = []
        self.properties: List[Dict] = []
        self.signals: List[Dict] = []
        self.constants: List[Dict] = []
        self.inherits: str = ""
        self.is_abstract: bool = False

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'parent_class': self.parent_class,
            'description': self.description,
            'methods': self.methods,
            'properties': self.properties,
            'signals': self.signals,
            'constants': self.constants,
            'inherits': self.inherits,
            'is_abstract': self.is_abstract
        }


class TutorialInfo:
    """Parsed information about a tutorial."""

    def __init__(self, title: str):
        self.title = title
        self.description: str = ""
        self.sections: List[Dict] = []
        self.code_examples: List[Dict] = []
        self.related_classes: List[str] = []

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description,
            'sections': self.sections,
            'code_examples': self.code_examples,
            'related_classes': self.related_classes
        }


def parse_class(content: str) -> Optional[ClassInfo]:
    """
    Parse a Godot class reference RST file.

    Args:
        content: RST content of a class reference

    Returns:
        ClassInfo object with parsed data
    """
    lines = content.split('\n')
    if not lines:
        return None

    class_name = lines[0].strip()
    if not class_name:
        return None

    cls = ClassInfo(class_name)

    i = 1
    section = None

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Check for section headers
        if re.match(r'^[=\-~]+$', line):
            section_header = lines[i-1].strip() if i > 0 else ""
            section = section_header.lower()
            i += 1
            continue

        # Parse parent class
        if line.strip().startswith('Inherits:'):
            cls.inherits = line.split(':', 1)[1].strip()
            cls.parent_class = cls.inherits
            i += 1
            continue

        # Parse abstract marker
        if '@abstract' in line or line.strip().startswith('@abstract'):
            cls.is_abstract = True
            i += 1
            continue

        # Parse description
        if not section and line.strip() and not line.strip().startswith('..'):
            if not cls.description:
                cls.description += line.strip() + " "
            else:
                cls.description += line.strip() + " "
            i += 1
            continue

        # Parse method
        if section == 'methods':
            if line.strip().startswith('.. method::') or re.match(r'^\s+func\s+\w+\(', line):
                method_match = re.search(r'func\s+(\w+)\s*\((.*?)\)', line)
                if method_match:
                    method_name = method_match.group(1)
                    params_str = method_match.group(2)
                    params = parse_parameters(params_str)

                    # Get description (next lines until empty or new directive)
                    description = []
                    i += 1
                    while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('..'):
                        # Extract indentation
                        stripped = lines[i].lstrip()
                        indent = len(lines[i]) - len(stripped)
                        description.append(stripped)
                        i += 1

                    cls.methods.append({
                        'name': method_name,
                        'parameters': params,
                        'description': ' '.join(description).strip(),
                        'indentation': indent
                    })
                    continue

            # Handle .. method:: directive format
            if line.strip().startswith('.. method::'):
                method_name = line.split('::')[1].strip()
                # Get description
                description = []
                i += 1
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('..'):
                    description.append(lines[i].strip())
                    i += 1

                cls.methods.append({
                    'name': method_name,
                    'description': ' '.join(description).strip()
                })
                continue

        # Parse property
        if section == 'properties':
            # Format: property_name: type
            if re.match(r'^\s*\w+:\s*\w+', line):
                match = re.match(r'^\s*(\w+):\s*(\w+)', line)
                if match:
                    prop_name = match.group(1)
                    prop_type = match.group(2)

                    # Get description
                    description = []
                    i += 1
                    while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('..'):
                        description.append(lines[i].strip())
                        i += 1

                    cls.properties.append({
                        'name': prop_name,
                        'type': prop_type,
                        'description': ' '.join(description).strip()
                    })
                    continue

        # Parse signal
        if section == 'signals':
            if line.strip().startswith('.. signal::') or re.match(r'^\s*signal\s+\w+', line):
                signal_match = re.search(r'signal\s+(\w+)(?:\s*\((.*?)\))?', line)
                if signal_match:
                    signal_name = signal_match.group(1)
                    params_str = signal_match.group(2) or ""
                    params = parse_parameters(params_str)

                    # Get description
                    description = []
                    i += 1
                    while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('..'):
                        description.append(lines[i].strip())
                        i += 1

                    cls.signals.append({
                        'name': signal_name,
                        'parameters': params,
                        'description': ' '.join(description).strip()
                    })
                    continue

        # Parse constant
        if section == 'constants':
            if line.strip().startswith('.. constant::') or re.match(r'^\s*const\s+\w+', line):
                const_match = re.search(r'const\s+(\w+)(?:\s*=\s*(\w+))?', line)
                if const_match:
                    const_name = const_match.group(1)
                    const_value = const_match.group(2) or "N/A"

                    # Get description
                    description = []
                    i += 1
                    while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('..'):
                        description.append(lines[i].strip())
                        i += 1

                    cls.constants.append({
                        'name': const_name,
                        'value': const_value,
                        'description': ' '.join(description).strip()
                    })
                    continue

        i += 1

    return cls


def parse_parameters(params_str: str) -> List[Dict]:
    """
    Parse function parameters string.

    Args:
        params_str: Parameters string (e.g., "pos: Vector2, rotation: float")

    Returns:
        List of parameter dictionaries
    """
    params = []
    if not params_str.strip():
        return params

    for param in params_str.split(','):
        param = param.strip()
        if not param:
            continue

        if ':' in param:
            name, type_str = param.split(':', 1)
            params.append({
                'name': name.strip(),
                'type': type_str.strip()
            })
        else:
            params.append({
                'name': param,
                'type': None
            })

    return params


def parse_tutorial(content: str) -> TutorialInfo:
    """
    Parse a tutorial RST file.

    Args:
        content: RST content of a tutorial

    Returns:
        TutorialInfo object with parsed data
    """
    lines = content.split('\n')
    title = lines[0].strip() if lines else "Untitled Tutorial"

    tutorial = TutorialInfo(title)

    sections = []
    current_section = None
    current_content = []

    for i, line in enumerate(lines):
        # Check for section header
        if i > 0 and re.match(r'^[=\-~]+$', lines[i-1]):
            # Save previous section
            if current_section:
                sections.append({
                    'name': current_section,
                    'content': '\n'.join(current_content)
                })
                current_content = []

            current_section = lines[i-1].strip()
            continue

        # Skip directive lines for parsing
        if line.strip().startswith('.. '):
            continue

        # Skip RST role lines
        if line.strip().startswith('.. role::'):
            continue

        if line.strip():
            current_content.append(line.strip())

    # Save last section
    if current_section:
        sections.append({
            'name': current_section,
            'content': '\n'.join(current_content)
        })

    tutorial.sections = sections
    tutorial.description = ' '.join(sections[0]['content'].split()[:100]) if sections else ""

    return tutorial


def find_class_file(class_name: str) -> Optional[Path]:
    """
    Find the RST file for a Godot class.

    Args:
        class_name: Name of the class (e.g., 'Node2D')

    Returns:
        Path to the RST file, or None if not found
    """
    docs_source = get_docs_source()
    classes_dir = docs_source / 'classes'

    if not classes_dir.exists():
        return None

    # Try direct name
    class_file = classes_dir / f'{class_name.lower()}.rst'
    if class_file.exists():
        return class_file

    # Try with underscores for 2D/3D
    class_file = classes_dir / f'{class_name.lower().replace("2d", "_2d").replace("3d", "_3d")}.rst'
    if class_file.exists():
        return class_file

    # Search by content
    for rst_file in classes_dir.glob('*.rst'):
        try:
            content = rst_file.read_text(encoding='utf-8')
            if re.search(rf'^\.\. class::\s*{re.escape(class_name)}', content, re.MULTILINE | re.IGNORECASE):
                return rst_file
        except (UnicodeDecodeError, PermissionError):
            continue

    return None


def extract_code_blocks(content: str) -> List[Dict]:
    """
    Extract code blocks from RST content.

    Args:
        content: RST content

    Returns:
        List of code block dictionaries with language and content
    """
    code_blocks = []

    # Match .. code-block:: directives
    pattern = r'\.\. code-block::\s*(\w+)\s*\n\s*\n(.*?)(?=\n\s*\n|\.\. |$)'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    for lang, code in matches:
        # Clean up the code
        code = code.strip()
        # Remove leading/trailing whitespace lines
        lines = code.split('\n')
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        if lines:
            code_blocks.append({
                'language': lang.lower(),
                'code': '\n'.join(lines)
            })

    return code_blocks


def get_class_hierarchy(class_name: str) -> List[str]:
    """
    Get the inheritance hierarchy of a class.

    Args:
        class_name: Starting class name

    Returns:
        List of class names from the class up to Object
    """
    hierarchy = [class_name]
    current_class = class_name

    while current_class:
        file_path = find_class_file(current_class)
        if not file_path:
            break

        content = file_path.read_text(encoding='utf-8')
        match = re.search(r'^\.\. class::\s*(\S+)', content, re.MULTILINE)
        if match:
            current_class = match.group(1)

        inherits_match = re.search(r'^Inherits:\s*(\S+)', content, re.MULTILINE)
        if inherits_match:
            parent = inherits_match.group(1)
            hierarchy.append(parent)
            current_class = parent
        else:
            break

    return hierarchy


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: parse_rst.py <class_name|file_path>")
        sys.exit(1)

    arg = sys.argv[1]
    docs_source = get_docs_source()

    # Check if it's a file path
    if Path(arg).exists():
        file_path = Path(arg)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to parse as class
        cls = parse_class(content)
        if cls:
            print(f"Class: {cls.name}")
            print(f"Inherits: {cls.inherits}")
            print(f"Abstract: {cls.is_abstract}")
            print(f"\nMethods ({len(cls.methods)}):")
            for m in cls.methods[:10]:
                print(f"  - {m['name']}")
            print(f"\nProperties ({len(cls.properties)}):")
            for p in cls.properties[:10]:
                print(f"  - {p['name']}: {p['type']}")
            print(f"\nSignals ({len(cls.signals)}):")
            for s in cls.signals[:10]:
                print(f"  - {s['name']}")
        else:
            print("Could not parse as class reference")
    else:
        # Try to find and parse as class
        file_path = find_class_file(arg)
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            cls = parse_class(content)
            if cls:
                print(f"Class: {cls.name}")
                print(f"Inherits: {cls.inherits}")
                print(f"Abstract: {cls.is_abstract}")
                print(f"\nMethods ({len(cls.methods)}):")
                for m in cls.methods[:10]:
                    print(f"  - {m['name']}")
                print(f"\nProperties ({len(cls.properties)}):")
                for p in cls.properties[:10]:
                    print(f"  - {p['name']}: {p['type']}")
                print(f"\nSignals ({len(cls.signals)}):")
                for s in cls.signals[:10]:
                    print(f"  - {s['name']}")
            else:
                print("Could not parse class")
        else:
            print(f"Class '{arg}' not found")
