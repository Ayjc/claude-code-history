"""History reader module for Claude Code prompts."""

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set
import json


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


class HistoryReader:
    """Reads and parses Claude Code conversation history."""
    
    CLAUDE_DIR = Path.home() / ".claude"
    PROJECTS_DIR = CLAUDE_DIR / "projects"
    
    def get_all(self) -> List[ClaudePrompt]:
        """
        Get all Claude Code prompts from all projects.
        
        Returns:
            List of ClaudePrompt objects sorted by timestamp (newest first).
        """
        prompts = []
        
        if not self.PROJECTS_DIR.exists():
            return []
        
        for project in self.PROJECTS_DIR.iterdir():
            if project.is_dir():
                prompts.extend(self._read_project(project))
        
        # Sort by timestamp, newest first
        return sorted(prompts, key=lambda x: x.timestamp, reverse=True)
    
    def _read_project(self, project_path: Path) -> List[ClaudePrompt]:
        """Read all session files from a single project."""
        prompts = []
        sessions_dir = project_path / "sessions"
        
        if not sessions_dir.exists():
            return prompts
        
        for session_file in sessions_dir.glob("*.json"):
            prompt = self._parse_session(session_file, project_path)
            if prompt:
                prompts.append(prompt)
        
        return prompts
    
    def _parse_session(
        self, session_file: Path, project_path: Path
    ) -> Optional[ClaudePrompt]:
        """
        Parse a single session JSON file.
        
        Args:
            session_file: Path to the session JSON file.
            project_path: Path to the project directory.
            
        Returns:
            ClaudePrompt object or None if parsing fails.
        """
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extract the first user message as the prompt
            messages = data.get("messages", [])
            first_prompt = ""
            
            for msg in messages:
                if msg.get("role") == "user":
                    first_prompt = msg.get("content", "")
                    break
            
            # If no user message found, use empty string
            if not first_prompt:
                first_prompt = ""
            
            return ClaudePrompt(
                id=session_file.stem,
                prompt=first_prompt,
                timestamp=datetime.fromtimestamp(session_file.stat().st_mtime),
                project_path=str(project_path),
            )
            
        except (json.JSONDecodeError, IOError) as e:
            # Log error but continue processing other files
            print(f"Warning: Failed to parse {session_file}: {e}")
            return None
    
    def get_by_project(self, project_name: str) -> List[ClaudePrompt]:
        """
        Get prompts from a specific project.
        
        Args:
            project_name: Name or path of the project.
            
        Returns:
            List of ClaudePrompt objects from that project.
        """
        prompts = []
        
        if not self.PROJECTS_DIR.exists():
            return []
        
        for project in self.PROJECTS_DIR.iterdir():
            if project.is_dir() and project_name in project.name:
                prompts.extend(self._read_project(project))
        
        return sorted(prompts, key=lambda x: x.timestamp, reverse=True)
    
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
        prompts = []
        
        if not self.PROJECTS_DIR.exists():
            return []
        
        for project in self.PROJECTS_DIR.iterdir():
            if not project.is_dir():
                continue
            
            should_include = any(name in project.name for name in project_names)
            
            if exclude:
                if not should_include:
                    prompts.extend(self._read_project(project))
            else:
                if should_include:
                    prompts.extend(self._read_project(project))
        
        return sorted(prompts, key=lambda x: x.timestamp, reverse=True)
    
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
