"""
Test script to verify database functionality
"""

from database_manager import DatabaseManager

def test_database():
    print("Testing Database Manager...")
    
    # Initialize database
    db = DatabaseManager()
    print("✅ Database initialized")
    
    # Test saving analysis
    test_analysis = {
        'product_details': {
            'type': 'Sneakers',
            'brand': 'Nike',
            'model': 'Air Max',
            'color': 'Black/White'
        },
        'authenticity_status': 'authentic',
        'confidence_score': 0.85,
        'detailed_analysis': {
            'logo_analysis': 'Logo appears genuine',
            'quality_analysis': 'High quality materials'
        }
    }
    
    analysis_id = db.save_analysis(test_analysis, image_filename="test_image.jpg")
    if analysis_id:
        print(f"✅ Test analysis saved with ID: {analysis_id}")
    else:
        print("❌ Failed to save test analysis")
        return False
    
    # Test loading history
    history = db.get_analysis_history(limit=5)
    print(f"✅ Loaded {len(history)} analysis records")
    
    # Test statistics
    stats = db.get_statistics(days=30)
    print(f"✅ Statistics: {stats}")
    
    # Test database info
    db_info = db.get_database_size()
    print(f"✅ Database info: {db_info}")
    
    print("\n🎉 All database tests passed!")
    return True

if __name__ == "__main__":
    test_database()