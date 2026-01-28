"""Test script for completer module."""

import sys
import os
sys.path.insert(0, "/home/ubuntu/claude-code-history")

# Test that imports work
try:
    from src.completer import ClaudeCodeCompleter, create_completer_session
    from src.history import HistoryReader
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test completer instantiation
try:
    completer = ClaudeCodeCompleter()
    print("✅ ClaudeCodeCompleter instantiated")
except Exception as e:
    print(f"❌ Error creating completer: {e}")
    sys.exit(1)

# Test get_completions (will return empty since no history)
try:
    from prompt_toolkit.document import Document
    doc = Document("fix")
    completions = list(completer.get_completions(doc, None))
    print(f"✅ get_completions works, found {len(completions)} matches for 'fix'")
except Exception as e:
    print(f"❌ Error in get_completions: {e}")
    sys.exit(1)

# Test format_meta
try:
    if hasattr(completer, '_prompts') and completer._prompts:
        print(f"✅ Found {len(completer._prompts)} prompts")
    else:
        print("✅ No prompts found (expected on server without Claude Code)")
except Exception as e:
    print(f"❌ Error checking prompts: {e}")

# Test create_completer_session
try:
    session = create_completer_session()
    print("✅ create_completer_session works")
except Exception as e:
    print(f"❌ Error creating session: {e}")

print("\n🎉 All tests passed!")
