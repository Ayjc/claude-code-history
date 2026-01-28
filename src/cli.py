"""Command line interface for Claude Code History."""

import argparse
import sys
from pathlib import Path
from typing import List, Dict

from .history import HistoryReader, ClaudePrompt
from .fzf_interface import FzfInterface
from .completer import interactive_search
from .config import Config, init_config, get_config
from .display import Formatter, Colors
import time


def print_prompts(prompts: List, limit: int = 20):
    """Print prompts in a readable format with enhanced formatting."""
    if not prompts:
        print(Formatter.format_warning("No prompts found"))
        return

    print(Formatter.format_header("Search Results", len(prompts)))

    for i, p in enumerate(prompts[:limit], 1):
        print(Formatter.format_prompt_line(p, i))

    if len(prompts) > limit:
        remaining = len(prompts) - limit
        print()
        print(Formatter.format_info(f"{remaining} more results (use --limit to see more)"))


def print_prompts_detailed(prompts: List, limit: int = 20):
    """Print prompts with full details."""
    if not prompts:
        print(Formatter.format_warning("No prompts found"))
        return

    print(Formatter.format_header("Detailed Results", len(prompts)))

    for i, p in enumerate(prompts[:limit], 1):
        print(Formatter.format_prompt_detailed(p, i))
        print()

    if len(prompts) > limit:
        remaining = len(prompts) - limit
        print(Formatter.format_info(f"{remaining} more results (use --limit to see more)"))


def print_config(config: Config):
    """Print current configuration with enhanced formatting."""
    print(Formatter.format_header("Configuration"))

    rows = [
        ["max_results", str(config.max_results)],
        ["fzf_height", config.fzf_height],
        ["show_timestamp", str(config.show_timestamp)],
        ["show_project", str(config.show_project)],
        ["truncate_length", str(config.truncate_length)],
        ["fzf_layout", config.fzf_layout],
        ["fzf_border", str(config.fzf_border)],
        ["interactive_truncate", str(config.interactive_truncate)],
    ]

    for key, value in rows:
        print(f"  {Colors.BRIGHT_CYAN}{key}:{Colors.RESET} {Colors.WHITE}{value}{Colors.RESET}")


def print_projects(projects: List[str]):
    """Print list of projects with enhanced formatting."""
    if not projects:
        print(Formatter.format_warning("No projects found"))
        return

    print(Formatter.format_header("Projects", len(projects)))

    for i, name in enumerate(projects, 1):
        print(f"  {Colors.BRIGHT_CYAN}{i}.{Colors.RESET} {Colors.WHITE}{name}{Colors.RESET}")


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

    # Get prompts with filtering and timing
    start_time = time.perf_counter()
    prompts = reader.search_multi(
        query=args.query,
        projects=projects,
        exclude_projects=exclude_projects,
    )
    elapsed = time.perf_counter() - start_time

    if not prompts:
        print(Formatter.format_warning("No prompts found"))

        # Show cache stats if available
        stats = reader.get_cache_stats()
        if stats.get('enabled'):
            print()
            print(Formatter.format_stats(stats))

        sys.exit(0)

    # Show search info for queries
    if args.query:
        print(Formatter.format_search_info(args.query, len(prompts), elapsed))
        print()
    
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
        print()
        print(Formatter.format_info("Install fzf for better experience: brew install fzf"))
        return

    # Build item info for preview
    item_info = build_item_info(prompts)
    items = [p.prompt for p in prompts]

    # Prepare preview script
    preview_script = Path(__file__).parent.parent / "scripts" / "preview.py"

    # Fzf interface with enhanced preview
    if show_preview and preview_script.exists():
        # Build preview command with item info
        preview_cmd = f"python3 {preview_script} {{}} '{{}}'"

        result = fzf.search(
            items,
            prompt=f"{Colors.BRIGHT_CYAN}🔍 Search prompts:{Colors.RESET} ",
            height=config.fzf_height,
            layout=config.fzf_layout,
            border=config.fzf_border,
            preview=True,
            preview_window=f"{args.preview_position}:60%:wrap",
        )
    else:
        result = fzf.search(
            items,
            prompt=f"{Colors.BRIGHT_CYAN}🔍 Search prompts:{Colors.RESET} ",
            height=config.fzf_height,
            layout=config.fzf_layout,
            border=config.fzf_border,
        )
    
    if result:
        print(result)


if __name__ == "__main__":
    main()
