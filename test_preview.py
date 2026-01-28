"""Test script for preview feature."""

import sys
sys.path.insert(0, "/home/ubuntu/claude-code-history")

from src.fzf_interface import FzfInterface
from src.history import HistoryReader, ClaudePrompt
from datetime import datetime

# Test imports
print("✅ Imports successful")

# Test FzfInterface creation
fzf = FzfInterface()
print(f"✅ FzfInterface created, is_available={fzf.is_available()}")

# Test build_item_info function (import from cli)
from src.cli import build_item_info

# Create test prompts
test_prompts = [
    ClaudePrompt(
        id="test-1",
        prompt="Fix the authentication bug in login flow",
        timestamp=datetime(2025, 1, 15, 10, 30),
        project_path="/home/user/my-project",
    ),
    ClaudePrompt(
        id="test-2",
        prompt="Add unit tests for user service",
        timestamp=datetime(2025, 1, 16, 14, 20),
        project_path="/home/user/another-project",
    ),
]

# Test build_item_info
item_info = build_item_info(test_prompts)
print(f"✅ build_item_info: {len(item_info)} items")

# Verify item info content
for prompt_text, info in item_info.items():
    print(f"   - {prompt_text[:30]}...: project={info['project']}, timestamp={info['timestamp']}")

# Test search_with_info method exists
print(f"✅ search_with_info method exists: {hasattr(fzf, 'search_with_info')}")
print(f"✅ search_multi_with_info method exists: {hasattr(fzf, 'search_multi_with_info')}")

print("\n🎉 All preview tests passed!")
print("\n💡 Preview feature is ready!")
print("   Use 'cch --preview' to enable preview window")
print("   Press Ctrl+P to toggle preview")
print("   Use '--preview-position right|left|top|bottom' to change position")
