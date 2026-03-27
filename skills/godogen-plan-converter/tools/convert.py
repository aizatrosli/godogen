#!/usr/bin/env python3
"""
Godogen Plan Converter

Converts a generic PLAN.md into godogen-compatible format.
Adds: **Status:**, **Targets:**, **Depends on:** fields
Preserves: **Goal:**, **Requirements:**, **Verify:**

Usage: convert.sh <input_plan.md> [output_plan.md]
"""

import sys
import re
import argparse
from pathlib import Path

# Target inference patterns: (regex pattern, target inference)
TARGET_PATTERNS = [
    # Player/Character
    (r'(?:player|character|movement|third\.?person|spring\.?arm|camera).*?(?:controller|actor|agent)',
     'scripts/player/player_controller.gd, scenes/player.tscn, scripts/player/camera_controller.gd'),

    # Vault/Level Generation
    (r'(?:vault|generation|procedural|room|corridor|shaft|biome|nav.*?mesh).*?(?:generator|system|manager)',
     'scripts/vault/vault_generator.gd, scripts/vault/room_generator.gd, scripts/vault/biome_system.gd, scenes/vault/vault_manager.tscn'),

    # Enemies
    (r'(?:enemy|ai|stamper|filing.*?cabinet|inspector|patrol|chase|detection).*?(?:ai|system|controller)',
     'scripts/enemies/enemy_base.gd, scripts/enemies/enemy_state_machine.gd, scripts/enemies/vision_system.gd, scripts/enemies/sound_detection.gd, scenes/enemies/'),

    # Ropes/Physics Systems
    (r'(?:rope|physics|pulley|winch|hauling|extraction|anchor).*?(?:system|physics|mechanic)',
     'scripts/systems/rope_physics.gd, scripts/systems/rope_climbing.gd, scripts/systems/winch_mechanic.gd, scenes/systems/rope.tscn'),

    # Parcels/Items
    (r'(?:parcel|item|object|cargo|delivery).*?(?:behavior|physics|handler|system)',
     'scripts/parcels/parcel.gd, scripts/parcels/parcel_tier_system.gd, scenes/parcels/parcel_common.tscn'),

    # Special Parcels
    (r'(?:special.*?parcel|magentic|anti.?gravity|screamer|slippery|mimic|ticking|sticky|bouncy|heavy.*?breather)',
     'scripts/parcels/parcel_tier_system.gd, scripts/parcels/magnetic_behavior.gd, scripts/parcels/antigravity_behavior.gd, scripts/parcels/screamer_behavior.gd, scripts/parcels/slippery_behavior.gd, scripts/parcels/heavy_breather_behavior.gd, scripts/parcels/ticking_behavior.gd, scripts/parcels/mimic_behavior.gd, scripts/parcels/sticky_behavior.gd, scripts/parcels/bouncy_behavior.gd, scenes/parcels/'),

    # UI
    (r'(?:ui|menu|hud|hud|screen|interface|panel).*?(?:manager|screen|system)',
     'scripts/ui/ui_manager.gd, scenes/ui/'),

    # Shop/Progression
    (r'(?:shop|supply.*?room|upgrade|progression|economy|credit|currency).*?(?:system|manager|ui)',
     'scripts/ui/shop_manager.gd, scripts/systems/economy.gd, scripts/upgrades/*.gd, scenes/ui/shop_ui.tscn'),

    # Multiplayer/Network
    (r'(?:multiplayer|network|sync|enet|host|join|spawner|synchronizer)',
     'scripts/networking/network_manager.gd, scripts/networking/multiplayer_spawner.gd, scripts/networking/sync_manager.gd, scripts/autoload/network_manager.gd'),

    # Autoloads
    (r'(?:game.*?manager|shift.*?timer|quota.*?manager|voice.*?chat|vault.*?manager)',
     'scripts/autoload/game_manager.gd, scripts/autoload/shift_timer.gd, scripts/autoload/quota_manager.gd, scripts/autoload/voice_chat.gd, scripts/autoload/vault_manager.gd'),

    # Presentation/Test
    (r'(?:presentation|video|test|capture|cinematic|showcase)',
     'test/presentation.gd, screenshots/presentation/'),

    # Death/Status
    (r'(?:death|terminated|ragdoll|spectator|status).*?(?:system|handler|mechanic)',
     'scripts/player/player_death.gd, scripts/player/spectator_mode.gd'),

    # Voice/Chat
    (r'(?:voice|chat|microphone|proximity|audio).*?(?:system|capture|playback|animation)',
     'scripts/systems/proximity_voice.gd, scripts/systems/microphone_capture.gd, scripts/player/jaw_animation.gd'),

    # Quota/Daily
    (r'(?:quota|daily|shift|day.*?advancement|warning).*?(?:system|tracker|manager)',
     'scripts/systems/quota_tracker.gd, scripts/systems/day_advancement.gd, scripts/systems/warning_system.gd'),

    # Items/Equipment
    (r'(?:item|equipment|rope.*?item|pulley.*?item|chalk|packing.*?tape).*?(?:handler|system)',
     'scripts/items/rope_item.gd, scripts/items/pulley_item.gd, scripts/items/chalk_item.gd, scripts/items/packing_tape_item.gd'),
]

