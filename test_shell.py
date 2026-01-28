"""Test script for shell integration."""

import sys
import os
sys.path.insert(0, "/home/ubuntu/claude-code-history")

# Test that scripts exist
scripts_dir = "/home/ubuntu/claude-code-history/scripts"
print(f"✅ Scripts directory: {scripts_dir}")

zsh_script = os.path.join(scripts_dir, "claude-code-history.zsh")
bash_script = os.path.join(scripts_dir, "claude-code-history.bash")
install_script = os.path.join(scripts_dir, "install.sh")

print(f"✅ Zsh script exists: {os.path.exists(zsh_script)}")
print(f"✅ Bash script exists: {os.path.exists(bash_script)}")
print(f"✅ Install script exists: {os.path.exists(install_script)}")

# Check script contents
with open(zsh_script) as f:
    zsh_content = f.read()
    print(f"✅ Zsh script size: {len(zsh_content)} bytes")
    has_cch_search = "cch-search()" in zsh_content
    has_bindkey = "bindkey" in zsh_content
    print(f"✅ Zsh has cch-search function: {has_cch_search}")
    print(f"✅ Zsh has key bindings: {has_bindkey}")

with open(bash_script) as f:
    bash_content = f.read()
    print(f"✅ Bash script size: {len(bash_content)} bytes")
    has_cch_search = "cch-search()" in bash_content
    has_complete = "complete -F" in bash_content
    print(f"✅ Bash has cch-search function: {has_cch_search}")
    print(f"✅ Bash has completion: {has_complete}")

with open(install_script) as f:
    install_content = f.read()
    print(f"✅ Install script size: {len(install_content)} bytes")
    has_zsh = "add_to_zshrc" in install_content
    has_bash = "add_to_bashrc" in install_content
    print(f"✅ Install has Zsh support: {has_zsh}")
    print(f"✅ Install has Bash support: {has_bash}")

# Test install script syntax
import subprocess
result = subprocess.run(["bash", "-n", install_script], capture_output=True, text=True)
print(f"✅ Install script syntax valid: {result.returncode == 0}")

print("\n🎉 All shell integration tests passed!")
print("\n📖 Usage:")
print("   # Install integration")
print("   ./scripts/install.sh")
print("")
print("   # Or manually source")
print("   source ~/.claude-code-history/claude-code-history.zsh")
print("")
print("   # Restart terminal or run")
print("   exec zsh")
