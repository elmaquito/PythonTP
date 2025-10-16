"""
Setup script for Restaurant Access Control System
Helps with installation and dependency management
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True


def install_requirements():
    """Install required packages"""
    print("\\n📦 Installing required packages...")
    
    try:
        # Try to install with specific versions that are more likely to work on Windows
        windows_requirements = [
            "numpy==1.21.6",
            "opencv-python==4.5.5.64", 
            "Pillow==9.5.0",
            "glob2==0.7"
        ]
        
        for package in windows_requirements:
            print(f"Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️  Warning: Could not install {package}")
                print(result.stderr)
            else:
                print(f"✅ Installed {package}")
        
        # Try to install face recognition packages (these might fail on Windows)
        advanced_packages = ["cmake", "dlib", "face-recognition"]
        
        print("\\n🔄 Attempting to install face recognition packages...")
        print("Note: These may fail on Windows without proper C++ build tools")
        
        for package in advanced_packages:
            print(f"Trying to install {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️  Could not install {package} - using demo mode instead")
            else:
                print(f"✅ Installed {package}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False


def create_sample_data():
    """Create sample data and directory structure"""
    print("\\n📁 Creating sample data...")
    
    # Ensure directories exist
    directories = ["images", "docs/screenshots", "tests"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create a simple test image placeholder
    if not os.path.exists("images/README.txt"):
        with open("images/README.txt", "w") as f:
            f.write("""Student Images Directory
======================

Place student photos here with the naming convention:
{student_id}_{first_name}_{last_name}.jpg

Examples:
- 20240001_Jean_Dupont.jpg
- 20240002_Marie_Martin.jpg

Requirements:
- One face per image
- Good lighting
- JPG, PNG, or similar format
- Minimum 100x100 pixels
""")
        print("✅ Created images directory instructions")


def test_basic_functionality():
    """Test basic functionality"""
    print("\\n🧪 Testing basic functionality...")
    
    try:
        # Test database module
        from db import StudentDatabase
        db = StudentDatabase("test_setup.json")
        db.add_student("TEST001", "Test", "Student", "test.jpg", 25.0)
        
        student = db.get_student("TEST001")
        if student and student["first_name"] == "Test":
            print("✅ Database module working")
        else:
            print("❌ Database module test failed")
            return False
        
        # Clean up test file
        if os.path.exists("test_setup.json"):
            os.remove("test_setup.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🍽️  Restaurant Access Control System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        print("⚠️  Some packages failed to install, but basic functionality may still work")
    
    # Create sample data
    create_sample_data()
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\\n❌ Setup completed with errors")
        return False
    
    print("\\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\\n📋 Next steps:")
    print("1. Run 'python demo.py' to test the demo version")
    print("2. If face recognition packages installed successfully:")
    print("   Run 'python main.py' for the full version")
    print("3. Add student photos to the 'images' directory")
    print("4. Read README.md for detailed instructions")
    
    # Check if face recognition is available
    try:
        import face_recognition
        print("\\n🎉 Face recognition is available - full functionality enabled!")
    except ImportError:
        print("\\n⚠️  Face recognition not available - using demo mode")
        print("   This is normal on Windows without C++ build tools")
        print("   The demo version fully demonstrates the application structure")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)