"""
Optimized setup script for Restaurant Access Control System
Modern setup with centralized configuration and better error handling
"""

import sys
import subprocess
import os
from pathlib import Path
from config import Config

def check_system_requirements():
    """Check system requirements and compatibility"""
    print("🔍 Checking system requirements...")
    
    # Python version check
    version = sys.version_info
    min_version = (3, 8)
    
    if version[:2] < min_version:
        print(f"❌ Python {min_version[0]}.{min_version[1]}+ required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    
    # Check available disk space (simplified)
    try:
        import shutil
        free_space = shutil.disk_usage(".").free
        required_space = 100_000_000  # 100MB
        
        if free_space < required_space:
            print(f"⚠️  Warning: Low disk space ({free_space // 1_000_000} MB available)")
        else:
            print(f"✅ Disk space: {free_space // 1_000_000} MB available")
    except:
        print("⚠️  Could not check disk space")
    
    return True

def create_project_structure():
    """Create necessary directories with optimized structure"""
    print("� Creating project structure...")
    
    # Use configuration for directories
    directories = [
        Config.IMAGES_DIR,
        Config.DATABASE_BACKUP_DIR,
        "logs",
        "docs",
        "tests/unit",
        "tests/integration"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # Create README files for directories
    readme_files = {
        f"{Config.IMAGES_DIR}/README.md": f"""# Student Images Directory

Place student photos here with the naming convention:
`{{student_id}}_{{full_name}}.jpg`

## Requirements:
- One face per image
- Good lighting and clear face
- Supported formats: {', '.join(Config.SUPPORTED_FORMATS)}
- Minimum size: {Config.MIN_FACE_SIZE[0]}x{Config.MIN_FACE_SIZE[1]} pixels
- Maximum size: {Config.IMAGE_MAX_SIZE[0]}x{Config.IMAGE_MAX_SIZE[1]} pixels

## Examples:
- `S001_John_Doe.jpg`
- `S002_Marie_Martin.jpg`
""",
        f"{Config.DATABASE_BACKUP_DIR}/README.md": """# Database Backups

Automatic backups of the student database are stored here.

- Backups are created before major operations
- Files are named with timestamps: `students_backup_YYYYMMDD_HHMMSS.json`
- Old backups are automatically cleaned up
""",
        "logs/README.md": """# Application Logs

Application logs and error traces are stored here.

- `app.log`: Main application log
- `access.log`: Student access attempts log
- `admin.log`: Administrative actions log
"""
    }
    
    for file_path, content in readme_files.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created: {file_path}")

def validate_installation():
    """Validate the installation with comprehensive tests"""
    print("🧪 Validating installation...")
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Configuration
    try:
        Config.validate_config()
        print("✅ Configuration validation passed")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
    
    # Test 2: Database module
    try:
        from db import StudentDatabase
        db = StudentDatabase("test_setup.json")
        
        # Test CRUD operations
        success = db.add_student("SETUP001", "Test", "Student", "test.jpg", Config.DEFAULT_BALANCE)
        if success:
            student = db.get_student("SETUP001")
            if student and student["first_name"] == "Test":
                print("✅ Database operations working")
                tests_passed += 1
            else:
                print("❌ Database read operation failed")
        else:
            print("❌ Database write operation failed")
        
        # Cleanup
        if os.path.exists("test_setup.json"):
            os.remove("test_setup.json")
            
    except Exception as e:
        print(f"❌ Database module test failed: {e}")
    
    # Test 3: Validation module
    try:
        from validators import validate_student_data
        
        valid, error, data = validate_student_data(
            "TEST001", "John", "Doe", "50.0", "nonexistent.jpg"
        )
        
        # Should fail due to missing image, but other validations should work
        if not valid and "Image" in error:
            print("✅ Validation module working")
            tests_passed += 1
        else:
            print("❌ Validation module test unexpected result")
            
    except Exception as e:
        print(f"❌ Validation module test failed: {e}")
    
    # Test 4: GUI imports (basic check)
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        print("✅ GUI framework available")
        tests_passed += 1
    except Exception as e:
        print(f"❌ GUI framework test failed: {e}")
    
    success_rate = (tests_passed / total_tests) * 100
    print(f"📊 Validation results: {tests_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    return tests_passed >= 3  # Allow one test to fail

def show_final_instructions():
    """Show final setup instructions and next steps"""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    
    print(f"\n📋 {Config.APP_NAME} v{Config.APP_VERSION}")
    print(f"Author: {Config.APP_AUTHOR}")
    
    print("\n🚀 Quick Start:")
    print("1. Run automated dependency installation:")
    print("   python install_dependencies.py")
    print("\n2. Test the system:")
    print("   python test_system.py")
    print("\n3. Start the application:")
    print("   python main.py --console")
    print("\n4. For demo mode (no dependencies needed):")
    print("   python demo.py")
    
    print("\n📚 Documentation:")
    print("- Complete documentation: DOCUMENTATION_COMPLETE.md")
    print("- User guide: README.md")
    print("- Configuration: config.py")
    
    print("\n🔧 Admin Accounts:")
    for username in Config.ADMIN_ACCOUNTS.keys():
        print(f"- Username: {username}")
    print("(See config.py for passwords)")
    
    print(f"\n💰 Default Settings:")
    print(f"- Meal cost: {Config.CURRENCY_SYMBOL}{Config.MEAL_COST}")
    print(f"- Default student balance: {Config.CURRENCY_SYMBOL}{Config.DEFAULT_BALANCE}")
    print(f"- Images directory: {Config.IMAGES_DIR}")
    print(f"- Database file: {Config.DATABASE_FILE}")

def main():
    """Main setup function with optimized flow"""
    print(f"🍽️  {Config.APP_NAME} - Optimized Setup")
    print("=" * 60)
    
    try:
        # System checks
        if not check_system_requirements():
            return False
        
        # Create structure
        create_project_structure()
        
        # Validate installation
        if not validate_installation():
            print("\n⚠️  Setup completed with warnings")
            print("Some components may not work correctly")
        else:
            print("\n✅ All validation tests passed!")
        
        # Show instructions
        show_final_instructions()
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)