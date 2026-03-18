"""
🔑 API Key Setup Helper
Automatically adds your Gemini API key to dashboard.py
"""

import os

def setup_api_key():
    print("🚀 Gemini API Key Setup Helper")
    print("=" * 40)
    
    # Get API key from user
    print("\n📋 Instructions:")
    print("1. Go to https://aistudio.google.com/")
    print("2. Sign in with your Google account") 
    print("3. Create a new API key")
    print("4. Copy the key (starts with 'AIza')")
    print()
    
    api_key = input("🔑 Paste your Gemini API key here: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting...")
        return
    
    if not api_key.startswith("AIza"):
        print("⚠️ Warning: API key doesn't start with 'AIza' - make sure it's correct")
        confirm = input("Continue anyway? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Setup cancelled")
            return
    
    # Read dashboard.py
    dashboard_file = "dashboard.py"
    if not os.path.exists(dashboard_file):
        print(f"❌ Error: {dashboard_file} not found in current directory")
        return
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the placeholder
        old_line = 'self.gemini_api_key = "YOUR_GEMINI_API_KEY_HERE"'
        new_line = f'self.gemini_api_key = "{api_key}"'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            # Write back to file
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Success! API key added to dashboard.py")
            print(f"🔧 Updated line: {new_line}")
            print()
            print("🚀 Next steps:")
            print("1. Restart your dashboard if it's running")
            print("2. Upload an image to test AI analysis")
            print("3. Look for '✅ Configured' status in the sidebar")
            
        elif f'self.gemini_api_key = "{api_key}"' in content:
            print("✅ API key already configured!")
            
        else:
            print("⚠️ Could not find the API key line to replace")
            print("Please manually edit line 59 in dashboard.py:")
            print(f'Change: self.gemini_api_key = "YOUR_GEMINI_API_KEY_HERE"')
            print(f'To:     self.gemini_api_key = "{api_key}"')
            
    except Exception as e:
        print(f"❌ Error updating file: {e}")
        print(f"Please manually add your API key to line 59 in dashboard.py")

if __name__ == "__main__":
    setup_api_key()
    input("\nPress Enter to exit...")