# Default targets for common task patterns
DEFAULT_TARGETS = {
    'visual': 'scenes/player.tscn, scenes/ui/hud.tscn, scenes/main/main.tscn, scripts/player/player_controller.gd, scripts/main/main_controller.gd, scripts/ui/hud.gd, scripts/autoload/game_manager.gd, project.godot',
    'player': 'scenes/player.tscn, scripts/player/player_controller.gd, scripts/player/camera_controller.gd',
    'vault': 'scripts/vault/vault_generator.gd, scenes/vault/vault_manager.tscn, scripts/vault/room_generator.gd',
    'enemies': 'scripts/enemies/enemy_base.gd, scenes/enemies/*.tscn, scripts/enemies/stamper_ai.gd, scripts/enemies/filing_cabinet_ai.gd',
    'extraction': 'scenes/systems/rope.tscn, scripts/systems/rope_physics.gd, scripts/systems/rope_climbing.gd, scripts/systems/winch_mechanic.gd',
    'parcels': 'scripts/parcels/parcel.gd, scenes/parcels/parcel_common.tscn, scripts/parcels/parcel_tier_system.gd',
    'special': 'scripts/parcels/magnetic_behavior.gd, scripts/parcels/antigravity_behavior.gd, scripts/parcels/screamer_behavior.gd, scripts/parcels/slippery_behavior.gd, scripts/parcels/heavy_breather_behavior.gd, scripts/parcels/ticking_behavior.gd, scripts/parcels/mimic_behavior.gd, scripts/parcels/sticky_behavior.gd, scripts/parcels/bouncy_behavior.gd, scenes/parcels/',
    'ui': 'scenes/ui/main_menu.tscn, scenes/ui/shop_ui.tscn, scripts/ui/main_menu_manager.gd, scripts/ui/shop_manager.gd',
    'progression': 'scripts/systems/economy.gd, scripts/systems/day_advancement.gd, scripts/systems/warning_system.gd, scripts/upgrades/*.gd',
    'network': 'scripts/autoload/network_manager.gd, scripts/networking/multiplayer_spawner.gd, scripts/networking/sync_manager.gd',
    'voice': 'scripts/systems/proximity_voice.gd, scripts/systems/microphone_capture.gd, scripts/player/jaw_animation.gd',
    'video': 'test/presentation.gd, screenshots/presentation/',
    'death': 'scripts/player/player_death.gd, scripts/player/spectator_mode.gd, scripts/systems/death_system.gd',
    'autolad': 'scripts/autoload/game_manager.gd, scripts/autoload/shift_timer.gd, scripts/autoload/quota_manager.gd, scripts/autoload/voice_chat.gd, scripts/autoload/vault_manager.gd',
}


