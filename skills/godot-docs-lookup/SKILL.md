---
name: godot-docs-lookup
description: |
  Primary reference agent for searching godot-docs.
  Searches across classes, tutorials, and getting_started for documentation.
---

# Godot Docs Lookup

The primary search agent for finding documentation in the godot-docs repository.

## Purpose

Find and retrieve relevant documentation from `godot-docs/` for game development tasks.

## Capabilities

- Search `godot-docs/` for API documentation, tutorials, and examples
- Cross-reference between `classes/` and `tutorials/`
- Extract relevant sections for user queries
- Provide file paths to source documentation

## Usage

### From a game development context

```
User: "How do I implement player movement in Godot?"

Agent workflow:
1. Search for "movement" in godot-docs/tutorials/
2. Find relevant class references (CharacterBody2D, CharacterBody3D)
3. Extract tutorial guidance and class API info
4. Return compiled answer with references
```

### Tool commands

```bash
# Search for a topic
skills/godot-docs-lookup/tools/search.sh "player movement"

# Find a class
skills/godot-docs-lookup/tools/search.sh Node2D class

# Find tutorials for a topic
skills/godot-docs-lookup/tools/search.sh animation tutorial
```

## Search Categories

| Category | Path | Description |
|----------|------|-------------|
| `class` | `classes/*.rst` | Godot class API reference |
| `tutorial` | `tutorials/*/` | Topic tutorials (2d, 3d, animation, etc.) |
| `getting_started` | `getting_started/` | Beginner guides |
| `best_practices` | `tutorials/best_practices/` | Design patterns and tips |
| `engine_details` | `engine_details/` | Internal engine documentation |

## Related Skills

- `godot-docs-classref` - Detailed class reference parsing
- `godot-docs-tutorial-finder` - Tutorial-specific matching
- `godot-docs-core` - Shared utilities
