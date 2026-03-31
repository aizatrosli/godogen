---
name: godot-task
description: |
  Execute a single Godot development task — generate scenes and/or scripts, verify visually.
context: fork
---

# Godot Task Executor

All files below are in `${CLAUDE_SKILL_DIR}/`. Load progressively — read each file when its phase begins, not upfront.

| File | Purpose | When to read |
|------|---------|--------------|
| `quirks.md` | Known Godot gotchas and workarounds | Before writing any code |
| `gdscript.md` | GDScript syntax reference | Before writing any code |
| `scene-generation.md` | Building `.tscn` files via headless GDScript builders | Targets include `.tscn` |
| `script-generation.md` | Writing runtime `.gd` scripts for node behavior | Targets include `.gd` |
| `coordination.md` | Ordering scene + script generation | Targets include both `.tscn` and `.gd` |
| `test-harness.md` | Writing `test/test_{id}.gd` verification scripts | Before writing test harness |
| `capture.md` | Screenshot/video capture with GPU detection | Before capturing screenshots |
| `visual-qa.md` | Automated screenshot comparison against reference | `reference.png` exists and task has visual output |
| `doc_api/_common.md` | Index of ~128 common Godot classes (one-line each) | Need API ref; scan to find class names |
| `doc_api/_other.md` | Index of ~732 remaining Godot classes | Need API ref; class isn't in `_common.md` |
| `doc_api/{ClassName}.md` | Full API reference for a single Godot class | Need API ref; look up specific class |

Bootstrap doc_api: `bash ${CLAUDE_SKILL_DIR}/tools/ensure_doc_api.sh`

Execute a single development task from PLAN.md. The task block is passed as `$ARGUMENTS` — a markdown block copied verbatim from PLAN.md, starting with `## N. Task Name` and containing all task fields (`**Status:**`, `**Targets:**`, `**Classes to use:**`, `**Goal:**`, `**Requirements:**`, `**Verify:**`).

$ARGUMENTS

## Workflow

1. **Pre-task verification** — Call `Skill(skill="godot-docs-verify")` with task description.
   - This reads the `**Classes to use:**` field from the task.
   - Verifies all classes exist in official Godot documentation.
   - Fails task if any class not found.
   - Saves lookup cache to `temp/docs_lookups_task_{N}.md`.
2. **Analyze the task** — read the task's **Targets** and **Classes to use** to determine what to generate:
   - `scenes/*.tscn` targets → generate scene builder(s)
   - `scripts/*.gd` targets → generate runtime script(s)
   - Both → generate scenes FIRST, then scripts (scenes create nodes that scripts attach to)
3. **Import assets** — run `timeout 60 godot --headless --import` to generate `.import` files for any new textures, GLBs, or resources. Without this, `load()` fails with "No loader found" errors. Re-run after modifying existing assets.
4. **Generate scene(s)** — write GDScript scene builder, compile to produce `.tscn`
5. **Generate script(s)** — write `.gd` files to `scripts/`
   - Use `doc_api/` files for API reference when writing code.
   - For each method call, verify against `doc_api/{ClassName}.md` if unsure.
6. **Pre-validate scripts** — catch compilation errors early before full project validation. For each newly written or modified `.gd` file, run `timeout 30 godot --headless --quit 2>&1` and filter the output for errors mentioning that file's path.
7. **Validate** — run `timeout 60 godot --headless --quit 2>&1` to parse-check all project scripts.
8. **Fix errors** — if Godot reports errors, read output, fix files, re-run. Repeat until clean.
   - For `Invalid call` / `method not found` errors:
     - Call `Skill(skill="godot-docs-lookup")` to verify the class/method exists.
     - Compare internal knowledge vs official docs.
     - Fix based on documentation, not assumptions.