def infer_targets(task_text: str) -> str:
    """Infer file targets from task description."""
    text_lower = task_text.lower()

    # Try pattern matching first
    for pattern, targets in TARGET_PATTERNS:
        if re.search(pattern, text_lower):
            return targets

    # Check for specific keywords
    if 'visual' in text_lower or 'architecture' in text_lower:
        return DEFAULT_TARGETS['visual']
    if 'vault' in text_lower or 'procedural' in text_lower or 'generation' in text_lower:
        return DEFAULT_TARGETS['vault']
    if 'enemy' in text_lower or 'ai' in text_lower:
        return DEFAULT_TARGETS['enemies']
    if 'rope' in text_lower or 'extraction' in text_lower or 'winch' in text_lower:
        return DEFAULT_TARGETS['extraction']
    if 'parcel' in text_lower and ('special' in text_lower or 'behavior' in text_lower):
        return DEFAULT_TARGETS['special']
    if 'parcel' in text_lower:
        return DEFAULT_TARGETS['parcels']
    if 'ui' in text_lower or 'menu' in text_lower or 'hud' in text_lower:
        return DEFAULT_TARGETS['ui']
    if 'progression' in text_lower or 'upgrade' in text_lower or 'shop' in text_lower:
        return DEFAULT_TARGETS['progression']
    if 'network' in text_lower or 'multiplayer' in text_lower:
        return DEFAULT_TARGETS['network']
    if 'voice' in text_lower or 'chat' in text_lower:
        return DEFAULT_TARGETS['voice']
    if 'video' in text_lower or 'presentation' in text_lower or 'test' in text_lower:
        return DEFAULT_TARGETS['video']
    if 'death' in text_lower or 'terminated' in text_lower:
        return DEFAULT_TARGETS['death']

    # Default: infer from task name
    task_words = text_lower.split()
    if any(w in task_words for w in ['player', 'movement']):
        return DEFAULT_TARGETS['player']
    if any(w in task_words for w in ['ui', 'menu', 'hud']):
        return DEFAULT_TARGETS['ui']

    return 'scripts/autoload/generic_manager.gd, scenes/generic.tscn'


def parse_task_block(text: str) -> dict:
    """Parse a single task block from markdown."""
    lines = text.strip().split('\n')

    task = {
        'number': None,
        'name': None,
        'status': None,
        'targets': None,
        'depends': None,
        'goal': None,
        'requirements': None,
        'verify': None,
    }

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Task header: ## N. Task Name
        if line.startswith('## '):
            match = re.match(r'##\s+(\d+)\.\s+(.+)', line)
            if match:
                task['number'] = int(match.group(1))
                task['name'] = match.group(2).strip()

        # Field parsing: - **Field:** value (colon inside the bold markers)
        elif line.startswith('- **'):
            # Match multi-word field names like "Depends on"
            match = re.match(r'-\s*\*\*(.+?):(?:\*\*|\*)?\s*(.*)', line)
            if match:
                field_name = match.group(1).lower().strip()
                field_value = match.group(2).strip()

                if field_name == 'status':
                    task['status'] = field_value
                elif field_name == 'targets':
                    task['targets'] = field_value
                elif field_name == 'depends on':
                    task['depends'] = field_value
                elif field_name == 'goal':
                    task['goal'] = field_value
                elif field_name == 'requirements':
                    # Requirements can span multiple lines
                    req_lines = [field_value]
                    i += 1
                    while i < len(lines):
                        req_line = lines[i].strip()
                        if req_line.startswith('- ') and not re.match(r'-\s*\*\*', req_line):
                            req_lines.append(req_line[2:])
                            i += 1
                        else:
                            break
                    task['requirements'] = '\n'.join(req_lines)
                    continue
                elif field_name == 'verify':
                    task['verify'] = field_value

        i += 1

    return task


def format_task_block(task: dict) -> str:
    """Format a task block in godogen format."""
    lines = []

    # Header
    lines.append(f"## {task['number']}. {task['name']}")
    lines.append("")

    # Fields (in godogen order)
    lines.append(f"- **Status:** {task['status'] or 'pending'}")
    task_desc = f"{task['name']} {task.get('goal', '')} {task.get('requirements', '')}"
    lines.append(f"- **Targets:** {task['targets'] or infer_targets(task_desc)}")
    lines.append(f"- **Depends on:** {task['depends'] or '(none)'}")
    lines.append("")

    # Original fields
    if task['goal']:
        lines.append(f"- **Goal:** {task['goal']}")
    if task['requirements']:
        lines.append(f"- **Requirements:**")
        for req_line in task['requirements'].split('\n'):
            if req_line.strip():
                lines.append(f"  - {req_line.strip()}")
    if task['verify']:
        lines.append(f"- **Verify:** {task['verify']}")

    return '\n'.join(lines)


