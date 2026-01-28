"""Test script for config module."""

import sys
sys.path.insert(0, "/home/ubuntu/claude-code-history")

from src.config import Config, ConfigManager, get_config, init_config

# Test imports
print("✅ Imports successful")

# Test Config creation
config = Config()
print(f"✅ Config created with defaults: max_results={config.max_results}")

# Test init_config
config_path = init_config()
print(f"✅ Config initialized: {config_path}")

# Test get_config
loaded_config = get_config()
print(f"✅ Config loaded: max_results={loaded_config.max_results}")

# Test ConfigManager
manager = ConfigManager()
print(f"✅ ConfigManager created: max_results={manager.get('max_results')}")

# Test value modification
config.max_results = 100
print(f"✅ Config modified: max_results={config.max_results}")

# Test _to_dict
config_dict = config._to_dict()
print(f"✅ Config to dict: {len(config_dict)} keys")

print("\n🎉 All config tests passed!")
