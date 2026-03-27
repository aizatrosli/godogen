#!/usr/bin/env python3
"""
Parse a Godot class RST file and output information.
Used by godot-docs-classref agent.
"""

import sys
import json
import re
from pathlib import Path


def parse_class_rst(file_path: str) -> dict:
    """
    Parse a Godot class RST file.

    Args:
        file_path: Path to the RST file

    Returns:
        Dictionary with class information
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    result = {
        'name': lines[0].strip() if lines else 'Unknown',
        'file': file_path,
        'inherits': '',
        'parent_class': '',
        'description': '',
        'methods': [],
        'properties': [],
        'signals': [],
        'constants': [],
        'is_abstract': False
    }

    i = 1
    current_section = None

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Section headers (lines of =, -, or ~)
        if re.match(r'^[=\-~]+$', line):
            if i > 0:
                current_section = lines[i-1].strip().lower()
            i += 1
            continue

        # Inherits line
        if line.strip().startswith('Inherits:'):
            inherits = line.split(':', 1)[1].strip()
            result['inherits'] = inherits
            result['parent_class'] = inherits
            i += 1
            continue

        # Abstract marker
        if '@abstract' in line:
            result['is_abstract'] = True
            i += 1
            continue

        # Description (before any section)
        if current_section is None and line.strip() and not line.strip().startswith('..'):
            if not result['description']:
                result['description'] = line.strip()
            else:
                result['description'] += ' ' + line.strip()
            i += 1
            continue

        # Methods section
        if current_section == 'methods':
            # Method directive
            if line.strip().startswith('.. method::'):
                method_line = line.split('::', 1)[1].strip()
                method_name = method_line.split('(')[0].strip()

                # Get description
                description = []
                i += 1
                indent = None
                while i < len(lines) and lines[i].strip():
                    if not description and lines[i].strip().startswith(':param'):
                        break
                    description.append(lines[i].strip())
                    i += 1

                result['methods'].append({
                    'name': method_name,
                    'description': ' '.join(description).strip(),
                    'signature': method_line
                })
                continue

        # Properties section
        if current_section == 'properties':
            # Property pattern: name: type
            prop_match = re.match(r'^(\w+):\s*(\w+)', line)
            if prop_match:
                prop_name = prop_match.group(1)
                prop_type = prop_match.group(2)

                # Get description
                description = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    description.append(lines[i].strip())
                    i += 1

                result['properties'].append({
                    'name': prop_name,
                    'type': prop_type,
                    'description': ' '.join(description).strip()
                })
                continue

        # Signals section
        if current_section == 'signals':
            # Signal directive
            if line.strip().startswith('.. signal::'):
                signal_line = line.split('::', 1)[1].strip()
                signal_name = signal_line.split('(')[0].strip()

                # Get description
                description = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    if not description and lines[i].strip().startswith(':param'):
                        break
                    description.append(lines[i].strip())
                    i += 1

                result['signals'].append({
                    'name': signal_name,
                    'description': ' '.join(description).strip(),
                    'signature': signal_line
                })
                continue

        # Constants section
        if current_section == 'constants':
            # Constant pattern
            const_match = re.match(r'^(\w+)(?:\s*=\s*(\S+))?', line)
            if const_match:
                const_name = const_match.group(1)
                const_value = const_match.group(2) or 'N/A'

                # Get description
                description = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    description.append(lines[i].strip())
                    i += 1

                result['constants'].append({
                    'name': const_name,
                    'value': const_value,
                    'description': ' '.join(description).strip()
                })
                continue

        i += 1

    return result


def print_class_info(class_info: dict):
    """Print class information in human-readable format."""
    print(f"## {class_info['name']}")
    print()

    if class_info['inherits']:
        print(f"**Inherits:** {class_info['inherits']}")
        print()

    if class_info['is_abstract']:
        print("*Abstract class - cannot be instantiated*")
        print()

    if class_info['description']:
        print(class_info['description'])
        print()

    # Methods
    if class_info['methods']:
        print("### Methods")
        print()
        for method in class_info['methods']:
            sig = method.get('signature', method['name'])
            print(f"**{method['name']}({sig})**")
            if method.get('description'):
                print(f"  {method['description']}")
            print()

    # Properties
    if class_info['properties']:
        print("### Properties")
        print()
        for prop in class_info['properties']:
            print(f"**{prop['name']}: {prop['type']}**")
            if prop.get('description'):
                print(f"  {prop['description']}")
            print()

    # Signals
    if class_info['signals']:
        print("### Signals")
        print()
        for signal in class_info['signals']:
            print(f"**{signal['name']}**")
            if signal.get('description'):
                print(f"  {signal['description']}")
            print()

    # Constants
    if class_info['constants']:
        print("### Constants")
        print()
        for const in class_info['constants']:
            print(f"**{const['name']} = {const['value']}**")
            if const.get('description'):
                print(f"  {const['description']}")
            print()


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_class.py <class_file> [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    is_json = '--json' in sys.argv

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    class_info = parse_class_rst(file_path)

    if is_json:
        print(json.dumps(class_info, indent=2))
    else:
        print_class_info(class_info)


if __name__ == '__main__':
    main()
