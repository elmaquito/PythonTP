"""
Simple demo version for testing without face recognition dependencies
This version demonstrates the application structure and GUI functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from datetime import datetime


class SimpleFaceRecognitionUtils:
    """Simplified face recognition simulator for demo purposes"""
    
    def __init__(self, images_directory="images"):
        self.images_directory = images_directory
        self.known_names = []
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)
    
    def load_known_faces(self):
        """Simulate loading faces from images directory"""
        image_files = []
        extensions = ['*.jpg', '*.jpeg', '*.png']
        
        import glob
        for ext in extensions:
            image_files.extend(glob.glob(os.path.join(self.images_directory, ext)))
        
        self.known_names = []
        for image_path in image_files:
            filename = os.path.basename(image_path)
            student_id = filename.split('_')[0] if '_' in filename else filename.split('.')[0]
            self.known_names.append(student_id)
        
        print(f"Demo: Loaded {len(self.known_names)} known faces")
        return len(self.known_names)
    
    def validate_image_quality(self, image_path):
        """Simulate image validation"""
        if not os.path.exists(image_path):
            return False, "Image file does not exist"
        
        # Simple validation - check file size
        try:
            size = os.path.getsize(image_path)
            if size < 1000:  # Less than 1KB
                return False, "Image file too small"
            return True, "Image is suitable (demo mode)"
        except:
            return False, "Error reading image file"
    
    def identify_face_from_file(self, image_path):
        """Simulate face identification from file"""
        # In demo mode, we'll simulate recognition by checking if filename contains a known student ID
        filename = os.path.basename(image_path)
        
        # Simple simulation: if the filename starts with a known student ID, recognize it
        for student_id in self.known_names:
            if filename.startswith(student_id):
                return student_id, 0.85  # Return 85% confidence
        
        # If no match found, simulate random recognition for demo
        if self.known_names:
            import random
            if random.random() > 0.3:  # 70% chance of recognition
                return random.choice(self.known_names), 0.75
        
        return None, 0.0
    
    def identify_face_from_camera(self):
        """Simulate camera recognition"""
        # In demo mode, simulate camera not available
        messagebox.showinfo("Demo Mode", 
                           "Camera recognition is simulated in demo mode.\n" +
                           "In real implementation, this would use live camera feed.")
        
        # Simulate recognition of first known student if any
        if self.known_names:
            return self.known_names[0], 0.80, None
        return None, 0.0, None
    
    def save_student_image(self, student_id, name, image_source):
        """Simulate saving student image"""
        safe_name = name.replace(" ", "_").replace(".", "")
        filename = f"{student_id}_{safe_name}.jpg"
        filepath = os.path.join(self.images_directory, filename)
        
        if isinstance(image_source, str) and os.path.exists(image_source):
            # Copy the file
            import shutil
            shutil.copy2(image_source, filepath)
            print(f"Demo: Student image saved: {filepath}")
            return filepath
        else:
            raise ValueError("Demo mode: Please provide a valid image file path")


class StudentDatabase:
    """Student database management using JSON"""
    
    def __init__(self, db_file="students.json"):
        self.db_file = db_file
        self.students = {}
        self.load_database()
    
    def load_database(self):
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.students = json.load(f)
                print(f"Database loaded: {len(self.students)} students")
            else:
                print("No existing database found. Creating new one.")
                self.students = {}
        except Exception as e:
            print(f"Error loading database: {e}")
            self.students = {}
    
    def save_database(self):
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.students, f, indent=4, ensure_ascii=False)
            print(f"Database saved: {len(self.students)} students")
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def add_student(self, student_id, first_name, last_name, image_path, initial_balance=50.0):
        if student_id in self.students:
            print(f"Student {student_id} already exists!")
            return False
        
        self.students[student_id] = {
            "first_name": first_name,
            "last_name": last_name,
            "image_path": image_path,
            "balance": initial_balance,
            "created_date": datetime.now().isoformat(),
            "last_access": None,
            "access_count": 0
        }
        
        self.save_database()
        print(f"Student {first_name} {last_name} (ID: {student_id}) added successfully")
        return True
    
    def get_student(self, student_id):
        return self.students.get(student_id)
    
    def get_all_students(self):
        return self.students.copy()
    
    def deduct_balance(self, student_id, amount=4.0):
        if student_id not in self.students:
            return False, "Student not found"
        
        student = self.students[student_id]
        current_balance = student["balance"]
        
        if current_balance < amount:
            return False, f"Insufficient balance. Current: €{current_balance:.2f}, Required: €{amount:.2f}"
        
        student["balance"] = current_balance - amount
        student["last_access"] = datetime.now().isoformat()
        student["access_count"] += 1
        
        self.save_database()
        return True, f"Access granted. Remaining balance: €{student['balance']:.2f}"
    
    def add_balance(self, student_id, amount):
        if student_id not in self.students:
            return False
        
        self.students[student_id]["balance"] += amount
        self.save_database()
        return True


class DemoRestaurantGUI:
    """Demo version of the Restaurant Access Control GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Restaurant Access Control System - DEMO VERSION")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize components
        self.db = StudentDatabase()
        self.face_utils = SimpleFaceRecognitionUtils()
        self.face_utils.load_known_faces()
        
        # GUI state
        self.current_mode = tk.StringVar(value="access")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Title with demo notice
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=10)
        
        tk.Label(title_frame, text="Restaurant Access Control System", 
                font=('Arial', 16, 'bold'), bg='#f0f0f0').pack()
        tk.Label(title_frame, text="DEMO VERSION - Face Recognition Simulated", 
                font=('Arial', 10), fg='red', bg='#f0f0f0').pack()
        
        # Mode selection
        mode_frame = tk.Frame(self.root, bg='#f0f0f0')
        mode_frame.pack(pady=10)
        
        tk.Label(mode_frame, text="Mode:", font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(mode_frame, text="Access Control", variable=self.current_mode, 
                      value="access", command=self.switch_mode, bg='#f0f0f0').pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Student Management", variable=self.current_mode, 
                      value="admin", command=self.switch_mode, bg='#f0f0f0').pack(side=tk.LEFT, padx=10)
        
        # Content frame
        self.content_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.switch_mode()
    
    def switch_mode(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if self.current_mode.get() == "access":
            self.create_access_widgets()
        else:
            self.create_admin_widgets()
    
    def create_access_widgets(self):
        tk.Label(self.content_frame, text="Student Access Control", 
                font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        # Demo buttons
        button_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Simulate Camera Recognition", 
                 command=self.simulate_camera, font=('Arial', 12), 
                 bg='#4CAF50', fg='white', pady=10, padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Select Image File", 
                 command=self.select_image_file, font=('Arial', 12), 
                 bg='#2196F3', fg='white', pady=10, padx=20).pack(side=tk.LEFT, padx=10)
        
        # Results area
        self.result_text = tk.Text(self.content_frame, height=15, width=80, font=('Arial', 10))
        self.result_text.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = """DEMO MODE INSTRUCTIONS:

1. First add some students in 'Student Management' mode
2. Use 'Simulate Camera Recognition' to test access control
3. Use 'Select Image File' to test file-based recognition
4. The system will simulate face recognition results

Note: In the full version, this would use real facial recognition with camera."""
        
        self.result_text.insert(tk.END, instructions)
    
    def create_admin_widgets(self):
        tk.Label(self.content_frame, text="Student Management", 
                font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        # Student form
        form_frame = tk.LabelFrame(self.content_frame, text="Add New Student", bg='#f0f0f0')
        form_frame.pack(fill=tk.X, pady=10)
        
        # Form fields
        fields_frame = tk.Frame(form_frame, bg='#f0f0f0')
        fields_frame.pack(padx=20, pady=10)
        
        tk.Label(fields_frame, text="Student ID:", bg='#f0f0f0').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.student_id_entry = tk.Entry(fields_frame, width=30)
        self.student_id_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(fields_frame, text="First Name:", bg='#f0f0f0').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.first_name_entry = tk.Entry(fields_frame, width=30)
        self.first_name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(fields_frame, text="Last Name:", bg='#f0f0f0').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.last_name_entry = tk.Entry(fields_frame, width=30)
        self.last_name_entry.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(fields_frame, text="Initial Balance (€):", bg='#f0f0f0').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.balance_entry = tk.Entry(fields_frame, width=30)
        self.balance_entry.insert(0, "50.0")
        self.balance_entry.grid(row=3, column=1, padx=10, pady=5)
        
        # Image selection
        tk.Label(fields_frame, text="Photo:", bg='#f0f0f0').grid(row=4, column=0, sticky=tk.W, pady=5)
        tk.Button(fields_frame, text="Select Image File", 
                 command=self.select_student_image).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        self.selected_image_path = None
        self.image_status = tk.Label(fields_frame, text="No image selected", bg='#f0f0f0')
        self.image_status.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Add student button
        tk.Button(fields_frame, text="Add Student", command=self.add_student,
                 font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white', 
                 pady=10, padx=20).grid(row=6, column=1, pady=20)
        
        # Student list
        list_frame = tk.LabelFrame(self.content_frame, text="Current Students", bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for student list
        columns = ('ID', 'Name', 'Balance', 'Access Count')
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=150)
        
        self.student_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh button
        tk.Button(list_frame, text="Refresh List", command=self.refresh_student_list,
                 bg='#2196F3', fg='white').pack(pady=5)
        
        self.refresh_student_list()
    
    def simulate_camera(self):
        student_id, confidence, _ = self.face_utils.identify_face_from_camera()
        
        if student_id:
            student = self.db.get_student(student_id)
            if student:
                success, message = self.db.deduct_balance(student_id)
                
                result = f"\\n{'='*50}\\n"
                result += f"CAMERA RECOGNITION RESULT (SIMULATED)\\n"
                result += f"{'='*50}\\n"
                result += f"Student: {student['first_name']} {student['last_name']}\\n"
                result += f"ID: {student_id}\\n"
                result += f"Confidence: {confidence:.2%}\\n"
                
                if success:
                    result += f"✓ ACCESS GRANTED\\n{message}\\n"
                else:
                    result += f"✗ ACCESS DENIED\\n{message}\\n"
            else:
                result = f"\\n✗ Student ID {student_id} not found in database\\n"
        else:
            result = f"\\n✗ No face recognized (simulated)\\n"
        
        self.result_text.insert(tk.END, result)
        self.result_text.see(tk.END)
    
    def select_image_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Student Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_path:
            is_valid, message = self.face_utils.validate_image_quality(file_path)
            
            if not is_valid:
                messagebox.showwarning("Invalid Image", message)
                return
            
            student_id, confidence = self.face_utils.identify_face_from_file(file_path)
            
            result = f"\\n{'='*50}\\n"
            result += f"FILE RECOGNITION RESULT\\n"
            result += f"File: {os.path.basename(file_path)}\\n"
            result += f"{'='*50}\\n"
            
            if student_id:
                student = self.db.get_student(student_id)
                if student:
                    success, message = self.db.deduct_balance(student_id)
                    
                    result += f"Student: {student['first_name']} {student['last_name']}\\n"
                    result += f"ID: {student_id}\\n"
                    result += f"Confidence: {confidence:.2%}\\n"
                    
                    if success:
                        result += f"✓ ACCESS GRANTED\\n{message}\\n"
                    else:
                        result += f"✗ ACCESS DENIED\\n{message}\\n"
                else:
                    result += f"✗ Student ID {student_id} not found in database\\n"
            else:
                result += f"✗ No face recognized in image\\n"
            
            self.result_text.insert(tk.END, result)
            self.result_text.see(tk.END)
    
    def select_student_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Student Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        
        if file_path:
            is_valid, message = self.face_utils.validate_image_quality(file_path)
            
            if is_valid:
                self.selected_image_path = file_path
                self.image_status.config(text=f"✓ {os.path.basename(file_path)}")
            else:
                messagebox.showwarning("Invalid Image", message)
                self.image_status.config(text="✗ Invalid image")
    
    def add_student(self):
        try:
            student_id = self.student_id_entry.get().strip()
            first_name = self.first_name_entry.get().strip()
            last_name = self.last_name_entry.get().strip()
            balance_str = self.balance_entry.get().strip()
            
            if not all([student_id, first_name, last_name, balance_str]):
                messagebox.showwarning("Invalid Input", "Please fill in all fields")
                return
            
            if not self.selected_image_path:
                messagebox.showwarning("Invalid Input", "Please select a student photo")
                return
            
            balance = float(balance_str)
            
            # Save student image
            full_name = f"{first_name} {last_name}"
            image_path = self.face_utils.save_student_image(student_id, full_name, self.selected_image_path)
            
            # Add to database
            success = self.db.add_student(student_id, first_name, last_name, image_path, balance)
            
            if success:
                self.face_utils.load_known_faces()
                messagebox.showinfo("Success", f"Student {full_name} added successfully!")
                
                # Clear form
                self.student_id_entry.delete(0, tk.END)
                self.first_name_entry.delete(0, tk.END)
                self.last_name_entry.delete(0, tk.END)
                self.balance_entry.delete(0, tk.END)
                self.balance_entry.insert(0, "50.0")
                self.selected_image_path = None
                self.image_status.config(text="No image selected")
                
                self.refresh_student_list()
            else:
                messagebox.showerror("Error", "Student ID already exists!")
                
        except ValueError:
            messagebox.showwarning("Invalid Input", "Balance must be a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")
    
    def refresh_student_list(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        students = self.db.get_all_students()
        for student_id, student in students.items():
            self.student_tree.insert('', tk.END, values=(
                student_id,
                f"{student['first_name']} {student['last_name']}",
                f"€{student['balance']:.2f}",
                student.get('access_count', 0)
            ))
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("Starting Restaurant Access Control System - Demo Version")
    print("Note: This demo version simulates face recognition functionality")
    
    app = DemoRestaurantGUI()
    app.run()