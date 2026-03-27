---
name: godot-docs-classref
description: |
  Class reference parsing and lookup for Godot classes.
  Parses RST class files and extracts structured API information.
---

# Godot Docs Class Reference

The class reference agent for parsing and looking up Godot class documentation.

## Purpose

Find and explain Godot classes from `godot-docs/classes/` with structured data.

## Capabilities

- Parse RST class reference files
- Extract class hierarchy, methods, properties, signals
- Provide usage examples from related tutorials
- Cross-reference with engine API docs

## Usage

### From a game development context

```
User: "What methods does CharacterBody2D have for movement?"

Agent workflow:
1. Find class file: classes/character_body_2d.rst
2. Parse methods section
3. Extract movement-related methods (move_and_slide, etc.)
4. Return structured API info
```

### Tool commands

```bash
# Parse a specific class
skills/godot-docs-classref/tools/parse_class.sh Node2D

# Get class info in JSON format
skills/godot-docs-classref/tools/parse_class.sh Area2D --json
```

## Class Structure

Godot classes in the docs follow this RST structure:

```rst
ClassName
Inherits: ParentClass

Description paragraph...

Methods
-------
.. method:: method_name(params)
    Method description

Properties
----------
property_name: type
    Property description

Signals
-------
.. signal:: signal_name(params)
    Signal description
```

## Related Skills

- `godot-docs-lookup` - Primary search agent
- `godot-docs-core` - Shared RST parsing utilities
