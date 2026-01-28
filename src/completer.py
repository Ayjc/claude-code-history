"""Auto-completion module for Claude Code prompts."""

from typing import List, Optional, Callable
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style

from .history import HistoryReader, ClaudePrompt


class ClaudeCodeCompleter(Completer):
    """Completer that suggests Claude Code prompts from history."""
    
    def __init__(
        self,
        history_reader: Optional[HistoryReader] = None,
        max_display: int = 10,
    ):
        """
        Initialize the completer.
        
        Args:
            history_reader: HistoryReader instance. If None, creates new one.
            max_display: Maximum number of suggestions to display.
        """
        self.history_reader = history_reader or HistoryReader()
        self.max_display = max_display
        self._prompts: List[ClaudePrompt] = []
        self._load_prompts()
    
    def _load_prompts(self):
        """Load prompts from history."""
        try:
            self._prompts = self.history_reader.get_all()
        except Exception:
            self._prompts = []
    
    def get_completions(
        self,
        document,
        complete_event,
    ) -> List[Completion]:
        """
        Get completions for the current document.
        
        Args:
            document: The current document.
            complete_event: The complete event.
            
        Yields:
            Completion objects.
        """
        word = document.get_word_before_cursor()
        
        if not word:
            return
        
        # Filter prompts containing the word
        matches = [
            p for p in self._prompts
            if word.lower() in p.prompt.lower()
        ]
        
        # Limit display count
        for prompt in matches[:self.max_display]:
            yield Completion(
                text=prompt.prompt,
                start_position=-len(word),
                display=prompt.prompt[:80] + "...",
                display_meta=self._format_meta(prompt),
            )
    
    def _format_meta(self, prompt: ClaudePrompt) -> str:
        """Format meta information for display."""
        parts = []
        
        if prompt.project_path:
            project_name = prompt.project_path.split("/")[-1]
            parts.append(f"📁 {project_name}")
        
        if prompt.timestamp:
            date_str = prompt.timestamp.strftime("%m-%d %H:%M")
            parts.append(f"📅 {date_str}")
        
        return " | ".join(parts)
    
    def refresh(self):
        """Refresh prompts from history."""
        self._load_prompts()


def create_completer_session(
    history_reader: Optional[HistoryReader] = None,
    style: Optional[Style] = None,
) -> PromptSession:
    """
    Create an interactive prompt session with completion.
    
    Args:
        history_reader: Optional HistoryReader instance.
        style: Optional custom style.
        
    Returns:
        PromptSession with auto-completion enabled.
    """
    completer = ClaudeCodeCompleter(history_reader)
    
    # Define custom key bindings
    kb = KeyBindings()
    
    @kb.add(Keys.ControlG, filter=True)
    def cancel(event):
        """Cancel and clear the input."""
        event.app.exit("", result=None)
    
    @kb.add(Keys.ControlR, filter=True)
    def refresh(event):
        """Refresh completions from history."""
        completer.refresh()
        # Trigger completion again
        event.app.current_buffer.complete_while_typing()
    
    # Default style
    if style is None:
        style = Style.from_dict({
            "completer": "fg:ansigreen",
            "meta": "fg:ansicyan",
            "prefix": "fg:ansiyellow",
        })
    
    session = PromptSession(
        completer=completer,
        complete_while_typing=True,
        key_bindings=kb,
        style=style,
    )
    
    return session


def interactive_search(
    history_reader: Optional[HistoryReader] = None,
    prompt_text: str = "Search prompts: ",
) -> Optional[str]:
    """
    Run an interactive search with auto-completion.
    
    Args:
        history_reader: Optional HistoryReader instance.
        prompt_text: Prompt text to display.
        
    Returns:
        Selected prompt text, or None if cancelled.
    """
    session = create_completer_session(history_reader)
    
    try:
        result = session.prompt(
            prompt_text,
            complete_while_typing=True,
        )
        return result if result else None
    except KeyboardInterrupt:
        return None
    except Exception as e:
        print(f"Error during interactive search: {e}")
        return None


def interactive_search_with_preview(
    history_reader: Optional[HistoryReader] = None,
    prompt_text: str = "Search: ",
) -> Optional[str]:
    """
    Run interactive search with preview window.
    
    Args:
        history_reader: Optional HistoryReader instance.
        prompt_text: Prompt text to display.
        
    Returns:
        Selected prompt text, or None if cancelled.
    """
    from prompt_toolkit.layout.containers import VSplit, Window
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.layout.layout import Layout
    
    # Get prompts
    reader = history_reader or HistoryReader()
    prompts = reader.get_all()
    
    if not prompts:
        print("No prompts found.")
        return None
    
    # Create preview function
    def get_preview_text(prompt_text: str) -> str:
        for p in prompts:
            if prompt_text in p.prompt:
                lines = [
                    "=" * 60,
                    f"Prompt: {p.prompt[:100]}...",
                    "",
                    f"Project: {p.project_path}",
                    f"Date: {p.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                    "",
                    f"ID: {p.id}",
                    "=" * 60,
                ]
                return "\n".join(lines)
        return "No match found"
    
    # Simple version without complex layout
    return interactive_search(history_reader, prompt_text)
