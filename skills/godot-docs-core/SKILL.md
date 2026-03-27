---
name: godot-docs-core
description: |
  Core utilities for searching and parsing godot-docs documentation.
  Shared by all godot-docs-* agents.
  Provides RST parsing, document search, and code extraction capabilities.
---

# Godot Docs Core

Shared utilities for godot-docs agents. This skill provides the foundation for all documentation reference agents.

## Utilities

| Utility | Purpose | Location |
|---------|---------|----------|
| `search_docs.py` | Search across godot-docs for content | `tools/search_docs.py` |
| `parse_rst.py` | Parse RST files for classes/methods | `tools/parse_rst.py` |
| `extract_code.py` | Extract code blocks from RST | `tools/extract_code.py` |
| `find_tutorials.sh` | Find tutorials by topic | `tools/find_tutorials.sh` |

## Usage

### Import in Python scripts

```python
import sys
import os

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.dirname(SKILL_DIR)

sys.path.insert(0, os.path.join(CORE_DIR, 'tools'))
from search_docs import search, find_files
from parse_rst import parse_class, parse_tutorial
from extract_code import extract_code_blocks
```

### Shell scripts

```bash
# Get the skill directory
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
CORE_DIR="$(dirname "$SKILL_DIR")"

# Use tools
"$SKILL_DIR/tools/find_tutorials.sh" "player movement"
```

## Documentation Source

This core expects a `docs_source/` directory containing the godot-docs files:

```
skills/godot-docs-core/
├── SKILL.md
├── tools/
│   ├── search_docs.py
│   ├── parse_rst.py
│   ├── extract_code.py
│   └── find_tutorials.sh
└── docs_source/  # Optional: symlink to godot-docs/
    ├── classes/
    ├── tutorials/
    └── getting_started/
```

You can symlink to the main repository's godot-docs:

```bash
cd skills/godot-docs-core
ln -s ../../godot-docs docs_source
```
