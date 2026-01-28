"""Configuration management module."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
import json


@dataclass
class Config:
    """Configuration class for Claude Code History."""
    
    # General settings
    max_results: int = 20
    fzf_height: str = "40%"
    
    # Display settings
    show_timestamp: bool = True
    show_project: bool = True
    truncate_length: int = 80
    
    # fzf settings
    fzf_layout: str = "reverse"
    fzf_border: bool = True
    
    # Interactive settings
    interactive_truncate: int = 100
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """
        Load configuration from file.
        
        Args:
            config_path: Path to config file. If None, uses default locations.
            
        Returns:
            Config object with loaded settings.
        """
        config = cls()
        
        if config_path is None:
            config_path = cls._find_config_file()
        
        if config_path and config_path.exists():
            config = cls._parse_file(config_path)
        
        return config
    
    @staticmethod
    def _find_config_file() -> Optional[Path]:
        """Find config file in standard locations."""
        # Priority: XDG_CONFIG_HOME > ~/.config > ~/.claude-code-history
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        
        locations = [
            Path(xdg_config) / "cch" / "config.toml" if xdg_config else None,
            Path.home() / ".config" / "cch" / "config.toml",
            Path.home() / ".cch" / "config.toml",
            Path.home() / ".claude-code-history" / "config.toml",
        ]
        
        for loc in locations:
            if loc and loc.exists():
                return loc
        
        return None
    
    @classmethod
    def _parse_file(cls, config_path: Path) -> "Config":
        """Parse config file and update settings."""
        config = cls()
        
        try:
            import toml
            data = toml.load(config_path)
            config = cls._apply_dict(config, data)
        except ImportError:
            # Fallback to json if toml not available
            try:
                with open(config_path) as f:
                    data = json.load(f)
                config = cls._apply_dict(config, data)
            except (json.JSONDecodeError, IOError):
                pass
        
        return config
    
    @classmethod
    def _apply_dict(cls, config: "Config", data: Dict[str, Any]) -> "Config":
        """Apply dictionary values to config."""
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def save(self, config_path: Optional[Path] = None) -> Path:
        """
        Save configuration to file.
        
        Args:
            config_path: Path to save config. If None, uses default location.
            
        Returns:
            Path to saved config file.
        """
        if config_path is None:
            config_path = self._get_default_config_path()
        
        # Create parent directories
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import toml
            with open(config_path, "w") as f:
                toml.dump(self._to_dict(), f)
        except ImportError:
            # Fallback to json
            with open(config_path, "w") as f:
                json.dump(self._to_dict(), f, indent=2)
        
        return config_path
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "max_results": self.max_results,
            "fzf_height": self.fzf_height,
            "show_timestamp": self.show_timestamp,
            "show_project": self.show_project,
            "truncate_length": self.truncate_length,
            "fzf_layout": self.fzf_layout,
            "fzf_border": self.fzf_border,
            "interactive_truncate": self.interactive_truncate,
        }
    
    @staticmethod
    def _get_default_config_path() -> Path:
        """Get default config path."""
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "cch" / "config.toml"
        return Path.home() / ".config" / "cch" / "config.toml"
    
    @classmethod
    def init(cls, config_path: Optional[Path] = None) -> Path:
        """
        Initialize default config file.
        
        Args:
            config_path: Path to save config. If None, uses default location.
            
        Returns:
            Path to created config file.
        """
        config = cls()
        return config.save(config_path)


class ConfigManager:
    """Manager for configuration files."""
    
    def __init__(self):
        self.config = Config.load()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """Set a config value."""
        setattr(self.config, key, value)
    
    def reload(self):
        """Reload configuration from file."""
        self.config = Config.load()
    
    def save(self, config_path: Optional[Path] = None) -> Path:
        """Save current configuration."""
        return self.config.save(config_path)


def get_config() -> Config:
    """Get the current configuration."""
    return Config.load()


def init_config(config_path: Optional[Path] = None) -> Path:
    """
    Initialize a new config file.
    
    Args:
        config_path: Optional path to config file.
        
    Returns:
        Path to created config file.
    """
    return Config.init(config_path)
