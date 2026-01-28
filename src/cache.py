"""Caching layer for Claude Code History."""

import pickle
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class CacheMetadata:
    """Metadata for cache validation."""

    file_path: str
    mtime: float
    size: int

    def is_valid(self) -> bool:
        """Check if file hasn't changed since cache was created."""
        path = Path(self.file_path)
        if not path.exists():
            return False

        stat = path.stat()
        return stat.st_mtime == self.mtime and stat.st_size == self.size

    @staticmethod
    def from_path(file_path: Path) -> 'CacheMetadata':
        """Create metadata from file path."""
        stat = file_path.stat()
        return CacheMetadata(
            file_path=str(file_path),
            mtime=stat.st_mtime,
            size=stat.st_size,
        )


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""

    metadata: CacheMetadata
    prompts: List[Dict]  # Serialized prompts

    def is_valid(self) -> bool:
        """Check if cache entry is still valid."""
        return self.metadata.is_valid()


class HistoryCache:
    """Fast caching layer for history data."""

    CACHE_DIR = Path.home() / ".cache" / "claude-code-history"
    CACHE_VERSION = 1

    def __init__(self):
        """Initialize cache."""
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._cache_file = self.CACHE_DIR / f"history_v{self.CACHE_VERSION}.pkl"
        self._index_file = self.CACHE_DIR / f"index_v{self.CACHE_VERSION}.pkl"

    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file path for cache key."""
        return hashlib.md5(str(file_path).encode()).hexdigest()

    def load(self) -> Optional[Dict[str, CacheEntry]]:
        """Load cache from disk."""
        if not self._cache_file.exists():
            return None

        try:
            with open(self._cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            # Cache corrupted, ignore
            return None

    def save(self, cache: Dict[str, CacheEntry]):
        """Save cache to disk."""
        try:
            with open(self._cache_file, 'wb') as f:
                pickle.dump(cache, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print(f"Warning: Failed to save cache: {e}")

    def get_valid_entries(
        self, file_paths: List[Path]
    ) -> Tuple[Dict[str, CacheEntry], List[Path]]:
        """
        Get valid cache entries and list of files that need reloading.

        Returns:
            Tuple of (valid_cache_dict, files_to_reload)
        """
        cache = self.load()
        if cache is None:
            return {}, file_paths

        valid_cache = {}
        files_to_reload = []

        for file_path in file_paths:
            file_hash = self._get_file_hash(file_path)

            if file_hash in cache and cache[file_hash].is_valid():
                valid_cache[file_hash] = cache[file_hash]
            else:
                files_to_reload.append(file_path)

        return valid_cache, files_to_reload

    def update_entries(
        self,
        existing_cache: Dict[str, CacheEntry],
        new_entries: Dict[str, CacheEntry]
    ):
        """Update cache with new entries."""
        existing_cache.update(new_entries)
        self.save(existing_cache)

    def clear(self):
        """Clear all cache files."""
        if self._cache_file.exists():
            self._cache_file.unlink()
        if self._index_file.exists():
            self._index_file.unlink()

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        if not self._cache_file.exists():
            return {
                "exists": False,
                "size": 0,
                "entries": 0,
            }

        cache = self.load()
        if cache is None:
            return {
                "exists": False,
                "size": 0,
                "entries": 0,
            }

        size = self._cache_file.stat().st_size

        # Count valid entries
        valid_count = sum(1 for entry in cache.values() if entry.is_valid())

        return {
            "exists": True,
            "size": size,
            "size_mb": size / 1024 / 1024,
            "total_entries": len(cache),
            "valid_entries": valid_count,
            "invalid_entries": len(cache) - valid_count,
        }
