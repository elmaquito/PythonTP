"""
GUI module for the Restaurant Access Control System
Provides Tkinter-based interface for student management and access control
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import PhotoImage
import os
import threading
import time
import sys
import subprocess
from db import StudentDatabase

# Try to import optional dependencies
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV (cv2) not available - camera features will be disabled")

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available - some image features will be limited")

try:
    from face_recognition_utils import FaceRecognitionUtils
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: Face recognition not available - using simulation mode")
    # Import the simple version from demo
    from demo import SimpleFaceRecognitionUtils as FaceRecognitionUtils


class RestaurantAccessGUI:
    """Main GUI application for restaurant access control"""
    
    def __init__(self, authenticated_user=None, user_role=None):
        """Initialize the GUI application

        Args:
            authenticated_user: optional username of the authenticated user
            user_role: optional role string ('admin' or 'student')
        """
        self.root = tk.Tk()
        self.root.title("Restaurant Access Control System")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize components
        self.db = StudentDatabase()
        self.face_utils = FaceRecognitionUtils()
        
        # Load known faces at startup
        self.face_utils.load_known_faces()
        
        # Authentication info (may be provided by caller)
        self.authenticated_user = authenticated_user
        self.user_role = user_role or 'admin'

    # GUI state variables
        self.current_mode = tk.StringVar(value="access")
        self.camera_active = False
        self.camera_thread = None

        # Camera configuration (resize for faster rendering)
        # Lower values = faster but lower quality
        self.camera_width = 480
        self.camera_height = 360

        # Store last raw frame (RGB numpy array) for background identification
        self._last_frame = None
        self._identifying = False
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Setup GUI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Success.TLabel', font=('Arial', 11), foreground='green', background='#f0f0f0')
        style.configure('Error.TLabel', font=('Arial', 11), foreground='red', background='#f0f0f0')
        style.configure('Big.TButton', font=('Arial', 12, 'bold'), padding=10)
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Build user menu
        self.refresh_user_menu()
        # Main title
        title_label = ttk.Label(self.root, text="Restaurant Access Control System", 
                               style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Mode selection frame
        mode_frame = ttk.Frame(self.root)
        mode_frame.pack(pady=10)
        
        ttk.Label(mode_frame, text="Mode:", style='Header.TLabel').pack(side=tk.LEFT, padx=5)
        
        access_radio = ttk.Radiobutton(mode_frame, text="Access Control", 
                                      variable=self.current_mode, value="access",
                                      command=self.switch_mode)
        access_radio.pack(side=tk.LEFT, padx=10)
        # Only show admin/student management option for admin users
        if getattr(self, 'user_role', 'admin') != 'student':
            admin_radio = ttk.Radiobutton(mode_frame, text="Student Management", 
                                         variable=self.current_mode, value="admin",
                                         command=self.switch_mode)
            admin_radio.pack(side=tk.LEFT, padx=10)
        
        # Main content frame
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Initialize with access control mode
        self.switch_mode()
    
    def switch_mode(self):
        """Switch between access control and admin modes"""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if self.current_mode.get() == "access":
            self.create_access_control_widgets()
        else:
            self.create_admin_widgets()
        # After rebuilding mode widgets, refresh the user menu (role may hide options)
        try:
            self.refresh_user_menu()
        except Exception:
            pass

    def refresh_user_menu(self):
        """Rebuild the top-level user menu according to current authenticated user/role."""
        try:
            menubar = tk.Menu(self.root)
            user_menu = tk.Menu(menubar, tearoff=0)
            user_label = self.authenticated_user if getattr(self, 'authenticated_user', None) else 'Not logged'
            user_menu.add_command(label=f"User: {user_label}", state='disabled')
            user_menu.add_separator()

            # If current role is student, offer quick balance view
            if getattr(self, 'user_role', None) == 'student':
                user_menu.add_command(label="View My Balance", command=self.view_my_balance)
            # Switch user (in-process relogin)
            user_menu.add_command(label="Switch User", command=self.open_relogin_dialog)
            # Logout (full exit)
            user_menu.add_command(label="Logout", command=self.logout_and_restart)

            menubar.add_cascade(label="User", menu=user_menu)
            try:
                self.root.config(menu=menubar)
                # store reference for potential updates
                self._menubar = menubar
                self._user_menu = user_menu
            except Exception:
                pass
        except Exception:
            # Best-effort menu rebuild; ignore failures
            pass

    def open_relogin_dialog(self):
        """Open an in-process login dialog and update the authenticated user/role without restarting."""
        try:
            # Import auth helper lazily to avoid circular imports at module load
            from main import AdminAuthentication

            auth = AdminAuthentication()
            # Use the GUI dialog directly (non-blocking within this call)
            creds = auth.show_login_dialog(self.root)
            if creds is None:
                # user cancelled
                return

            username, password = creds
            if auth.verify_credentials(username, password):
                # Update local auth state
                self.authenticated_user = username
                self.user_role = auth.DEFAULT_USER_ROLES.get(username, 'admin')
                messagebox.showinfo("Switch User", f"Switched user to {username}")

                # Refresh UI according to new role
                # If switching to student role, ensure admin widgets are hidden
                try:
                    # If currently in admin mode but role is student, switch to access mode
                    if self.user_role == 'student' and self.current_mode.get() != 'access':
                        self.current_mode.set('access')
                        self.switch_mode()
                    else:
                        # Recreate the current mode to ensure widgets reflect role
                        self.switch_mode()
                except Exception:
                    pass

                # Rebuild menu to show/hide student options
                self.refresh_user_menu()
            else:
                messagebox.showerror("Authentication Failed", "Invalid username or password.")
        except Exception as e:
            messagebox.showerror("Error", f"Re-login failed: {e}")

    def view_my_balance(self):
        """Show the currently authenticated student's balance (student role)."""
        try:
            student_id = getattr(self, 'authenticated_user', None)
            if not student_id:
                messagebox.showinfo("My Balance", "No student account associated with this session.")
                return

            student = self.db.get_student(student_id)
            if not student:
                messagebox.showinfo("My Balance", f"Student record not found for ID: {student_id}")
                return

            balance = student.get('balance', 0.0)
            messagebox.showinfo("My Balance", f"Student: {student.get('first_name','')} {student.get('last_name','')}\nID: {student_id}\nCurrent balance: €{balance:.2f}")

            # Audit the balance consultation
            try:
                self.db.audit_balance_check(student_id, actor=getattr(self, 'authenticated_user', None))
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve balance: {e}")
    def create_access_control_widgets(self):
        """Create access control interface"""
        # Stop camera if it was running
        self.stop_camera()
        
        # Title
        ttk.Label(self.content_frame, text="Student Access Control", 
                 style='Header.TLabel').pack(pady=10)
        
        # Camera section with side panel for recognized students
        camera_frame = ttk.LabelFrame(self.content_frame, text="Camera Access", padding=15)
        camera_frame.pack(fill=tk.BOTH, pady=10, expand=True)

        # Inner container to hold camera (left) and recognized list (right)
        camera_inner = ttk.Frame(camera_frame)
        camera_inner.pack(fill=tk.BOTH, expand=True)

        # Left: camera controls + display
        camera_left = ttk.Frame(camera_inner)
        camera_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Camera controls
        camera_controls = ttk.Frame(camera_left)
        camera_controls.pack(pady=5)

        self.camera_btn = ttk.Button(camera_controls, text="Start Camera", 
                                    command=self.toggle_camera, style='Big.TButton')
        self.camera_btn.pack(side=tk.LEFT, padx=5)

        self.capture_btn = ttk.Button(camera_controls, text="Capture & Identify", 
                                     command=self.capture_and_identify, style='Big.TButton',
                                     state=tk.DISABLED)
        self.capture_btn.pack(side=tk.LEFT, padx=5)

        # (No per-student quick balance button in this trimmed UI)

        # Camera display
        self.camera_frame_widget = ttk.Label(camera_left, text="Camera feed will appear here")
        self.camera_frame_widget.pack(pady=10, fill=tk.BOTH, expand=True)

        # Right: recognized students list
        recognized_panel = ttk.LabelFrame(camera_inner, text="Recognized Students", padding=8)
        recognized_panel.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ('Name', 'ID', 'Balance', 'Time', 'Status')
        self.recognized_tree = ttk.Treeview(recognized_panel, columns=cols, show='headings', height=10)
        for c in cols:
            self.recognized_tree.heading(c, text=c)
            # set reasonable width
            if c == 'Name':
                self.recognized_tree.column(c, width=140)
            elif c == 'Time':
                self.recognized_tree.column(c, width=120)
            else:
                self.recognized_tree.column(c, width=80)

        self.recognized_tree.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        scrollbar = ttk.Scrollbar(recognized_panel, orient=tk.VERTICAL, command=self.recognized_tree.yview)
        self.recognized_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # File upload section
        file_frame = ttk.LabelFrame(self.content_frame, text="Upload Image", padding=15)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(file_frame, text="Select Image File", 
                  command=self.select_image_file, style='Big.TButton').pack(pady=5)
        
        # Results section
        self.results_frame = ttk.LabelFrame(self.content_frame, text="Access Results", padding=15)
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_label = ttk.Label(self.results_frame, text="No identification attempts yet", 
                                     font=('Arial', 12))
        self.result_label.pack(pady=20)
    
    def create_admin_widgets(self):
        """Create admin interface for student management"""
        # Stop camera if it was running
        self.stop_camera()
        
        # Title
        ttk.Label(self.content_frame, text="Student Management", 
                 style='Header.TLabel').pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add student tab
        add_tab = ttk.Frame(notebook)
        notebook.add(add_tab, text="Add Student")
        self.create_add_student_tab(add_tab)
        
        # View students tab
        view_tab = ttk.Frame(notebook)
        notebook.add(view_tab, text="View Students")
        self.create_view_students_tab(view_tab)
        
        # Manage balance tab
        balance_tab = ttk.Frame(notebook)
        notebook.add(balance_tab, text="Manage Balance")
        self.create_balance_tab(balance_tab)
    
    def create_add_student_tab(self, parent):
        """Create add student tab"""
        # Form frame
        form_frame = ttk.Frame(parent)
        form_frame.pack(padx=20, pady=20, fill=tk.X)
        
        # Student ID
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.student_id_entry = ttk.Entry(form_frame, width=30)
        self.student_id_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # First name
        ttk.Label(form_frame, text="First Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.first_name_entry = ttk.Entry(form_frame, width=30)
        self.first_name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Last name
        ttk.Label(form_frame, text="Last Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.last_name_entry = ttk.Entry(form_frame, width=30)
        self.last_name_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Initial balance
        ttk.Label(form_frame, text="Initial Balance (€):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.balance_entry = ttk.Entry(form_frame, width=30)
        self.balance_entry.insert(0, "50.0")
        self.balance_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Image selection
        ttk.Label(form_frame, text="Photo:").grid(row=4, column=0, sticky=tk.W, pady=5)
        image_buttons_frame = ttk.Frame(form_frame)
        image_buttons_frame.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        
        ttk.Button(image_buttons_frame, text="Select File", 
                  command=self.select_student_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(image_buttons_frame, text="Take Photo", 
                  command=self.take_student_photo).pack(side=tk.LEFT, padx=5)
        
        self.selected_image_path = None
        self.image_status_label = ttk.Label(form_frame, text="No image selected")
        self.image_status_label.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Add button
        ttk.Button(form_frame, text="Add Student", 
                  command=self.add_student, style='Big.TButton').grid(row=6, column=1, pady=20)
    
    def create_view_students_tab(self, parent):
        """Create view students tab"""
        # Controls frame
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(controls_frame, text="Refresh List", 
                  command=self.refresh_student_list).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="Reload Face Database", 
                  command=self.reload_face_database).pack(side=tk.LEFT, padx=5)
        
        # Student list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview for student list
        columns = ('ID', 'Name', 'Balance', 'Last Access', 'Access Count')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=150)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        
        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load initial data
        self.refresh_student_list()
    
    def create_balance_tab(self, parent):
        """Create balance management tab"""
        # Form frame
        balance_frame = ttk.Frame(parent)
        balance_frame.pack(padx=20, pady=20, fill=tk.X)
        
        # Student selection
        ttk.Label(balance_frame, text="Student ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.balance_student_id = ttk.Entry(balance_frame, width=30)
        self.balance_student_id.grid(row=0, column=1, padx=10, pady=5)
        
        # Amount
        ttk.Label(balance_frame, text="Amount (€):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.balance_amount = ttk.Entry(balance_frame, width=30)
        self.balance_amount.grid(row=1, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(balance_frame)
        button_frame.grid(row=2, column=1, pady=20, sticky=tk.W)
        
        ttk.Button(button_frame, text="Add Balance", 
                  command=self.add_balance).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Check Balance", 
                  command=self.check_balance).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.balance_status = ttk.Label(balance_frame, text="")
        self.balance_status.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if not self.camera_active:
            self.start_camera()
        else:
            self.stop_camera()
    
    def start_camera(self):
        """Start camera feed"""
        if not CV2_AVAILABLE:
            messagebox.showerror("Camera Not Available", 
                               "OpenCV (cv2) is not installed.\n" +
                               "Camera functionality is not available.\n" +
                               "Please use the 'Select Image File' option instead.")
            return
            
        try:
            self.cap = cv2.VideoCapture(0)
            # Try to reduce resolution for better performance if supported
            try:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.camera_width))
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.camera_height))
            except Exception:
                pass
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open camera")
                return
            
            self.camera_active = True
            self.camera_btn.config(text="Stop Camera")
            self.capture_btn.config(state=tk.NORMAL)
            
            # Start camera feed using Tkinter's after method (no thread needed)
            self.update_camera_feed()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {e}")
    
    def stop_camera(self):
        """Stop camera feed"""
        if self.camera_active:
            self.camera_active = False
            if hasattr(self, 'cap'):
                self.cap.release()
            # Check if widgets exist before trying to configure them
            try:
                if hasattr(self, 'camera_btn') and self.camera_btn.winfo_exists():
                    self.camera_btn.config(text="Start Camera")
                if hasattr(self, 'capture_btn') and self.capture_btn.winfo_exists():
                    self.capture_btn.config(state=tk.DISABLED)
                if hasattr(self, 'camera_frame_widget') and self.camera_frame_widget.winfo_exists():
                    self.camera_frame_widget.config(image='', text="Camera stopped")
            except tk.TclError:
                # Widgets may have been destroyed, ignore the error
                pass
    
    def update_camera_feed(self):
        """Update camera feed in GUI using scheduled callbacks instead of continuous loop"""
        if not CV2_AVAILABLE or not self.camera_active:
            return
            
        try:
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to display format
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Resize to configured camera size (faster if smaller)
                frame = cv2.resize(frame, (self.camera_width, self.camera_height))

                # Store last frame for identification (small copy)
                try:
                    self._last_frame = frame.copy()
                except Exception:
                    self._last_frame = frame

                # Convert to PhotoImage for display
                if PIL_AVAILABLE:
                    image = Image.fromarray(frame)
                    photo = ImageTk.PhotoImage(image)

                    # Update GUI in main thread
                    self.camera_frame_widget.config(image=photo, text="")
                    self.camera_frame_widget.image = photo  # Keep a reference
                else:
                    # Without PIL, just show a message
                    self.camera_frame_widget.config(text="Camera active (PIL not available for display)")
            
            # Schedule next update if camera is still active
            if self.camera_active:
                self.root.after(33, self.update_camera_feed)  # ~30 FPS (33ms)
                
        except Exception as e:
            print(f"Camera feed error: {e}")
            self.camera_active = False
    
    def capture_and_identify(self):
        """Capture current frame and identify student"""
        if not self.camera_active:
            messagebox.showwarning("Warning", "Camera is not active")
            return

        # Prevent multiple simultaneous identification runs
        if self._identifying:
            messagebox.showinfo("Info", "Identification already in progress")
            return

        # Start identification in a background thread to avoid blocking the UI
        self._identifying = True
        thread = threading.Thread(target=self._capture_and_identify_worker, daemon=True)
        thread.start()

    def _capture_and_identify_worker(self):
        """Background worker: uses the last captured frame for identification"""
        try:
            # If face recognition not available, fall back to the utility that may use its own camera
            if not FACE_RECOGNITION_AVAILABLE:
                student_id, confidence, captured_image = self.face_utils.identify_face_from_camera()
            else:
                # Use the last frame captured by update_camera_feed
                frame = None
                try:
                    frame = None if self._last_frame is None else self._last_frame.copy()
                except Exception:
                    frame = self._last_frame

                if frame is None:
                    # Nothing to identify
                    self.root.after(0, lambda: self._apply_identification_result(None, 0.0, None, "No frame available for identification"))
                    return

                # Perform encoding and identification (CPU-bound, done in background)
                encoding = self.face_utils.encode_face_from_array(frame)

                if encoding is not None:
                    student_id, confidence = self.face_utils.identify_face(encoding)
                    captured_image = frame
                else:
                    student_id, confidence, captured_image = None, 0.0, frame

            # Schedule result handling on the main thread
            self.root.after(0, lambda: self._apply_identification_result(student_id, confidence, captured_image, None))

        except Exception as e:
            self.root.after(0, lambda: self._apply_identification_result(None, 0.0, None, f"Identification error: {e}"))
        finally:
            self._identifying = False

    def _apply_identification_result(self, student_id, confidence, captured_image, error_message):
        """Apply identification result back on the GUI thread"""
        try:
            if error_message:
                messagebox.showerror("Error", error_message)
                return

            if student_id:
                # Get student info
                student = self.db.get_student(student_id)
                if student:
                    # Attempt access
                    success, message = self.db.deduct_balance(student_id)

                    if success:
                        result_text = f"✓ ACCESS GRANTED\n\n"
                        result_text += f"Student: {student['first_name']} {student['last_name']}\n"
                        result_text += f"ID: {student_id}\n"
                        result_text += f"Confidence: {confidence:.2%}\n"
                        result_text += f"{message}"
                        self.result_label.config(text=result_text, foreground='green')
                    else:
                        result_text = f"✗ ACCESS DENIED\n\n"
                        result_text += f"Student: {student['first_name']} {student['last_name']}\n"
                        result_text += f"ID: {student_id}\n"
                        result_text += f"Reason: {message}"
                        self.result_label.config(text=result_text, foreground='red')
                else:
                    self.result_label.config(text=f"✗ Student ID {student_id} not found in database", 
                                               foreground='red')
            else:
                self.result_label.config(text="✗ No face recognized or confidence too low", 
                                         foreground='red')

            # Update recognized students list
            try:
                if student_id:
                    # fetch student info if available
                    student = self.db.get_student(student_id)
                    if student:
                        name = f"{student['first_name']} {student['last_name']}"
                        balance = student.get('balance', 0.0)
                        status = 'Access Granted' if success else 'Access Denied'
                        self.add_recognized_entry(name, student_id, balance, status)
                    else:
                        self.add_recognized_entry('Unknown student', '—', None, 'Unknown')
                else:
                    # Unknown student
                    self.add_recognized_entry('Unknown student', '—', None, 'Unknown')
            except Exception:
                pass

            # Optionally overlay name on camera display for a short time
            if captured_image is not None and student_id:
                try:
                    # Draw the student's name on a copy of the frame and display it briefly
                    display = captured_image.copy()
                    # Resize to display size
                    display = cv2.resize(display, (self.camera_width, self.camera_height))
                    # Convert to PIL
                    if PIL_AVAILABLE:
                        img = Image.fromarray(display)
                        from PIL import ImageDraw, ImageFont
                        draw = ImageDraw.Draw(img)
                        try:
                            font = ImageFont.truetype("arial.ttf", 20)
                        except Exception:
                            font = None
                        text = f"{student['first_name']} {student['last_name']}"
                        draw.text((10, 10), text, fill=(255, 255, 0), font=font)
                        photo = ImageTk.PhotoImage(img)
                        self.camera_frame_widget.config(image=photo)
                        self.camera_frame_widget.image = photo
                        # Restore normal feed after a short delay
                        self.root.after(1500, lambda: None)
                except Exception:
                    pass

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply identification result: {e}")

    def add_recognized_entry(self, name: str, student_id: str, balance, status: str):
        """Add an entry to the recognized students list with timestamp."""
        try:
            from datetime import datetime
            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            bal_str = f"€{balance:.2f}" if isinstance(balance, (int, float)) else '—'
            # Insert into treeview
            try:
                self.recognized_tree.insert('', tk.END, values=(name, student_id, bal_str, ts, status))
                # Scroll to bottom
                self.recognized_tree.yview_moveto(1.0)
            except Exception:
                pass
        except Exception:
            pass
    
    def select_image_file(self):
        """Select and identify from image file"""
        file_path = filedialog.askopenfilename(
            title="Select Student Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_path:
            try:
                # Validate image
                is_valid, message = self.face_utils.validate_image_quality(file_path)
                
                if not is_valid:
                    messagebox.showwarning("Invalid Image", message)
                    return
                
                # Identify face
                student_id, confidence = self.face_utils.identify_face_from_file(file_path)
                
                if student_id:
                    # Get student info
                    student = self.db.get_student(student_id)
                    if student:
                        # Attempt access
                        success, message = self.db.deduct_balance(student_id)
                        
                        if success:
                            result_text = f"✓ ACCESS GRANTED\n\n"
                            result_text += f"Student: {student['first_name']} {student['last_name']}\n"
                            result_text += f"ID: {student_id}\n"
                            result_text += f"Confidence: {confidence:.2%}\n"
                            result_text += f"{message}"
                            self.result_label.config(text=result_text, foreground='green')
                        else:
                            result_text = f"✗ ACCESS DENIED\n\n"
                            result_text += f"Student: {student['first_name']} {student['last_name']}\n"
                            result_text += f"ID: {student_id}\n"
                            result_text += f"Reason: {message}"
                            self.result_label.config(text=result_text, foreground='red')
                    else:
                        self.result_label.config(text=f"✗ Student ID {student_id} not found in database", 
                                               foreground='red')
                else:
                    self.result_label.config(text="✗ No face recognized or confidence too low", 
                                           foreground='red')
                    
            except Exception as e:
                messagebox.showerror("Error", f"Image processing failed: {e}")
    
    def select_student_image(self):
        """Select image for new student"""
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_path:
            # Validate image
            is_valid, message = self.face_utils.validate_image_quality(file_path)
            
            if is_valid:
                self.selected_image_path = file_path
                self.image_status_label.config(text=f"✓ Image selected: {os.path.basename(file_path)}")
            else:
                messagebox.showwarning("Invalid Image", message)
                self.image_status_label.config(text="✗ Invalid image")

    # per-student quick balance UI removed; use admin 'Check Balance' in management tab instead
    
    def take_student_photo(self):
        """Take photo with camera for new student"""
        # This would open a simple camera capture dialog
        messagebox.showinfo("Feature Not Implemented", 
                           "Camera photo capture for student registration will be implemented in next version.\n" +
                           "Please use 'Select File' option for now.")
    
    def add_student(self):
        """Add new student to database"""
        try:
            # Get form data
            student_id = self.student_id_entry.get().strip()
            first_name = self.first_name_entry.get().strip()
            last_name = self.last_name_entry.get().strip()
            balance_str = self.balance_entry.get().strip()
            
            # Validate input
            if not all([student_id, first_name, last_name, balance_str]):
                messagebox.showwarning("Invalid Input", "Please fill in all fields")
                return
            
            if not self.selected_image_path:
                messagebox.showwarning("Invalid Input", "Please select a student photo")
                return
            
            try:
                balance = float(balance_str)
            except ValueError:
                messagebox.showwarning("Invalid Input", "Balance must be a valid number")
                return
            
            # Save student image
            full_name = f"{first_name} {last_name}"
            image_path = self.face_utils.save_student_image(student_id, full_name, self.selected_image_path)
            
            # Add to database
            success = self.db.add_student(student_id, first_name, last_name, image_path, balance)
            
            if success:
                # Reload face database
                self.face_utils.load_known_faces()
                
                messagebox.showinfo("Success", f"Student {full_name} added successfully!")
                
                # Clear form
                self.student_id_entry.delete(0, tk.END)
                self.first_name_entry.delete(0, tk.END)
                self.last_name_entry.delete(0, tk.END)
                self.balance_entry.delete(0, tk.END)
                self.balance_entry.insert(0, "50.0")
                self.selected_image_path = None
                self.image_status_label.config(text="No image selected")
            else:
                messagebox.showerror("Error", "Student ID already exists!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")
    
    def refresh_student_list(self):
        """Refresh the student list"""
        # Clear current items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        # Add students
        students = self.db.get_all_students()
        for student_id, student in students.items():
            last_access = student.get('last_access', 'Never')
            if last_access and last_access != 'Never':
                # Format datetime
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(last_access)
                    last_access = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            self.student_tree.insert('', tk.END, values=(
                student_id,
                f"{student['first_name']} {student['last_name']}",
                f"€{student['balance']:.2f}",
                last_access,
                student.get('access_count', 0)
            ))
    
    def reload_face_database(self):
        """Reload face recognition database"""
        try:
            count = self.face_utils.load_known_faces()
            messagebox.showinfo("Success", f"Reloaded {count} face encodings")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload face database: {e}")
    
    def add_balance(self):
        """Add balance to student account"""
        try:
            student_id = self.balance_student_id.get().strip()
            amount_str = self.balance_amount.get().strip()
            
            if not student_id or not amount_str:
                messagebox.showwarning("Invalid Input", "Please enter student ID and amount")
                return
            
            amount = float(amount_str)
            success = self.db.add_balance(student_id, amount)
            
            if success:
                student = self.db.get_student(student_id)
                self.balance_status.config(text=f"✓ Added €{amount:.2f}. New balance: €{student['balance']:.2f}")
                self.refresh_student_list()
            else:
                self.balance_status.config(text="✗ Student not found")
                
        except ValueError:
            messagebox.showwarning("Invalid Input", "Amount must be a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add balance: {e}")
    
    def check_balance(self):
        """Check student balance"""
        try:
            student_id = self.balance_student_id.get().strip()
            
            if not student_id:
                messagebox.showwarning("Invalid Input", "Please enter student ID")
                return
            
            student = self.db.get_student(student_id)
            
            if student:
                # Audit the balance check (actor = authenticated user if available)
                try:
                    self.db.audit_balance_check(student_id, actor=getattr(self, 'authenticated_user', None))
                except Exception:
                    pass

                self.balance_status.config(text=f"Current balance: €{student['balance']:.2f}")
            else:
                self.balance_status.config(text="✗ Student not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check balance: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_camera()
        self.root.destroy()

    def switch_user(self):
        """Prompt to switch user by restarting the application (simple flow)."""
        try:
            if messagebox.askyesno("Switch User", "Switching user will restart the application. Continue?"):
                self.logout_and_restart()
        except Exception:
            # Fallback: just restart
            self.logout_and_restart()

    def logout_and_restart(self):
        """Restart the application to allow login as a different user.

        This launches main.py (if present) with the same Python executable and
        exits the current process. It's a simple approach that avoids in-process
        re-auth complexity.
        """
        try:
            python = sys.executable
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_path = os.path.join(script_dir, 'main.py')
            if os.path.exists(main_path):
                subprocess.Popen([python, main_path])
            else:
                subprocess.Popen([python, os.path.abspath(__file__)])
        except Exception as e:
            print(f"Restart failed: {e}")
        finally:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass
            # Ensure process exit
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


# For testing GUI independently
if __name__ == "__main__":
    app = RestaurantAccessGUI()
    app.run()