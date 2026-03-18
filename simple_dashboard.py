import streamlit as st
import cv2
import numpy as np
from PIL import Image
import requests
import json
import base64
import io

# Page configuration
st.set_page_config(
    page_title="Product Authenticity Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

class SimpleProductAnalyzer:
    def __init__(self):
        self.gemini_api_key = "AIzaSyAueXPGSLYTGLC2GEBDPxpNIxiJ4_2tkA8"
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
    
    def image_to_base64(self, image):
        """Convert PIL image to base64 string"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            
            # Convert to base64
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            return base64_string
        except Exception as e:
            print(f"Error converting image: {str(e)}")
            return None
    
    def analyze_product(self, image):
        """Analyze product authenticity using AI"""
        if not self.gemini_api_key:
            return None, "API key not configured"
        
        try:
            # Convert image to base64
            image_base64 = self.image_to_base64(image)
            if not image_base64:
                return None, "Failed to process image"
            
            # Simple prompt for product analysis
            prompt = """
            Analyze this product image and determine if it's authentic or fake. 
            
            Provide your analysis in this exact JSON format:
            {
                "authenticity_status": "authentic" or "fake" or "uncertain",
                "confidence_score": 0.8,
                "product_type": "what type of product this is",
                "brand": "brand name if visible",
                "key_findings": ["finding 1", "finding 2", "finding 3"],
                "recommendation": "brief recommendation",
                "summary": "2-3 sentence summary of your analysis"
            }
            
            Only respond with the JSON, no other text.
            """
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1024,
                    "responseMimeType": "application/json"
                }
            }
            
            # Make API request
            url = f"{self.gemini_api_url}?key={self.gemini_api_key}"
            response = requests.post(
                url, 
                headers={'Content-Type': 'application/json'}, 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text_response = result['candidates'][0]['content']['parts'][0]['text']
                    
                    try:
                        analysis_result = json.loads(text_response)
                        return analysis_result, None
                    except json.JSONDecodeError:
                        # Try to extract JSON from response
                        start_idx = text_response.find('{')
                        end_idx = text_response.rfind('}') + 1
                        if start_idx != -1 and end_idx != 0:
                            json_str = text_response[start_idx:end_idx]
                            analysis_result = json.loads(json_str)
                            return analysis_result, None
                        else:
                            return None, "Could not parse AI response"
                else:
                    return None, "No response from AI"
            elif response.status_code == 503:
                return None, "🤖 AI service is busy. Please try again in a moment."
            else:
                return None, f"API error: {response.status_code}"
                
        except Exception as e:
            return None, f"Analysis error: {str(e)}"

def main():
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = SimpleProductAnalyzer()
    
    # Main title
    st.title("🔍 Product Authenticity Checker")
    st.markdown("### Upload a product image to check if it's authentic or fake")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a product image...",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear image of the product you want to analyze"
    )
    
    if uploaded_file is not None:
        # Load and display image
        try:
            image = Image.open(uploaded_file)
            
            # Show upload success
            st.success(f"✅ Image uploaded: {uploaded_file.name}")
            
            # Analyze button
            if st.button("🚀 **ANALYZE AUTHENTICITY**", type="primary", use_container_width=True):
                
                with st.spinner("🤖 Analyzing product authenticity..."):
                    # Run analysis
                    result, error = st.session_state.analyzer.analyze_product(image)
                
                if error:
                    st.error(f"❌ {error}")
                    st.info("💡 Please try again in a few moments")
                else:
                    # Display results
                    st.markdown("---")
                    st.markdown("## 📋 **ANALYSIS RESULTS**")
                    
                    # Two columns: image and results
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("📷 **Your Product**")
                        st.image(image, caption="Analyzed Product", use_column_width=True)
                    
                    with col2:
                        if result:
                            status = result.get('authenticity_status', 'unknown')
                            confidence = result.get('confidence_score', 0.0)
                            
                            # Big result display
                            st.subheader("🎯 **AUTHENTICITY RESULT**")
                            
                            if status == 'authentic':
                                st.success("✅ **AUTHENTIC**")
                                st.metric("Confidence", f"{confidence:.0%}")
                            elif status == 'fake':
                                st.error("🚨 **FAKE/COUNTERFEIT**")
                                st.metric("Confidence", f"{confidence:.0%}")
                            else:
                                st.warning("⚠️ **UNCERTAIN**")
                                st.metric("Confidence", f"{confidence:.0%}")
                            
                            # Product info
                            st.markdown("**Product Details:**")
                            st.write(f"• **Type:** {result.get('product_type', 'Unknown')}")
                            st.write(f"• **Brand:** {result.get('brand', 'Unknown')}")
                    
                    # Key findings
                    if result and result.get('key_findings'):
                        st.markdown("---")
                        st.subheader("🔍 **Key Analysis Points**")
                        for finding in result['key_findings']:
                            st.write(f"• {finding}")
                    
                    # Recommendation
                    if result and result.get('recommendation'):
                        st.markdown("---")
                        st.subheader("💡 **Recommendation**")
                        st.info(result['recommendation'])
                    
                    # Summary
                    if result and result.get('summary'):
                        st.markdown("---")
                        st.subheader("📖 **Analysis Summary**")
                        st.write(result['summary'])
        
        except Exception as e:
            st.error(f"❌ Error loading image: {str(e)}")
    else:
        st.info("📎 Please upload a product image to begin analysis")

if __name__ == "__main__":
    main()