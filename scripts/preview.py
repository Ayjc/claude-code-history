#!/usr/bin/env python3
"""Enhanced preview script for fzf integration."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from display import Colors, Formatter, format_relative_time
from datetime import datetime


def preview_prompt(prompt_text: str, item_info: dict):
    """
    Generate enhanced preview for a prompt.

    Args:
        prompt_text: The prompt text
        item_info: Additional info (project, timestamp, id, full_prompt)
    """
    # Header
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}  Prompt Preview{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{'═' * 70}{Colors.RESET}")
    print()

    # Metadata
    project = item_info.get('project', 'Unknown')
    timestamp_str = item_info.get('timestamp', '')
    prompt_id = item_info.get('id', '')
    full_prompt = item_info.get('full_prompt', prompt_text)

    # Parse timestamp
    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
        relative = format_relative_time(timestamp)
        time_display = f"{timestamp_str} ({relative})"
    except:
        time_display = timestamp_str

    print(f"{Colors.BRIGHT_BLUE}📁 Project:{Colors.RESET}")
    print(f"   {Colors.WHITE}{project}{Colors.RESET}")
    print()

    print(f"{Colors.BRIGHT_GREEN}🕐 Time:{Colors.RESET}")
    print(f"   {Colors.WHITE}{time_display}{Colors.RESET}")
    print()

    print(f"{Colors.BRIGHT_MAGENTA}🔑 ID:{Colors.RESET}")
    print(f"   {Colors.DIM}{prompt_id}{Colors.RESET}")
    print()

    # Separator
    print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}")
    print()

    # Full prompt content
    print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}Prompt Content:{Colors.RESET}")
    print()

    # Word wrap the prompt
    max_width = 68
    words = full_prompt.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        if current_length + word_length + len(current_line) > max_width:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length
        else:
            current_line.append(word)
            current_length += word_length

    if current_line:
        lines.append(" ".join(current_line))

    for line in lines:
        print(f"  {Colors.WHITE}{line}{Colors.RESET}")

    print()

    # Footer with stats
    word_count = len(full_prompt.split())
    char_count = len(full_prompt)

    print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}")
    print(f"{Colors.DIM}Words: {word_count} │ Characters: {char_count}{Colors.RESET}")


def main():
    """Main preview function."""
    if len(sys.argv) < 2:
        print("Usage: preview.py <prompt_text> [info_json]")
        sys.exit(1)

    prompt_text = sys.argv[1]

    # Try to load additional info
    item_info = {}
    if len(sys.argv) > 2:
        try:
            item_info = json.loads(sys.argv[2])
        except:
            pass

    preview_prompt(prompt_text, item_info)


if __name__ == "__main__":
    main()
