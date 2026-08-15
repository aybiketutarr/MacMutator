#!/usr/bin/env python3

import argparse
import os
import random
import re
import shutil
import subprocess
import sys
import time


VERSION = "1.3.0"

STATE_DIR = "/var/lib/macmutator"


# ─────────────────────────────────────────────────────────────
# ANSI COLORS
# ─────────────────────────────────────────────────────────────

BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
BOLD = "\033[1m"


# ─────────────────────────────────────────────────────────────
# TERMINAL HELPERS
# ─────────────────────────────────────────────────────────────

def terminal_supports_color():
    return sys.stdout.isatty()


def color(text, colour):
    if terminal_supports_color():
        return f"{colour}{text}{RESET}"

    return text


def status(symbol, message, symbol_color=BLUE):
    print(
        f"{color('[', WHITE)}"
        f" {color(symbol, symbol_color)} "
        f"{color(']', WHITE)} "
        f"{color(message, WHITE)}"
    )


def print_banner():
    banner = r"""
███╗   ███╗ █████╗  ██████╗███╗   ███╗██╗   ██╗████████╗ ██████╗ ██████╗
████╗ ████║██╔══██╗██╔════╝████╗ ████║██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗
██╔████╔██║███████║██║     ██╔████╔██║██║   ██║   ██║   ██║   ██║██████╔╝
██║╚██╔╝██║██╔══██║██║     ██║╚██╔╝██║██║   ██║   ██║   ██║   ██║██╔══██╗
██║ ╚═╝ ██║██║  ██║╚██████╗██║ ╚═╝ ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██║
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝     ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝
"""

    print(color(banner, BLUE))

    print(
        color(
            "─" * 78,
            GRAY
        )
    )

    print(
    f"{color('MAC Address Manipulation Tool', WHITE)}"
    f"{' ' * 15}"
    f"{color('Developed by Aybike Tutar', CYAN)}"
)

    print(
    f"{' ' * 42}"
    f"{color('  github.com/aybiketutarr', BLUE)}"
)

    print(
        color(
            "─" * 78,
            GRAY
        )
    )

    print()


def print_usage():
    print(color("Usage:", WHITE))

    print(
        f"  {color('sudo macmutator --random eth0', CYAN)}"
    )

    print(
        f"  {color('macmutator --show eth0', CYAN)}"
    )

    print(
        f"  {color('sudo macmutator --restore eth0', CYAN)}"
    )

    print()


# ─────────────────────────────────────────────────────────────
# SYSTEM HELPERS
# ─────────────────────────────────────────────────────────────

def command_exists(command):
    return shutil.which(command) is not None


def require_ip_command():
    if not command_exists("ip"):
        status(
            "!",
            "The 'ip' command was not found.",
            RED
        )

        print(
            color(
                "[!] Please install the iproute2 package.",
                RED
            )
        )

        sys.exit(1)


def require_root():
    if os.geteuid() != 0:
        status(
            "!",
            "Root privileges are required for this operation.",
            RED
        )

        print()

        status(
            "*",
            "Example: sudo macmutator --random eth0",
            BLUE
        )

        sys.exit(1)


def run_command(command):
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

    except FileNotFoundError:
        raise RuntimeError(
            f"Required command not found: {command[0]}"
        )

    except subprocess.CalledProcessError as error:

        stderr = error.stderr.strip()

        if stderr:
            raise RuntimeError(stderr)

        raise RuntimeError(
            f"Command failed: {' '.join(command)}"
        )


# ─────────────────────────────────────────────────────────────
# NETWORK FUNCTIONS
# ─────────────────────────────────────────────────────────────

