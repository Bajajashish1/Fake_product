import os
import glob
import shutil

def cleanup_workspace():
    # Files to remove
    files_to_remove = [
        # Backup and temporary files
        'dashboard_backup.py',
        'dashboard_clean.py',
        'temp_dashboard_*.py',
        'temp_backup_*.json',
        
        # Multiple versions
        'modern_dashboard.py',
        'simple_dashboard.py',
        
        # Test results
        'test_result_*.jpg',
        
        # Old documentation
        'API_INTEGRATION_GUIDE.md',
        'BATCH_UPLOAD_FIX_REPORT.md',
        'BATCH_UPLOAD_GUIDE.md',
        'CAMERA_SESSION_STATE_FIX.md',
        'DRAG_DROP_FIX_REPORT.md',
        'GEMINI_API_GUIDE.md',
        'PANDAS_IMPORT_FIX_REPORT.md',
        'PRODUCT_HISTORY_FIX_REPORT.md',
        'QUICK_FIX_GUIDE.md',
        'QUICK_SETUP_GUIDE.md',
        'README_COMPLETE.md',
        'README_dashboard.md',
        'SHOE_DETECTION_GUIDE.md',
        'THEME_SHOWCASE.md',
        'TITLE_UPDATE_REPORT.md',
        'UPLOAD_CAMERA_FIXED.md',
        'UPLOAD_FIX_REPORT.md',
        
        # Duplicate functionality files
        'browse_products.py',
        'check_database.py',
        'show_db.py',
        'view_database.py',
        
        # Cache files
        '__pycache__',
        '*.pyc'
    ]
    
    # Keep track of removed files
    removed_files = []
    
    print("🧹 Starting workspace cleanup...")
    
    for pattern in files_to_remove:
        # Use glob to match patterns
        matches = glob.glob(pattern)
        for file_path in matches:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    removed_files.append(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    removed_files.append(file_path)
            except Exception as e:
                print(f"❌ Error removing {file_path}: {str(e)}")
    
    print("\n✅ Cleanup complete!")
    print(f"\nRemoved {len(removed_files)} unnecessary files and directories:")
    for file in removed_files:
        print(f"  - {file}")

if __name__ == "__main__":
    cleanup_workspace()