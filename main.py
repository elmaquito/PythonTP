"""
Main application entry point for Restaurant Access Control System
Handles admin authentication and application startup
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
import os


class AdminAuthentication:
    """Handles admin authentication for secure access"""
    
    # Default admin credentials (in production, these should be encrypted and stored securely)
    DEFAULT_ADMIN_CREDENTIALS = {
        "admin": "restaurant123",
        "manager": "access456",
        "supervisor": "control789",
        "StudentX": "studentx123"
    }
    # Map users to roles. 'admin' role has full access; 'student' role has restricted access.
    DEFAULT_USER_ROLES = {
        "admin": "admin",
        "manager": "admin",
        "supervisor": "admin",
        "StudentX": "student"
    }
    
    def __init__(self):
        """Initialize authentication system"""
        self.authenticated = False
        self.username = None
        self.role = None
    
    def authenticate(self) -> bool:
        """
        Show authentication dialog and verify credentials
        
        Returns:
            True if authentication successful, False otherwise
        """
        # Try GUI authentication first
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Show authentication dialog
            credentials = self.show_login_dialog(root)
            
            if credentials is None:
                root.destroy()
                return False  # User cancelled
            
            username, password = credentials
            
            # Verify credentials
            if self.verify_credentials(username, password):
                self.authenticated = True
                self.username = username
                # assign role if known
                self.role = self.DEFAULT_USER_ROLES.get(username, 'admin')
                messagebox.showinfo("Authentication Successful", 
                                   f"Welcome, {username}!\nAccess granted to Restaurant Control System.")
                root.destroy()
                return True
            else:
                messagebox.showerror("Authentication Failed", 
                                   "Invalid username or password.\nAccess denied.")
                root.destroy()
                return False
                
        except Exception as e:
            print(f"GUI authentication failed: {e}")
            print("Falling back to console authentication...")
            return self.console_authenticate()
    
    def console_authenticate(self) -> bool:
        """
        Console-based authentication fallback
        
        Returns:
            True if authentication successful, False otherwise
        """
        import getpass
        
        print("\n" + "="*50)
        print("CONSOLE AUTHENTICATION")
        print("="*50)
        print("Available accounts:")
        for user, pwd in self.DEFAULT_ADMIN_CREDENTIALS.items():
            print(f"  Username: {user} | Password: {pwd}")
        print("="*50)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                username = input("Username: ").strip()
                password = getpass.getpass("Password: ").strip()
                
                if self.verify_credentials(username, password):
                    self.authenticated = True
                    self.username = username
                    self.role = self.DEFAULT_USER_ROLES.get(username, 'admin')
                    print(f"✅ Authentication successful! Welcome, {username}")
                    return True
                else:
                    remaining = max_attempts - attempt - 1
                    if remaining > 0:
                        print(f"❌ Invalid credentials. {remaining} attempts remaining.")
                    else:
                        print("❌ Authentication failed. Maximum attempts reached.")
                        
            except KeyboardInterrupt:
                print("\n❌ Authentication cancelled by user.")
                return False
            except Exception as e:
                print(f"❌ Error during authentication: {e}")
                
        return False
    
    def show_login_dialog(self, parent) -> tuple:
        """
        Show custom login dialog
        
        Args:
            parent: Parent window
            
        Returns:
            Tuple of (username, password) or None if cancelled
        """
        # Create login dialog
        dialog = tk.Toplevel(parent)
        dialog.title("Restaurant Access Control - Admin Login")
        dialog.geometry("400x280")
        dialog.resizable(False, False)
        dialog.configure(bg='#f0f0f0')
        
        # Center the dialog on screen
        dialog.transient(parent)
        dialog.grab_set()
        
        # Position dialog in center of screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (280 // 2)
        dialog.geometry(f"400x280+{x}+{y}")
        
        # Bring dialog to front and focus
        dialog.lift()
        dialog.attributes('-topmost', True)
        dialog.after_idle(dialog.attributes, '-topmost', False)
        dialog.focus_force()
        
        # Result variable
        result = None
        
        # Create dialog content
        tk.Label(dialog, text="Administrator Authentication", 
                font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=20)
        
        # Username field
        username_frame = tk.Frame(dialog, bg='#f0f0f0')
        username_frame.pack(pady=5)
        tk.Label(username_frame, text="Username:", bg='#f0f0f0').pack(side=tk.LEFT)
        username_entry = tk.Entry(username_frame, width=20, font=('Arial', 10))
        username_entry.pack(side=tk.LEFT, padx=10)
        
        # Password field
        password_frame = tk.Frame(dialog, bg='#f0f0f0')
        password_frame.pack(pady=5)
        tk.Label(password_frame, text="Password:", bg='#f0f0f0').pack(side=tk.LEFT)
        password_entry = tk.Entry(password_frame, width=20, font=('Arial', 10), show='*')
        password_entry.pack(side=tk.LEFT, padx=10)
        
        # Button frame
        button_frame = tk.Frame(dialog, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        def on_login():
            nonlocal result
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if username and password:
                result = (username, password)
                dialog.destroy()
            else:
                messagebox.showwarning("Invalid Input", "Please enter both username and password")
        
        def on_cancel():
            dialog.destroy()
        
        tk.Button(button_frame, text="Login", command=on_login, 
                 bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=on_cancel,
                 bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Info text
        info_text = "Default credentials:\\n" + \
                   "admin / restaurant123\\n" + \
                   "manager / access456\\n" + \
                   "supervisor / control789"
        tk.Label(dialog, text=info_text, font=('Arial', 8), bg='#f0f0f0', 
                fg='#666666', justify=tk.LEFT).pack(pady=10)
        
        # Focus on username entry after a brief delay
        dialog.after(100, lambda: username_entry.focus_set())
        
        # Bind Enter key to login
        dialog.bind('<Return>', lambda e: on_login())
        password_entry.bind('<Return>', lambda e: on_login())
        
        # Make sure dialog is visible
        dialog.deiconify()
        dialog.update()
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """
        Verify admin credentials
        
        Args:
            username: Entered username
            password: Entered password
            
        Returns:
            True if credentials are valid, False otherwise
        """
        return (username in self.DEFAULT_ADMIN_CREDENTIALS and 
                self.DEFAULT_ADMIN_CREDENTIALS[username] == password)
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.authenticated
    
    def get_username(self) -> str:
        """Get authenticated username"""
        return self.username

    def get_role(self) -> str:
        """Get role of authenticated user"""
        return self.role


def check_dependencies():
    """
    Check if required dependencies are installed
    
    Returns:
        Tuple of (all_installed, missing_packages)
    """
    required_packages = [
        ('cv2', 'opencv-python'),
        ('face_recognition', 'face-recognition'),
        ('numpy', 'numpy'),
        ('PIL', 'Pillow')
    ]
    
    missing_packages = []
    
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)
    
    return len(missing_packages) == 0, missing_packages


def show_dependency_error(missing_packages):
    """Show error message for missing dependencies"""
    root = tk.Tk()
    root.withdraw()
    
    error_msg = "Missing Required Dependencies\\n\\n"
    error_msg += "The following packages need to be installed:\\n"
    for package in missing_packages:
        error_msg += f"  • {package}\\n"
    error_msg += "\\nTo install all dependencies, run:\\n"
    error_msg += "pip install -r requirements.txt"
    
    messagebox.showerror("Missing Dependencies", error_msg)
    root.destroy()


def main():
    """Main application entry point"""
    print("Restaurant Access Control System")
    print("=" * 40)
    
    # Check for special modes
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
    console_auth = len(sys.argv) > 1 and sys.argv[1] == "--console"
    
    # Check dependencies first
    deps_ok, missing = check_dependencies()
    
    # Initialize authentication
    auth = AdminAuthentication()
    
    if test_mode:
        print("Running in test mode - skipping authentication")
        auth.authenticated = True
        auth.username = "test_admin"
        auth.role = 'admin'
    elif console_auth:
        print("Using console authentication mode")
        if not auth.console_authenticate():
            print("Authentication failed or cancelled. Exiting.")
            return 1
    else:
        print("Starting admin authentication...")
        print("📋 Please check for the authentication dialog window!")
        print("📋 Default credentials: admin / restaurant123")
        print("📋 If dialog doesn't appear, try: python main.py --console")
        
        # Authenticate user
        if not auth.authenticate():
            print("Authentication failed or cancelled. Exiting.")
            return 1
    
    print(f"Authentication successful. User: {auth.get_username()}")
    
    try:
        # Always try to load the full GUI first, regardless of dependencies
        print("Attempting to start full version...")
        
        full_gui_loaded = False
        try:
            from gui import RestaurantAccessGUI
            # Pass authenticated user and role to GUI so it can adapt the UI
            app = RestaurantAccessGUI(authenticated_user=auth.get_username(), user_role=(auth.get_role() or 'admin'))
            print("✅ Full GUI with face recognition initialized successfully.")
            full_gui_loaded = True
        except ImportError as e:
            print(f"⚠️  Could not import full GUI modules: {e}")
            if not deps_ok:
                print("Missing dependencies:")
                for package in missing:
                    print(f"  - {package}")
        except Exception as e:
            print(f"⚠️  Error initializing full GUI: {e}")
        
        # If full GUI failed, use demo version
        if not full_gui_loaded:
            print("📱 Starting demo version instead...")
            try:
                from demo import DemoRestaurantGUI
                app = DemoRestaurantGUI()
                # attach auth info if demo GUI doesn't accept constructor args
                try:
                    app.authenticated_user = auth.get_username()
                    app.user_role = auth.get_role() or 'admin'
                except Exception:
                    pass
                print("✅ Demo GUI initialized successfully.")
            except Exception as e:
                print(f"❌ Error initializing demo GUI: {e}")
                return 1
        
        # Authentication info passed to GUI (or attached for demo GUI above)
        
        if test_mode:
            print("Test mode: GUI initialization successful, exiting without running")
            return 0
        
        # Run the application
        print("Starting GUI application...")
        app.run()
        
        print("Application closed.")
        return 0
        
    except Exception as e:
        error_msg = f"Failed to start application: {e}"
        print(f"Error: {error_msg}")
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Application Error", error_msg)
        root.destroy()
        
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\\nApplication interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\\nUnexpected error: {e}")
        sys.exit(1)