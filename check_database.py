from database_manager import DatabaseManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    try:
        # Initialize database
        db = DatabaseManager()
        
        # Try to get history
        history = db.get_analysis_history()
        print(f"\nFound {len(history)} records in database")
        
        # Create tables if needed
        db._init_database()
        print("\n✅ Database initialized successfully")
        
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Checking database setup...")
    check_database()