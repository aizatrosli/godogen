---
name: godot-docs-tutorial-finder
description: |
  Tutorial matching and extraction for Godot development.
  Finds relevant tutorials based on development tasks and extracts step-by-step guidance.
---

# Godot Docs Tutorial Finder

The tutorial matching agent for finding relevant tutorials for game development tasks.

## Purpose

Match game development tasks to tutorials in `godot-docs/tutorials/` and extract step-by-step guidance.

## Capabilities

- Search tutorial topics by task description
- Extract step-by-step instructions
- Find code examples and asset patterns
- Suggest related tutorials

## Tutorial Categories

| Category | Path | Typical Topics |
|----------|------|----------------|
| 2D | `tutorials/2d/` | Sprites, tilemaps, 2D physics |
| 3D | `tutorials/3d/` | Meshes, materials, lights |
| Animation | `tutorials/animation/` | AnimationTree, AnimationPlayer |
| Audio | `tutorials/audio/` | Sound, music, audio buses |
| Export | `tutorials/export/` | Publishing to platforms |
| IO | `tutorials/io/` | File I/O, saving/loading |
| Inputs | `tutorials/inputs/` | Input handling, actions |
| Math | `tutorials/math/` | Vector math, trigonometry |
| Navigation | `tutorials/navigation/` | Pathfinding, NavMap |
| Networking | `tutorials/networking/` | Multiplayer, RPC |
| Performance | `tutorials/performance/` | Optimization techniques |
| Physics | `tutorials/physics/` | Collision, rigid bodies |
| Platform | `tutorials/platform/` | Mobile, desktop, web |
| Plugins | `tutorials/plugins/` | Editor plugins |
| Rendering | `tutorials/rendering/` | Shaders, materials, post-processing |
| Scripting | `tutorials/scripting/` | GDScript, C#, C++ |
| Shaders | `tutorials/shaders/` | Custom shader code |
| UI | `tutorials/ui/` | Control nodes, layouts |
| XR | `tutorials/xr/` | VR/AR development |

## Usage

### From a game development context

```
User: "How do I implement a save system?"

Agent workflow:
1. Search for "save" in tutorials/io/
2. Match "saving/loading" tutorial
3. Extract steps and code examples
4. Return guidance with class references
```

### Tool commands

```bash
# Search tutorials by topic
skills/godot-docs-tutorial-finder/tools/find_tutorials.sh "player movement"

# Get tutorial steps
skills/godot-docs-tutorial-finder/tools/extract_steps.sh tutorials/2d/2d_tutorials_index.rst
```

## Related Skills

- `godot-docs-lookup` - Primary search agent
- `godot-docs-gdscript-helper` - Code example extraction
- `godot-docs-core` - Shared utilities
