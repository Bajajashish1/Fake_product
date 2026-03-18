"""
Migration script to convert existing JSON history files to SQLite database
This script will preserve all existing data during the database migration.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import os

# Add current directory to path to import database_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager

def migrate_json_to_database():
    """Migrate existing JSON history files to SQLite database"""
    print("Starting migration from JSON to SQLite database...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Path to existing history files
    history_dir = Path("product_history")
    
    if not history_dir.exists():
        print("No existing history directory found. Creating new database...")
        return True
    
    # Files to migrate
    files_to_migrate = {
        'analysis_history.json': 'analysis_history',
        'favorites.json': 'favorites',
        'flagged_products.json': 'flagged_products'
    }
    
    migration_count = 0
    
    # Migrate analysis history
    analysis_file = history_dir / 'analysis_history.json'
    if analysis_file.exists():
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            print(f"Found {len(history_data)} analysis records to migrate...")
            
            for i, analysis in enumerate(history_data):
                try:
                    # Convert old format to new format if needed
                    if isinstance(analysis, dict):
                        # Save to database
                        analysis_id = db_manager.save_analysis(analysis)
                        if analysis_id:
                            migration_count += 1
                            
                            # Update flags if this was in favorites or flagged
                            updates = {}
                            
                            # Check if this analysis was favorited
                            favorites_file = history_dir / 'favorites.json'
                            if favorites_file.exists():
                                with open(favorites_file, 'r', encoding='utf-8') as f:
                                    favorites = json.load(f)
                                    # Simple check - you might need to adjust based on your data structure
                                    if analysis in favorites:
                                        updates['is_favorite'] = True
                            
                            # Check if this analysis was flagged
                            flagged_file = history_dir / 'flagged_products.json'
                            if flagged_file.exists():
                                with open(flagged_file, 'r', encoding='utf-8') as f:
                                    flagged = json.load(f)
                                    if analysis in flagged:
                                        updates['is_flagged'] = True
                            
                            # Apply updates if any
                            if updates:
                                db_manager.update_analysis(analysis_id, updates)
                        
                        if (i + 1) % 10 == 0:
                            print(f"Migrated {i + 1}/{len(history_data)} records...")
                
                except Exception as e:
                    print(f"Error migrating record {i}: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"Error reading analysis history file: {str(e)}")
    
    # Create backup of original files
    if migration_count > 0:
        backup_dir = history_dir / "json_backup"
        backup_dir.mkdir(exist_ok=True)
        
        for filename in files_to_migrate.keys():
            original_file = history_dir / filename
            if original_file.exists():
                backup_file = backup_dir / f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    import shutil
                    shutil.copy2(original_file, backup_file)
                    print(f"Backed up {filename} to {backup_file}")
                except Exception as e:
                    print(f"Warning: Could not backup {filename}: {str(e)}")
    
    print(f"Migration completed! Migrated {migration_count} records to SQLite database.")
    print(f"Database location: {db_manager.db_path}")
    
    # Show database statistics
    stats = db_manager.get_statistics(days=365)  # Get all-time stats
    print(f"\nDatabase Statistics:")
    print(f"Total analyses: {stats.get('total_analyses', 0)}")
    print(f"Authenticity breakdown: {stats.get('authenticity_counts', {})}")
    
    db_info = db_manager.get_database_size()
    print(f"Database size: {db_info.get('database_size_mb', 0)} MB")
    
    return True

def verify_migration():
    """Verify the migration was successful"""
    print("\nVerifying migration...")
    
    db_manager = DatabaseManager()
    
    # Get some sample data
    history = db_manager.get_analysis_history(limit=5)
    
    if history:
        print(f"✅ Successfully loaded {len(history)} recent analysis records")
        print("Sample record:")
        sample = history[0]
        print(f"  - ID: {sample.get('id')}")
        print(f"  - Timestamp: {sample.get('timestamp')}")
        print(f"  - Brand: {sample.get('brand')}")
        print(f"  - Authenticity: {sample.get('authenticity_status')}")
        print(f"  - Confidence: {sample.get('confidence_score')}")
    else:
        print("⚠️ No records found in database")
    
    # Test database functionality
    try:
        stats = db_manager.get_statistics(days=30)
        print(f"✅ Statistics function working: {len(stats)} stat categories")
    except Exception as e:
        print(f"❌ Statistics function error: {str(e)}")
    
    try:
        db_info = db_manager.get_database_size()
        print(f"✅ Database info function working: {db_info.get('database_size_mb', 0)} MB")
    except Exception as e:
        print(f"❌ Database info function error: {str(e)}")

if __name__ == "__main__":
    try:
        success = migrate_json_to_database()
        if success:
            verify_migration()
            print("\n🎉 Migration completed successfully!")
            print("\nYou can now use the new SQLite database with enhanced features:")
            print("- Better performance and reliability")
            print("- Advanced filtering and search")
            print("- Comprehensive statistics")
            print("- Data integrity and backup features")
        else:
            print("\n❌ Migration failed. Please check the error messages above.")
    except Exception as e:
        print(f"\n❌ Migration error: {str(e)}")
        print("Please ensure you have the required dependencies and permissions.")