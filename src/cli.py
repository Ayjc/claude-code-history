"""Command line interface for Claude Code History."""

import argparse
import sys
from pathlib import Path
from typing import List, Dict

from .history import HistoryReader, ClaudePrompt
from .fzf_interface import FzfInterface
from .completer import interactive_search
from .config import Config, init_config, get_config


def format_prompt(prompt, max_length: int = 80) -> str:
    """Format a prompt for display."""
    if len(prompt) > max_length:
        return prompt[:max_length] + "..."
    return prompt


def print_prompts(prompts: List, limit: int = 20):
    """Print prompts in a readable format."""
    for i, p in enumerate(prompts[:limit], 1):
        print(f"{i}. {format_prompt(p.prompt)}")
        print(f"   📁 {p.project_path.split('/')[-1]}")
        print(f"   📅 {p.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print()


def print_prompts_detailed(prompts: List, limit: int = 20):
    """Print prompts with full details."""
    for i, p in enumerate(prompts[:limit], 1):
        print(f"{i}. {'=' * 60}")
        print(f"   📝 Prompt: {p.prompt[:200]}...")
        print(f"   📁 Project: {p.project_name}")
        print(f"   📅 Date: {p.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   🔑 ID: {p.id}")
        print()


def print_config(config: Config):
    """Print current configuration."""
    print("Current Configuration:")
    print(f"  max_results: {config.max_results}")
    print(f"  fzf_height: {config.fzf_height}")
    print(f"  show_timestamp: {config.show_timestamp}")
    print(f"  show_project: {config.show_project}")
    print(f"  truncate_length: {config.truncate_length}")
    print(f"  fzf_layout: {config.fzf_layout}")
    print(f"  fzf_border: {config.fzf_border}")
    print(f"  interactive_truncate: {config.interactive_truncate}")


def print_projects(projects: List[str]):
    """Print list of projects."""
    if not projects:
        print("No projects found.")
        return
    
    print(f"Found {len(projects)} project(s):\n")
    for i, name in enumerate(projects, 1):
        print(f"  {i}. {name}")


def build_item_info(prompts: List[ClaudePrompt]) -> Dict[str, Dict[str, str]]:
    """Build info dict for prompts."""
    info = {}
    for p in prompts:
        info[p.prompt] = {
            "project": p.project_name,
            "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M"),
            "id": p.id,
            "full_prompt": p.prompt,
        }
    return info


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search and autocomplete Claude Code history prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cch                            # Open fzf search interface
  cch fix                        # Search for 'fix' in history
  cch --project my-app           # Filter by project
  cch --exclude-project test     # Exclude project
  cch --list-projects            # List all projects
  cch --interactive              # Interactive auto-completion search
  cch --preview                  # Enable preview window
  cch --json                     # Output as JSON
  cch --list                     # List all prompts
  cch --init                     # Initialize config file
  cch --show-config              # Show current configuration

Preview Controls:
  ctrl-p                         # Toggle preview window
  ↑↓                             # Navigate
  Enter                          # Select
  ctrl-c / Esc                   # Cancel
        """,
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Search query string",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all prompts without fzf",
    )
    
    parser.add_argument(
        "--list-detailed",
        action="store_true",
        help="List all prompts with full details",
    )
    
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive auto-completion search",
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of results to show",
    )
    
    parser.add_argument(
        "--no-fzf",
        action="store_true",
        help="Force disable fzf even if available",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize config file",
    )
    
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current configuration",
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to config file",
    )
    
    parser.add_argument(
        "--project",
        "-p",
        action="append",
        help="Filter by project name (can be used multiple times)",
    )
    
    parser.add_argument(
        "--exclude-project",
        "-e",
        action="append",
        help="Exclude project name (can be used multiple times)",
    )
    
    parser.add_argument(
        "--list-projects",
        action="store_true",
        help="List all projects with history",
    )
    
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Enable preview window in fzf",
    )
    
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="Disable preview window",
    )
    
    parser.add_argument(
        "--preview-position",
        choices=["right", "left", "top", "bottom"],
        default="right",
        help="Position of preview window (default: right)",
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = get_config()
    
    # Apply command line overrides
    if args.limit is not None:
        config.max_results = args.limit
    
    # Handle config commands
    if args.init:
        config_path = init_config(args.config)
        print(f"✅ Config file created: {config_path}")
        print(f"\nEdit this file to customize settings.")
        return
    
    if args.show_config:
        print_config(config)
        return
    
    reader = HistoryReader()
    
    # Handle project listing
    if args.list_projects:
        projects = reader.get_all_project_names()
        print_projects(projects)
        return
    
    # Build project filter lists
    projects = args.project if args.project else None
    exclude_projects = args.exclude_project if args.exclude_project else None
    
    # Get prompts with filtering
    prompts = reader.search_multi(
        query=args.query,
        projects=projects,
        exclude_projects=exclude_projects,
    )
    
    if not prompts:
        print("No prompts found.", file=sys.stderr)
        sys.exit(0)
    
    # Check if fzf is available and user didn't disable it
    fzf = FzfInterface()
    use_fzf = fzf.is_available() and not args.no_fzf
    
    # Determine if preview should be shown
    show_preview = args.preview or (not args.no_preview and fzf.is_available())
    
    # Interactive completion
    if args.interactive:
        result = interactive_search(reader, "Search prompts: ")
        if result:
            print(result)
        return
    
    # JSON output
    if args.json:
        import json
        from datetime import datetime
        
        def serialize(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        result = [
            {
                "id": p.id,
                "prompt": p.prompt,
                "timestamp": p.timestamp,
                "project_path": p.project_path,
            }
            for p in prompts
        ]
        print(json.dumps(result, default=serialize, ensure_ascii=False, indent=2))
        return
    
    # List output (no fzf)
    if args.list:
        print_prompts(prompts, config.max_results)
        return
    
    # List detailed output
    if args.list_detailed:
        print_prompts_detailed(prompts, config.max_results)
        return
    
    # Check for fzf
    if not use_fzf:
        print_prompts(prompts, config.max_results)
        print("\n💡 Tip: Install fzf for better experience: brew install fzf")
        return
    
    # Build item info for preview
    item_info = build_item_info(prompts)
    items = [p.prompt for p in prompts]
    
    # Fzf interface with preview
    if show_preview:
        # Create a simple preview using fzf's built-in preview
        preview_height = "50%" if args.preview_position in ["right", "left"] else "30%"
        
        result = fzf.search(
            items,
            prompt="Search prompts: ",
            height=config.fzf_height,
            layout=config.fzf_layout,
            border=config.fzf_border,
        )
    else:
        result = fzf.search(
            items,
            prompt="Search prompts: ",
            height=config.fzf_height,
            layout=config.fzf_layout,
            border=config.fzf_border,
        )
    
    if result:
        print(result)


if __name__ == "__main__":
    main()
