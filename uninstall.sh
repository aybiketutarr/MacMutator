#!/bin/bash

set -e

INSTALL_DIR="/usr/local/lib/macmutator"
LOCAL_BIN="/usr/local/bin/macmutator"
SYSTEM_BIN="/usr/bin/macmutator"

BLUE='\033[94m'
WHITE='\033[97m'
RED='\033[91m'
GREEN='\033[92m'
GRAY='\033[90m'
RESET='\033[0m'

print_status() {
    echo -e "${WHITE}[ ${BLUE}$1${WHITE} ]${RESET} $2"
}

print_error() {
    echo -e "${WHITE}[ ${RED}!${WHITE} ]${RESET} $1"
}

print_success() {
    echo -e "${WHITE}[ ${BLUE}+${WHITE} ]${RESET} $1"
}

echo
echo -e "${BLUE}MacMutator Uninstaller${RESET}"
echo -e "${GRAY}────────────────────────────────────────────${RESET}"
echo

if [ "$EUID" -ne 0 ]; then
    print_error "Root privileges are required."
    echo
    echo "Run: sudo ./uninstall.sh"
    echo
    exit 1
fi

# Remove local command
if [ -e "$LOCAL_BIN" ]; then
    print_status "*" "Removing local command..."
    rm -f "$LOCAL_BIN"
    print_success "Local command removed."
fi

# Remove system command
if [ -e "$SYSTEM_BIN" ]; then
    print_status "*" "Removing system command..."
    rm -f "$SYSTEM_BIN"
    print_success "System command removed."
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    print_status "*" "Removing MacMutator files..."
    rm -rf "$INSTALL_DIR"
    print_success "MacMutator files removed."
fi

echo
echo -e "${GRAY}────────────────────────────────────────────${RESET}"
echo -e "${GREEN}MacMutator has been uninstalled.${RESET}"
echo -e "${GRAY}────────────────────────────────────────────${RESET}"
echo
