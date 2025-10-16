"""
Main application entry point for Restaurant Access Control System
Handles admin authentication and application startup
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import sys
import os
from gui import RestaurantAccessGUI


class AdminAuthentication:
    """Handles admin authentication for secure access"""
    
    # Default admin credentials (in production, these should be encrypted and stored securely)
    DEFAULT_ADMIN_CREDENTIALS = {
        "admin": "restaurant123",
        "manager": "access456",
        "supervisor": "control789"
    }
    
    def __init__(self):
        """Initialize authentication system"""
        self.authenticated = False
        self.username = None
    
    def authenticate(self) -> bool:
        """
        Show authentication dialog and verify credentials
        
        Returns:
            True if authentication successful, False otherwise
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        try:
            # Show authentication dialog
            credentials = self.show_login_dialog(root)
            
            if credentials is None:
                return False  # User cancelled
            
            username, password = credentials
            
            # Verify credentials
            if self.verify_credentials(username, password):
                self.authenticated = True
                self.username = username
                messagebox.showinfo("Authentication Successful", 
                                   f"Welcome, {username}!\nAccess granted to Restaurant Control System.")
                return True
            else:
                messagebox.showerror("Authentication Failed", 
                                   "Invalid username or password.\nAccess denied.")
                return False
                
        except Exception as e:
            messagebox.showerror("Authentication Error", f"An error occurred: {e}")
            return False
        finally:
            root.destroy()
    
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
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.configure(bg='#f0f0f0')
        
        # Center the dialog
        dialog.transient(parent)
        dialog.grab_set()
        
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
        
        # Focus on username entry
        username_entry.focus()
        
        # Bind Enter key to login
        dialog.bind('<Return>', lambda e: on_login())
        
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
    
    # Check dependencies first
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print("Error: Missing required dependencies:")
        for package in missing:
            print(f"  - {package}")
        print("\\nPlease install dependencies with: pip install -r requirements.txt")
        
        # Show GUI error message as well
        show_dependency_error(missing)
        return 1
    
    print("All dependencies are available.")
    
    # Initialize authentication
    auth = AdminAuthentication()
    
    print("Starting admin authentication...")
    
    # Authenticate user
    if not auth.authenticate():
        print("Authentication failed or cancelled. Exiting.")
        return 1
    
    print(f"Authentication successful. User: {auth.get_username()}")
    
    try:
        # Start main application
        print("Starting Restaurant Access Control System...")
        app = RestaurantAccessGUI()
        print("GUI initialized successfully.")
        
        # Add authentication info to the app if needed
        app.authenticated_user = auth.get_username()
        
        # Run the application
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