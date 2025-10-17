"""
Utilities for input validation and data sanitization
Centralizes all validation logic with configuration-based rules
"""

import re
import os
from typing import Tuple, Optional
from config import active_config as Config

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class InputValidator:
    """Centralized input validation for the application"""
    
    @staticmethod
    def validate_student_id(student_id: str) -> Tuple[bool, str]:
        """
        Validate student ID format and uniqueness
        
        Args:
            student_id: Student identifier to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not student_id or not student_id.strip():
            return False, "Student ID cannot be empty"
        
        student_id = student_id.strip()
        
        # Length check
        if len(student_id) < 3 or len(student_id) > 20:
            return False, "Student ID must be between 3 and 20 characters"
        
        # Character validation: alphanumeric only
        if not re.match(r'^[a-zA-Z0-9]+$', student_id):
            return False, "Student ID can only contain letters and numbers"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
        """
        Validate first/last name fields
        
        Args:
            name: Name to validate
            field_name: Field name for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, f"{field_name} cannot be empty"
        
        name = name.strip()
        
        # Length check
        if len(name) < 2 or len(name) > 50:
            return False, f"{field_name} must be between 2 and 50 characters"
        
        # Character validation: letters, spaces, hyphens, accents
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$', name):
            return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, ""
    
    @staticmethod
    def validate_balance(balance_str: str) -> Tuple[bool, str, float]:
        """
        Validate and parse balance amount
        
        Args:
            balance_str: Balance as string
            
        Returns:
            Tuple of (is_valid, error_message, parsed_value)
        """
        if not balance_str or not balance_str.strip():
            return False, "Balance cannot be empty", 0.0
        
        try:
            balance = float(balance_str.strip())
        except ValueError:
            return False, "Balance must be a valid number", 0.0
        
        if balance < 0:
            return False, "Balance cannot be negative", 0.0
        
        if balance > 1000:  # Reasonable upper limit
            return False, "Balance cannot exceed €1000", 0.0
        
        return True, "", balance
    
    @staticmethod
    def validate_image_file(image_path: str) -> Tuple[bool, str]:
        """
        Validate image file for student photo
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not image_path or not image_path.strip():
            return False, "Please select an image file"
        
        if not os.path.exists(image_path):
            return False, "Image file does not exist"
        
        # Check file extension
        _, ext = os.path.splitext(image_path.lower())
        if ext not in Config.SUPPORTED_FORMATS:
            supported = ", ".join(Config.SUPPORTED_FORMATS)
            return False, f"Unsupported format. Supported: {supported}"
        
        # Check file size (basic)
        try:
            file_size = os.path.getsize(image_path)
            if file_size < 1000:  # Less than 1KB
                return False, "Image file too small (minimum 1KB)"
            
            if file_size > 10_000_000:  # More than 10MB
                return False, "Image file too large (maximum 10MB)"
        except OSError:
            return False, "Cannot read image file"
        
        # Advanced validation if PIL available
        if PIL_AVAILABLE:
            try:
                with Image.open(image_path) as img:
                    # Check dimensions
                    width, height = img.size
                    min_width, min_height = Config.MIN_FACE_SIZE
                    
                    if width < min_width or height < min_height:
                        return False, f"Image too small (minimum {min_width}x{min_height})"
                    
                    # Check if it's a valid image format
                    if img.format not in ['JPEG', 'PNG', 'BMP']:
                        return False, "Invalid image format"
                        
            except Exception as e:
                return False, f"Invalid image file: {str(e)}"
        
        return True, ""

class DataSanitizer:
    """Sanitizes and normalizes input data"""
    
    @staticmethod
    def sanitize_student_id(student_id: str) -> str:
        """Normalize student ID"""
        return student_id.strip().upper() if student_id else ""
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """Normalize name (title case, clean whitespace)"""
        if not name:
            return ""
        
        # Clean whitespace and normalize
        name = " ".join(name.strip().split())
        
        # Title case for each word
        return " ".join(word.capitalize() for word in name.split())
    
    @staticmethod
    def sanitize_balance(balance: float) -> float:
        """Round balance to 2 decimal places"""
        return round(balance, 2)

class SecurityValidator:
    """Security-related validation"""
    
    @staticmethod
    def validate_admin_credentials(username: str, password: str) -> Tuple[bool, str]:
        """
        Validate admin login credentials
        
        Args:
            username: Admin username
            password: Admin password
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or not username.strip():
            return False, "Username cannot be empty"
        
        if not password:
            return False, "Password cannot be empty"
        
        username = username.strip().lower()
        
        # Check against configured accounts
        if username not in Config.ADMIN_ACCOUNTS:
            return False, "Invalid credentials"
        
        if Config.ADMIN_ACCOUNTS[username] != password:
            return False, "Invalid credentials"
        
        return True, ""
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe (no path traversal, etc.)"""
        if not filename:
            return False
        
        # No path separators or dangerous characters
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        return not any(char in filename for char in dangerous_chars)

# Utility functions for common validation patterns
def validate_student_data(student_id: str, first_name: str, last_name: str, 
                         balance_str: str, image_path: str) -> Tuple[bool, str, dict]:
    """
    Comprehensive validation for student data
    
    Returns:
        Tuple of (is_valid, error_message, sanitized_data)
    """
    errors = []
    sanitized_data = {}
    
    # Validate and sanitize each field
    valid_id, id_error = InputValidator.validate_student_id(student_id)
    if not valid_id:
        errors.append(f"ID: {id_error}")
    else:
        sanitized_data['student_id'] = DataSanitizer.sanitize_student_id(student_id)
    
    valid_first, first_error = InputValidator.validate_name(first_name, "First name")
    if not valid_first:
        errors.append(f"First name: {first_error}")
    else:
        sanitized_data['first_name'] = DataSanitizer.sanitize_name(first_name)
    
    valid_last, last_error = InputValidator.validate_name(last_name, "Last name")
    if not valid_last:
        errors.append(f"Last name: {last_error}")
    else:
        sanitized_data['last_name'] = DataSanitizer.sanitize_name(last_name)
    
    valid_balance, balance_error, balance_value = InputValidator.validate_balance(balance_str)
    if not valid_balance:
        errors.append(f"Balance: {balance_error}")
    else:
        sanitized_data['balance'] = DataSanitizer.sanitize_balance(balance_value)
    
    valid_image, image_error = InputValidator.validate_image_file(image_path)
    if not valid_image:
        errors.append(f"Image: {image_error}")
    else:
        sanitized_data['image_path'] = image_path
    
    if errors:
        return False, "; ".join(errors), {}
    
    return True, "", sanitized_data

# Export main classes and functions
__all__ = [
    'InputValidator', 
    'DataSanitizer', 
    'SecurityValidator', 
    'validate_student_data'
]