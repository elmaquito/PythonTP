#!/usr/bin/env python3
"""
Maintenance script for Restaurant Access Control System
Performs cleanup, optimization, and health checks
"""

import os
import sys
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from config import active_config as Config

class MaintenanceManager:
    """Handles system maintenance tasks"""
    
    def __init__(self):
        self.report = []
        self.errors = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log maintenance activities"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.report.append(log_entry)
    
    def log_error(self, message: str):
        """Log errors"""
        self.log(message, "ERROR")
        self.errors.append(message)
    
    def cleanup_orphaned_images(self) -> int:
        """Remove image files not referenced in database"""
        self.log("Checking for orphaned images...")
        
        try:
            # Load current database
            if not os.path.exists(Config.DATABASE_FILE):
                self.log("No database file found, skipping image cleanup")
                return 0
            
            with open(Config.DATABASE_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)
            
            # Get referenced images
            referenced_images = set()
            for student_data in students.values():
                if 'image_path' in student_data:
                    # Extract just the filename
                    image_path = student_data['image_path']
                    if os.path.basename(image_path):
                        referenced_images.add(os.path.basename(image_path))
            
            # Check images directory
            if not os.path.exists(Config.IMAGES_DIR):
                self.log(f"Images directory {Config.IMAGES_DIR} does not exist")
                return 0
            
            orphaned_count = 0
            total_freed_space = 0
            
            for filename in os.listdir(Config.IMAGES_DIR):
                file_path = os.path.join(Config.IMAGES_DIR, filename)
                
                # Skip non-image files and README
                if not any(filename.lower().endswith(ext) for ext in Config.SUPPORTED_FORMATS):
                    continue
                
                if filename not in referenced_images:
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        orphaned_count += 1
                        total_freed_space += file_size
                        self.log(f"Removed orphaned image: {filename}")
                    except OSError as e:
                        self.log_error(f"Could not remove {filename}: {e}")
            
            if orphaned_count > 0:
                self.log(f"Cleaned up {orphaned_count} orphaned images, freed {total_freed_space // 1024} KB")
            else:
                self.log("No orphaned images found")
            
            return orphaned_count
            
        except Exception as e:
            self.log_error(f"Error during image cleanup: {e}")
            return 0
    
    def cleanup_old_backups(self) -> int:
        """Remove backups older than retention period"""
        self.log("Cleaning up old backups...")
        
        try:
            backup_dir = Config.DATABASE_BACKUP_DIR
            if not os.path.exists(backup_dir):
                self.log("No backup directory found")
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=Config.BACKUP_RETENTION_DAYS)
            removed_count = 0
            total_freed_space = 0
            
            for filename in os.listdir(backup_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(backup_dir, filename)
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        removed_count += 1
                        total_freed_space += file_size
                        self.log(f"Removed old backup: {filename}")
                except OSError as e:
                    self.log_error(f"Could not remove backup {filename}: {e}")
            
            if removed_count > 0:
                self.log(f"Removed {removed_count} old backups, freed {total_freed_space // 1024} KB")
            else:
                self.log("No old backups to remove")
            
            return removed_count
            
        except Exception as e:
            self.log_error(f"Error during backup cleanup: {e}")
            return 0
    
    def optimize_database(self) -> bool:
        """Optimize database file (remove unused keys, compact JSON)"""
        self.log("Optimizing database...")
        
        try:
            if not os.path.exists(Config.DATABASE_FILE):
                self.log("No database file to optimize")
                return True
            
            # Load and analyze database
            with open(Config.DATABASE_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)
            
            original_size = os.path.getsize(Config.DATABASE_FILE)
            optimized_students = {}
            
            # Clean and validate each student record
            for student_id, student_data in students.items():
                cleaned_data = {}
                
                # Keep only valid fields
                valid_fields = ['first_name', 'last_name', 'image_path', 'balance', 
                               'created_date', 'last_access', 'access_count']
                
                for field in valid_fields:
                    if field in student_data:
                        cleaned_data[field] = student_data[field]
                
                # Ensure required fields have defaults
                if 'balance' not in cleaned_data:
                    cleaned_data['balance'] = Config.DEFAULT_BALANCE
                if 'access_count' not in cleaned_data:
                    cleaned_data['access_count'] = 0
                if 'created_date' not in cleaned_data:
                    cleaned_data['created_date'] = datetime.now().isoformat()
                
                optimized_students[student_id] = cleaned_data
            
            # Save optimized database
            with open(Config.DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(optimized_students, f, indent=2, ensure_ascii=False)
            
            new_size = os.path.getsize(Config.DATABASE_FILE)
            space_saved = original_size - new_size
            
            if space_saved > 0:
                self.log(f"Database optimized, saved {space_saved} bytes")
            else:
                self.log("Database already optimal")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error during database optimization: {e}")
            return False
    
    def check_system_health(self) -> dict:
        """Perform system health checks"""
        self.log("Performing system health checks...")
        
        health_report = {
            'database_size': 0,
            'image_count': 0,
            'backup_count': 0,
            'total_students': 0,
            'disk_usage': 0,
            'issues': []
        }
        
        try:
            # Database health
            if os.path.exists(Config.DATABASE_FILE):
                health_report['database_size'] = os.path.getsize(Config.DATABASE_FILE)
                
                with open(Config.DATABASE_FILE, 'r', encoding='utf-8') as f:
                    students = json.load(f)
                    health_report['total_students'] = len(students)
                
                # Check for database size warning
                if health_report['database_size'] > Config.DATABASE_MAX_SIZE:
                    health_report['issues'].append(f"Database size ({health_report['database_size'] // 1024} KB) exceeds recommended limit")
            
            # Images health
            if os.path.exists(Config.IMAGES_DIR):
                image_files = [f for f in os.listdir(Config.IMAGES_DIR) 
                              if any(f.lower().endswith(ext) for ext in Config.SUPPORTED_FORMATS)]
                health_report['image_count'] = len(image_files)
            
            # Backups health
            if os.path.exists(Config.DATABASE_BACKUP_DIR):
                backup_files = [f for f in os.listdir(Config.DATABASE_BACKUP_DIR) 
                               if f.endswith('.json')]
                health_report['backup_count'] = len(backup_files)
            
            # Disk usage
            try:
                total_size = 0
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        try:
                            total_size += os.path.getsize(os.path.join(root, file))
                        except OSError:
                            pass
                health_report['disk_usage'] = total_size
            except Exception:
                health_report['issues'].append("Could not calculate disk usage")
            
            # Log health summary
            self.log(f"Health check complete: {health_report['total_students']} students, "
                    f"{health_report['image_count']} images, {health_report['backup_count']} backups")
            
            if health_report['issues']:
                for issue in health_report['issues']:
                    self.log_error(f"Health issue: {issue}")
            
            return health_report
            
        except Exception as e:
            self.log_error(f"Error during health check: {e}")
            health_report['issues'].append(f"Health check failed: {e}")
            return health_report
    
    def generate_maintenance_report(self) -> str:
        """Generate comprehensive maintenance report"""
        report_content = []
        report_content.append(f"MAINTENANCE REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("=" * 60)
        report_content.append("")
        
        # Add all logged activities
        for entry in self.report:
            report_content.append(entry)
        
        report_content.append("")
        report_content.append("SUMMARY")
        report_content.append("-" * 30)
        report_content.append(f"Total activities: {len(self.report)}")
        report_content.append(f"Errors encountered: {len(self.errors)}")
        
        if self.errors:
            report_content.append("")
            report_content.append("ERRORS")
            report_content.append("-" * 30)
            for error in self.errors:
                report_content.append(f"• {error}")
        
        return "\n".join(report_content)
    
    def run_full_maintenance(self):
        """Run complete maintenance cycle"""
        self.log("Starting full maintenance cycle...")
        
        # Cleanup tasks
        orphaned_images = self.cleanup_orphaned_images()
        old_backups = self.cleanup_old_backups()
        
        # Optimization tasks
        db_optimized = self.optimize_database()
        
        # Health check
        health_report = self.check_system_health()
        
        # Summary
        self.log("Maintenance cycle complete")
        self.log(f"Cleaned: {orphaned_images} images, {old_backups} backups")
        self.log(f"Database optimization: {'Success' if db_optimized else 'Failed'}")
        self.log(f"System health: {len(health_report['issues'])} issues found")
        
        return len(self.errors) == 0

def main():
    """Main maintenance function"""
    print(f"🔧 {Config.APP_NAME} - Maintenance Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "full"
    
    maintenance = MaintenanceManager()
    
    try:
        if command == "full" or command == "all":
            success = maintenance.run_full_maintenance()
        elif command == "images":
            maintenance.cleanup_orphaned_images()
            success = len(maintenance.errors) == 0
        elif command == "backups":
            maintenance.cleanup_old_backups()
            success = len(maintenance.errors) == 0
        elif command == "optimize":
            success = maintenance.optimize_database()
        elif command == "health":
            health = maintenance.check_system_health()
            success = len(health['issues']) == 0
        else:
            print(f"Unknown command: {command}")
            print("Available commands: full, images, backups, optimize, health")
            return False
        
        # Generate and save report
        report_content = maintenance.generate_maintenance_report()
        
        # Save report to logs directory
        Config.ensure_directories()
        report_file = f"logs/maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📋 Maintenance report saved: {report_file}")
        
        if success:
            print("✅ Maintenance completed successfully!")
        else:
            print("⚠️  Maintenance completed with warnings/errors")
        
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️  Maintenance interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Maintenance failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)