9. **Generate test harness** — write `test/test_{task_id}.gd` implementing the task's **Verify** scenario.
10. **Capture screenshots** — run test with GPU display (or xvfb fallback) and `--write-movie` to produce PNGs
11. **Verify visually** — read captured PNGs and check three things:
    - **Task goal:** does the screenshot match the **Verify** description?
    - **Visual consistency:** if `reference.png` exists, compare against it — color palette, scale proportions, camera angle, and visual density should be consistent.
    - **Visual quality & logic:** look for obvious bugs — geometry clipping, objects floating, wrong assets, text overflow, UI elements overlapping or cut off.
    Also check harness stdout for `ASSERT FAIL`.
    If any check fails, identify the issue, fix scene/script/test, and repeat from step 3 (or step 4 if only scripts changed).
12. **Visual QA** — run automated visual QA when applicable.
13. **Documentation audit** — After task completion, append a `## Task N — {Name}` section to `MEMORY.md` (never overwrite earlier entries). Include:
    - **Classes:** Godot classes used (`CharacterBody3D`, `SpringArm3D`, ...)
    - **Methods:** `ClassName.method_name()` one per line, note if verified via `doc_api/`
    - **Workarounds:** non-obvious fixes needed (cross-reference quirks.md where applicable)
    - **Conflicts:** discrepancies between internal knowledge and official docs
    - **Warnings:** deprecated methods used — flag with ⚠️
14. **Store final evidence** — save screenshots in `screenshots/{task_folder}/` before reporting completion.

## Iteration Tracking

Steps 3-11 form an **implement → screenshot → verify → VQA** loop.

There is no fixed limit for the overall implement→screenshot→verify loop — use judgment:
- If there is progress — even in small, iterative steps — keep going. Screenshots and file updates are cheap.
- If you recognize a **fundamental limitation** (wrong architecture, missing engine feature, broken assumption), stop early — even after 2-5 iterations. More loops won't help.
- The signal to stop is **"I'm making the same kind of fix repeatedly without convergence"**.

The **VQA fix cycle** (step 11) has a separate hard limit: max 3 fix-and-rerun cycles. After 3, the root cause is upstream — report to orchestrator. See `visual-qa.md`.

## Reporting to Orchestrator

Always end your response with:
- **Screenshot path:** `screenshots/{task_folder}/` and which frames best represent the result (e.g., `frame0003.png`, `frame0006.png`)
- **What each screenshot shows** — one line per frame
- **VQA report:** path to `visual-qa/{N}.md` (or "skipped" if non-visual), note which mode (static/dynamic)

On failure, also include:
- What's still wrong
- What you tried and why it didn't fix it
- Your best guess at the root cause (include VQA report content if relevant)

The caller (godogen orchestrator) will decide whether to adjust the task, re-scaffold, or accept the current state.

## Commands

```bash
# Import new/modified assets (MUST run before scene builders):
timeout 60 godot --headless --import

# Compile a scene builder (produces .tscn):
timeout 60 godot --headless --script <path_to_gd_builder>

# Validate all project scripts (parse check):
timeout 60 godot --headless --quit 2>&1
```

**Structured error recovery:** When a compilation error is caught:
1. Parse the error — extract the file path, line number, and error type from Godot's output
2. Look up the class — if the error mentions an unknown method or property, read `doc_api/{ClassName}.md` for the class involved
3. Check quirks — cross-reference against `quirks.md` for known patterns (`:=` with `instantiate()`, polymorphic math functions, Camera2D `current`, etc.)
4. Fix and re-validate — edit the specific file, then re-run the pre-validation step on that file only before proceeding

**Error handling:** Parse Godot's stderr/stdout for error lines. Common issues:
- `Parser Error` — syntax error in GDScript, fix the line indicated
- `Invalid call` / `method not found` — wrong node type or API usage, look up the class in `doc_api`
- `Cannot infer type` — `:=` used with `instantiate()` or polymorphic math functions, see type inference rules
- Script hangs — missing `quit()` call in scene builder; kill the process and add `quit()`

## Project Memory

Read `MEMORY.md` before starting work — it contains discoveries from previous tasks (workarounds, Godot quirks, asset details, architectural decisions). After completing your task, write back anything useful you learned: what worked, what failed, technical specifics others will need.
