"""Fzf interface module for fuzzy search."""

import subprocess
from typing import List, Optional, Callable, Dict, Any


class FzfInterface:
    """Wrapper for fzf fuzzy search functionality."""
    
    def is_available(self) -> bool:
        """
        Check if fzf is installed and available.
        
        Returns:
            True if fzf is available, False otherwise.
        """
        result = subprocess.run(
            ["which", "fzf"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    
    def search(
        self,
        items: List[str],
        prompt: str = "Search: ",
        height: str = "40%",
        layout: str = "reverse",
        border: bool = True,
        preview: bool = False,
        preview_window: str = "right:60%:wrap",
    ) -> Optional[str]:
        """
        Search items using fzf.

        Args:
            items: List of strings to search through.
            prompt: Prompt to display in fzf.
            height: Height of the fzf window.
            layout: Layout option (reverse, default).
            border: Whether to show border.
            preview: Whether to enable preview.
            preview_window: Preview window configuration.

        Returns:
            Selected item as string, or None if cancelled.
        """
        if not items:
            return None

        cmd = [
            "fzf",
            f"--prompt={prompt}",
            f"--height={height}",
            f"--layout={layout}",
            "--ansi",  # Support ANSI colors
        ]

        if border:
            cmd.append("--border")

        if preview:
            # Simple preview showing the full text
            cmd.extend([
                "--preview=echo {}",
                f"--preview-window={preview_window}",
                "--bind=ctrl-p:toggle-preview",
            ])

        result = subprocess.run(
            cmd,
            input="\n".join(items),
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        return None
    
    def search_with_preview(
        self,
        items: List[str],
        preview_callback: Callable[[str], str],
        prompt: str = "Search: ",
        height: str = "60%",
        preview_height: str = "40%",
        layout: str = "reverse",
        border: bool = True,
        preview_position: str = "right",
    ) -> Optional[str]:
        """
        Search items using fzf with preview window.
        
        Args:
            items: List of strings to search through.
            preview_callback: Function that returns preview content for an item.
            prompt: Prompt to display in fzf.
            height: Height of the main fzf window.
            preview_height: Height of preview window.
            layout: Layout option (reverse, default).
            border: Whether to show border.
            preview_position: Position of preview window (right, left, top, bottom).
            
        Returns:
            Selected item as string, or None if cancelled.
        """
        if not items:
            return None
        
        # Build preview command
        import shlex
        preview_cmd = f"echo {{}} | xargs -I {{}} sh -c '{preview_callback.__code__.co_filename}'"
        
        cmd = [
            "fzf",
            f"--prompt={prompt}",
            f"--height={height}",
            f"--layout={layout}",
            f"--preview={preview_cmd}",
            f"--preview-window={preview_position},{preview_height},wrap",
            "--bind=ctrl-p:toggle-preview",
        ]
        
        if border:
            cmd.append("--border")
        
        result = subprocess.run(
            cmd,
            input="\n".join(items),
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        
        return None
    
    def search_with_info(
        self,
        items: List[str],
        item_info: Dict[str, Dict[str, str]],
        prompt: str = "Search: ",
        height: str = "60%",
        layout: str = "reverse",
    ) -> Optional[str]:
        """
        Search items with preview showing additional info.
        
        Args:
            items: List of strings to search through.
            item_info: Dict mapping item to info dict (timestamp, project, etc.)
            prompt: Prompt to display in fzf.
            height: Height of the fzf window.
            layout: Layout option (reverse, default).
            
        Returns:
            Selected item as string, or None if cancelled.
        """
        if not items:
            return None
        
        # Create preview that shows info for selected item
        def get_preview(item: str) -> str:
            info = item_info.get(item, {})
            lines = []
            if info.get("project"):
                lines.append(f"📁 Project: {info['project']}")
            if info.get("timestamp"):
                lines.append(f"📅 Date: {info['timestamp']}")
            if info.get("id"):
                lines.append(f"🔑 ID: {info['id']}")
            lines.append("")
            lines.append("=" * 50)
            lines.append(item[:500] if len(item) > 500 else item)
            return "\n".join(lines)
        
        return self.search_with_preview(
            items=items,
            preview_callback=get_preview,
            prompt=prompt,
            height=height,
            preview_height="50%",
            layout=layout,
            preview_position="right",
        )
    
    def search_multi(
        self,
        items: List[str],
        prompt: str = "Select: ",
        multi: bool = True,
    ) -> List[str]:
        """
        Search and select multiple items.
        
        Args:
            items: List of strings to search through.
            prompt: Prompt to display.
            multi: Allow multiple selections.
            
        Returns:
            List of selected items.
        """
        if not items:
            return []
        
        cmd = [
            "fzf",
            f"--prompt={prompt}",
            "--height=60%",
            "--layout=reverse",
            "--border",
        ]
        
        if multi:
            cmd.extend(["--multi", "--bind=ctrl-a:select-all"])
        
        result = subprocess.run(
            cmd,
            input="\n".join(items),
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")
        
        return []
    
    def search_multi_with_info(
        self,
        items: List[str],
        item_info: Dict[str, Dict[str, str]],
        prompt: str = "Select: ",
    ) -> List[str]:
        """
        Search and select multiple items with preview.
        
        Args:
            items: List of strings to search through.
            item_info: Dict mapping item to info dict.
            prompt: Prompt to display.
            
        Returns:
            List of selected items.
        """
        if not items:
            return []
        
        if not self.is_available():
            return items
        
        # Simple preview command
        preview_cmd = "echo {} | head -c 300"
        
        cmd = [
            "fzf",
            f"--prompt={prompt}",
            "--height=60%",
            "--layout=reverse",
            "--border",
            "--multi",
            "--bind=ctrl-a:select-all",
            f"--preview={preview_cmd}",
            "--preview-window=right,50%,wrap",
            "--bind=ctrl-p:toggle-preview",
        ]
        
        result = subprocess.run(
            cmd,
            input="\n".join(items),
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")
        
        return []
