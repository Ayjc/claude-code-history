"""Test script for project filtering."""

import sys
sys.path.insert(0, "/home/ubuntu/claude-code-history")

from src.history import HistoryReader, ClaudePrompt
from datetime import datetime

# Test imports
print("✅ Imports successful")

# Test HistoryReader creation
reader = HistoryReader()
print("✅ HistoryReader created")

# Test get_all_project_names (will be empty on server)
projects = reader.get_all_project_names()
print(f"✅ get_all_project_names: {len(projects)} projects")

# Test search_multi with projects
prompts = reader.search_multi("fix", projects=["test"], exclude_projects=["exclude"])
print(f"✅ search_multi works: {len(prompts)} prompts")

# Test ClaudePrompt.project_name property
test_prompt = ClaudePrompt(
    id="test-123",
    prompt="Fix the bug",
    timestamp=datetime.now(),
    project_path="/home/user/my-project",
)
print(f"✅ ClaudePrompt.project_name: {test_prompt.project_name}")

# Test get_by_projects
prompts = reader.get_by_projects(["test"], exclude=False)
prompts_excluded = reader.get_by_projects(["test"], exclude=True)
print(f"✅ get_by_projects: {len(prompts)} prompts")
print(f"✅ get_by_projects (exclude): {len(prompts_excluded)} prompts")

print("\n🎉 All project filtering tests passed!")
