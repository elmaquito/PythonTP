"""
Facial recognition utilities for student identification
Handles face encoding, comparison, and image processing
"""

import cv2
import face_recognition
import numpy as np
import os
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageTk
import glob


class FaceRecognitionUtils:
    """Handles face recognition operations"""
    
    def __init__(self, images_directory: str = "images"):
        """
        Initialize face recognition system
        
        Args:
            images_directory: Directory containing student images
        """
        self.images_directory = images_directory
        self.known_encodings = []
        self.known_names = []
        self.tolerance = 0.6  # Face recognition tolerance (lower = more strict)
        
        # Ensure images directory exists
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)
            print(f"Created images directory: {images_directory}")
    
    def load_known_faces(self) -> int:
        """
        Load and encode all known faces from the images directory
        
        Returns:
            Number of faces loaded
        """
        self.known_encodings.clear()
        self.known_names.clear()
        
        # Supported image formats
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif']
        image_files = []
        
        for extension in extensions:
            image_files.extend(glob.glob(os.path.join(self.images_directory, extension)))
            image_files.extend(glob.glob(os.path.join(self.images_directory, extension.upper())))
        
        loaded_count = 0
        
        for image_path in image_files:
            try:
                # Extract student ID from filename (assuming format: studentid_name.jpg)
                filename = os.path.basename(image_path)
                student_id = filename.split('_')[0] if '_' in filename else filename.split('.')[0]
                
                # Load and encode the image
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    # Use the first face found in the image
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(student_id)
                    loaded_count += 1
                    print(f"Loaded face for student ID: {student_id}")
                else:
                    print(f"No face found in image: {image_path}")
                    
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
        
        print(f"Loaded {loaded_count} known faces")
        return loaded_count
    
    def encode_face_from_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Encode a single face from an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Face encoding array or None if no face found
        """
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            
            if encodings:
                return encodings[0]  # Return first face found
            else:
                print("No face detected in the image")
                return None
                
        except Exception as e:
            print(f"Error encoding face from {image_path}: {e}")
            return None
    
    def encode_face_from_array(self, image_array: np.ndarray) -> Optional[np.ndarray]:
        """
        Encode a face from a numpy array (e.g., from camera)
        
        Args:
            image_array: Image as numpy array (RGB format)
            
        Returns:
            Face encoding array or None if no face found
        """
        try:
            encodings = face_recognition.face_encodings(image_array)
            
            if encodings:
                return encodings[0]  # Return first face found
            else:
                return None
                
        except Exception as e:
            print(f"Error encoding face from array: {e}")
            return None
    
    def identify_face(self, unknown_encoding: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Identify a face by comparing it with known faces
        
        Args:
            unknown_encoding: Face encoding to identify
            
        Returns:
            Tuple of (student_id, confidence) or (None, 0.0) if no match
        """
        if not self.known_encodings:
            print("No known faces loaded. Please load faces first.")
            return None, 0.0
        
        # Compare with all known faces
        distances = face_recognition.face_distance(self.known_encodings, unknown_encoding)
        
        # Find the best match
        min_distance_index = np.argmin(distances)
        min_distance = distances[min_distance_index]
        
        # Check if the best match is within tolerance
        if min_distance <= self.tolerance:
            student_id = self.known_names[min_distance_index]
            confidence = 1.0 - min_distance  # Convert distance to confidence
            return student_id, confidence
        
        return None, 0.0
    
    def identify_face_from_camera(self) -> Tuple[Optional[str], float, Optional[np.ndarray]]:
        """
        Capture image from camera and identify face
        
        Returns:
            Tuple of (student_id, confidence, captured_image) or (None, 0.0, None) if failed
        """
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return None, 0.0, None
        
        try:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not capture frame")
                return None, 0.0, None
            
            # Convert BGR to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Encode the face
            encoding = self.encode_face_from_array(rgb_frame)
            
            if encoding is not None:
                # Identify the face
                student_id, confidence = self.identify_face(encoding)
                return student_id, confidence, rgb_frame
            else:
                print("No face detected in camera image")
                return None, 0.0, rgb_frame
                
        except Exception as e:
            print(f"Error during camera capture: {e}")
            return None, 0.0, None
        finally:
            cap.release()
    
    def identify_face_from_file(self, image_path: str) -> Tuple[Optional[str], float]:
        """
        Identify face from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (student_id, confidence) or (None, 0.0) if no match
        """
        encoding = self.encode_face_from_image(image_path)
        
        if encoding is not None:
            return self.identify_face(encoding)
        else:
            return None, 0.0
    
    def save_student_image(self, student_id: str, name: str, image_source) -> str:
        """
        Save a student's image to the images directory
        
        Args:
            student_id: Student identifier
            name: Student's full name
            image_source: Image file path or numpy array
            
        Returns:
            Path to saved image file
        """
        # Create filename: studentid_name.jpg
        safe_name = name.replace(" ", "_").replace(".", "")
        filename = f"{student_id}_{safe_name}.jpg"
        filepath = os.path.join(self.images_directory, filename)
        
        try:
            if isinstance(image_source, str):
                # Copy from existing file
                import shutil
                shutil.copy2(image_source, filepath)
            elif isinstance(image_source, np.ndarray):
                # Save numpy array as image
                # Convert RGB to BGR for OpenCV
                if len(image_source.shape) == 3:
                    bgr_image = cv2.cvtColor(image_source, cv2.COLOR_RGB2BGR)
                else:
                    bgr_image = image_source
                cv2.imwrite(filepath, bgr_image)
            else:
                raise ValueError("Unsupported image source type")
            
            print(f"Student image saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving student image: {e}")
            raise
    
    def detect_faces_in_image(self, image_path: str) -> List[Dict]:
        """
        Detect all faces in an image and return their locations
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of face dictionaries with locations and encodings
        """
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            faces = []
            for i, (location, encoding) in enumerate(zip(face_locations, face_encodings)):
                faces.append({
                    'location': location,  # (top, right, bottom, left)
                    'encoding': encoding,
                    'index': i
                })
            
            return faces
            
        except Exception as e:
            print(f"Error detecting faces in {image_path}: {e}")
            return []
    
    def validate_image_quality(self, image_path: str) -> Tuple[bool, str]:
        """
        Validate if an image is suitable for face recognition
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                return False, "Image file does not exist"
            
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Check image dimensions
            height, width = image.shape[:2]
            if height < 100 or width < 100:
                return False, "Image is too small (minimum 100x100 pixels)"
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                return False, "No faces detected in the image"
            elif len(face_locations) > 1:
                return False, "Multiple faces detected. Please use an image with only one face"
            
            # Check face size
            top, right, bottom, left = face_locations[0]
            face_height = bottom - top
            face_width = right - left
            
            if face_height < 50 or face_width < 50:
                return False, "Face is too small in the image"
            
            return True, "Image is suitable for face recognition"
            
        except Exception as e:
            return False, f"Error validating image: {e}"


# Test the face recognition utilities
if __name__ == "__main__":
    fr_utils = FaceRecognitionUtils()
    
    # Test loading known faces
    count = fr_utils.load_known_faces()
    print(f"Loaded {count} known faces")
    
    # Test image validation
    test_image = "test_image.jpg"
    if os.path.exists(test_image):
        is_valid, message = fr_utils.validate_image_quality(test_image)
        print(f"Image validation: {is_valid}, {message}")