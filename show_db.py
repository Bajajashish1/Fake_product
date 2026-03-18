import sqlite3
import os

db_path = os.path.join("product_history", "counterfeit_detection.db")

if not os.path.exists(db_path):
    print(f"Database file not found at: {db_path}")
else:
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print("No tables found in database.")
            else:
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