def add_documentation_sections(content: str) -> str:
    """Add godogen documentation sections to the plan."""

    sections = [
        "## Task Execution Instructions",
        "",
        "Each task is executed via `Skill(skill=\"godot-task\")` with the full task block. The orchestrator (godogen) manages task flow:",
        "",
        "1. Find next ready task (status=pending, all dependencies done)",
        "2. Update task status to `in_progress`",
        "3. Execute task via godot-task skill",
        "4. Update task status to `done` or `done (partial)` based on verification",
        "5. Commit changes: `git add . && git commit -m \"Task N done\"`",
        "6. Repeat until all tasks complete",
        "",
        "## Asset Management",
        "",
        "- **ASSETS.md** - Tracks generated assets, budgets, and references",
        "- **reference.png** - Visual anchor for art direction (generated in phase 1)",
        "- Asset generation uses `skills/godogen/tools/asset_gen.py` for xAI Grok images and Tripo3D GLBs",
        "- Budget tracking via `assets/budget.json`",
        "",
        "## Visual QA",
        "",
        "- Each task generates screenshots in `screenshots/{task_folder}/`",
        "- VQA reports stored in `visual-qa/{N}.md`",
        "- Visual QA uses `skills/godot-task/scripts/visual_qa.py` with Gemini 3 Flash",
        "- Compare against reference.png for consistency",
        "",
        "## Memory",
        "",
        "- **MEMORY.md** - Technical discoveries, workarounds, Godot quirks",
        "- Read before each task, write back after task completion",
    ]

    return content + '\n\n' + '\n'.join(sections)


def convert_plan(input_path: str, output_path: str = None):
    """Convert a PLAN.md file to godogen format."""

    input_file = Path(input_path)
    if not input_file.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if output_path is None:
        output_path = str(input_file)

    output_file = Path(output_path)

    # Read input
    content = input_file.read_text()

    # Split into tasks and preamble
    task_headers = re.findall(r'##\s+\d+\.\s+.+', content)

    if not task_headers:
        print("Error: No tasks found in PLAN.md", file=sys.stderr)
        sys.exit(1)

    # Parse each task
    tasks = []
    # Match tasks separated by --- or end of file
    pattern = r'(##\s+\d+\.\s+.+?)(?=\n{1,2}---\n{0,2}##\s+\d+\.\s+|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        task = parse_task_block(match)
        if task['name']:
            tasks.append(task)

    if not tasks:
        print("Error: Failed to parse tasks from PLAN.md", file=sys.stderr)
        sys.exit(1)

    # Format tasks in order
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append(format_task_block(task))

    # Find and preserve preamble (title + description before first task)
    preamble_match = re.match(r'^(##.*?)(?=\n\n##\s+\d+\.\s+\d+\.\s+)', content, re.DOTALL)
    preamble = preamble_match.group(1) if preamble_match else "# Game Plan\n\n"

    # Build output
    output_lines = [preamble]
    output_lines.append('')
    output_lines.append('---')
    output_lines.append('')

    # Add separator before each task (except first)
    for i, task in enumerate(formatted_tasks):
        if i > 0:
            output_lines.append('---')
            output_lines.append('')
        output_lines.append(task)

    output_lines.append('')
    output_lines.append('---')
    output_lines.append('')

    # Add documentation sections
    output_lines.append(add_documentation_sections(''))

    output = '\n'.join(output_lines)

    # Write output
    output_file.write_text(output)
    print(f"Converted: {input_path} -> {output_path}")
    print(f"Tasks processed: {len(tasks)}")


def main():
    parser = argparse.ArgumentParser(description='Convert a generic PLAN.md to godogen format')
    parser.add_argument('input', help='Input PLAN.md file path')
    parser.add_argument('output', nargs='?', default=None, help='Output file path (defaults to input)')

    args = parser.parse_args()
    convert_plan(args.input, args.output)


if __name__ == '__main__':
    main()
