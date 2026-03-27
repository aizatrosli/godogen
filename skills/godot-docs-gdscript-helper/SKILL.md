---
name: godot-docs-gdscript-helper
description: |
  GDScript code example extraction from godot-docs tutorials.
  Extracts and validates GDScript examples for game development.
---

# Godot Docs GDScript Helper

The GDScript code example extraction agent.

## Purpose

Extract and validate GDScript examples from `godot-docs/` for game development tasks.

## Capabilities

- Find GDScript examples in RST files
- Extract complete code blocks with formatting
- Provide context for example usage
- Validate syntax patterns

## Usage

### From a game development context

```
User: "Show me a GDScript example for input handling"

Agent workflow:
1. Search godot-docs/tutorials/inputs/ for GDScript examples
2. Extract input action patterns
3. Return working code with context
```

### Tool commands

```bash
# Extract GDScript examples for a topic
skills/godot-docs-gdscript-helper/tools/extract.sh "Input"

# Get examples from a specific class
skills/godot-docs-gdscript-helper/tools/extract.sh CharacterBody2D class
```

## GDScript Reference

This agent works with the GDScript syntax reference from:
- `skills/godot-task/gdscript.md` - Full syntax reference
- `godot-docs/_extensions/gdscript.py` - Pygments lexer

## Example Output

```
## Input Handling Example

**Context:** Getting input in the main game loop

```gdscript
func _process(delta: float) -> void:
    var input_dir := Vector2.ZERO

    if Input.is_action_pressed("move_right"):
        input_dir.x += 1
    if Input.is_action_pressed("move_left"):
        input_dir.x -= 1
    if Input.is_action_pressed("move_up"):
        input_dir.y += 1
    if Input.is_action_pressed("move_down"):
        input_dir.y -= 1

    velocity = input_dir * max_speed
    move_and_slide()
```

**Related classes:**
- [Input](classes/input.rst)
- [CharacterBody2D](classes/character_body_2d.rst)
```

## Related Skills

- `godot-docs-core` - Shared code extraction utilities
- `godot-task/gdscript.md` - GDScript syntax reference
