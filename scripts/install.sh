#!/bin/bash
# Claude Code History - Shell Integration Installer
# 
# Usage:
#   ./install.sh              # Interactive installation
#   ./install.sh --zsh        # Zsh only
#   ./install.sh --bash       # Bash only
#   ./install.sh --uninstall  # Remove integration
#   ./install.sh --force      # Overwrite existing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZSH_SCRIPT="$SCRIPT_DIR/claude-code-history.zsh"
BASH_SCRIPT="$SCRIPT_DIR/claude-code-history.bash"
INSTALL_DIR="${HOME}/.claude-code-history"
ZSHRC="${HOME}/.zshrc"
BASHRC="${HOME}/.bashrc"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}!${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Create install directory
mkdir -p "$INSTALL_DIR"

# Copy scripts
cp "$ZSH_SCRIPT" "$INSTALL_DIR/"
cp "$BASH_SCRIPT" "$INSTALL_DIR/"

log_info "Scripts copied to $INSTALL_DIR/"

# Detect shell
detect_shell() {
    if [[ -n "$ZSH_VERSION" ]]; then
        echo "zsh"
    elif [[ -n "$BASH_VERSION" ]]; then
        echo "bash"
    else
        echo "unknown"
    fi
}

# Add to zshrc
add_to_zshrc() {
    local source_line="source \"${INSTALL_DIR}/claude-code-history.zsh\""
    
    if [[ -f "$ZSHRC" ]] && grep -q "claude-code-history.zsh" "$ZSHRC"; then
        log_warn "Zsh integration already exists in $ZSHRC"
        return 1
    fi
    
    echo "" >> "$ZSHRC"
    echo "# Claude Code History" >> "$ZSHRC"
    echo "$source_line" >> "$ZSHRC"
    
    log_info "Added Zsh integration to $ZSHRC"
    return 0
}

# Add to bashrc
add_to_bashrc() {
    local source_line="source \"${INSTALL_DIR}/claude-code-history.bash\""
    
    if [[ -f "$BASHRC" ]] && grep -q "claude-code-history.bash" "$BASHRC"; then
        log_warn "Bash integration already exists in $BASHRC"
        return 1
    fi
    
    echo "" >> "$BASHRC"
    echo "# Claude Code History" >> "$BASHRC"
    echo "$source_line" >> "$BASHRC"
    
    log_info "Added Bash integration to $BASHRC"
    return 0
}

# Remove from zshrc
remove_from_zshrc() {
    if [[ ! -f "$ZSHRC" ]]; then
        return
    fi
    
    local tmp=$(mktemp)
    
    # Remove Claude Code History section
    awk '/^# Claude Code History/,/^$/ { if (/^$/) { print; next } next } { print }' "$ZSHRC" > "$tmp"
    mv "$tmp" "$ZSHRC"
    
    log_info "Removed Zsh integration from $ZSHRC"
}

# Remove from bashrc
remove_from_bashrc() {
    if [[ ! -f "$BASHRC" ]]; then
        return
    fi
    
    local tmp=$(mktemp)
    
    # Remove Claude Code History section
    awk '/^# Claude Code History/,/^$/ { if (/^$/) { print; next } next } { print }' "$BASHRC" > "$tmp"
    mv "$tmp" "$BASHRC"
    
    log_info "Removed Bash integration from $BASHRC"
}

# Uninstall
uninstall() {
    log_info "Uninstalling Claude Code History integration..."
    
    remove_from_zshrc 2>/dev/null || true
    remove_from_bashrc 2>/dev/null || true
    
    log_info "Uninstall complete. To fully remove, delete $INSTALL_DIR"
}

# Main
main() {
    local install_zsh=false
    local install_bash=false
    local do_uninstall=false
    local force=false
    
    # Parse args
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --zsh)
                install_zsh=true
                shift
                ;;
            --bash)
                install_bash=true
                shift
                ;;
            --uninstall)
                do_uninstall=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Uninstall
    if [[ "$do_uninstall" == "true" ]]; then
        uninstall
        exit 0
    fi
    
    # Detect shell if no specific shell requested
    if [[ "$install_zsh" == "false" && "$install_bash" == "false" ]]; then
        local shell=$(detect_shell)
        case "$shell" in
            zsh)
                install_zsh=true
                ;;
            bash)
                install_bash=true
                ;;
            *)
                # Default to both
                install_zsh=true
                install_bash=true
                ;;
        esac
    fi
    
    # Install
    local installed=false
    
    if [[ "$install_zsh" == "true" ]]; then
        if add_to_zshrc || [[ "$force" == "true" ]]; then
            installed=true
        fi
    fi
    
    if [[ "$install_bash" == "true" ]]; then
        if add_to_bashrc || [[ "$force" == "true" ]]; then
            installed=true
        fi
    fi
    
    if [[ "$installed" == "true" ]]; then
        echo ""
        log_info "Installation complete!"
        echo ""
        echo "Next steps:"
        echo "  1. Restart your terminal: exec zsh"
        echo "  2. Or source the integration: source $ZSH_SCRIPT"
        echo ""
        echo "Commands:"
        echo "  cch              # Search prompts"
        echo "  cch --preview    # Search with preview"
        echo "  cch --interactive # Interactive mode"
        echo ""
        echo "Key bindings (after restart):"
        echo "  Ctrl+R  Search and insert"
        echo ""
    fi
}

main "$@"
