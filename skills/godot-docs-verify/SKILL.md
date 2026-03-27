---
name: godot-docs-verify
description: |
  Pre-task validation that requires Godot documentation lookup before task execution.
context: fork
---

# Godot Documentation Verification

## Purpose

Enforce mandatory documentation consultation before task execution. This skill ensures that:
1. All Godot classes used in a task are declared in PLAN.md
2. Documentation is looked up BEFORE code generation
3. API methods are verified against official docs
4. Deprecated methods are flagged

## Integration with godot-task

This skill is a **pre-flight hook** that runs BEFORE `godot-task` executes the actual task:

```
1. User: Execute Task N
2. orchestrator: Skill(skill="godot-docs-verify") with Task N
3. verify: Read "Classes to use" from PLAN.md
4. verify: Call godot-docs-lookup for each class
5. verify: Save results to temp/docs_lookups_task_N.md
6. verify: Fail if any lookup fails
7. verify: Success → allow godot-task to proceed
8. orchestrator: Skill(skill="godot-task") with Task N
```

## Requirements

### PLAN.md Task Format

Each task MUST include a `**Classes to use:**` field:

```markdown
## N. Task Name

- **Status:** pending
- **Targets:** scenes/path.tscn, scripts/path.gd
- **Depends on:** M
- **Classes to use:** CharacterBody3D, Area3D, NavigationAgent3D
- **Documentation checked:** [ ] Before execution (auto-filled by verify)
- **Goal:** Create player character
- **Requirements:** ...
- **Verify:** ...
```

### Required Classes

The skill expects one or more class names separated by commas. Valid classes:
- Core: `CharacterBody3D`, `RigidBody3D`, `Area3D`, `Node3D`
- Multiplayer: `MultiplayerSpawner`, `ENetMultiplayerPeer`
- Audio: `AudioStreamPlayer3D`, `AudioServer`
- Navigation: `NavigationAgent3D`
- File: `FileAccess`, `DirAccess`
- Rendering: `GPUParticles3D`, `DirectionalLight3D`
- Tree: `SceneTree`, `ResourceLoader`

## Workflow

1. **Parse task argument** - Extract "Classes to use" field from task description
2. **Lookup each class** - Call `godot-docs-lookup` for each declared class
3. **Validate results** - Ensure all lookups succeeded
4. **Save lookup cache** - Store results in `temp/docs_lookups_task_N.md`
5. **Report status** - Return success/failure to orchestrator

## Commands

```bash
# Run verification (inside skill directory):
bash ${CLAUDE_SKILL_DIR}/tools/verify.sh "<task description>"

# Verify specific classes only:
bash ${CLAUDE_SKILL_DIR}/tools/verify.sh --classes "CharacterBody3D,Area3D" "<task description>"
```

## Output

On success, writes to `temp/docs_lookups_task_N.md`:

```markdown
# Task {N} Documentation Lookup

## Classes Verified

### CharacterBody3D
- Status: Found
- Source: https://docs.godotengine.org/en/stable/classes/class_characterbody3d.html
- Key methods: move_and_slide(), is_on_floor(), velocity

### Area3D
- Status: Found
- Source: https://docs.godotengine.org/en/stable/classes/class_area3d.html
- Key methods: body_entered, body_exited, get_overlapping_bodies()

## Lookup Timestamp
2026-03-27T05:00:00Z

## Verification Status
[✓] All {count} classes found in official documentation
```

On failure, exits with code 1 and error message:
```
ERROR: Class 'NonExistentClass' not found in Godot documentation
```

## Error Conditions

| Condition | Error | Action |
|-----------|-------|--------|
| Class not declared | "No 'Classes to use' field found" | Task cannot proceed |
| Class not found | "Class 'X' not found in docs" | Task fails, retry with correct class |
| Lookup fails | "Documentation lookup failed" | Retry, check network/docs repo |
| Deprecated method | "Method 'X' deprecated" | Flag warning, suggest replacement |

## Usage Example

```
Execute Task 2: Player Movement

- **Classes to use:** CharacterBody3D, Input, SceneTree
```

Verification will:
1. Look up `CharacterBody3D` API
2. Look up `Input` (static class) API
3. Look up `SceneTree` API
4. Save results to `temp/docs_lookups_task_2.md`
5. Allow task to proceed
