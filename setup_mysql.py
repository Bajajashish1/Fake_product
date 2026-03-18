"""
Setup script for MySQL database configuration
"""

import subprocess
import sys
import os

def install_requirements():
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mysql-connector-python"])

def setup_database():
    print("\n🔧 Setting up MySQL database connection...")
    
    # Get database configuration from user
    host = input("Enter MySQL host (default: localhost): ") or "localhost"
    user = input("Enter MySQL username (default: root): ") or "root"
    password = input("Enter MySQL password: ")
    database = input("Enter database name (default: counterfeit_detection): ") or "counterfeit_detection"
    
    # Create configuration file
    config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }
    
    # Save configuration
    with open('db_config.py', 'w') as f:
        f.write(f"""# MySQL Database Configuration
DB_CONFIG = {{
    'host': '{host}',
    'user': '{user}',
    'password': '{password}',
    'database': '{database}'
}}
""")
    
    print("\n✅ Database configuration saved successfully!")
    print("\nTo test the connection, run: python test_database.py")

if __name__ == "__main__":
    print("🚀 Setting up MySQL database for Counterfeit Detection System...")
    install_requirements()
    setup_database()