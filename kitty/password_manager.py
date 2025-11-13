#!/usr/bin/env python3
"""
A kitty kitten plugin that integrates with macOS Keychain for password management.
Uses fzf for selection and stores passwords under the account 'kitty-pass'.
"""

import getpass
import os
import subprocess
import sys
from pathlib import Path


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


def get_existing_keys() -> list[str]:
    """
    Retrieve all service keys from macOS Keychain where account='kitty-pass'.

    Returns:
        List of service key names
    """
    awk_script = """
    BEGIN {RS="keychain: "}
    /acct"<blob>="kitty-pass"/ {
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


def select_key_with_fzf(existing_keys: list[str]) -> tuple[str, bool]:
    """
    Use fzf to select an existing key or create a new one.

    Args:
        existing_keys: List of existing service keys

    Returns:
        Tuple of (selected_key, is_delete_action)
    """
    try:
        input_data = "\n".join(existing_keys)
        env = get_shell_env()
        fzf_cmd = find_fzf_path()

        result = subprocess.run(
            [
                fzf_cmd,
                "--print-query",
                "--prompt=Select password key or enter new (ctrl+D to delete): ",
                "--bind=ctrl-d:become(echo DELETE:{})+accept",
                "--header=↵ Use password | ctrl+D Delete | Ctrl+C Cancel",
            ],
            input=input_data,
            text=True,
            capture_output=True,
            check=False,  # fzf returns non-zero exit codes for valid states (1=no match, 130=cancelled)
            env=env,
        )

        # Check if user wants to delete (output starts with DELETE:)
        output = result.stdout.strip()
        if output.startswith("DELETE:"):
            key_to_delete = output[7:]  # Remove "DELETE:" prefix
            return (key_to_delete, True)

        # fzf returns:
        # - exit code 0: user selected an item
        # - exit code 1: user entered new text (no match)
        # - exit code 130: user cancelled (Ctrl+C)

        if result.returncode == 130:
            # User cancelled
            return ("", False)

        output_lines = output.split("\n")

        if result.returncode == 0 and len(output_lines) >= 2:
            # User selected an existing item (last line is the selection)
            return (output_lines[-1], False)
        elif len(output_lines) >= 1:
            # User entered new text (first line is the query)
            return (output_lines[0], False)

        return ("", False)
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


def add_password_to_keychain(service: str, password: str) -> None:
    """
    Add a new password to macOS Keychain.

    Args:
        service: Service name (key)
        password: Password to store

    Raises:
        KittenError: If the password cannot be added
    """
    try:
        subprocess.run(
            ["security", "add-generic-password", "-a", "kitty-pass", "-s", service, "-w", password],
            check=True,
            capture_output=True,
        )
        print(f"✓ Password for '{service}' added to keychain successfully")
    except subprocess.CalledProcessError as e:
        error_msg = f"Error adding password to keychain: {e.stderr.decode()}"
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
            ["security", "find-generic-password", "-a", "kitty-pass", "-s", service, "-w"],
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


def delete_password_from_keychain(service: str) -> None:
    """
    Delete a password from macOS Keychain.

    Args:
        service: Service name (key)

    Raises:
        KittenError: If the password cannot be deleted
    """
    try:
        subprocess.run(
            ["security", "delete-generic-password", "-a", "kitty-pass", "-s", service],
            check=True,
            capture_output=True,
        )
        print(f"✓ Password for '{service}' deleted successfully")
    except subprocess.CalledProcessError as e:
        error_msg = f"Error deleting password from keychain: {e.stderr.decode()}"
        raise KittenError(error_msg) from e


def confirm_delete(service: str) -> bool:
    """
    Ask user to confirm deletion. Press Enter to delete, type 'no' to cancel.

    Args:
        service: Service name to delete

    Returns:
        True if user confirms deletion, False otherwise
    """
    print(f"\n⚠️  WARNING: About to DELETE password for: '{service}'")
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
        Password string to be pasted, or empty string if adding new password
    """
    try:
        # Get existing keys from keychain
        existing_keys = get_existing_keys()

        # Let user select or enter a key using fzf
        selected_key, is_delete = select_key_with_fzf(existing_keys)

        if not selected_key:
            # User cancelled
            return ""

        # Handle delete action
        if is_delete:
            if selected_key in existing_keys:
                if confirm_delete(selected_key):
                    delete_password_from_keychain(selected_key)
                    kitty_input("\nPress Enter to continue...")
                else:
                    kitty_input("\nPress Enter to continue...")
                return ""
            else:
                raise KittenError(f"Cannot delete: '{selected_key}' does not exist")

        # Check if this is a new key or existing one
        if selected_key in existing_keys:
            # Existing key - retrieve and return password
            password = get_password_from_keychain(selected_key)
            print(f"✓ Retrieved password for '{selected_key}'")
            return password
        else:
            # New key - prompt for password and store it
            print(f"\nCreating new password entry for: {selected_key}")
            password = getpass.getpass("Enter password (hidden): ")

            if not password:
                raise KittenError("Password cannot be empty")

            # Confirm password
            password_confirm = getpass.getpass("Confirm password: ")

            if password != password_confirm:
                raise KittenError("Passwords do not match")

            password = password.strip()

            # Store in keychain
            add_password_to_keychain(selected_key, password)
            kitty_input("\nPress Enter to continue...")
            # Return empty string - don't paste when adding new password
            return ""

    except KittenError as e:
        # Display error message and wait for user to acknowledge
        print(f"\n❌ Error: {e}", file=sys.stderr)
        kitty_input("\nPress Enter to continue...")
        return ""
    except KeyboardInterrupt:
        # User interrupted with Ctrl+C
        return ""
    except Exception as e:
        # Unexpected error
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        kitty_input("\nPress Enter to continue...")
        return ""


from kittens.tui.handler import result_handler


@result_handler(type_of_input="text")
def handle_result(args, answer, target_window_id, boss):  # noqa: ARG001
    """
    Handle the result from main() - paste password to the active window if non-empty.

    Args:
        args: Command line arguments
        answer: Return value from main() (the password)
        target_window_id: ID of the window that launched the kitten
        boss: Boss instance for controlling kitty
    """
    # Get the target window
    w = boss.window_id_map.get(target_window_id)

    if w is None:
        return

    # If answer is non-empty, paste it
    if answer:
        w.paste(answer)


if __name__ == "__main__":
    # For testing purposes
    result = main(sys.argv[1:])
    if result:
        print(f"Would paste: {'*' * len(result)}")
