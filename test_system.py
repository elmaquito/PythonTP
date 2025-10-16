"""
Comprehensive test script for Restaurant Access Control System
Tests all major components and functionality
"""

import sys
import os
import json
import tempfile
from pathlib import Path


class SystemTester:
    """Comprehensive system testing"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        print(f"Testing {test_name}...", end=" ")
        try:
            result = test_func()
            if result:
                print("✅ PASS")
                self.tests_passed += 1
                self.test_results.append((test_name, "PASS", None))
            else:
                print("❌ FAIL")
                self.tests_failed += 1
                self.test_results.append((test_name, "FAIL", "Test returned False"))
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.tests_failed += 1
            self.test_results.append((test_name, "ERROR", str(e)))
    
    def test_imports(self):
        """Test all critical imports"""
        try:
            # Test main imports
            import main
            from main import AdminAuthentication, check_dependencies
            
            # Test demo imports
            from demo import DemoRestaurantGUI, StudentDatabase, SimpleFaceRecognitionUtils
            
            # Test database
            from db import StudentDatabase as FullDB
            
            return True
        except Exception as e:
            print(f"Import error: {e}")
            return False
    
    def test_database(self):
        """Test database functionality"""
        try:
            from db import StudentDatabase
            
            # Create test database
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                test_db_path = f.name
            
            db = StudentDatabase(test_db_path)
            
            # Test adding student
            result1 = db.add_student("TEST001", "John", "Doe", "test.jpg", 50.0)
            if not result1:
                return False
            
            # Test getting student
            student = db.get_student("TEST001")
            if not student or student["first_name"] != "John":
                return False
            
            # Test balance operations
            success, msg = db.deduct_balance("TEST001", 4.0)
            if not success:
                return False
            
            # Check balance was deducted
            student = db.get_student("TEST001")
            if student["balance"] != 46.0:
                return False
            
            # Test insufficient balance
            db.students["TEST001"]["balance"] = 2.0
            success, msg = db.deduct_balance("TEST001", 4.0)
            if success:  # Should fail with insufficient balance
                return False
            
            # Clean up
            os.unlink(test_db_path)
            
            return True
        except Exception:
            return False
    
    def test_face_recognition_utils(self):
        """Test face recognition utilities (demo version)"""
        try:
            from demo import SimpleFaceRecognitionUtils
            
            # Create temporary images directory
            with tempfile.TemporaryDirectory() as temp_dir:
                utils = SimpleFaceRecognitionUtils(temp_dir)
                
                # Test loading (should work with empty dir)
                count = utils.load_known_faces()
                if count != 0:  # Should be 0 for empty directory
                    return False
                
                # Test image validation
                # Create a dummy file
                dummy_file = os.path.join(temp_dir, "test.jpg")
                with open(dummy_file, "w") as f:
                    f.write("dummy content" * 100)  # Make it larger than 1KB
                
                is_valid, msg = utils.validate_image_quality(dummy_file)
                if not is_valid:  # Should pass basic size check
                    return False
                
                return True
        except Exception:
            return False
    
    def test_authentication(self):
        """Test authentication system"""
        try:
            from main import AdminAuthentication
            
            auth = AdminAuthentication()
            
            # Test credential verification
            if not auth.verify_credentials("admin", "restaurant123"):
                return False
            
            if auth.verify_credentials("admin", "wrong_password"):
                return False
            
            if auth.verify_credentials("wrong_user", "restaurant123"):
                return False
            
            return True
        except Exception:
            return False
    
    def test_dependency_check(self):
        """Test dependency checking"""
        try:
            from main import check_dependencies
            
            deps_ok, missing = check_dependencies()
            
            # Should return boolean and list
            if not isinstance(deps_ok, bool) or not isinstance(missing, list):
                return False
            
            # If deps not ok, should have missing packages
            if not deps_ok and len(missing) == 0:
                return False
            
            return True
        except Exception:
            return False
    
    def test_gui_initialization(self):
        """Test GUI can be initialized without running"""
        try:
            from demo import DemoRestaurantGUI
            
            app = DemoRestaurantGUI()
            
            # Check basic attributes exist
            if not hasattr(app, 'root'):
                return False
            
            if not hasattr(app, 'db'):
                return False
            
            if not hasattr(app, 'face_utils'):
                return False
            
            # Don't actually run the GUI
            app.root.destroy()
            
            return True
        except Exception:
            return False
    
    def test_main_functionality(self):
        """Test main.py functionality without GUI"""
        try:
            import subprocess
            import sys
            
            # Test main.py in test mode
            result = subprocess.run([
                sys.executable, "main.py", "--test"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"Main.py test failed with return code {result.returncode}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
                return False
            
            # Check for expected output
            if "Authentication successful" not in result.stdout:
                return False
            
            if "GUI initialization successful" not in result.stdout:
                return False
            
            return True
        except Exception as e:
            print(f"Main functionality test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Restaurant Access Control System - Comprehensive Tests")
        print("=" * 60)
        
        # Run all tests
        self.run_test("Import Statements", self.test_imports)
        self.run_test("Database Operations", self.test_database)
        self.run_test("Face Recognition Utils", self.test_face_recognition_utils)
        self.run_test("Authentication System", self.test_authentication)
        self.run_test("Dependency Checking", self.test_dependency_check)
        self.run_test("GUI Initialization", self.test_gui_initialization)
        self.run_test("Main Application", self.test_main_functionality)
        
        # Print summary
        print("\\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        # Show detailed results for failed tests
        if self.tests_failed > 0:
            print(f"\\n❌ FAILED TESTS:")
            for name, status, error in self.test_results:
                if status in ["FAIL", "ERROR"]:
                    print(f"  - {name}: {status}")
                    if error:
                        print(f"    Error: {error}")
        
        # Overall result
        if self.tests_failed == 0:
            print(f"\\n🎉 ALL TESTS PASSED! System is ready for use.")
            return True
        else:
            print(f"\\n⚠️  Some tests failed. Check the errors above.")
            return False


def main():
    """Run comprehensive system tests"""
    tester = SystemTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)