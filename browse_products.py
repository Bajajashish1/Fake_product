import sqlite3
import os
from datetime import datetime

def format_product_info(row):
    """Format a product record in a readable way"""
    return f"""
{'='*50}
Product ID: {row[0]}
Analyzed on: {row[1]}

Product Details:
--------------
Type: {row[4]}
Brand: {row[5]}
Model: {row[6]}
Color: {row[7]}
Price Range: {row[8]}

Analysis Results:
---------------
Authenticity: {row[9]}
Confidence Score: {row[10]:.2f}%

Detailed Analysis:
----------------
Logo Analysis: {row[11]}
Quality Analysis: {row[12]}
Material Analysis: {row[13]}
Pricing Analysis: {row[14]}

Overall Verdict: {row[15]}

Additional Information:
--------------------
Recommendations: {row[16]}
Risk Factors: {row[17]}
Verification Methods: {row[18]}

Status:
------
Favorite: {'Yes' if row[20] else 'No'}
Flagged: {'Yes' if row[21] else 'No'}
{'='*50}
"""

def browse_products():
    db_path = os.path.join("product_history", "counterfeit_detection.db")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
        
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM analysis_history")
            total = cursor.fetchone()[0]
            
            if total == 0:
                print("No products found in the database.")
                return
                
            print(f"\nFound {total} analyzed products.\n")
            
            # Get all products ordered by timestamp
            cursor.execute("""
                SELECT * FROM analysis_history 
                ORDER BY timestamp DESC
            """)
            
            products = cursor.fetchall()
            
            while True:
                print("\nOptions:")
                print("1. Show all products")
                print("2. Show authentic products")
                print("3. Show counterfeit products")
                print("4. Show flagged products")
                print("5. Show favorite products")
                print("6. Exit")
                
                choice = input("\nEnter your choice (1-6): ")
                
                if choice == '6':
                    break
                    
                filtered_products = []
                
                if choice == '1':
                    filtered_products = products
                    print("\nShowing all products:")
                elif choice == '2':
                    filtered_products = [p for p in products if p[9] == 'Authentic']
                    print("\nShowing authentic products:")
                elif choice == '3':
                    filtered_products = [p for p in products if p[9] == 'Counterfeit']
                    print("\nShowing counterfeit products:")
                elif choice == '4':
                    filtered_products = [p for p in products if p[21]]  # is_flagged
                    print("\nShowing flagged products:")
                elif choice == '5':
                    filtered_products = [p for p in products if p[20]]  # is_favorite
                    print("\nShowing favorite products:")
                else:
                    print("Invalid choice. Please try again.")
                    continue
                
                if not filtered_products:
                    print("No products found matching this criteria.")
                    continue
                    
                for product in filtered_products:
                    print(format_product_info(product))
                    input("Press Enter to see next product...")
                
    except Exception as e:
        print(f"Error browsing products: {str(e)}")

if __name__ == "__main__":
    browse_products()