#!/bin/bash

set -e

INSTALL_DIR="/usr/local/lib/macmutator"
LOCAL_BIN="/usr/local/bin/macmutator"
SYSTEM_BIN="/usr/bin/macmutator"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_FILE="$SCRIPT_DIR/src/macmutator.py"

BLUE='\033[94m'
CYAN='\033[96m'
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
echo -e "${BLUE}MacMutator Installer${RESET}"
echo -e "${GRAY}────────────────────────────────────────────${RESET}"
echo

# ------------------------------------------------------------
# Root check
# ------------------------------------------------------------

if [ "$EUID" -ne 0 ]; then
    print_error "Root privileges are required."
    echo
    echo -e "Run: ${CYAN}sudo ./install.sh${RESET}"
    echo
    exit 1
fi

# ------------------------------------------------------------
# Source check
# ------------------------------------------------------------

if [ ! -f "$SOURCE_FILE" ]; then
    print_error "MacMutator source file was not found."
    echo
    echo "Expected:"
    echo "  $SOURCE_FILE"
    echo
    exit 1
fi

# ------------------------------------------------------------
# Python check
# ------------------------------------------------------------

print_status "*" "Checking Python 3..."

if ! command -v python3 >/dev/null 2>&1; then
    print_error "Python 3 is not installed."
    exit 1
fi

PYTHON_PATH="$(command -v python3)"

print_success "Python 3 found: $PYTHON_PATH"

# ------------------------------------------------------------
# ip command check
# ------------------------------------------------------------

print_status "*" "Checking ip command..."

if ! command -v ip >/dev/null 2>&1; then
    print_error "The 'ip' command was not found."
    echo
    echo "Please install the iproute2 package."
    echo
    exit 1
fi

print_success "ip command found."

# ------------------------------------------------------------
# Prepare installation directory
# ------------------------------------------------------------

print_status "*" "Preparing installation directory..."

mkdir -p "$INSTALL_DIR"

# ------------------------------------------------------------
# Install source
# ------------------------------------------------------------

print_status "*" "Installing MacMutator source..."

cp "$SOURCE_FILE" "$INSTALL_DIR/macmutator.py"

chmod 755 "$INSTALL_DIR/macmutator.py"

print_success "Source installed."

# ------------------------------------------------------------
# Create launcher
# ------------------------------------------------------------

print_status "*" "Creating system launcher..."

cat > "$LOCAL_BIN" <<EOF
#!/bin/sh

exec "$PYTHON_PATH" "$INSTALL_DIR/macmutator.py" "\$@"
EOF

chmod 755 "$LOCAL_BIN"

print_success "Launcher created at $LOCAL_BIN"

# ------------------------------------------------------------
# Create /usr/bin compatibility launcher
# ------------------------------------------------------------

print_status "*" "Creating sudo-compatible command..."

cat > "$SYSTEM_BIN" <<EOF
#!/bin/sh

exec "$PYTHON_PATH" "$INSTALL_DIR/macmutator.py" "\$@"
EOF

chmod 755 "$SYSTEM_BIN"

print_success "Sudo-compatible command created."

# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------

print_status "*" "Verifying installation..."

if [ ! -x "$LOCAL_BIN" ]; then
    print_error "Local launcher verification failed."
    exit 1
fi

if [ ! -x "$SYSTEM_BIN" ]; then
    print_error "System launcher verification failed."
    exit 1
fi

if [ ! -x "$INSTALL_DIR/macmutator.py" ]; then
    print_error "Source verification failed."
    exit 1
fi

# ------------------------------------------------------------
# Complete
# ------------------------------------------------------------

echo
echo -e "${GRAY}────────────────────────────────────────────${RESET}"
echo -e "${GREEN}MacMutator has been installed successfully.${RESET}"
echo -e "${GRAY}────────────────────────────────────────────${RESET}"
echo

echo -e "${WHITE}Installation directory:${RESET}"
echo -e "  ${CYAN}$INSTALL_DIR${RESET}"

echo
echo -e "${WHITE}User command:${RESET}"
echo -e "  ${CYAN}$LOCAL_BIN${RESET}"

echo
echo -e "${WHITE}System command:${RESET}"
echo -e "  ${CYAN}$SYSTEM_BIN${RESET}"

echo
echo -e "${WHITE}You can now run MacMutator from any directory:${RESET}"
echo
echo -e "  ${CYAN}macmutator --help${RESET}"
echo -e "  ${CYAN}macmutator --show eth0${RESET}"
echo -e "  ${CYAN}sudo macmutator --random eth0${RESET}"
echo -e "  ${CYAN}sudo macmutator --restore eth0${RESET}"
echo

echo -e "${GREEN}Installation complete.${RESET}"
echo
