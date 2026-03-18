"""
🚀 Dashboard Launcher - Multiple Detection Options
"""

import streamlit as st
import subprocess
import sys

def main():
    st.set_page_config(
        page_title="Dashboard Launcher",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 Fake Product Detection Dashboard Launcher")
    st.markdown("Choose the perfect detection interface for your shoe analysis needs")
    
    # Dashboard options
    st.markdown("## 📊 Available Dashboards")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🏠 **Modern Dashboard**
        **Best for: Comprehensive Analysis**
        
        ✅ **Features:**
        - API Integration (Gemini + OpenAI)
        - Modern dark theme interface
        - Enhanced feedback system
        - Batch processing capabilities
        
        📍 **Status:** ✅ Running on port 8502
        """)
        
        if st.button("🌟 Launch Modern Dashboard", key="modern"):
            st.success("🚀 Opening Modern Dashboard...")
            st.markdown("**URL:** http://localhost:8502")
    
    with col2:
        st.markdown("""
        ### 👟 **Enhanced Shoe Detector**
        **Best for: Shoe-Specific Analysis**
        
        ✅ **Features:**
        - Specialized for footwear detection
        - Enhanced image quality analysis
        - Color & texture assessment
        - Photography improvement tips
        
        📍 **Status:** ✅ Running on port 8503
        """)
        
        if st.button("👟 Launch Shoe Detector", key="shoe"):
            st.success("🚀 Opening Enhanced Shoe Detector...")
            st.markdown("**URL:** http://localhost:8503")
    
    with col3:
        st.markdown("""
        ### 🔧 **Original Dashboard**
        **Best for: Simple & Reliable**
        
        ✅ **Features:**
        - Basic YOLO detection
        - Simple, fast interface
        - Stable performance
        - No API dependencies
        
        📍 **Status:** Available on demand
        """)
        
        if st.button("⚡ Launch Original Dashboard", key="original"):
            st.success("🚀 Launching Original Dashboard...")
            try:
                subprocess.Popen([
                    sys.executable, "-m", "streamlit", "run", 
                    "dashboard.py", "--server.port", "8504"
                ])
                st.markdown("**URL:** http://localhost:8504")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Usage recommendations
    st.markdown("---")
    st.markdown("## 💡 For Best Shoe Detection Results")
    
    st.markdown("""
    ### 🎯 **Recommended Workflow:**
    1. **Start with:** 👟 Enhanced Shoe Detector for specialized feedback
    2. **Then try:** 🌟 Modern Dashboard for API-powered insights
    3. **Fallback:** ⚡ Original Dashboard for basic detection
    
    ### 📸 **Photography Tips:**
    - Use good lighting (natural light preferred)
    - Show the entire shoe including brand labels
    - Use plain background for better contrast
    - Take multiple angles for comprehensive analysis
    - Ensure shoes are in focus and clearly visible
    """)

if __name__ == "__main__":
    main()