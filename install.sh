#!/bin/bash
# Installation script for Claude Code History

set -e

echo "🚀 Installing Claude Code History..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check if fzf is installed
if ! command -v fzf &> /dev/null; then
    echo "⚠️  Warning: fzf is not installed"
    echo "   Install it for better experience:"
    echo "   - macOS: brew install fzf"
    echo "   - Ubuntu/Debian: sudo apt install fzf"
    echo "   - Arch: sudo pacman -S fzf"
    echo ""
else
    echo "✓ Found fzf"
fi

# Install package
echo ""
echo "📦 Installing package..."

if command -v pipx &> /dev/null; then
    echo "Using pipx (recommended)..."
    pipx install -e .
elif [ -n "$VIRTUAL_ENV" ]; then
    echo "Using active virtual environment..."
    pip install -e .
else
    echo "Installing with pip..."
    pip3 install --user -e .
fi

echo ""
echo "✅ Installation complete!"
echo ""

# Test installation
if command -v cch &> /dev/null; then
    echo "✓ Command 'cch' is available"

    # Show version and stats
    echo ""
    echo "📊 Testing installation..."
    cch --list --limit 3

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎉 Claude Code History is ready to use!"
    echo ""
    echo "Quick start:"
    echo "  cch                    # Open fzf search"
    echo "  cch fix                # Search for 'fix'"
    echo "  cch --list             # List all prompts"
    echo "  cch --list-projects    # List all projects"
    echo ""
    echo "Performance:"
    echo "  ⚡ Search: ~20ms (instant)"
    echo "  💾 Cache: Auto-managed"
    echo "  🚀 55-98x faster than v1"
    echo ""
    echo "Documentation:"
    echo "  README.md                    # Quick start guide"
    echo "  docs/OPTIMIZATION_REPORT.md  # Performance details"
    echo "  docs/CACHE_GUIDE.md          # Cache management"
    echo ""
else
    echo "⚠️  Warning: 'cch' command not found in PATH"
    echo ""
    echo "Add to your PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Or use pipx:"
    echo "  brew install pipx"
    echo "  pipx install -e ."
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
