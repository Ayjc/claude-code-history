# Claude Code History - Bash Integration
# 
# Add to ~/.bashrc or save as ~/.claude-code-history/claude-code-history.bash
# and source it in ~/.bashrc: source ~/.claude-code-history/claude-code-history.bash
#
# Requires: pip install claude-code-history

# Check if cch command exists
if ! command -v cch &> /dev/null; then
    return
fi

# Configuration
export CCH_FZF_HEIGHT="${CCH_FZF_HEIGHT:-50%}"
export CCH_MAX_RESULTS="${CCH_MAX_RESULTS:-50}"

# Aliases
alias cch='cch'
alias cchp='cch --list-projects'
alias cchf='cch --preview'
alias cchi='cch --interactive'

# Main search function
cch-search() {
    local selected
    selected=$(cch --preview --preview-position right 2>/dev/null)
    if [[ -n "$selected" ]]; then
        # Copy to clipboard (macOS)
        if command -v pbcopy &> /dev/null; then
            printf '%s' "$selected" | pbcopy
            echo "Copied to clipboard!"
        fi
        # Linux clipboard
        if command -v xclip &> /dev/null; then
            printf '%s' "$selected" | xclip -selection clipboard
            echo "Copied to clipboard!"
        fi
        # Print for terminal use
        printf '%s\n' "$selected"
    fi
}

# Insert selected prompt into current readline buffer
cch-insert() {
    local selected
    selected=$(cch --preview --preview-position right 2>/dev/null)
    if [[ -n "$selected" ]]; then
        READLINE_LINE="$selected"
        READLINE_POINT=${#selected}
    fi
}

# Bind to Ctrl+R if fzf is available
if command -v fzf &> /dev/null; then
    # Add to readline
    bind -x '"\C-r": cch-search'
fi

# Complete for cch command
_cch_completion() {
    local cur prev words cword
    _init_completion || return
    
    local opts="--help --version --init --show-config --list-projects --json --list --interactive --preview --no-preview --list-detailed"
    local long_opts="--project --exclude-project --limit --config --preview-position"
    
    if [[ "$cur" == --* ]]; then
        COMPREPLY=($(compgen -W "$opts $long_opts" -- "$cur"))
    elif [[ "$cur" == -* ]]; then
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
    else
        COMPREPLY=($(compgen -W "$opts" -- "$cur"))
    fi
}

complete -F _cch_completion cch

# Print installation info
claude-code-history-info() {
    cat << EOF
Claude Code History - Bash Integration
======================================

Available commands:
  cch <query>              Search prompts
  cch --preview            Search with preview
  cch --interactive        Interactive mode
  cch --list-projects      List projects

Functions:
  cch-search()             Search and copy to clipboard
  cch-insert()             Search and insert at cursor

Key bindings:
  Ctrl+R                   Search (if fzf available)

For more info: cch --help
EOF
}

# Auto-load message
if [[ "$BASH_INTERACTIVE" == "true" ]] || [[ $- == *i* ]]; then
    echo "✅ Claude Code History loaded. Type 'claude-code-history-info' for help."
fi
