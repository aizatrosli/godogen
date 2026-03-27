#!/usr/bin/env python3
"""
Godogen Plan Converter Agent

This agent converts a generic game plan (PLAN.md) into godogen-compatible format.
Can be invoked via the Skill() command or CLI.
"""

import sys
import re
from pathlib import Path

# Import from the main converter
sys.path.insert(0, str(Path(__file__).parent))
from convert import convert_plan, parse_task_block, infer_targets


def run_agent(plan_path: str, output_path: str = None) -> str:
    """
    Agent interface - convert plan file to godogen format.

    Args:
        plan_path: Path to input PLAN.md file
        output_path: Optional output path (defaults to overwriting input)

    Returns:
        Converted PLAN.md content
    """
    input_file = Path(plan_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")

    content = input_file.read_text()
    result = convert_plan(content, output_path)
    return result


if __name__ == '__main__':
    if len(sys.argv) > 1:
        output = run_agent(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
        print(output)
    else:
        print("Usage: agent.py <plan.md> [output.md]")
        print("       cat plan.md | python3 agent.py")
