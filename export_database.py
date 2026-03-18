import sqlite3
import json
from datetime import datetime
import os

def export_database():
    # Connect to the database
    db_path = os.path.join(os.getcwd(), "product_history", "counterfeit_detection.db")
    export_dir = os.path.join(os.getcwd(), "product_history")
    export_path = os.path.join(export_dir, f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    # Ensure export directory exists
    os.makedirs(export_dir, exist_ok=True)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Create a cursor
            cursor = conn.cursor()
            
            # Get all data from analysis_history
            cursor.execute('''
                SELECT id, image_filename, product_type, brand, model, color, 
                       price_range, authenticity_status, confidence_score,
                       logo_analysis, quality_analysis, material_analysis,
                       pricing_analysis, overall_verdict, recommendations,
                       risk_factors, verification_methods, timestamp,
                       is_favorite, is_flagged
                FROM analysis_history
            ''')
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                item = dict(zip(columns, row))
                # Convert datetime string to more readable format
                if item['timestamp']:
                    item['timestamp'] = datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                data.append(item)
            
            # Create export data structure
            export_data = {
                "export_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "total_records": len(data),
                "analyses": data
            }
            
            # Write to file
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully exported {len(data)} records to {export_path}")
            return export_path
            
    except Exception as e:
        print(f"❌ Error exporting database: {str(e)}")
        return None

if __name__ == "__main__":
    export_database()