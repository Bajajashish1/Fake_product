import sqlite3
import os

def view_database():
    db_path = os.path.join("product_history", "counterfeit_detection.db")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print("No tables found in database.")
                return
                
            for table in tables:
                table_name = table[0]
                print(f"\n📊 Table: {table_name}")
                
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print("\nColumns:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
                
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"\nTotal records: {count}")
                
    except Exception as e:
        print(f"Error reading database: {str(e)}")

if __name__ == "__main__":
    view_database()

def view_database():
    # Connect to the database
    db_path = os.path.join("product_history", "counterfeit_detection.db")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
        
    try:
            
        with sqlite3.connect(db_path) as conn:
            # Create a cursor
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print("\n📊 Database Tables:")
            for table in tables:
                print(f"- {table[0]}")
                
                # Get column info
                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = cursor.fetchall()
                print("\nColumns:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
                
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"\nTotal records: {count}")
                
                if count > 0:
                    # Show sample data (first record)
                    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 1")
                    sample = cursor.fetchone()
                    print("\nSample record:")
                    for col, val in zip([c[1] for c in columns], sample):
                        print(f"  {col}: {val}")
                
                print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    view_database()