def interface_exists(interface):
    result = subprocess.run(
        [
            "ip",
            "link",
            "show",
            interface
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def get_current_mac(interface):
    result = run_command(
        [
            "ip",
            "link",
            "show",
            interface
        ]
    )

    match = re.search(
        r"link/\S+\s+([0-9a-fA-F:]{17})",
        result.stdout
    )

    if not match:
        raise RuntimeError(
            f"Could not determine the MAC address of {interface}."
        )

    return match.group(1).lower()


def generate_random_mac():
    mac = [
        random.randint(0x00, 0xFF)
        for _ in range(6)
    ]

    # Locally administered address.
    # Clear multicast bit.
    mac[0] = (mac[0] & 0xFC) | 0x02

    return ":".join(
        f"{byte:02x}"
        for byte in mac
    )


def validate_mac(mac):
    pattern = (
        r"^[0-9a-fA-F]{2}"
        r"(:[0-9a-fA-F]{2}){5}$"
    )

    return bool(
        re.fullmatch(pattern, mac)
    )


# ─────────────────────────────────────────────────────────────
# STATE MANAGEMENT
# ─────────────────────────────────────────────────────────────

def state_file(interface):
    safe_interface = re.sub(
        r"[^a-zA-Z0-9_.-]",
        "_",
        interface
    )

    return os.path.join(
        STATE_DIR,
        safe_interface
    )


def ensure_state_directory():
    os.makedirs(
        STATE_DIR,
        mode=0o700,
        exist_ok=True
    )

    try:
        os.chmod(
            STATE_DIR,
            0o700
        )
    except OSError:
        pass


def save_original_mac(interface, mac):
    ensure_state_directory()

    path = state_file(interface)

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(mac + "\n")

    os.chmod(
        path,
        0o600
    )


def load_original_mac(interface):
    path = state_file(interface)

    if not os.path.isfile(path):
        return None

    try:
        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            mac = file.read().strip()

    except OSError as error:
        raise RuntimeError(
            f"Could not read saved MAC address: {error}"
        )

    if not validate_mac(mac):
        raise RuntimeError(
            "The saved MAC address is invalid."
        )

    return mac.lower()


def remove_original_mac(interface):
    path = state_file(interface)

    try:
        if os.path.exists(path):
            os.remove(path)

    except OSError as error:
        raise RuntimeError(
            f"Could not remove saved MAC address: {error}"
        )


# ─────────────────────────────────────────────────────────────
# PROGRESS BAR
# ─────────────────────────────────────────────────────────────

def progress_bar(label, action, width=42):
    print(
        f"    {color('▸', BLUE)} "
        f"{color(label, WHITE)}"
    )

    try:
        action()

    except Exception:
        print(
            f"    {color('✗', RED)} "
            f"{color('FAILED', RED)}"
        )

        raise

    for current in range(width + 1):

        percentage = int(
            (current / width) * 100
        )

        filled = "█" * current
        empty = "░" * (width - current)

        line = (
            f"\r    "
            f"{color(filled, BLUE)}"
            f"{color(empty, GRAY)}"
            f" {color(f'{percentage:3d}%', WHITE)}"
        )

        print(
            line,
            end="",
            flush=True
        )

        time.sleep(0.008)

    print(
        f"  {color('OK', GREEN)}"
    )


# ─────────────────────────────────────────────────────────────
# MAC INFORMATION PANEL
# ─────────────────────────────────────────────────────────────

def print_mac_panel(
    interface,
    old_mac,
    new_mac,
    title="MAC MUTATED"
):
    print()

    border = color(
        "┌────────────────────────────────────────┐",
        BLUE
    )

    separator = color(
        "├────────────────────────────────────────┤",
        BLUE
    )

    bottom = color(
        "└────────────────────────────────────────┘",
        BLUE
    )

    print(f"    {border}")

    print(
        f"    {color('│', BLUE)}"
        f"{color(title.center(40), WHITE)}"
        f"{color('│', BLUE)}"
    )

    print(f"    {separator}")

    print(
        f"    {color('│', BLUE)} "
        f"{color('Interface :', WHITE)} "
        f"{color(interface, CYAN)}"
        f"{' ' * max(0, 27 - len(interface))}"
        f"{color('│', BLUE)}"
    )

    print(
        f"    {color('│', BLUE)} "
        f"{color('Old MAC   :', WHITE)} "
        f"{color(old_mac, GRAY)}"
        f"  "
        f"{color('│', BLUE)}"
    )

    print(
        f"    {color('│', BLUE)} "
        f"{color('New MAC   :', WHITE)} "
        f"{color(new_mac, CYAN)}"
        f"  "
        f"{color('│', BLUE)}"
    )

    print(f"    {bottom}")
    print()


# ─────────────────────────────────────────────────────────────
# RANDOM MAC OPERATION
# ─────────────────────────────────────────────────────────────

def change_mac(interface, new_mac):

    require_root()
    require_ip_command()

    old_mac = None

    try:

        # -----------------------------------------------------
        # STEP 1 — Check interface
        # -----------------------------------------------------

        def check_interface():

            if not interface_exists(interface):
                raise RuntimeError(
                    f"Network interface not found: {interface}"
                )

        progress_bar(
            "Checking network interface...",
            check_interface
        )

        # -----------------------------------------------------
        # STEP 2 — Read current MAC
        # -----------------------------------------------------

        def read_mac():

            nonlocal old_mac

            old_mac = get_current_mac(
                interface
            )

        progress_bar(
            "Reading current MAC address...",
            read_mac
        )

        # -----------------------------------------------------
        # STEP 3 — Save original MAC
        # -----------------------------------------------------

        saved_mac = load_original_mac(
            interface
        )

        if saved_mac is None:

            def save_mac():

                save_original_mac(
                    interface,
                    old_mac
                )

            progress_bar(
                "Saving original MAC address...",
                save_mac
            )

        else:

            status(
                "*",
                "Original MAC already saved. Keeping existing record.",
                BLUE
            )

        # -----------------------------------------------------
        # STEP 4 — Display information
        # -----------------------------------------------------

        print()

        status(
            "*",
            f"Interface : {interface}",
            BLUE
        )

        status(
            "*",
            f"Old MAC   : {old_mac}",
            BLUE
        )

        status(
            "*",
            f"New MAC   : {new_mac}",
            BLUE
        )

        print()

        # -----------------------------------------------------
        # STEP 5 — Interface DOWN
        # -----------------------------------------------------

        def interface_down():

            run_command(
                [
                    "ip",
                    "link",
                    "set",
                    "dev",
                    interface,
                    "down"
                ]
            )

        progress_bar(
            "Bringing interface down...",
            interface_down
        )

        # -----------------------------------------------------
        # STEP 6 — Assign MAC
        # -----------------------------------------------------

        def assign_mac():

            run_command(
                [
                    "ip",
                    "link",
                    "set",
                    "dev",
                    interface,
                    "address",
                    new_mac
                ]
            )

        progress_bar(
            "Assigning new MAC address...",
            assign_mac
        )

        # -----------------------------------------------------
        # STEP 7 — Interface UP
        # -----------------------------------------------------

        def interface_up():

            run_command(
                [
                    "ip",
                    "link",
                    "set",
                    "dev",
                    interface,
                    "up"
                ]
            )

        progress_bar(
            "Bringing interface up...",
            interface_up
        )

        # -----------------------------------------------------
        # STEP 8 — Verify
        # -----------------------------------------------------

        current_mac = None

        def verify_mac():

            nonlocal current_mac

            current_mac = get_current_mac(
                interface
            )

            if current_mac.lower() != new_mac.lower():

                raise RuntimeError(
                    "MAC address verification failed."
                )

        progress_bar(
            "Verifying new MAC address...",
            verify_mac
        )

        print()

        status(
            "+",
            "MAC address changed successfully.",
            BLUE
        )

        print_mac_panel(
            interface,
            old_mac,
            current_mac,
            "MAC MUTATED"
        )

    except Exception as error:

        print()

        status(
            "!",
            str(error),
            RED
        )

        sys.exit(1)


# ─────────────────────────────────────────────────────────────
# SHOW MAC
# ─────────────────────────────────────────────────────────────

def show_mac(interface):

    require_ip_command()

    try:

        def check_interface():

            if not interface_exists(interface):

                raise RuntimeError(
                    f"Network interface not found: {interface}"
                )

        progress_bar(
            "Checking network interface...",
            check_interface
        )

        mac = None

        def read_mac():

            nonlocal mac

            mac = get_current_mac(
                interface
            )

        progress_bar(
            "Reading MAC address...",
            read_mac
        )

        print()

        status(
            "+",
            f"Interface : {interface}",
            BLUE
        )

        status(
            "+",
            f"MAC       : {mac}",
            BLUE
        )

        print()

    except Exception as error:

        print()

        status(
            "!",
            str(error),
            RED
        )

        sys.exit(1)


# ─────────────────────────────────────────────────────────────
# RESTORE MAC
# ─────────────────────────────────────────────────────────────

def restore_mac(interface):

    require_root()
    require_ip_command()

    original_mac = None
    current_mac = None

    try:

        # -----------------------------------------------------
        # STEP 1 — Check interface
        # -----------------------------------------------------

        def check_interface():

            if not interface_exists(interface):

                raise RuntimeError(
                    f"Network interface not found: {interface}"
                )

        progress_bar(
            "Checking network interface...",
            check_interface
        )

        # -----------------------------------------------------
        # STEP 2 — Load original MAC
        # -----------------------------------------------------

        def load_mac():

            nonlocal original_mac

            original_mac = load_original_mac(
                interface
            )

            if original_mac is None:

                raise RuntimeError(
                    f"No original MAC address is saved for {interface}."
                )

        progress_bar(
            "Loading original MAC address...",
            load_mac
        )

        # -----------------------------------------------------
        # STEP 3 — Read current MAC
        # -----------------------------------------------------

        def read_current():

            nonlocal current_mac

            current_mac = get_current_mac(
                interface
            )

        progress_bar(
            "Reading current MAC address...",
            read_current
        )

        print()

        status(
            "*",
            f"Interface : {interface}",
            BLUE
        )

        status(
            "*",
            f"Current   : {current_mac}",
            BLUE
        )

        status(
            "*",
            f"Original  : {original_mac}",
            BLUE
        )

        print()

        # -----------------------------------------------------
        # STEP 4 — Interface DOWN
        # -----------------------------------------------------

        def interface_down():

            run_command(
                [
                    "ip",
                    "link",
                    "set",
                    "dev",
                    interface,
                    "down"
                ]
            )

        progress_bar(
            "Bringing interface down...",
            interface_down
        )

        # -----------------------------------------------------
        # STEP 5 — Restore original MAC
        # -----------------------------------------------------

        def restore_address():

            run_command(
                [
                    "ip",
                    "link",
                    "set",
                    "dev",
                    interface,
                    "address",
                    original_mac
                ]
            )

        progress_bar(
            "Restoring original MAC address...",
            restore_address
        )

        # -----------------------------------------------------
        # STEP 6 — Interface UP
        # -----------------------------------------------------

        def interface_up():

            run_command(
                [
                    "ip",
                    "link",
                    "set",
                    "dev",
                    interface,
                    "up"
                ]
            )

        progress_bar(
            "Bringing interface up...",
            interface_up
        )

        # -----------------------------------------------------
        # STEP 7 — Verify
        # -----------------------------------------------------

        def verify_restore():

            nonlocal current_mac

            current_mac = get_current_mac(
                interface
            )

            if current_mac.lower() != original_mac.lower():

                raise RuntimeError(
                    "Original MAC address verification failed."
                )

        progress_bar(
            "Verifying restored MAC address...",
            verify_restore
        )

        # -----------------------------------------------------
        # STEP 8 — Remove saved state
        # -----------------------------------------------------

        def remove_state():

            remove_original_mac(
                interface
            )

        progress_bar(
            "Removing saved MAC state...",
            remove_state
        )

        print()

        status(
            "+",
            "Original MAC address restored successfully.",
            BLUE
        )

        print_mac_panel(
            interface,
            current_mac,
            original_mac,
            "MAC RESTORED"
        )

    except Exception as error:

        print()

        status(
            "!",
            str(error),
            RED
        )

        sys.exit(1)


# ─────────────────────────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────────────────────────

def parse_arguments():

    parser = argparse.ArgumentParser(
        prog="macmutator",
        description=(
            "MacMutator - Linux MAC address "
            "manipulation tool."
        )
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"MacMutator {VERSION}"
    )

    parser.add_argument(
        "--random",
        metavar="INTERFACE",
        help=(
            "Generate and apply a random "
            "locally administered MAC address."
        )
    )

    parser.add_argument(
        "--show",
        metavar="INTERFACE",
        help=(
            "Display the current MAC address."
        )
    )

    parser.add_argument(
        "--restore",
        metavar="INTERFACE",
        help=(
            "Restore the original MAC address "
            "saved by MacMutator."
        )
    )

    return parser.parse_args()


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():

    args = parse_arguments()

    actions = [
        args.random is not None,
        args.show is not None,
        args.restore is not None
    ]

    selected_actions = sum(actions)

    # ---------------------------------------------------------
    # NO ACTION
    # ---------------------------------------------------------

    if selected_actions == 0:

        print_banner()

        status(
            "*",
            "No operation specified.",
            BLUE
        )

        print()

        print_usage()

        return

    # ---------------------------------------------------------
    # MULTIPLE ACTIONS
    # ---------------------------------------------------------

    if selected_actions > 1:

        print_banner()

        status(
            "!",
            "Only one operation can be used at a time.",
            RED
        )

        print()

        sys.exit(1)

    # ---------------------------------------------------------
    # RANDOM
    # ---------------------------------------------------------

    if args.random is not None:

        print_banner()

        new_mac = generate_random_mac()

        if not validate_mac(new_mac):

            status(
                "!",
                "An invalid MAC address was generated.",
                RED
            )

            sys.exit(1)

        change_mac(
            args.random,
            new_mac
        )

    # ---------------------------------------------------------
    # SHOW
    # ---------------------------------------------------------

    elif args.show is not None:

        print_banner()

        show_mac(
            args.show
        )

    # ---------------------------------------------------------
    # RESTORE
    # ---------------------------------------------------------

    elif args.restore is not None:

        print_banner()

        restore_mac(
            args.restore
        )


if __name__ == "__main__":
    main()
