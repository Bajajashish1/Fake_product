"""
Quick test script to verify upload functionality is working
"""

import streamlit as st
from PIL import Image
import io

def test_upload():
    st.title("🧪 Upload Functionality Test")
    
    # Test file uploader
    uploaded_file = st.file_uploader(
        "Test file upload",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a test image"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
        
        try:
            # Test image processing
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Uploaded: {uploaded_file.name}", width=300)
            
            # Test file details
            st.write(f"**File size:** {len(uploaded_file.getvalue())} bytes")
            st.write(f"**Image size:** {image.size}")
            st.write(f"**Image mode:** {image.mode}")
            
            st.success("🎉 Upload functionality is working perfectly!")
            
        except Exception as e:
            st.error(f"❌ Error processing image: {str(e)}")
    
    else:
        st.info("👆 Please upload an image file to test")

if __name__ == "__main__":
    test_upload()