"""
Main application entry point for Restaurant Access Control System.
This file provides a small, robust authentication flow (GUI with
console fallback) and starts the main GUI or demo GUI.
"""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Tuple


class AdminAuthentication:
    """Simple authentication handler with GUI and console fallback."""

    DEFAULT_ADMIN_CREDENTIALS = {
        "admin": "restaurant123",
        "manager": "access456",
        "supervisor": "control789",
        "StudentX": "studentx123",
    }

    DEFAULT_USER_ROLES = {
        "admin": "admin",
        "manager": "admin",
        "supervisor": "admin",
        "StudentX": "student",
    }

    def __init__(self) -> None:
        self.authenticated = False
        self.username: Optional[str] = None
        self.role: Optional[str] = None

    def verify_credentials(self, username: str, password: str) -> bool:
        return self.DEFAULT_ADMIN_CREDENTIALS.get(username) == password

    def show_login_dialog(self, parent: tk.Misc) -> Optional[Tuple[str, str]]:
        """Show a simple login dialog and return (username, password) or None.

        Uses standard simpledialog prompts anchored to a transient hidden root.
        This avoids creating multiple visible Tk instances and is simpler to
        use across platforms.
        """

        try:
            from tkinter import simpledialog

            root = tk.Tk()
            root.withdraw()

            # Ask for username then password (password uses show='*')
            username = simpledialog.askstring("Login", "Username:", parent=root)
            if username is None:
                root.destroy()
                return None

            password = simpledialog.askstring("Login", "Password:", show='*', parent=root)
            root.destroy()

            if password is None:
                return None

            return username.strip(), password
        except Exception:
            # If dialogs fail for any reason, gracefully return None so caller
            # can fallback to console authentication.
            return None

    def console_authenticate(self) -> bool:
        """Fallback console authentication (non-interactive uses)."""
        import getpass

        attempts = 3
        for _ in range(attempts):
            try:
                username = input("Username: ").strip()
                password = getpass.getpass("Password: ")
            except (KeyboardInterrupt, EOFError):
                print("Authentication cancelled")
                return False

            if self.verify_credentials(username, password):
                self.authenticated = True
                self.username = username
                self.role = self.DEFAULT_USER_ROLES.get(username, "admin")
                print(f"Authentication successful. Welcome, {username}")
                return True
            else:
                print("Invalid credentials, try again.")

        print("Authentication failed: maximum attempts reached.")
        return False

    def authenticate(self) -> bool:
        """Try GUI auth first, fall back to console auth on error or cancellation."""
        try:
            # Directly show the login dialog. The dialog creates its own Tk instance
            # to ensure it is visible (some OSes require a top-level Tk window).
            creds = self.show_login_dialog(None)

            if creds is None:
                return False

            username, password = creds
            if self.verify_credentials(username, password):
                self.authenticated = True
                self.username = username
                self.role = self.DEFAULT_USER_ROLES.get(username, "admin")
                try:
                    messagebox.showinfo("Authentication", f"Welcome, {username}")
                except Exception:
                    pass
                return True
            else:
                try:
                    messagebox.showerror("Authentication Failed", "Invalid username or password")
                except Exception:
                    pass
                return False

        except Exception:
            # GUI unavailable or error during GUI auth -> console fallback
            return self.console_authenticate()

    def get_username(self) -> Optional[str]:
        return self.username

    def get_role(self) -> Optional[str]:
        return self.role


def check_dependencies() -> Tuple[bool, list]:
    required = [
        ("cv2", "opencv-python"),
        ("face_recognition", "face-recognition"),
        ("numpy", "numpy"),
        ("PIL", "Pillow"),
    ]
    missing = []
    for mod, pkg in required:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    return (len(missing) == 0), missing


def main() -> int:
    print("Restaurant Access Control System")
    print("=" * 50)

    test_mode = "--test" in sys.argv
    console_mode = "--console" in sys.argv

    deps_ok, missing = check_dependencies()

    auth = AdminAuthentication()

    if test_mode:
        auth.authenticated = True
        auth.username = "test_admin"
        auth.role = "admin"
    elif console_mode:
        if not auth.console_authenticate():
            return 1
    else:
        if not auth.authenticate():
            return 1

    user = auth.get_username() or "(unknown)"
    role = auth.get_role() or "admin"
    print(f"Authentication successful. User: {user} (role: {role})")

    # Lightweight startup logging to help diagnose GUI visibility issues
    def _log_startup(msg: str) -> None:
        try:
            with open('start_debug.log', 'a', encoding='utf-8') as f:
                from datetime import datetime
                f.write(f"[{datetime.now().isoformat()}] {msg}\n")
        except Exception:
            pass

    _log_startup(f"Authenticated user={user} role={role}")

    # Try to initialize full GUI, fall back to demo GUI
    full_gui_loaded = False
    app = None
    try:
        _log_startup("Attempting to import gui.RestaurantAccessGUI")
        from gui import RestaurantAccessGUI  # type: ignore

        _log_startup("gui imported; initializing RestaurantAccessGUI")
        app = RestaurantAccessGUI(authenticated_user=user, user_role=role)
        full_gui_loaded = True
        print("Full GUI initialized")
        _log_startup("Full GUI initialized successfully")
    except ImportError:
        print("Full GUI not available (missing dependencies).")
        _log_startup("ImportError when importing gui - falling back to demo")
        if not deps_ok:
            print("Missing packages:")
            for p in missing:
                print(f" - {p}")
    except Exception as e:  # other initialization errors
        print(f"Error initializing full GUI: {e}")
        _log_startup(f"Error initializing full GUI: {e}")

    if not full_gui_loaded:
        try:
            _log_startup("Attempting to import demo.DemoRestaurantGUI")
            from demo import DemoRestaurantGUI  # type: ignore

            app = DemoRestaurantGUI()
            # best-effort attach auth info
            try:
                setattr(app, "authenticated_user", user)
                setattr(app, "user_role", role)
            except Exception:
                pass
            print("Demo GUI initialized")
            _log_startup("Demo GUI initialized")
        except Exception as e:
            print(f"Failed to initialize demo GUI: {e}")
            _log_startup(f"Failed to initialize demo GUI: {e}")
            return 1

    if test_mode:
        print("Test mode: initialization complete.")
        return 0

    # Run the GUI app
    try:
        print("Starting application...")
        _log_startup("Starting application run()")
        app.run()
        print("Application exited cleanly.")
        _log_startup("Application exited cleanly")
        return 0
    except Exception as e:
        print(f"Application runtime error: {e}")
        try:
            tmp = tk.Tk()
            tmp.withdraw()
            messagebox.showerror("Application Error", str(e))
            tmp.destroy()
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)