"""Claude Code History - Search and autocomplete Claude Code prompts."""

__version__ = "0.1.0"

from .history import HistoryReader, ClaudePrompt
from .fzf_interface import FzfInterface
from .completer import (
    ClaudeCodeCompleter,
    create_completer_session,
    interactive_search,
)
from .config import Config, ConfigManager, get_config, init_config

__all__ = [
    "HistoryReader",
    "ClaudePrompt",
    "FzfInterface",
    "ClaudeCodeCompleter",
    "create_completer_session",
    "interactive_search",
    "Config",
    "ConfigManager",
    "get_config",
    "init_config",
]
