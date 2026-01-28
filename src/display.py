"""Enhanced display formatting for Claude Code History."""

from typing import List
from datetime import datetime
from .history import ClaudePrompt


class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class Formatter:
    """Enhanced formatting for prompts."""

    @staticmethod
    def format_prompt_line(prompt: ClaudePrompt, index: int, max_length: int = 100) -> str:
        """
        Format a single prompt line with colors and icons.

        Args:
            prompt: The prompt to format
            index: The index number
            max_length: Maximum length for prompt text

        Returns:
            Formatted string with colors
        """
        # Truncate prompt text
        text = prompt.prompt
        if len(text) > max_length:
            text = text[:max_length] + "..."

        # Format timestamp
        time_str = prompt.timestamp.strftime("%Y-%m-%d %H:%M")

        # Build formatted line
        parts = [
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{index}.{Colors.RESET}",
            f"{Colors.WHITE}{text}{Colors.RESET}",
            f"{Colors.DIM}│{Colors.RESET}",
            f"{Colors.BRIGHT_BLUE}📁 {prompt.project_name}{Colors.RESET}",
            f"{Colors.DIM}│{Colors.RESET}",
            f"{Colors.BRIGHT_GREEN}🕐 {time_str}{Colors.RESET}",
        ]

        return " ".join(parts)

    @staticmethod
    def format_prompt_detailed(prompt: ClaudePrompt, index: int) -> str:
        """
        Format a prompt with full details.

        Args:
            prompt: The prompt to format
            index: The index number

        Returns:
            Multi-line formatted string
        """
        lines = [
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{'─' * 70}{Colors.RESET}",
            f"{Colors.BRIGHT_YELLOW}#{index}{Colors.RESET} {Colors.BOLD}{prompt.prompt[:100]}{Colors.RESET}",
            "",
            f"{Colors.BRIGHT_BLUE}📁 Project:{Colors.RESET} {prompt.project_name}",
            f"{Colors.BRIGHT_GREEN}🕐 Time:{Colors.RESET}    {prompt.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"{Colors.BRIGHT_MAGENTA}🔑 ID:{Colors.RESET}      {prompt.id}",
            "",
            f"{Colors.DIM}Full prompt:{Colors.RESET}",
            f"{Colors.WHITE}{prompt.prompt}{Colors.RESET}",
        ]

        return "\n".join(lines)

    @staticmethod
    def format_header(title: str, count: int = None) -> str:
        """
        Format a section header.

        Args:
            title: Header title
            count: Optional count to display

        Returns:
            Formatted header string
        """
        if count is not None:
            title = f"{title} ({count} results)"

        lines = [
            "",
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{'═' * 70}{Colors.RESET}",
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}  {title}{Colors.RESET}",
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{'═' * 70}{Colors.RESET}",
            "",
        ]

        return "\n".join(lines)

    @staticmethod
    def format_stats(stats: dict) -> str:
        """
        Format cache statistics.

        Args:
            stats: Statistics dictionary

        Returns:
            Formatted stats string
        """
        if not stats.get('enabled'):
            return f"{Colors.YELLOW}⚠️  Cache disabled{Colors.RESET}"

        lines = [
            f"{Colors.BRIGHT_CYAN}{Colors.BOLD}Cache Statistics:{Colors.RESET}",
            f"  {Colors.GREEN}✓{Colors.RESET} Size: {Colors.BRIGHT_WHITE}{stats.get('size_mb', 0):.2f} MB{Colors.RESET}",
            f"  {Colors.GREEN}✓{Colors.RESET} Entries: {Colors.BRIGHT_WHITE}{stats.get('valid_entries', 0)}{Colors.RESET}",
        ]

        if stats.get('in_memory_cached'):
            lines.append(f"  {Colors.GREEN}✓{Colors.RESET} In-memory: {Colors.BRIGHT_GREEN}Active ⚡{Colors.RESET}")

        return "\n".join(lines)

    @staticmethod
    def format_search_info(query: str, count: int, elapsed: float) -> str:
        """
        Format search information.

        Args:
            query: Search query
            count: Number of results
            elapsed: Time elapsed in seconds

        Returns:
            Formatted info string
        """
        # Performance indicator
        if elapsed < 0.1:
            perf = f"{Colors.BRIGHT_GREEN}⚡ Instant{Colors.RESET}"
        elif elapsed < 0.5:
            perf = f"{Colors.GREEN}✓ Fast{Colors.RESET}"
        else:
            perf = f"{Colors.YELLOW}○ OK{Colors.RESET}"

        return (
            f"{Colors.BRIGHT_CYAN}Search:{Colors.RESET} '{query}' "
            f"{Colors.DIM}│{Colors.RESET} "
            f"{Colors.BRIGHT_WHITE}{count}{Colors.RESET} results "
            f"{Colors.DIM}│{Colors.RESET} "
            f"{perf} ({elapsed*1000:.0f}ms)"
        )

    @staticmethod
    def format_error(message: str) -> str:
        """Format error message."""
        return f"{Colors.BRIGHT_RED}✗ Error:{Colors.RESET} {message}"

    @staticmethod
    def format_warning(message: str) -> str:
        """Format warning message."""
        return f"{Colors.BRIGHT_YELLOW}⚠️  Warning:{Colors.RESET} {message}"

    @staticmethod
    def format_success(message: str) -> str:
        """Format success message."""
        return f"{Colors.BRIGHT_GREEN}✓ Success:{Colors.RESET} {message}"

    @staticmethod
    def format_info(message: str) -> str:
        """Format info message."""
        return f"{Colors.BRIGHT_BLUE}ℹ Info:{Colors.RESET} {message}"


class TableFormatter:
    """Format data as tables."""

    @staticmethod
    def format_table(headers: List[str], rows: List[List[str]]) -> str:
        """
        Format data as a table.

        Args:
            headers: Column headers
            rows: Data rows

        Returns:
            Formatted table string
        """
        if not rows:
            return ""

        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))

        # Format header
        header_line = " │ ".join(
            f"{Colors.BOLD}{h:<{w}}{Colors.RESET}"
            for h, w in zip(headers, widths)
        )

        separator = "─┼─".join("─" * w for w in widths)

        # Format rows
        row_lines = []
        for row in rows:
            row_line = " │ ".join(
                f"{str(cell):<{w}}"
                for cell, w in zip(row, widths)
            )
            row_lines.append(row_line)

        return "\n".join([
            header_line,
            f"{Colors.DIM}{separator}{Colors.RESET}",
            *row_lines
        ])


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time.

    Args:
        dt: Datetime to format

    Returns:
        Relative time string (e.g., "2 hours ago")
    """
    now = datetime.now(dt.tzinfo)
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks}w ago"
    else:
        months = int(seconds / 2592000)
        return f"{months}mo ago"
