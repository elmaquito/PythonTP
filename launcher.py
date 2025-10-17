"""
Simple launcher for Restaurant Access Control System
Automatically chooses the best version available
"""

import sys
import subprocess
import os


def main():
    """Launch the restaurant access control system"""
    print("🍽️  Restaurant Access Control System Launcher")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    venv_python = None
    if os.path.exists(".venv/Scripts/python.exe"):
        venv_python = ".venv/Scripts/python.exe"
        print("✅ Virtual environment detected")
    elif os.path.exists(".venv/bin/python"):
        venv_python = ".venv/bin/python"
        print("✅ Virtual environment detected")
    
    # Choose Python executable
    python_cmd = venv_python if venv_python else sys.executable
    
    print(f"Using Python: {python_cmd}")
    print()
    
    # Show options
    print("Choose version to launch:")
    print("1. Main Application (GUI authentication)")
    print("2. Main Application (console authentication)")
    print("3. Demo Version (quick start)")
    print("4. Exit")
    
    while True:
        choice = input("\\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\\n🚀 Starting main application with GUI authentication...")
            try:
                if venv_python:
                    subprocess.run([venv_python, "main.py"])
                else:
                    subprocess.run([python_cmd, "main.py"])
            except KeyboardInterrupt:
                print("\\n❌ Application interrupted by user")
            except Exception as e:
                print(f"\\n❌ Error starting application: {e}")
            break
            
        elif choice == '2':
            print("\\n🚀 Starting main application with console authentication...")
            try:
                if venv_python:
                    subprocess.run([venv_python, "main.py", "--console"])
                else:
                    subprocess.run([python_cmd, "main.py", "--console"])
            except KeyboardInterrupt:
                print("\\n❌ Application interrupted by user")
            except Exception as e:
                print(f"\\n❌ Error starting application: {e}")
            break
            
        elif choice == '3':
            print("\\n🚀 Starting demo version...")
            try:
                if venv_python:
                    subprocess.run([venv_python, "demo.py"])
                else:
                    subprocess.run([python_cmd, "demo.py"])
            except KeyboardInterrupt:
                print("\\n❌ Application interrupted by user")
            except Exception as e:
                print(f"\\n❌ Error starting demo: {e}")
            break
            
        elif choice == '4':
            print("\\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\\n\\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")
        sys.exit(1)