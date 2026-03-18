"""
Test MySQL database connection
"""

from mysql_database_manager import MySQLDatabaseManager
import sys

def test_connection():
    try:
        # Import configuration
        from db_config import DB_CONFIG
        
        print("🔄 Testing database connection...")
        
        # Initialize database manager
        db = MySQLDatabaseManager(**DB_CONFIG)
        
        # Try to access the database
        history = db.get_analysis_history()
        
        print("✅ Successfully connected to MySQL database!")
        print(f"Found {len(history)} existing records")
        
        return True
        
    except ImportError:
        print("❌ Database configuration not found!")
        print("Please run setup_mysql.py first to configure the database.")
        return False
        
    except Exception as e:
        print(f"❌ Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()