#!/usr/bin/env python3
"""
A kitty kitten plugin that integrates with macOS Keychain for SSH connection management.
Uses fzf for selection and stores SSH credentials under the account 'kitty-ssh'.
"""

import getpass
import os
import subprocess
import sys
import time
from pathlib import Path

from kitty.fast_data_types import add_timer, get_boss


class KittenError(Exception):
    """Base exception for kitten errors that should be displayed to the user."""


def kitty_input(prompt: str = "") -> str:
    """
    Read input from the user in a kitty kitten context.

    This function reads directly from /dev/tty to ensure it works correctly
    in kitten environment where stdin might be redirected.

    Args:
        prompt: The prompt to display to the user

    Returns:
        The user's input as a string (stripped of whitespace)
    """
    try:
        with open("/dev/tty", encoding="utf-8") as tty:
            if prompt:
                sys.stdout.write(prompt)
                sys.stdout.flush()
            response = tty.readline().strip()
            return response
    except Exception:  # noqa: BLE001
        # Fallback to regular input if /dev/tty is not available
        return input(prompt).strip()


def get_shell_env():
    """
    Get the environment variables from the user's shell to ensure PATH includes homebrew and other tools.

    Returns:
        Dictionary of environment variables with properly configured PATH
    """
    env = os.environ.copy()

    # Common homebrew paths on macOS
    homebrew_paths = [
        "/opt/homebrew/bin",  # Apple Silicon Macs
        "/usr/local/bin",  # Intel Macs
        "/opt/homebrew/sbin",
        "/usr/local/sbin",
    ]

    # Get existing PATH
    current_path = env.get("PATH", "")
    path_parts = current_path.split(":") if current_path else []

    # Add homebrew paths if they exist and aren't already in PATH
    for brew_path in homebrew_paths:
        if Path(brew_path).exists() and brew_path not in path_parts:
            path_parts.insert(0, brew_path)

    # Update PATH in environment
    env["PATH"] = ":".join(path_parts)

    return env


