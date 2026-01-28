# Claude Code History - Zsh Integration
# 
# Add to ~/.zshrc or save as ~/.claude-code-history/claude-code-history.zsh
# and source it in ~/.zshrc: source ~/.claude-code-history/claude-code-history.zsh
#
# Requires: pip install claude-code-history

# Check if cch command exists
if (( ! ${+commands[cch]} )); then
    return
fi

# Configuration variables
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
        if (( $+commands[pbcopy] )); then
            printf '%s' "$selected" | pbcopy
            echo "Copied to clipboard!"
        fi
        # Also print for terminal use
        printf '%s\n' "$selected"
    fi
}

# Insert selected prompt into current buffer
cch-insert() {
    local selected
    selected=$(cch --preview --preview-position right 2>/dev/null)
    if [[ -n "$selected" ]]; then
        BUFFER="$selected"
        CURSOR=$#BUFFER
        zle reset-prompt
    fi
}

# Search and execute (run as command)
cch-run() {
    local selected
    selected=$(cch --preview --preview-position right 2>/dev/null)
    if [[ -n "$selected" ]]; then
        print -z "$selected"
    fi
}

# Interactive mode with auto-completion
cch-interactive() {
    cch --interactive
}

# List all projects
cch-projects() {
    cch --list-projects
}

# Key bindings - add to your .zshrc or use the bindkey commands below
# bindkey '^r' cch-search        # Ctrl+R: Search and copy
# bindkey '^p' cch-insert        # Ctrl+P: Search and insert
# bindkey '^x^r' cch-interactive # Ctrl+X Ctrl+R: Interactive mode

# Completion function for cch
_cch_completion() {
    local -a opts
    opts=(
        '(--help --version --init --show-config --list-projects --json --list --interactive --preview --no-preview --list-detailed)'{--help,--version,--init,--show-config,--list-projects,--json,--list,--interactive,--preview,--no-preview,--list-detailed}
        '(--project --exclude-project --limit --config --preview-position)'{--project=,--exclude-project=,--limit=,--config=,--preview-position=}
        ':query::_default'
    )
    _describe -t command 'cch' opts
}

compdef _cch_completion cch

# FZF completion (if fzf is available)
if (( $+commands[fzf] )); then
    # Ctrl+R: Search history with fzf
    fzf-cch-history() {
        local selected
        selected=$(cch --preview --preview-position right 2>/dev/null)
        if [[ -n "$selected" ]]; then
            print -z "$selected"
        fi
    }
    
    # Bind Ctrl+R to search
    bindkey '^r' fzf-cch-history
fi

# Print installation info
claude-code-history-info() {
    cat << EOF
Claude Code History - Zsh Integration
=====================================

Available commands:
  cch <query>              Search prompts
  cch --preview            Search with preview
  cch --interactive        Interactive mode
  cch --list-projects      List projects
  cch -p <project>         Filter by project

Functions:
  cch-search()             Search and copy to clipboard
  cch-insert()             Search and insert at cursor
  cch-run()                Search and run as command
  cch-interactive()        Interactive mode

Key bindings (add to ~/.zshrc):
  bindkey '^r' cch-search     # Ctrl+R: Search
  bindkey '^p' cch-insert     # Ctrl+P: Insert

For more info: cch --help
EOF
}

# Auto-load when sourced
print "✅ Claude Code History loaded. Type 'claude-code-history-info' for help."
