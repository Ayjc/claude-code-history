# Claude Code History

🔍 **Search and autocomplete Claude Code prompts with fuzzy search**

<p align="center">
  <img src="https://img.shields.io/pypi/v/claude-code-history?style=flat-square" alt="PyPI">
  <img src="https://img.shields.io/python versions/claude-code-history?style=flat-square" alt="Python">
  <img src="https://img.shields.io/license/claude-code-history?style=flat-square" alt="MIT">
</p>

---

## ✨ Features

- 🔍 **Fuzzy Search** - Use fzf to quickly find prompts
- ✨ **Auto-completion** - Get suggestions as you type
- 📅 **Project Filtering** - Filter by project directory
- 🎨 **Clean UI** - Beautiful terminal interface
- 🚀 **Fast** - Written in Python with prompt_toolkit

---

## 🚀 Quick Start

### Install

```bash
# Using pip
pip install claude-code-history

# Or from source
git clone https://github.com/yourname/claude-code-history.git
cd claude-code-history
pip install -e .
```

### Install fzf (required)

```bash
# macOS
brew install fzf

# Ubuntu/Debian
sudo apt install fzf

# Arch
sudo pacman -S fzf
```

### Usage

```bash
# Open fzf search interface
cch

# Search for a specific prompt
cch fix

# Interactive auto-completion search
cch --interactive
cch -i

# List all prompts (no fzf)
cch --list

# Output as JSON
cch --json

# Limit results
cch --limit 50
```

---

## 📖 Features in Detail

### Fuzzy Search

Launch an interactive fzf interface to search through your Claude Code history:

```bash
cch
```

Use arrow keys to navigate, Enter to select, Ctrl+C to cancel.

### Search with Query

Search for prompts containing specific text:

```bash
cch fix        # Find prompts about fixing bugs
cch migration  # Find prompts about database migrations
cch test       # Find prompts about testing
```

### Interactive Auto-Completion

Launch an interactive search with auto-completion:

```bash
cch --interactive
cch -i
```

As you type, you'll get real-time suggestions from your history. Use arrow keys to navigate, Enter to select.

### Project Filtering

Filter prompts by project:

```bash
# Coming soon
cch --project my-app
```

### JSON Output

Get machine-readable output:

```bash
cch --json | jq '.[] | select(.project_path | contains("my-app"))'
```

---

## 🔧 Configuration

### Config File

Create `~/.config/cch/config.toml`:

```toml
[general]
max_results = 50
fzf_height = "50%"

[display]
show_timestamp = true
show_project = true
truncate_length = 80
```

### Environment Variables

```bash
export CCH_FZF_HEIGHT="60%"    # Override fzf height
export CCH_MAX_RESULTS=100     # Override max results
```

---

## 📂 Data Location

Claude Code stores history in:

```
~/.claude/projects/<project-name>/sessions/*.json
```

This tool reads all session files and provides a unified search interface.

---

## 🛠️ Development

### Setup

```bash
git clone https://github.com/yourname/claude-code-history.git
cd claude-code-history

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Project Structure

```
claude-code-history/
├── src/
│   ├── __init__.py         # Package entry
│   ├── cli.py              # CLI interface
│   ├── history.py          # History reading
│   ├── fzf_interface.py    # fzf wrapper
│   └── completer.py        # Auto-completion
├── tests/
│   ├── test_history.py
│   └── test_completer.py
├── pyproject.toml
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [fzf](https://github.com/junegunn/fzf) - The fuzzy finder
- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) - Python CLI library
- [Oh My Zsh](https://github.com/ohmyzsh/ohmyzsh) - Inspiration for the plugin system

---

<p align="center">
  Made with ❤️ by AlexY
</p>

---

## 🔧 Configuration

### Initialize Config

```bash
cch --init
```

This creates `~/.config/cch/config.toml` with default settings.

### Config File

```toml
[general]
max_results = 50           # Max prompts to display
fzf_height = "50%"         # fzf window height

[display]
show_timestamp = true      # Show date in list
show_project = true        # Show project name
truncate_length = 80       # Truncate long prompts

[fzf]
fzf_layout = "reverse"     # fzf layout
fzf_border = true          # Show border

[interactive]
interactive_truncate = 100 # Truncate in interactive mode
```

### Config Locations

Config is searched in this order:
1. `$XDG_CONFIG_HOME/cch/config.toml`
2. `~/.config/cch/config.toml`
3. `~/.cch/config.toml`


---

## 📁 Project Filtering

### Filter by Project

```bash
# Filter by single project
cch --project my-app fix

# Filter by multiple projects
cch -p my-app -p another-app fix
```

### Exclude Projects

```bash
# Exclude test project
cch --exclude-project test fix

# Exclude multiple projects
cch -e test -e staging fix
```

### List Projects

```bash
cch --list-projects
```

This shows all projects with conversation history.

### Combine Filters

```bash
# Search in specific projects, excluding others
cch -p prod-app -e legacy fix

# Search with no query, just filter projects
cch -p my-app
```


---

## 👁️ Preview Feature

### Enable Preview Window

```bash
# Enable preview window (shows project, date, ID)
cch --preview

# Preview on the right (default)
cch --preview --preview-position right

# Preview on the left
cch --preview --preview-position left

# Preview on top
cch --preview --preview-position top

# Preview on bottom
cch --preview --preview-position bottom
```

### Preview Controls

| Key | Action |
|-----|--------|
| `Ctrl+P` | Toggle preview window |
| `↑` / `↓` | Navigate results |
| `Enter` | Select result |
| `Ctrl+C` / `Esc` | Cancel |

### Detailed List View

```bash
# View all prompts with full details (no fzf)
cch --list-detailed

# Limit results
cch --list-detailed --limit 10
```


---

## 🐚 Shell Integration

### Install Shell Integration

```bash
# Navigate to the project
cd claude-code-history

# Run install script
./scripts/install.sh

# Restart your terminal
exec zsh
```

### Manual Installation

**Zsh:**
```bash
# Add to ~/.zshrc
source ~/.claude-code-history/claude-code-history.zsh
```

**Bash:**
```bash
# Add to ~/.bashrc
source ~/.claude-code-history/claude-code-history.bash
```

### Commands After Installation

| Command | Description |
|---------|-------------|
| `cch` | Search prompts |
| `cch -p my-app` | Filter by project |
| `cch --preview` | Search with preview |
| `cch --interactive` | Interactive mode |
| `cchp` | List all projects |

### Functions

**Zsh:**
```zsh
cch-search()      # Search and copy to clipboard
cch-insert()      # Search and insert at cursor
cch-run()         # Search and execute
```

**Bash:**
```bash
cch-search()      # Search and copy to clipboard
```

### Key Bindings

Add to your `~/.zshrc`:

```zsh
# Ctrl+R: Search and insert at cursor
bindkey '^r' cch-search

# Ctrl+P: Insert without leaving current buffer
bindkey '^p' cch-insert
```

### Uninstall

```bash
./scripts/install.sh --uninstall
```