def find_fzf_path():
    """
    Try to find the fzf executable in common locations.

    Returns:
        Path to fzf executable, or just "fzf" if not found in known locations
    """
    # Try to find fzf using 'which' with the proper environment
    try:
        env = get_shell_env()
        result = subprocess.run(
            ["which", "fzf"],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # Common fzf installation locations
    common_paths = [
        "/opt/homebrew/bin/fzf",
        "/usr/local/bin/fzf",
        Path.home() / ".fzf/bin/fzf",
    ]

    for fzf_path in common_paths:
        fzf_file = Path(fzf_path)
        if fzf_file.exists() and fzf_file.is_file():
            return str(fzf_file)

    # Fallback to just "fzf" and let PATH resolution handle it
    return "fzf"


def parse_service_name(service: str) -> tuple[str, str, str]:
    """
    Parse service name in format "friendly-name|username@hostname".

    Args:
        service: Service name from keychain

    Returns:
        Tuple of (friendly_name, username, hostname)
    """
    if "|" in service:
        friendly_name, connection = service.split("|", 1)
        if "@" in connection:
            username, hostname = connection.split("@", 1)
            return friendly_name, username, hostname
    # Fallback for malformed entries
    return service, "", ""


def format_display_name(service: str) -> str:
    """
    Format service name for display in fzf.

    Args:
        service: Service name from keychain

    Returns:
        Formatted display string like "friendly-name (username@hostname)"
    """
    friendly_name, username, hostname = parse_service_name(service)
    if username and hostname:
        return f"{friendly_name} ({username}@{hostname})"
    return friendly_name


def get_existing_keys() -> list[str]:
    """
    Retrieve all service keys from macOS Keychain where account='kitty-ssh'.

    Returns:
        List of service key names
    """
    awk_script = """
    BEGIN {RS="keychain: "}
    /acct"<blob>="kitty-ssh"/ {
        if (match($0, /"svce"<blob>="[^"]+/)) {
            start = RSTART + 14;
            len = RLENGTH - 14;
            print substr($0, start, len)
        }
    }
    """

    try:
        # Run security dump-keychain and pipe to awk
        security_proc = subprocess.Popen(["security", "dump-keychain"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        awk_proc = subprocess.Popen(
            ["awk", awk_script], stdin=security_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        security_proc.stdout.close()
        output, _ = awk_proc.communicate()

        if output:
            return [key.strip() for key in output.strip().split("\n") if key.strip()]
        return []
    except Exception as e:
        raise KittenError(f"Error retrieving keychain keys: {e}") from e


def select_key_with_fzf(existing_keys: list[str]) -> tuple[str, str]:
    """
    Use fzf to select an existing SSH connection or create a new one.

    Args:
        existing_keys: List of existing service keys

    Returns:
        Tuple of (selected_key, action) where action is one of:
        - "connect": Connect to SSH (default)
        - "delete": Delete the connection
        - "paste_only": Only paste password without connecting
    """
    try:
        # Format display names for fzf
        display_items = [format_display_name(key) for key in existing_keys]
        input_data = "\n".join(display_items)
        env = get_shell_env()
        fzf_cmd = find_fzf_path()

        result = subprocess.run(
            [
                fzf_cmd,
                "--print-query",
                "--prompt=Select SSH connection or enter new name: ",
                "--bind=ctrl-d:become(echo DELETE:{})+accept",
                "--bind=ctrl-e:become(echo PASTE:{})+accept",
                "--header=↵ Connect | ctrl+D Delete | ctrl+F Paste password | Ctrl+C Cancel",
            ],
            input=input_data,
            text=True,
            capture_output=True,
            check=False,  # fzf returns non-zero exit codes for valid states (1=no match, 130=cancelled)
            env=env,
        )

        # Check the output for action prefixes
        output = result.stdout.strip()

        # Check if user wants to delete (output starts with DELETE:)
        if output.startswith("DELETE:"):
            display_name = output[7:]  # Remove "DELETE:" prefix
            # Find the actual service key from display name
            for i, display in enumerate(display_items):
                if display == display_name:
                    return (existing_keys[i], "delete")
            # If not found in display items, try to use as-is
            return (display_name, "delete")

        # Check if user wants to paste only (output starts with PASTE:)
        if output.startswith("PASTE:"):
            display_name = output[6:]  # Remove "PASTE:" prefix
            # Find the actual service key from display name
            for i, display in enumerate(display_items):
                if display == display_name:
                    return (existing_keys[i], "paste_only")
            # If not found in display items, try to use as-is
            return (display_name, "paste_only")

        # fzf returns:
        # - exit code 0: user selected an item
        # - exit code 1: user entered new text (no match)
        # - exit code 130: user cancelled (Ctrl+C)

        if result.returncode == 130:
            # User cancelled
            return ("", "")

        output_lines = output.split("\n")

        # fzf with --print-query outputs: query on first line, selection on last line
        # returncode 0 means user selected an item, 1 means no match/new input

        if result.returncode == 0:
            # User selected an existing item
            # With --print-query, last non-empty line is the selection
            selected_display = output_lines[-1] if output_lines else ""
            if not selected_display and len(output_lines) > 1:
                selected_display = output_lines[-2]

            # Find the actual service key from display name
            for i, display in enumerate(display_items):
                if display == selected_display:
                    print(f"DEBUG: Matched! Returning existing key: '{existing_keys[i]}'", file=sys.stderr)
                    return (existing_keys[i], "connect")

            return ("", "")
        elif result.returncode == 1:
            # User entered new text (no match)
            # First line is the query text
            new_name = output_lines[0] if output_lines else ""
            print(f"DEBUG: New name entered: '{new_name}'", file=sys.stderr)
            # Make sure it's not a display format name
            if "(" in new_name and ")" in new_name and "@" in new_name:
                # User might have typed something like the display format, extract friendly name
                new_name = new_name.split("(")[0].strip()
            return (new_name, "connect")

        return ("", "")
    except FileNotFoundError as e:
        env = get_shell_env()
        current_path = env.get("PATH", "")
        error_msg = (
            f"fzf command not found: {e}\n"
            f"Current PATH: {current_path}\n\n"
            "To install fzf:\n"
            "  brew install fzf\n\n"
            "Or if already installed, ensure it's in your PATH."
        )
        raise KittenError(error_msg) from e
    except Exception as e:
        raise KittenError(f"Error during fzf selection: {e}") from e


def add_ssh_to_keychain(friendly_name: str, username: str, hostname: str, password: str) -> None:
    """
    Add a new SSH connection to macOS Keychain.

    Args:
        friendly_name: Friendly name for the connection
        username: SSH username
        hostname: SSH hostname
        password: SSH password

    Raises:
        KittenError: If the SSH connection cannot be added
    """
    service = f"{friendly_name}|{username}@{hostname}"
    try:
        subprocess.run(
            ["security", "add-generic-password", "-a", "kitty-ssh", "-s", service, "-w", password],
            check=True,
            capture_output=True,
        )
        print(f"✓ SSH connection '{friendly_name}' ({username}@{hostname}) added successfully")
    except subprocess.CalledProcessError as e:
        error_msg = f"Error adding SSH connection to keychain: {e.stderr.decode()}"
        raise KittenError(error_msg) from e


def get_password_from_keychain(service: str) -> str:
    """
    Retrieve a password from macOS Keychain.

    Args:
        service: Service name (key)

    Returns:
        Password string

    Raises:
        KittenError: If the password cannot be retrieved
    """
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-a", "kitty-ssh", "-s", service, "-w"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = f"Could not retrieve password for '{service}'"
        if e.stderr:
            error_msg += f": {e.stderr.decode()}"
        raise KittenError(error_msg) from e


def delete_ssh_from_keychain(service: str) -> None:
    """
    Delete an SSH connection from macOS Keychain.

    Args:
        service: Service name (key)

    Raises:
        KittenError: If the SSH connection cannot be deleted
    """
    try:
        subprocess.run(
            ["security", "delete-generic-password", "-a", "kitty-ssh", "-s", service],
            check=True,
            capture_output=True,
        )
        friendly_name, username, hostname = parse_service_name(service)
        print(f"✓ SSH connection '{friendly_name}' ({username}@{hostname}) deleted successfully")
    except subprocess.CalledProcessError as e:
        error_msg = f"Error deleting SSH connection from keychain: {e.stderr.decode()}"
        raise KittenError(error_msg) from e


def copy_to_clipboard(text: str) -> None:
    """
    Copy text to macOS clipboard using pbcopy.

    Args:
        text: Text to copy to clipboard
    """
    try:
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
    except subprocess.CalledProcessError as e:
        raise KittenError(f"Failed to copy to clipboard: {e}") from e


def confirm_delete(service: str) -> bool:
    """
    Ask user to confirm deletion. Press Enter to delete, type 'no' to cancel.

    Args:
        service: Service name to delete

    Returns:
        True if user confirms deletion, False otherwise
    """
    friendly_name, username, hostname = parse_service_name(service)
    print("\n⚠️  WARNING: About to DELETE SSH connection:")
    print(f"  Name: {friendly_name}")
    print(f"  Connection: {username}@{hostname}")
    print("This action cannot be undone!")

    response = kitty_input("\nPress Enter to DELETE, or type 'no' to cancel: ").lower()

    if response == "" or response not in ["no", "n"]:
        return True
    else:
        print("❌ Deletion cancelled.")
        return False


def main(args):  # noqa: ARG001
    """
    Main function for the kitten - handles the terminal UI.

    Returns:
        SSH command string to execute, or empty string
    """
    while True:
        try:
            # Get existing keys from keychain
            existing_keys = get_existing_keys()

            # Let user select or enter a key using fzf
            selected_key, action = select_key_with_fzf(existing_keys)

            if not selected_key:
                # User cancelled
                return {}

            # Handle delete action
            if action == "delete":
                if selected_key in existing_keys:
                    if confirm_delete(selected_key):
                        delete_ssh_from_keychain(selected_key)
                        time.sleep(1)  # Brief delay to show success message
                        continue  # Return to fzf selection
                    else:
                        time.sleep(0.5)  # Brief delay before returning to fzf
                        continue  # Return to fzf selection
                else:
                    raise KittenError(f"Cannot delete: '{selected_key}' does not exist")

            # Handle paste only action
            if action == "paste_only":
                if selected_key in existing_keys:
                    # Existing connection - retrieve password and return for paste only
                    friendly_name, username, hostname = parse_service_name(selected_key)

                    if not username or not hostname:
                        raise KittenError(f"Invalid SSH connection format for '{selected_key}'")

                    password = get_password_from_keychain(selected_key)

                    print(f"✓ Pasting password for '{friendly_name}' ({username}@{hostname})")

                    # Return dict with password only for paste (no SSH command)
                    return {
                        "password_only": password,
                    }
                else:
                    raise KittenError(f"Cannot paste password: '{selected_key}' does not exist")

            # Check if this is a new connection or existing one
            if selected_key in existing_keys:
                # Existing connection - retrieve password and return SSH command with password
                friendly_name, username, hostname = parse_service_name(selected_key)

                if not username or not hostname:
                    raise KittenError(f"Invalid SSH connection format for '{selected_key}'")

                password = get_password_from_keychain(selected_key)

                print(f"✓ Connecting to '{friendly_name}' ({username}@{hostname})")

                # Return dict with SSH command and password for auto-paste
                ssh_cmd = (
                    f"kitty +kitten ssh -o UserKnownHostsFile=/dev/null "
                    f"-o StrictHostKeyChecking=no {username}@{hostname}"
                )
                return {
                    "ssh_command": ssh_cmd,
                    "password": password,
                }
            else:
                # New connection - prompt for details and store it
                friendly_name = selected_key
                print(f"\n Creating new SSH connection: {friendly_name}")

                username = kitty_input("Enter SSH username: ").strip()
                if not username:
                    raise KittenError("Username cannot be empty")

                hostname = kitty_input("Enter SSH hostname: ").strip()
                if not hostname:
                    raise KittenError("Hostname cannot be empty")

                password = getpass.getpass("Enter SSH password (hidden): ")
                if not password:
                    raise KittenError("Password cannot be empty")

                # Confirm password
                password_confirm = getpass.getpass("Confirm password: ")
                if password != password_confirm:
                    raise KittenError("Passwords do not match")

                # Store in keychain
                add_ssh_to_keychain(friendly_name, username, hostname, password)
                time.sleep(1)  # Brief delay to show success message
                continue  # Return to fzf selection

        except KittenError as e:
            # Display error message and wait for user to acknowledge
            print(f"\n❌ Error: {e}", file=sys.stderr)
            kitty_input("\nPress Enter to continue...")
            return {}
        except KeyboardInterrupt:
            # User interrupted with Ctrl+C
            return {}
        except Exception as e:
            # Unexpected error
            print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
            kitty_input("\nPress Enter to continue...")
            return {}


from kittens.tui.handler import result_handler


@result_handler(type_of_input="text")
def handle_result(args, answer, target_window_id, boss):  # noqa: ARG001
    """
    Handle the result from main() - send SSH command to the active window and auto-fill password.

    Args:
        args: Command line arguments
        answer: Return value from main() (dict with ssh_command and password, or password_only)
        target_window_id: ID of the window that launched the kitten
        boss: Boss instance for controlling kitty
    """
    # Get the target window
    w = boss.window_id_map.get(target_window_id)

    if w is None:
        return

    # If answer is empty dict, nothing to do
    if not answer:
        return

    # Check if this is a password-only paste request
    password_only = answer.get("password_only", "")
    if password_only:
        # Just paste the password without pressing Enter
        w.paste_text(password_only)
        return

    # Extract ssh_command and password from the answer dict
    ssh_command = answer.get("ssh_command", "")
    password = answer.get("password", "")

    if not ssh_command:
        return

    w.paste_text(ssh_command)
    w.send_key("Enter")

    # If we have a password, set up a timer to detect password prompt
    if password:
        attempt_count = 0  # Use list to allow modification in nested function
        max_attempts = 50
        interval = 0.05

        def check_for_password_prompt(timer_id: int | None) -> None:
            """Check screen content for password prompt and paste password if found."""
            nonlocal attempt_count
            attempt_count += 1

            # Get current active window dynamically
            current_boss = get_boss()
            current_window = current_boss.active_window

            # Fallback to original window if active window is None
            if current_window is None or current_window.destroyed:
                current_window = current_boss.window_id_map.get(target_window_id)

            # Check if window is valid
            if current_window is None or current_window.destroyed:
                return

            try:
                # Read screen content
                screen_text = current_window.as_text(as_ansi=False, add_history=False)

                # Check if "password:" appears in the screen (case-sensitive lowercase)
                if "password:" in screen_text.lower():
                    # Found password prompt! Paste password and send Enter
                    current_window.paste_text(password)
                    current_window.send_key("Enter")
                    return  # Stop checking

                # Check if we've reached max attempts
                if attempt_count >= max_attempts:
                    return  # Stop checking after max attempts

                # Schedule next check
                add_timer(check_for_password_prompt, interval, False)

            except Exception:
                # Silently handle any errors reading screen content
                pass

        # Start the timer
        add_timer(check_for_password_prompt, interval, False)

    # Paste the SSH command and execute it
    w.paste(ssh_command)
    w.send_key("Enter")
