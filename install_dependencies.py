#!/usr/bin/env python3
"""
Installation script for Restaurant Access Control System dependencies
Handles the specific order and Windows compatibility requirements
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    """Main installation process"""
    print("Restaurant Access Control System - Dependency Installer")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("⚠️  Warning: Python 3.8+ is recommended for best compatibility")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("Failed to upgrade pip, continuing anyway...")
    
    # Install dependencies in specific order
    dependencies = [
        ("numpy==1.24.3", "Installing NumPy (mathematical operations)"),
        ("Pillow==10.0.1", "Installing Pillow (image processing)"),
        ("opencv-python==4.8.1.78", "Installing OpenCV (computer vision)"),
        ("dlib-binary==19.24.1", "Installing dlib-binary (machine learning toolkit)"),
        ("face-recognition-models==0.3.0", "Installing face recognition models"),
        ("Click==8.3.0", "Installing Click (command line interface)"),
        ("face-recognition==1.3.0 --no-deps", "Installing face-recognition (facial recognition library)")
    ]
    
    failed_packages = []
    
    for package, description in dependencies:
        if not run_command(f"pip install {package}", description):
            failed_packages.append(package.split('==')[0])  # Store package name only
    
    # Test imports
    print("\n" + "=" * 60)
    print("Testing installed packages...")
    
    test_imports = [
        ("numpy", "import numpy; print(f'NumPy version: {numpy.__version__}')"),
        ("PIL", "from PIL import Image; print('Pillow: OK')"),
        ("cv2", "import cv2; print(f'OpenCV version: {cv2.__version__}')"),
        ("dlib", "import dlib; print('dlib: OK')"),
        ("face_recognition", "import face_recognition; print('face_recognition: OK')")
    ]
    
    working_packages = []
    broken_packages = []
    
    for package_name, test_code in test_imports:
        try:
            exec(test_code)
            working_packages.append(package_name)
            print(f"✓ {package_name}")
        except Exception as e:
            broken_packages.append(package_name)
            print(f"✗ {package_name}: {e}")
    
    # Final report
    print("\n" + "=" * 60)
    print("INSTALLATION REPORT")
    print("=" * 60)
    
    if working_packages:
        print("✓ Working packages:")
        for pkg in working_packages:
            print(f"  - {pkg}")
    
    if broken_packages:
        print("\n✗ Failed packages:")
        for pkg in broken_packages:
            print(f"  - {pkg}")
        
        print("\nTroubleshooting:")
        if "dlib" in broken_packages:
            print("- For dlib issues on Windows:")
            print("  1. Try: pip install cmake")
            print("  2. Then: pip install dlib")
            print("  3. Or install Visual Studio Build Tools")
        
        if "cv2" in broken_packages:
            print("- For OpenCV issues:")
            print("  1. Try: pip uninstall opencv-python")
            print("  2. Then: pip install opencv-python-headless")
    
    if not broken_packages:
        print("\n🎉 All dependencies installed successfully!")
        print("You can now run the application with: python main.py")
    else:
        print(f"\n⚠️  {len(broken_packages)} packages failed to install properly.")
        print("The application may run in demo mode without face recognition.")
    
    print("\nNote: The application has fallback modes and will work even if")
    print("some packages are missing, but full functionality requires all packages.")

if __name__ == "__main__":
    main()