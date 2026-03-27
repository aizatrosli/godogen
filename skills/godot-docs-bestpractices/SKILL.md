---
name: godot-docs-bestpractices
description: |
  Best practices and patterns agent for Godot development.
  Searches godot-docs for design patterns, performance tips, and common practices.
---

# Godot Docs Best Practices

The best practices and patterns agent for Godot development.

## Purpose

Find and apply Godot best practices from `godot-docs/` including:
- Design patterns and architectural guidance
- Performance optimization tips
- Common patterns and anti-patterns
- Editor workflow recommendations

## Capabilities

- Search `godot-docs/tutorials/best_practices/`
- Locate performance optimization tips
- Identify common patterns and anti-patterns
- Reference editor workflow tips

## Best Practices Categories

| Category | Description |
|----------|-------------|
| `tutorials/best_practices/` | General design patterns and tips |
| `tutorials/performance/` | Optimization techniques |
| `tutorials/editor/` | Editor workflow tips |
| `tutorials/troubleshooting/` | Common issues and solutions |
| `tutorials/migrating/` | Migration best practices |

## Usage

### From a game development context

```
User: "What are best practices for scene organization?"

Agent workflow:
1. Search best_practices for scene organization
2. Find performance tips for large scenes
3. Return guidance on node hierarchy, groups, etc.
```

### Tool commands

```bash
# Search best practices
skills/godot-docs-bestpractices/tools/search.sh "scene organization"

# Find performance tips
skills/godot-docs-bestpractices/tools/search.sh performance
```

## Common Patterns

The agent can identify and suggest common Godot patterns:

- **Signal-based communication:** Decoupled component interaction
- **Scene instancing:** Reusable game objects
- **Node groups:** Dynamic collections of related nodes
- **State machines:** Character/AI behavior management
- **Singletons (Autoloads):** Global state management

## Related Skills

- `godot-docs-lookup` - Primary search agent
- `godot-docs-core` - Shared utilities
