#!/usr/bin/env python3
"""
Deployment preparation script for Restaurant Access Control System
Prepares the system for production deployment
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from config import active_config as Config

class DeploymentManager:
    """Handles deployment preparation tasks"""
    
    def __init__(self):
        self.deployment_dir = "deployment"
        self.package_name = f"restaurant_access_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.report = []
    
    def log(self, message: str):
        """Log deployment activities"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.report.append(log_entry)
    
    def create_deployment_structure(self):
        """Create deployment directory structure"""
        self.log("Creating deployment structure...")
        
        # Clean existing deployment directory
        if os.path.exists(self.deployment_dir):
            shutil.rmtree(self.deployment_dir)
        
        # Create main deployment directory
        os.makedirs(self.deployment_dir, exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "src",
            "data",
            "docs",
            "scripts",
            "config"
        ]
        
        for subdir in subdirs:
            os.makedirs(os.path.join(self.deployment_dir, subdir), exist_ok=True)
        
        self.log(f"Created deployment directory: {self.deployment_dir}")
    
    def copy_source_files(self):
        """Copy source code files for deployment"""
        self.log("Copying source files...")
        
        src_dir = os.path.join(self.deployment_dir, "src")
        
        # Core application files
        core_files = [
            "main.py",
            "face_recognition_app.py",
            "config.py",
            "validators.py",
            "setup.py"
        ]
        
        for file in core_files:
            if os.path.exists(file):
                shutil.copy2(file, src_dir)
                self.log(f"Copied: {file}")
            else:
                self.log(f"Warning: {file} not found")
        
        # Copy utility scripts
        scripts_dir = os.path.join(self.deployment_dir, "scripts")
        utility_files = [
            "maintenance.py"
        ]
        
        for file in utility_files:
            if os.path.exists(file):
                shutil.copy2(file, scripts_dir)
                self.log(f"Copied utility: {file}")
    
    def copy_documentation(self):
        """Copy documentation files"""
        self.log("Copying documentation...")
        
        docs_dir = os.path.join(self.deployment_dir, "docs")
        
        # Documentation files
        doc_files = [
            "README.md",
            "DOCUMENTATION_COMPLETE.md"
        ]
        
        for file in doc_files:
            if os.path.exists(file):
                shutil.copy2(file, docs_dir)
                self.log(f"Copied documentation: {file}")
    
    def prepare_configuration(self):
        """Prepare deployment configuration"""
        self.log("Preparing deployment configuration...")
        
        config_dir = os.path.join(self.deployment_dir, "config")
        
        # Create deployment configuration
        deployment_config = {
            "deployment_info": {
                "version": "1.0.0",
                "build_date": datetime.now().isoformat(),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "dependencies": [
                    "opencv-python>=4.8.0",
                    "face-recognition>=1.3.0",
                    "dlib-binary>=19.24.0",
                    "numpy>=1.24.0",
                    "Pillow>=10.0.0"
                ]
            },
            "production_settings": {
                "debug_mode": False,
                "log_level": "INFO",
                "auto_backup": True,
                "backup_interval_hours": 24,
                "max_log_size_mb": 10,
                "camera_timeout": 30,
                "recognition_confidence": 0.6
            },
            "directories": {
                "data": "data",
                "images": "data/images", 
                "logs": "data/logs",
                "backups": "data/backups"
            }
        }
        
        # Save deployment configuration
        with open(os.path.join(config_dir, "deployment_config.json"), 'w', encoding='utf-8') as f:
            json.dump(deployment_config, f, indent=2, ensure_ascii=False)
        
        self.log("Created deployment configuration")
    
    def create_installation_script(self):
        """Create installation script for deployment"""
        self.log("Creating installation script...")
        
        install_script = '''#!/usr/bin/env python3
"""
Installation script for Restaurant Access Control System
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    dependencies = [
        "opencv-python>=4.8.0",
        "face-recognition>=1.3.0", 
        "dlib-binary>=19.24.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                          check=True, capture_output=True)
            print(f"✅ Installed: {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

def create_directory_structure():
    """Create required directories"""
    print("📁 Creating directory structure...")
    
    directories = [
        "data",
        "data/images",
        "data/logs", 
        "data/backups"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

def setup_initial_data():
    """Setup initial data files"""
    print("🗄️  Setting up initial data...")
    
    # Create empty database if it doesn't exist
    db_file = "data/students.json"
    if not os.path.exists(db_file):
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"✅ Created database: {db_file}")
    
    # Create images README
    images_readme = "data/images/README.md"
    if not os.path.exists(images_readme):
        with open(images_readme, 'w', encoding='utf-8') as f:
            f.write("# Student Images\\n\\nThis directory contains student profile images for face recognition.\\n")
        print(f"✅ Created: {images_readme}")

def main():
    """Main installation function"""
    print("🚀 Restaurant Access Control System - Installation")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return False
    
    # Setup directories and data
    create_directory_structure()
    setup_initial_data()
    
    print("\\n✅ Installation completed successfully!")
    print("\\n📋 Next steps:")
    print("1. Run 'python src/setup.py' to configure the system")
    print("2. Run 'python src/main.py' to start the application")
    print("3. Use 'python scripts/maintenance.py' for system maintenance")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
'''
        
        # Save installation script
        install_path = os.path.join(self.deployment_dir, "install.py")
        with open(install_path, 'w', encoding='utf-8') as f:
            f.write(install_script)
        
        self.log("Created installation script")
    
    def create_requirements_file(self):
        """Create requirements.txt for deployment"""
        self.log("Creating requirements.txt...")
        
        requirements = [
            "# Restaurant Access Control System Dependencies",
            "# Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "",
            "# Core dependencies",
            "opencv-python>=4.8.0",
            "face-recognition>=1.3.0",
            "dlib-binary>=19.24.0",
            "numpy>=1.24.0",
            "Pillow>=10.0.0",
            "",
            "# Optional development dependencies", 
            "# pytest>=7.0.0",
            "# black>=23.0.0",
            "# flake8>=6.0.0"
        ]
        
        req_path = os.path.join(self.deployment_dir, "requirements.txt")
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write("\\n".join(requirements))
        
        self.log("Created requirements.txt")
    
    def create_deployment_readme(self):
        """Create deployment README"""
        self.log("Creating deployment README...")
        
        readme_content = f'''# Restaurant Access Control System - Deployment Package

**Version**: 1.0.0  
**Build Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Python Version**: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}

## 📦 Package Contents

```
deployment/
├── src/                    # Source code
│   ├── main.py            # Main application
│   ├── face_recognition_app.py  # Core GUI application
│   ├── config.py          # Configuration management
│   ├── validators.py      # Input validation
│   └── setup.py           # System setup
├── scripts/               # Utility scripts
│   └── maintenance.py     # Maintenance tools
├── docs/                  # Documentation
│   ├── README.md          # Main documentation
│   └── DOCUMENTATION_COMPLETE.md  # Technical documentation
├── config/                # Configuration files
│   └── deployment_config.json    # Deployment settings
├── install.py             # Installation script
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Installation

1. **Extract the package** to your desired location
2. **Run the installer**:
   ```bash
   python install.py
   ```
3. **Configure the system**:
   ```bash
   python src/setup.py
   ```
4. **Start the application**:
   ```bash
   python src/main.py
   ```

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, Linux, macOS
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space minimum
- **Camera**: USB webcam or built-in camera

## 🔧 Configuration

The system uses centralized configuration management:

- **config.py**: Main configuration file
- **deployment_config.json**: Deployment-specific settings
- **data/**: Runtime data directory (created during installation)

## 📚 Documentation

Complete documentation is available in the `docs/` directory:

- **README.md**: User guide and basic documentation
- **DOCUMENTATION_COMPLETE.md**: Comprehensive technical documentation

## 🛠️ Maintenance

Use the maintenance script for system upkeep:

```bash
# Full maintenance
python scripts/maintenance.py full

# Specific tasks
python scripts/maintenance.py images    # Clean orphaned images
python scripts/maintenance.py backups   # Clean old backups
python scripts/maintenance.py optimize  # Optimize database
python scripts/maintenance.py health    # System health check
```

## 🔒 Security Features

- Input validation and sanitization
- Secure file handling
- Access control logging
- Backup and recovery system

## 📞 Support

For technical support or issues:

1. Check the complete documentation in `docs/DOCUMENTATION_COMPLETE.md`
2. Run system health check: `python scripts/maintenance.py health`
3. Review log files in `data/logs/`

## 📄 License

This software is provided as-is for educational and commercial use.

---

**Built with**: Python, OpenCV, face-recognition, Tkinter  
**Package generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
        
        readme_path = os.path.join(self.deployment_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.log("Created deployment README")
    
    def create_deployment_package(self):
        """Create deployment ZIP package"""
        self.log("Creating deployment package...")
        
        zip_filename = f"{self.package_name}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from deployment directory
            for root, dirs, files in os.walk(self.deployment_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.deployment_dir)
                    zipf.write(file_path, arcname)
        
        package_size = os.path.getsize(zip_filename) // 1024  # KB
        self.log(f"Created package: {zip_filename} ({package_size} KB)")
        
        return zip_filename
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        report_content = []
        report_content.append(f"DEPLOYMENT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("=" * 60)
        report_content.append("")
        
        # Add deployment activities
        for entry in self.report:
            report_content.append(entry)
        
        report_content.append("")
        report_content.append("DEPLOYMENT SUMMARY")
        report_content.append("-" * 30)
        report_content.append(f"Package name: {self.package_name}")
        report_content.append(f"Deployment directory: {self.deployment_dir}")
        report_content.append(f"Total activities: {len(self.report)}")
        
        return "\\n".join(report_content)
    
    def prepare_deployment(self):
        """Run complete deployment preparation"""
        self.log(f"Starting deployment preparation for {Config.APP_NAME}...")
        
        try:
            # Create deployment structure
            self.create_deployment_structure()
            
            # Copy files
            self.copy_source_files()
            self.copy_documentation()
            
            # Prepare configuration and scripts
            self.prepare_configuration()
            self.create_installation_script()
            self.create_requirements_file()
            self.create_deployment_readme()
            
            # Create package
            package_file = self.create_deployment_package()
            
            # Generate report
            report_content = self.generate_deployment_report()
            
            # Save report
            report_file = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.log("Deployment preparation completed successfully!")
            
            return True, package_file, report_file
            
        except Exception as e:
            self.log(f"Deployment preparation failed: {e}")
            return False, None, None

def main():
    """Main deployment function"""
    print(f"🚀 {Config.APP_NAME} - Deployment Preparation")
    print("=" * 50)
    
    try:
        deployment = DeploymentManager()
        success, package_file, report_file = deployment.prepare_deployment()
        
        if success:
            print(f"\\n✅ Deployment package ready: {package_file}")
            print(f"📋 Report saved: {report_file}")
            print("\\n📦 Package contents:")
            print("- Complete source code")
            print("- Installation script")
            print("- Configuration files")
            print("- Documentation")
            print("- Maintenance tools")
            print("\\n🚀 Ready for production deployment!")
        else:
            print("\\n❌ Deployment preparation failed")
        
        return success
        
    except KeyboardInterrupt:
        print("\\n⚠️  Deployment preparation interrupted")
        return False
    except Exception as e:
        print(f"\\n❌ Deployment preparation error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)