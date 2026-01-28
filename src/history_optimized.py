"""Optimized history reader module for Claude Code prompts."""

from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

try:
    from .cache import HistoryCache, CacheEntry, CacheMetadata
except ImportError:
    from cache import HistoryCache, CacheEntry, CacheMetadata


@dataclass
class ClaudePrompt:
    """Represents a single Claude Code prompt from history."""

    id: str
    prompt: str
    timestamp: datetime
    project_path: str

    def __str__(self) -> str:
        return self.prompt[:80] + "..." if len(self.prompt) > 80 else self.prompt

    @property
    def project_name(self) -> str:
        """Get project name from path."""
        return self.project_path.split("/")[-1]

    def to_dict(self) -> Dict:
        """Convert to dictionary for caching."""
        return {
            'id': self.id,
            'prompt': self.prompt,
            'timestamp': self.timestamp.isoformat(),
            'project_path': self.project_path,
        }

    @staticmethod
    def from_dict(data: Dict) -> 'ClaudePrompt':
        """Create from dictionary."""
        return ClaudePrompt(
            id=data['id'],
            prompt=data['prompt'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            project_path=data['project_path'],
        )


class HistoryReader:
    """Reads and parses Claude Code conversation history with caching."""

    CLAUDE_DIR = Path.home() / ".claude"
    PROJECTS_DIR = CLAUDE_DIR / "projects"

    def __init__(self, use_cache: bool = True, max_workers: int = 4):
        """
        Initialize history reader.

        Args:
            use_cache: Whether to use caching (default: True)
            max_workers: Number of parallel workers for file reading (default: 4)
        """
        self.use_cache = use_cache
        self.max_workers = max_workers
        self._cache = HistoryCache() if use_cache else None
        self._prompts_cache: Optional[List[ClaudePrompt]] = None

    def get_all(self, force_reload: bool = False) -> List[ClaudePrompt]:
        """
        Get all Claude Code prompts from all projects.

        Args:
            force_reload: Force reload from disk, ignoring cache

        Returns:
            List of ClaudePrompt objects sorted by timestamp (newest first).
        """
        # Return in-memory cache if available
        if not force_reload and self._prompts_cache is not None:
            return self._prompts_cache

        prompts = []

        if not self.PROJECTS_DIR.exists():
            return []

        # Get all session files
        all_files = []
        for project in self.PROJECTS_DIR.iterdir():
            if project.is_dir():
                all_files.extend(list(project.glob("*.jsonl")))

        if not all_files:
            return []

        # Use cache if enabled
        if self.use_cache and not force_reload:
            prompts = self._load_with_cache(all_files)
        else:
            prompts = self._load_without_cache(all_files)

        # Sort by timestamp, newest first
        prompts.sort(key=lambda x: x.timestamp, reverse=True)

        # Store in memory cache
        self._prompts_cache = prompts

        return prompts

    def _load_with_cache(self, all_files: List[Path]) -> List[ClaudePrompt]:
        """Load prompts using cache."""
        prompts = []

        # Get valid cache entries and files to reload
        valid_cache, files_to_reload = self._cache.get_valid_entries(all_files)

        # Load from valid cache
        for cache_entry in valid_cache.values():
            prompts.extend([
                ClaudePrompt.from_dict(p) for p in cache_entry.prompts
            ])

        # Load files that need reloading
        if files_to_reload:
            new_prompts, new_cache_entries = self._load_files_parallel(files_to_reload)
            prompts.extend(new_prompts)

            # Update cache
            self._cache.update_entries(valid_cache, new_cache_entries)

        return prompts

    def _load_without_cache(self, all_files: List[Path]) -> List[ClaudePrompt]:
        """Load prompts without cache."""
        prompts, _ = self._load_files_parallel(all_files)
        return prompts

    def _load_files_parallel(
        self, files: List[Path]
    ) -> tuple[List[ClaudePrompt], Dict[str, CacheEntry]]:
        """
        Load files in parallel.

        Returns:
            Tuple of (prompts, cache_entries)
        """
        prompts = []
        cache_entries = {}

        # Use ThreadPoolExecutor for parallel I/O
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._parse_session, f): f
                for f in files
            }

            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_prompts = future.result()
                    prompts.extend(file_prompts)

                    # Create cache entry
                    if self.use_cache:
                        file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
                        cache_entries[file_hash] = CacheEntry(
                            metadata=CacheMetadata.from_path(file_path),
                            prompts=[p.to_dict() for p in file_prompts],
                        )
                except Exception as e:
                    print(f"Warning: Failed to read {file_path}: {e}")

        return prompts, cache_entries

    def _parse_session(self, session_file: Path) -> List[ClaudePrompt]:
        """
        Parse a single session JSONL file.

        Args:
            session_file: Path to the session JSONL file.

        Returns:
            List of ClaudePrompt objects from this session.
        """
        prompts = []
        project_path = session_file.parent

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)

                        # Look for user messages
                        if data.get("type") == "user":
                            message = data.get("message", {})
                            content = message.get("content", "")
                            timestamp_str = data.get("timestamp", "")

                            # Handle content that might be string, list, or dict
                            if isinstance(content, str):
                                prompt_text = content
                            elif isinstance(content, list):
                                # Extract text from list of content blocks
                                prompt_text = " ".join(
                                    item.get("text", "") if isinstance(item, dict) else str(item)
                                    for item in content
                                )
                            else:
                                prompt_text = str(content) if content else ""

                            if prompt_text and timestamp_str:
                                # Parse ISO timestamp
                                timestamp = datetime.fromisoformat(
                                    timestamp_str.replace("Z", "+00:00")
                                )

                                prompts.append(ClaudePrompt(
                                    id=f"{session_file.stem}_{data.get('uuid', '')}",
                                    prompt=prompt_text,
                                    timestamp=timestamp,
                                    project_path=str(project_path),
                                ))

                    except json.JSONDecodeError:
                        continue

        except IOError as e:
            print(f"Warning: Failed to read {session_file}: {e}")

        return prompts

    def get_by_project(self, project_name: str) -> List[ClaudePrompt]:
        """
        Get prompts from a specific project.

        Args:
            project_name: Name or path of the project.

        Returns:
            List of ClaudePrompt objects from that project.
        """
        all_prompts = self.get_all()
        return [
            p for p in all_prompts
            if project_name in p.project_path
        ]

    def get_by_projects(
        self, project_names: List[str], exclude: bool = False
    ) -> List[ClaudePrompt]:
        """
        Get prompts from multiple projects.

        Args:
            project_names: List of project names to include/exclude.
            exclude: If True, exclude these projects instead.

        Returns:
            List of ClaudePrompt objects.
        """
        all_prompts = self.get_all()

        filtered = []
        for p in all_prompts:
            should_include = any(name in p.project_path for name in project_names)

            if exclude:
                if not should_include:
                    filtered.append(p)
            else:
                if should_include:
                    filtered.append(p)

        return filtered

    def get_all_project_names(self) -> List[str]:
        """
        Get list of all project names.

        Returns:
            List of project directory names.
        """
        if not self.PROJECTS_DIR.exists():
            return []

        return [
            project.name
            for project in self.PROJECTS_DIR.iterdir()
            if project.is_dir()
        ]

    def search(
        self,
        query: str,
        project: Optional[str] = None,
        exclude_project: Optional[str] = None,
    ) -> List[ClaudePrompt]:
        """
        Search prompts by query string with optional project filtering.

        Args:
            query: Search query string.
            project: Optional project name to filter by.
            exclude_project: Optional project name to exclude.

        Returns:
            List of ClaudePrompt objects matching the query.
        """
        query_lower = query.lower()

        # Get base prompts with project filtering
        if exclude_project:
            prompts = self.get_by_projects([exclude_project], exclude=True)
        elif project:
            prompts = self.get_by_project(project)
        else:
            prompts = self.get_all()

        # Apply query filter
        if query:
            prompts = [
                p for p in prompts
                if query_lower in p.prompt.lower()
            ]

        return prompts

    def search_multi(
        self,
        query: str,
        projects: Optional[List[str]] = None,
        exclude_projects: Optional[List[str]] = None,
    ) -> List[ClaudePrompt]:
        """
        Search with multiple project filters.

        Args:
            query: Search query string.
            projects: List of projects to include.
            exclude_projects: List of projects to exclude.

        Returns:
            List of ClaudePrompt objects.
        """
        query_lower = query.lower()

        # Start with all prompts
        if exclude_projects:
            prompts = self.get_by_projects(exclude_projects, exclude=True)
        elif projects:
            prompts = self.get_by_projects(projects)
        else:
            prompts = self.get_all()

        # Apply query filter
        if query:
            prompts = [
                p for p in prompts
                if query_lower in p.prompt.lower()
            ]

        return prompts

    def clear_cache(self):
        """Clear all cache."""
        if self._cache:
            self._cache.clear()
        self._prompts_cache = None

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        if not self._cache:
            return {"enabled": False}

        stats = self._cache.get_stats()
        stats["enabled"] = True
        stats["in_memory_cached"] = self._prompts_cache is not None
        if self._prompts_cache:
            stats["in_memory_count"] = len(self._prompts_cache)

        return stats
