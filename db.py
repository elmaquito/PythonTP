"""
Database module for managing student data
Handles student registration, balance management, and data persistence
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup simple audit logger
LOGGER_NAME = 'access_audit'
audit_logger = logging.getLogger(LOGGER_NAME)
if not audit_logger.handlers:
    audit_logger.setLevel(logging.INFO)
    fh = logging.FileHandler('access.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    audit_logger.addHandler(fh)


class StudentDatabase:
    """Manages student data using JSON file storage"""
    
    def __init__(self, db_file: str = "students.json"):
        """
        Initialize the database
        
        Args:
            db_file: Path to the JSON database file
        """
        self.db_file = db_file
        self.students = {}
        self.load_database()
    
    def load_database(self) -> None:
        """Load student data from JSON file"""
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
    
    def save_database(self) -> None:
        """Save student data to JSON file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.students, f, indent=4, ensure_ascii=False)
            print(f"Database saved: {len(self.students)} students")
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def add_student(self, student_id: str, first_name: str, last_name: str, 
                   image_path: str, initial_balance: float = 50.0) -> bool:
        """
        Add a new student to the database
        
        Args:
            student_id: Unique student identifier
            first_name: Student's first name
            last_name: Student's last name
            image_path: Path to student's photo
            initial_balance: Initial account balance (default 50.0)
            
        Returns:
            True if student was added successfully, False if already exists
        """
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
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """
        Get student information by ID
        
        Args:
            student_id: Student identifier
            
        Returns:
            Student data dictionary or None if not found
        """
        return self.students.get(student_id)
    
    def get_all_students(self) -> Dict:
        """Get all students data"""
        return self.students.copy()
    
    def update_balance(self, student_id: str, new_balance: float) -> bool:
        """
        Update student's balance
        
        Args:
            student_id: Student identifier
            new_balance: New balance amount
            
        Returns:
            True if updated successfully, False if student not found
        """
        if student_id not in self.students:
            return False
        
        self.students[student_id]["balance"] = new_balance
        self.save_database()
        return True
    
    def deduct_balance(self, student_id: str, amount: float = 4.0) -> Tuple[bool, str]:
        """
        Deduct amount from student's balance (for meal access)
        
        Args:
            student_id: Student identifier
            amount: Amount to deduct (default 4.0 for a meal)
            
        Returns:
            Tuple of (success, message)
        """
        if student_id not in self.students:
            # Audit: failed deduction - student not found
            audit_logger.info(f"DEDUCT_FAIL - {student_id} - reason=not_found - amount={amount}")
            return False, "Student not found"
        
        student = self.students[student_id]
        current_balance = student["balance"]
        
        if current_balance < amount:
            # Audit: insufficient balance
            audit_logger.info(f"DEDUCT_FAIL - {student_id} - reason=insufficient - current={current_balance} - amount={amount}")
            return False, f"Insufficient balance. Current: €{current_balance:.2f}, Required: €{amount:.2f}"
        
        # Deduct amount and update access info
        student["balance"] = current_balance - amount
        student["last_access"] = datetime.now().isoformat()
        student["access_count"] += 1

        self.save_database()
        # Audit: successful deduction
        audit_logger.info(f"DEDUCT_SUCCESS - {student_id} - amount={amount} - remaining={student['balance']}")
        return True, f"Access granted. Remaining balance: €{student['balance']:.2f}"
    
    def add_balance(self, student_id: str, amount: float) -> bool:
        """
        Add amount to student's balance
        
        Args:
            student_id: Student identifier
            amount: Amount to add
            
        Returns:
            True if added successfully, False if student not found
        """
        if student_id not in self.students:
            audit_logger.info(f"ADD_FAIL - {student_id} - reason=not_found - amount={amount}")
            return False
        
        self.students[student_id]["balance"] += amount
        self.save_database()
        audit_logger.info(f"ADD_SUCCESS - {student_id} - amount={amount} - new_balance={self.students[student_id]['balance']}")
        return True

    def audit_balance_check(self, student_id: str, actor: Optional[str] = None) -> None:
        """Log a balance consultation for traceability.

        Args:
            student_id: student whose balance was checked
            actor: who triggered the check (username) - optional
        """
        actor_part = f"actor={actor}" if actor else "actor=unknown"
        if student_id in self.students:
            bal = self.students[student_id].get('balance', 0.0)
            audit_logger.info(f"BALANCE_CHECK - {student_id} - {actor_part} - balance={bal}")
        else:
            audit_logger.info(f"BALANCE_CHECK_FAIL - {student_id} - {actor_part} - reason=not_found")
    
    def student_exists(self, student_id: str) -> bool:
        """Check if student exists in database"""
        return student_id in self.students
    
    def delete_student(self, student_id: str) -> bool:
        """
        Delete student from database
        
        Args:
            student_id: Student identifier
            
        Returns:
            True if deleted successfully, False if not found
        """
        if student_id not in self.students:
            return False
        
        del self.students[student_id]
        self.save_database()
        return True
    
    def get_student_stats(self) -> Dict:
        """Get database statistics"""
        if not self.students:
            return {"total_students": 0, "total_balance": 0, "avg_balance": 0}
        
        total_balance = sum(student["balance"] for student in self.students.values())
        avg_balance = total_balance / len(self.students)
        
        return {
            "total_students": len(self.students),
            "total_balance": total_balance,
            "avg_balance": avg_balance
        }


# Test the database functionality
if __name__ == "__main__":
    db = StudentDatabase("test_students.json")
    
    # Add test students
    db.add_student("12345", "Jean", "Dupont", "images/jean_dupont.jpg", 25.0)
    db.add_student("12346", "Marie", "Martin", "images/marie_martin.jpg", 30.0)
    
    # Test balance operations
    success, msg = db.deduct_balance("12345", 4.0)
    print(f"Deduct balance: {success}, {msg}")
    
    # Display stats
    stats = db.get_student_stats()
    print(f"Database stats: {stats}")