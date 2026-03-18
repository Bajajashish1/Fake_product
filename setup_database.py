"""
Setup script to install required packages for the database-enhanced counterfeit detection system
"""

import subprocess
import sys

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    """Install all required packages"""
    print("🚀 Setting up database-enhanced counterfeit detection system...")
    print("Installing required packages...\n")
    
    # List of required packages
    packages = [
        "streamlit",
        "opencv-python", 
        "pillow",
        "requests",
        "pandas",
        "plotly",
        "ultralytics",
        "numpy"
        # sqlite3 is included in Python standard library
    ]
    
    installed_count = 0
    failed_packages = []
    
    for package in packages:
        if install_package(package):
            installed_count += 1
        else:
            failed_packages.append(package)
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {installed_count}/{len(packages)} packages")
    
    if failed_packages:
        print(f"❌ Failed to install: {', '.join(failed_packages)}")
        print("\nPlease install these packages manually:")
        for package in failed_packages:
            print(f"  pip install {package}")
    else:
        print("🎉 All packages installed successfully!")
    
    print("\n🗄️ Database Features:")
    print("- SQLite database for reliable data storage")
    print("- Advanced filtering and search capabilities") 
    print("- Comprehensive statistics and analytics")
    print("- Data integrity and backup features")
    print("- Image storage with base64 encoding")
    
    print("\n🚀 Next Steps:")
    print("1. Run the migration script: python migrate_to_database.py")
    print("2. Start the dashboard: streamlit run dashboard.py")
    print("3. Enjoy enhanced data management!")

if __name__ == "__main__":
    main()