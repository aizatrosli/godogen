---
name: godogen-plan-converter
description: |
  Convert a generic game plan into a godogen-compatible PLAN.md
  with Status, Targets, Dependencies, and proper formatting.
---

# Godogen Plan Converter

Convert natural language game plans into godogen-compatible PLAN.md format.

## Purpose

Transform a generic development plan (with Goals, Requirements, Verify) into a structured godogen PLAN.md with:
- `**Status:**` field for each task (pending/in_progress/done)
- `**Targets:**` field with concrete file paths
- `**Depends on:**` field for task dependencies
- Proper formatting and documentation sections

## Capabilities

- Parse existing PLAN.md files with any task structure
- Infer file targets from task descriptions (scenes, scripts, UI, systems)
- Calculate task dependencies based on `Depends on` field or task order
- Add godogen-required fields to each task
- Generate documentation sections (Task Execution Instructions, Asset Management, Visual QA, Memory)
- Preserve original task content (Goal, Requirements, Verify)

## Usage

### Convert a plan file

```bash
# From repo root
cd /path/to/game-project
Skill(skill="godogen-plan-converter") with argument:
  Read /path/to/PLAN.md
  Convert to godogen format
  Write updated PLAN.md
```

### Direct invocation

```bash
# Use the converter tool
skills/godogen-plan-converter/tools/convert.sh /path/to/PLAN.md
```

### From a game context

```
User: "Convert my PLAN.md to godogen format"

Agent workflow:
1. Read existing PLAN.md
2. Parse task blocks (markdown headers with Requirements/Goal/Verify)
3. For each task:
   - Add **Status:** pending
   - Infer **Targets:** from task description
   - Add **Depends on:** based on task order or explicit deps
4. Add godogen documentation sections
5. Write updated PLAN.md
```

## Target Inference Patterns

The converter infers file targets based on task content:

| Task Content | Inferred Targets |
|--------------|------------------|
| "player movement", "third-person" | `scripts/player/player_controller.gd`, `scenes/player.tscn` |
| "vault generation", "procedural" | `scripts/vault/vault_generator.gd`, `scenes/vault/` |
| "enemy", "AI", "detection" | `scripts/enemies/*.gd`, `scenes/enemies/*.tscn` |
| "rope", "physics", "extraction" | `scripts/systems/rope_*.gd`, `scenes/systems/rope.tscn` |
| "UI", "menu", "hud", "shop" | `scenes/ui/*.tscn`, `scripts/ui/*.gd` |
| "parcel", "item", "object" | `scripts/parcels/*.gd`, `scenes/parcels/*.tscn` |
| "network", "multiplayer", "sync" | `scripts/networking/*.gd`, `scripts/autoload/network*.gd` |
| "progression", "upgrade", "economy" | `scripts/systems/economy.gd`, `scripts/upgrades/*.gd` |
| "presentation", "video", "test" | `test/presentation.gd`, `screenshots/` |

## Output Format

Each task is formatted as:

```markdown
## N. Task Name

- **Status:** pending
- **Targets:** scenes/path.tscn, scripts/path.gd
- **Depends on:** M
- **Goal:** ...
- **Requirements:** ...
- **Verify:** ...
```

## Documentation Sections Added

The converter adds these sections to the end of PLAN.md:

- **Task Execution Instructions** - How godogen orchestrates tasks
- **Asset Management** - ASSETS.md, reference.png, budget tracking
- **Visual QA** - Screenshot paths, VQA reports
- **Memory** - MEMORY.md usage

## Example

Input (generic plan):
```markdown
## 1. Player Movement
- **Goal:** Create player character
- **Requirements:** Third-person camera, move_and_slide
- **Verify:** Screenshot shows player moving with camera following
```

Output (godogen format):
```markdown
## 1. Player Movement

- **Status:** pending
- **Targets:** scenes/player.tscn, scripts/player/player_controller.gd, scripts/player/camera_controller.gd
- **Depends on:** (none)
- **Goal:** Create player character
- **Requirements:** Third-person camera, move_and_slide
- **Verify:** Screenshot shows player moving with camera following
```

## Related Skills

- `godogen` - Main orchestrator that reads converted PLAN.md
- `godot-task` - Executes individual tasks from PLAN.md
- `godot-docs-lookup` - Helps infer correct class references for targets
