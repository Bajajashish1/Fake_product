import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ultralytics import YOLO
import os
import tempfile
from pathlib import Path
import requests
import base64
import io
import json



# Configure page
st.set_page_config(
    page_title="🔍 Fake Product Detector ",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 3rem;
        margin-bottom: 2rem;
    }
    .detection-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

class FakeProductDetector:
    def __init__(self, model_path="runs/fake_product_detector27/weights/best.pt"):
        """Initialize the detector with the trained model and API configuration"""
        self.model_path = model_path
        self.model = None
        # Set your AI API key directly here
        self.gemini_api_key = "AIzaSyAueXPGSLYTGLC2GEBDPxpNIxiJ4_2tkA8"  # Internal API key
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
        self.load_model()
    
    def image_to_base64(self, image):
        """Convert PIL image to base64 string for API"""
        try:
            if isinstance(image, Image.Image):
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Resize if too large (API limits)
                max_size = 1024
                if max(image.size) > max_size:
                    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=90)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                return image_base64
            return None
        except Exception as e:
            st.error(f"Error converting image: {str(e)}")
            return None
    
    def analyze_with_ai_api(self, image):
        """Analyze image using AI for fake product detection with retry logic"""
        # Check if API key is properly configured
        if not self.gemini_api_key or self.gemini_api_key == "YOUR_GEMINI_API_KEY_HERE":
            return None, "AI analysis temporarily unavailable - API key not configured"
        
        # Retry configuration
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Convert image to base64
                image_base64 = self.image_to_base64(image)
                if not image_base64:
                    return None, "Failed to convert image to base64"
                
                print(f"DEBUG: Attempt {attempt + 1}/{max_retries}")
                print(f"DEBUG: API key present: {bool(self.gemini_api_key)}")
                print(f"DEBUG: Image converted to base64: {bool(image_base64)}")
                
                # Prepare API request
                headers = {
                    'Content-Type': 'application/json',
                }
                
                # Create the prompt for comprehensive product analysis
                prompt = """
                Perform a comprehensive analysis of this product image. Provide detailed information about the product and determine its authenticity.
                
                Please analyze these aspects thoroughly:
                
                1. PRODUCT IDENTIFICATION:
                - Product type and category
                - Brand name and model (if visible)
                - Product color and design details
                
                2. AUTHENTICITY ANALYSIS:
                - Brand logos and typography quality
                - Stitching patterns and construction
                - Material appearance and texture
                - Hardware quality (zippers, buttons, buckles)
                - Packaging and labels
                - Serial numbers or authenticity marks
                
                3. QUALITY ASSESSMENT:
                - Overall craftsmanship level
                - Material quality indicators
                - Construction durability signs
                - Finish and attention to detail
                
                4. COUNTERFEIT INDICATORS:
                - Misspellings or incorrect fonts
                - Poor quality materials or construction
                - Unusual design elements
                - Missing authentic features
                - Price inconsistencies (if known)
                
                5. DETAILED OBSERVATIONS:
                - Specific visual elements noted
                - Comparison to known authentic versions
                - Red flags or positive indicators
                
                Provide your comprehensive analysis in this JSON format:
                {
                    "product_details": {
                        "type": "product category",
                        "brand": "identified brand",
                        "model": "model name if visible",
                        "color": "primary colors",
                        "estimated_price_range": "price estimate if identifiable"
                    },
                    "authenticity_status": "authentic" or "fake" or "uncertain",
                    "confidence_score": 0.0-1.0,
                    "detailed_analysis": {
                        "logo_analysis": "brief 1-2 sentence assessment of brand logos",
                        "material_analysis": "brief 1-2 sentence assessment of materials",
                        "construction_analysis": "brief 1-2 sentence evaluation of build quality",
                        "hardware_analysis": "brief 1-2 sentence assessment of metal parts, zippers",
                        "packaging_analysis": "brief 1-2 sentence evaluation of tags, packaging"
                    },
                    "detected_issues": ["specific issues found"],
                    "positive_indicators": ["authentic features identified"],
                    "quality_assessment": {
                        "logo_quality": "excellent/good/poor/missing",
                        "material_quality": "excellent/good/poor",
                        "construction_quality": "excellent/good/poor",
                        "overall_craftsmanship": "excellent/good/poor"
                    },
                    "recommendations": {
                        "authenticity_verdict": "Brief 1-2 sentence verdict with key reason",
                        "purchase_advice": "Short recommendation - proceed or avoid",
                        "verification_tips": "1-2 brief verification steps"
                    },
                    "analysis_summary": "Brief 2-3 sentence summary of key findings and final verdict",
                    "expert_notes": "Short professional insight (1-2 sentences)"
                }
                
                IMPORTANT: Respond ONLY with the JSON object above. Do not include any additional text, explanations, or markdown formatting. Start your response with { and end with }.
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
                        "topK": 32,
                        "topP": 1,
                        "maxOutputTokens": 2048,
                        "stopSequences": [],
                        "candidateCount": 1,
                        "responseMimeType": "application/json"
                    }
                }
                
                # Make API request
                url = f"{self.gemini_api_url}?key={self.gemini_api_key}"
                print(f"DEBUG: Making API request to: {self.gemini_api_url}")
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                print(f"DEBUG: API response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"DEBUG: API response received successfully")
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        text_response = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"DEBUG: Text response length: {len(text_response) if text_response else 0}")
                        
                        # Try to extract JSON from the response
                        try:
                            # Try to parse the entire response as JSON first
                            try:
                                analysis_result = json.loads(text_response)
                                return analysis_result, None
                            except json.JSONDecodeError:
                                pass
                            
                            # Find JSON in the response if it's embedded
                            start_idx = text_response.find('{')
                            end_idx = text_response.rfind('}') + 1
                            
                            if start_idx != -1 and end_idx != 0:
                                json_str = text_response[start_idx:end_idx]
                                analysis_result = json.loads(json_str)
                                return analysis_result, None
                            else:
                                # If no JSON found, parse the text response manually
                                print(f"Raw response: {text_response}")  # Debug line
                                return self.parse_text_response(text_response), None
                                
                        except json.JSONDecodeError as e:
                            print(f"JSON parsing error: {e}")  # Debug line
                            print(f"Response text: {text_response}")  # Debug line
                            return self.parse_text_response(text_response), None
                    else:
                        return None, "No analysis generated by API"
                        
                elif response.status_code == 503:
                    # Handle 503 Service Unavailable - API overloaded
                    if attempt < max_retries - 1:
                        print(f"DEBUG: API overloaded (503), retrying in {retry_delay} seconds...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        return None, "🤖 AI service is currently busy. Please try again in a few moments. The Google Gemini API is experiencing high traffic."
                        
                elif response.status_code == 429:
                    # Handle 429 Too Many Requests - Rate limiting
                    if attempt < max_retries - 1:
                        print(f"DEBUG: Rate limited (429), retrying in {retry_delay} seconds...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        return None, "⏰ Too many requests. Please wait a moment and try again."
                        
                else:
                    # Other HTTP errors
                    error_msg = f"API request failed: {response.status_code}"
                    if response.text:
                        try:
                            error_json = response.json()
                            if 'error' in error_json and 'message' in error_json['error']:
                                error_msg = f"API Error: {error_json['error']['message']}"
                        except:
                            error_msg += f" - {response.text}"
                    return None, error_msg
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"DEBUG: Timeout, retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    return None, "⏱️ Request timeout. Please check your internet connection and try again."
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"DEBUG: Request error, retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    return None, f"🌐 Network error: {str(e)}"
                    
            except Exception as e:
                return None, f"💥 Unexpected error: {str(e)}"
        
        # If we reach here, all retries failed
        return None, "🔄 All retry attempts failed. Please try again later."
    
    def parse_text_response(self, text_response):
        """Parse a text response when JSON parsing fails"""
        # Try to extract useful information from the text
        text_lower = text_response.lower()
        
        # Determine authenticity status
        if "authentic" in text_lower and "fake" not in text_lower:
            status = "authentic"
            confidence = 0.8
        elif "fake" in text_lower or "counterfeit" in text_lower:
            status = "fake"
            confidence = 0.8
        else:
            status = "uncertain"
            confidence = 0.5
        
        # Extract basic issues
        issues = []
        if "poor quality" in text_lower:
            issues.append("Poor quality detected")
        if "logo" in text_lower and ("poor" in text_lower or "incorrect" in text_lower):
            issues.append("Logo quality concerns")
        if "material" in text_lower and "poor" in text_lower:
            issues.append("Material quality issues")
        
        return {
            "product_details": {
                "type": "Product",
                "brand": "Unknown",
                "model": "Unknown",
                "color": "Unknown",
                "estimated_price_range": "Unknown"
            },
            "authenticity_status": status,
            "confidence_score": confidence,
            "detailed_analysis": {
                "logo_analysis": "Analysis completed",
                "material_analysis": "Analysis completed",
                "construction_analysis": "Analysis completed",
                "hardware_analysis": "Analysis completed",
                "packaging_analysis": "Analysis completed"
            },
            "detected_issues": issues if issues else ["No specific issues detected"],
            "positive_indicators": ["AI analysis completed successfully"],
            "quality_assessment": {
                "logo_quality": "good",
                "material_quality": "good",
                "construction_quality": "good",
                "overall_craftsmanship": "good"
            },
            "recommendations": {
                "authenticity_verdict": f"Product appears to be {status}",
                "purchase_advice": "Review analysis details before purchasing",
                "verification_tips": "Consider professional authentication if needed"
            },
            "analysis_summary": f"AI analysis indicates product is {status} with {confidence:.0%} confidence. Review quality indicators for details.",
            "expert_notes": "Visual inspection completed with AI assistance."
        }
    
    def load_model(self):
        """Load the YOLO model"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                return True
            else:
                st.error(f"Model not found at: {self.model_path}")
                return False
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
            return False
    
    def detect_products(self, image, conf_threshold=0.25):
        """Run detection on an image"""
        if self.model is None:
            return None, "Model not loaded"
        
        try:
            # Run inference
            results = self.model(image, conf=conf_threshold, verbose=False)
            return results, None
        except Exception as e:
            return None, f"Detection error: {str(e)}"
    
    def draw_detections(self, image, results):
        """Draw bounding boxes and labels on the image"""
        if results is None or len(results) == 0:
            return image
        
        # Convert PIL to OpenCV format
        if isinstance(image, Image.Image):
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            image_cv = image.copy()
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    
                    # Get confidence and class
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = self.model.names[cls]
                    
                    # Store detection info
                    detections.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': (x1, y1, x2, y2)
                    })
                    
                    # Color based on class (red for fake, green for real)
                    color = (0, 0, 255) if class_name == 'fake' else (0, 255, 0)
                    
                    # Draw bounding box
                    cv2.rectangle(image_cv, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label background
                    label = f"{class_name}: {conf:.2f}"
                    (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(image_cv, (x1, y1 - label_height - 10), (x1 + label_width, y1), color, -1)
                    
                    # Draw label text
                    cv2.putText(image_cv, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Convert back to RGB for display
        image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        return Image.fromarray(image_rgb), detections

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 Fake Product Detector Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize detector
    if 'detector' not in st.session_state:
        st.session_state.detector = FakeProductDetector()
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # Model status
    model_status = "✅ Loaded" if st.session_state.detector.model else "❌ Not Loaded"
    st.sidebar.markdown(f"**Model Status:** {model_status}")
    
    # Camera availability
    st.sidebar.markdown(f"**📷 Camera:** 🟢 Available")
    
    # Confidence threshold
    conf_threshold = st.sidebar.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        help="Minimum confidence for detections"
    )
    
    # Analysis Settings
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Analysis Settings")
    
    # Image preprocessing options
    enhance_image = st.sidebar.checkbox(
        "🔧 Enhance Image Quality", 
        value=True, 
        help="Apply image enhancement for better analysis"
    )
    
    auto_crop = st.sidebar.checkbox(
        "✂️ Auto-Crop Product", 
        value=False, 
        help="Automatically crop to focus on the main product"
    )
    
    # Detection sensitivity
    detection_mode = st.sidebar.radio(
        "🎚️ Detection Sensitivity",
        ["🔍 Precise", "⚖️ Balanced", "🔬 Thorough"],
        index=1,
        help="Adjust how strict the authenticity analysis should be"
    )
    
    # Product category hint
    product_category = st.sidebar.selectbox(
        "👟 Product Category (Optional)",
        ["🔍 Auto-Detect", "👟 Footwear", "👜 Handbags", "⌚ Watches", "👕 Clothing", "🕶️ Accessories", "📱 Electronics"],
        help="Help focus the analysis on specific product features"
    )
    
    # Quick Actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Quick Actions")
    
    # Camera mode toggle
    camera_mode = st.sidebar.checkbox(
        "📷 Prefer Camera Mode",
        value=False,
        help="Default to camera tab for quick photo capture"
    )
    
    # Sample images
    if st.sidebar.button("📷 Load Sample Image"):
        st.session_state.use_sample = True
    
    # Clear results
    if st.sidebar.button("🗑️ Clear Results"):
        if 'results_history' in st.session_state:
            st.session_state.results_history = []
        st.rerun()
    
    # Export options
    if st.sidebar.button("📊 Export Analysis"):
        st.session_state.show_export = True
    
    # Comparison mode
    comparison_mode = st.sidebar.checkbox(
        "🔄 Comparison Mode",
        value=False,
        help="Compare multiple products side by side"
    )
    
    # Advanced options
    with st.sidebar.expander("⚙️ Advanced Options"):
        save_results = st.checkbox("💾 Auto-save Results", value=True, key="auto_save_checkbox")
        show_confidence_details = st.checkbox("📊 Show Confidence Breakdown", value=False, key="confidence_details_checkbox")
        enable_notifications = st.checkbox("🔔 Enable Notifications", value=True, key="notifications_checkbox")
    
    # Analysis History
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Recent Analysis")
    
    # Initialize history if not exists
    if 'results_history' not in st.session_state:
        st.session_state.results_history = []
    
    # Show last few results
    if st.session_state.results_history:
        recent_count = min(3, len(st.session_state.results_history))
        for i in range(recent_count):
            result = st.session_state.results_history[-(i+1)]
            status_emoji = {"authentic": "✅", "fake": "🚨", "uncertain": "⚠️"}.get(result.get('status', 'unknown'), "❓")
            st.sidebar.write(f"{status_emoji} {result.get('timestamp', 'Unknown')} - {result.get('confidence', 0):.0%}")
    else:
        st.sidebar.write("No recent analysis")
    
    # Performance Stats
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Session Stats")
    
    total_analyzed = len(st.session_state.results_history)
    if total_analyzed > 0:
        fake_count = sum(1 for r in st.session_state.results_history if r.get('status') == 'fake')
        authentic_count = sum(1 for r in st.session_state.results_history if r.get('status') == 'authentic')
        
        st.sidebar.metric("📊 Total Analyzed", total_analyzed)
        st.sidebar.metric("🚨 Fake Detected", fake_count)
        st.sidebar.metric("✅ Authentic Found", authentic_count)
    else:
        st.sidebar.write("No analysis performed yet")
    
    # Help & Tips
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Tips & Help")
    
    with st.sidebar.expander("📸 Best Photo Practices"):
        st.write("""
        **For optimal results:**
        • Use good lighting
        • Keep the product centered
        • Include brand logos/labels
        • Capture multiple angles
        • Avoid blurry images
        """)
    
    with st.sidebar.expander("🎯 Understanding Results"):
        st.write("""
        **Confidence Levels:**
        • 90-100%: Very confident
        • 70-89%: High confidence
        • 50-69%: Moderate confidence
        • Below 50%: Low confidence
        """)
    
    with st.sidebar.expander("🔍 What We Analyze"):
        st.write("""
        **Key Factors:**
        • Logo quality & placement
        • Material texture & finish
        • Stitching patterns
        • Hardware quality
        • Overall craftsmanship
        """)
    
    # Navigation
    page = st.sidebar.selectbox(
        "📊 Navigation",
        ["🔍 Detection", "📈 Performance Metrics", "📸 Batch Processing", "ℹ️ Model Info"]
    )
    
    if page == "🔍 Detection":
        # Store sidebar settings in session state for access in detection page
        st.session_state.enhance_image = enhance_image
        st.session_state.auto_crop = auto_crop
        st.session_state.detection_mode = detection_mode
        st.session_state.product_category = product_category
        st.session_state.comparison_mode = comparison_mode
        st.session_state.camera_mode = camera_mode
        detection_page(conf_threshold)
    elif page == "📈 Performance Metrics":
        metrics_page()
    elif page == "📸 Batch Processing":
        batch_processing_page(conf_threshold)
    elif page == "ℹ️ Model Info":
        model_info_page()

def detection_page(conf_threshold):
    """Main detection page"""
    from PIL import Image
    
    st.header("🤖 AI-Powered Product Authenticity Detection")
    
    # Handle sample image loading
    if st.session_state.get('use_sample', False):
        st.info("📷 Loading sample image for demonstration...")
        # Use one of the test result images as sample
        import os
        sample_files = [f for f in os.listdir('.') if f.startswith('test_result_') and f.endswith('.jpg')]
        if sample_files:
            sample_path = sample_files[0]  # Use first available test result
            try:
                # Store the path instead of the image object to avoid conflicts
                st.session_state.sample_image_path = sample_path
                uploaded_file = "SAMPLE_IMAGE"  # Flag to indicate sample image
                st.success(f"✅ Loaded sample image: {sample_path}")
            except Exception as e:
                st.error(f"❌ Could not load sample image: {str(e)}")
                uploaded_file = None
        else:
            st.warning("⚠️ No sample images found. Please upload your own image.")
            uploaded_file = None
        st.session_state.use_sample = False
    else:
        # Create tabs for different input methods
        # Check camera mode preference to order tabs
        camera_mode_pref = st.session_state.get('camera_mode', False)
        
        if camera_mode_pref:
            camera_tab, upload_tab = st.tabs(["📷 Live Camera", "📁 Upload Image"])
        else:
            upload_tab, camera_tab = st.tabs(["📁 Upload Image", "📷 Live Camera"])
        
        with upload_tab:
            # File upload
            uploaded_file = st.file_uploader(
                "Choose an image...",
                type=['jpg', 'jpeg', 'png'],
                help="Upload an image to detect fake products using AI",
                key="main_file_uploader"
            )
            
            # Debug: Show upload status
            if uploaded_file is not None:
                st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
                st.write(f"📊 File size: {uploaded_file.size} bytes")
                st.write(f"📁 File type: {uploaded_file.type}")
                
                # SHOW THE IMAGE FIRST
                try:
                    if hasattr(uploaded_file, 'read'):
                        image = Image.open(uploaded_file)
                    else:
                        image = uploaded_file
                    
                    st.markdown("---")
                    st.subheader("📷 **Your Uploaded Product**")
                    st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
                    
                    # THEN ANALYZE BUTTON - Right after showing image
                    st.markdown("---")
                    st.markdown("### 🎯 **Ready to Analyze!**")
                    
                    if st.button("🚀 **ANALYZE PRODUCT AUTHENTICITY**", key="immediate_analyze_btn", type="primary", use_container_width=True):
                        # Run analysis and show results immediately
                        with st.spinner("🤖 AI analyzing product authenticity..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            status_text.text("🔍 Initializing analysis...")
                            progress_bar.progress(20)
                            
                            status_text.text("📸 Processing image...")
                            progress_bar.progress(40)
                            
                            status_text.text("🧠 Running AI analysis...")
                            progress_bar.progress(60)
                            
                            # Make sure detector is initialized
                            if 'detector' not in st.session_state:
                                from enhanced_shoe_detector import EnhancedShoeDetector
                                st.session_state.detector = EnhancedShoeDetector()
                            
                            api_result, api_error = st.session_state.detector.analyze_with_ai_api(image)
                            
                            status_text.text("📊 Generating report...")
                            progress_bar.progress(80)
                            progress_bar.progress(100)
                            status_text.text("✅ Analysis complete!")
                            
                            # Clear progress indicators
                            import time
                            time.sleep(1)
                            progress_bar.empty()
                            status_text.empty()
                        
                        # SHOW RESULTS IMMEDIATELY
                        st.markdown("---")
                        st.markdown("## 📊 **ANALYSIS RESULTS**")
                        
                        if api_error:
                            st.error(f"⚠️ Analysis error: {api_error}")
                            st.info("💡 Please try again in a few moments")
                        else:
                            if api_result:
                                # Main result display
                                status = api_result.get('authenticity_status', 'unknown')
                                confidence = api_result.get('confidence_score', 0.0)
                                
                                # Big result banner
                                if status == 'authentic':
                                    st.success(f"✅ **AUTHENTIC** (Confidence: {confidence:.0%})")
                                elif status == 'fake':
                                    st.error(f"🚨 **FAKE/COUNTERFEIT** (Confidence: {confidence:.0%})")
                                else:
                                    st.warning(f"⚠️ **UNCERTAIN** (Confidence: {confidence:.0%})")
                                
                                # Product details
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.subheader("📝 **Product Information**")
                                    product_details = api_result.get('product_details', {})
                                    st.write(f"**Type:** {product_details.get('type', 'Unknown')}")
                                    st.write(f"**Brand:** {product_details.get('brand', 'Unknown')}")
                                    st.write(f"**Model:** {product_details.get('model', 'Unknown')}")
                                    st.write(f"**Color:** {product_details.get('color', 'Unknown')}")
                                
                                with col2:
                                    st.subheader("⭐ **Quality Assessment**")
                                    quality = api_result.get('quality_assessment', {})
                                    st.write(f"**Logo Quality:** {quality.get('logo_quality', 'N/A')}")
                                    st.write(f"**Material Quality:** {quality.get('material_quality', 'N/A')}")
                                    st.write(f"**Construction:** {quality.get('construction_quality', 'N/A')}")
                                    st.write(f"**Overall Craftsmanship:** {quality.get('overall_craftsmanship', 'N/A')}")
                                
                                # Issues and positive indicators
                                if api_result.get('detected_issues'):
                                    st.subheader("⚠️ **Issues Detected**")
                                    for issue in api_result['detected_issues']:
                                        st.warning(f"• {issue}")
                                
                                if api_result.get('positive_indicators'):
                                    st.subheader("✅ **Positive Indicators**")
                                    for positive in api_result['positive_indicators']:
                                        st.success(f"• {positive}")
                                
                                # Recommendations
                                if api_result.get('recommendations'):
                                    st.subheader("💡 **Expert Recommendations**")
                                    recs = api_result['recommendations']
                                    if recs.get('authenticity_verdict'):
                                        st.info(f"**Verdict:** {recs['authenticity_verdict']}")
                                    if recs.get('purchase_advice'):
                                        st.info(f"**Advice:** {recs['purchase_advice']}")
                                    if recs.get('verification_tips'):
                                        st.info(f"**Verification:** {recs['verification_tips']}")
                                
                                # Summary
                                if api_result.get('analysis_summary'):
                                    st.subheader("📖 **Summary**")
                                    st.write(api_result['analysis_summary'])
                            else:
                                st.info("Analysis completed but no detailed results available")
                
                except Exception as e:
                    st.error(f"❌ Error loading image: {str(e)}")
                    
            else:
                st.info("📎 No file uploaded yet")
                            status_text.text("� Initializing analysis...")
                            progress_bar.progress(20)
                            
                            status_text.text("📸 Processing image...")
                            progress_bar.progress(40)
                            
                            status_text.text("🧠 Running AI analysis...")
                            progress_bar.progress(60)
                            
                            # Make sure detector is initialized
                            if 'detector' not in st.session_state:
                                from enhanced_shoe_detector import EnhancedShoeDetector
                                st.session_state.detector = EnhancedShoeDetector()
                            
                            api_result, api_error = st.session_state.detector.analyze_with_ai_api(image)
                            
                            status_text.text("📊 Generating report...")
                            progress_bar.progress(80)
                            
                            progress_bar.progress(100)
                            status_text.text("✅ Analysis complete!")
                            
                            # Clear progress indicators
                            import time
                            time.sleep(1)
                            progress_bar.empty()
                            status_text.empty()
                            
                            # Store and display results
                            if api_error:
                                st.error(f"⚠️ Analysis error: {api_error}")
                                st.info("💡 Please check your internet connection and try again")
                            else:
                                st.session_state.analysis_result = api_result
                                st.session_state.analysis_error = api_error
                                st.session_state.show_results = True
                                
                                # Display results immediately
                                st.markdown("---")
                                st.subheader("📊 **ANALYSIS RESULTS**")
                                
                                if api_result:
                                    status = api_result.get('authenticity_status', 'unknown')
                                    confidence = api_result.get('confidence_score', 0.0)
                                    
                                    # Status display with color coding
                                    if status == 'authentic':
                                        st.success(f"✅ **AUTHENTIC** (Confidence: {confidence:.1%})")
                                    elif status == 'fake':
                                        st.error(f"🚨 **FAKE/COUNTERFEIT** (Confidence: {confidence:.1%})")
                                    else:
                                        st.warning(f"⚠️ **UNCERTAIN** (Confidence: {confidence:.1%})")
                                    
                                    # Show detailed analysis in organized sections
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.subheader("� **Product Details**")
                                        product_details = api_result.get('product_details', {})
                                        if product_details:
                                            st.write(f"**Type:** {product_details.get('type', 'Unknown')}")
                                            st.write(f"**Brand:** {product_details.get('brand', 'Unknown')}")
                                            st.write(f"**Model:** {product_details.get('model', 'Unknown')}")
                                            st.write(f"**Color:** {product_details.get('color', 'Unknown')}")
                                            st.write(f"**Price Range:** {product_details.get('estimated_price_range', 'Unknown')}")
                                    
                                    with col2:
                                        st.subheader("⭐ **Quality Assessment**")
                                        quality = api_result.get('quality_assessment', {})
                                        if quality:
                                            st.write(f"**Logo Quality:** {quality.get('logo_quality', 'N/A')}")
                                            st.write(f"**Material Quality:** {quality.get('material_quality', 'N/A')}")
                                            st.write(f"**Construction Quality:** {quality.get('construction_quality', 'N/A')}")
                                    
                                    # Detailed Analysis Section
                                    st.subheader("🔬 **Detailed Analysis**")
                                    detailed = api_result.get('detailed_analysis', {})
                                    if detailed:
                                        analysis_col1, analysis_col2 = st.columns(2)
                                        
                                        with analysis_col1:
                                            st.write(f"**Logo Analysis:** {detailed.get('logo_analysis', 'Not available')}")
                                            st.write(f"**Material Analysis:** {detailed.get('material_analysis', 'Not available')}")
                                            st.write(f"**Construction Analysis:** {detailed.get('construction_analysis', 'Not available')}")
                                        
                                        with analysis_col2:
                                            st.write(f"**Hardware Analysis:** {detailed.get('hardware_analysis', 'Not available')}")
                                            st.write(f"**Packaging Analysis:** {detailed.get('packaging_analysis', 'Not available')}")
                                    
                                    # Issues and Positive Indicators
                                    issues_col, positive_col = st.columns(2)
                                    
                                    with issues_col:
                                        st.subheader("⚠️ **Detected Issues**")
                                        issues = api_result.get('detected_issues', [])
                                        if issues and len(issues) > 0:
                                            for issue in issues:
                                                if issue != "No specific issues detected":
                                                    st.warning(f"• {issue}")
                                        else:
                                            st.success("✅ No specific issues detected")
                                    
                                    with positive_col:
                                        st.subheader("✅ **Positive Indicators**")
                                        positives = api_result.get('positive_indicators', [])
                                        if positives and len(positives) > 0:
                                            for positive in positives:
                                                st.success(f"• {positive}")
                                        else:
                                            st.info("No specific positive indicators noted")
                                    
        
        with camera_tab:
            st.write("📸 **Take a photo directly from your camera**")
            
            # Camera guidelines
            with st.expander("📋 Camera Photography Tips", expanded=False):
                st.markdown("""
                **For best results:**
                - 🔆 Use good lighting (natural light preferred)
                - 📐 Hold camera steady and keep product centered
                - 🔍 Focus on brand logos, labels, and construction details
                - 📏 Keep appropriate distance (not too close, not too far)
                - 🔄 Take multiple angles if needed
                - 📱 Hold device horizontally for wider view
                """)
            
            # Camera controls
            col_cam1, col_cam2 = st.columns(2)
            
            with col_cam1:
                auto_analyze = st.checkbox(
                    "🔄 Auto-analyze after capture",
                    value=True,
                    help="Automatically start analysis when photo is taken",
                    key="auto_analyze_checkbox"
                )
            
            with col_cam2:
                high_quality = st.checkbox(
                    "📸 High quality mode",
                    value=True,
                    help="Capture in higher resolution for better analysis",
                    key="high_quality_checkbox"
                )
            
            # Camera input
            camera_photo = st.camera_input(
                "Take a picture of the product",
                help="Position the product clearly in view and take a photo",
                key="main_camera_input"
            )
            
            if camera_photo is not None:
                uploaded_file = camera_photo
                
                # Camera mode success message
                st.success("📷 Photo captured successfully! Analysis starting...")
                
                # Show a preview of the captured image with enhanced info
                st.write("**📸 Captured Image Preview:**")
                col_preview1, col_preview2 = st.columns([1, 2])
                
                with col_preview1:
                    st.image(camera_photo, caption="Camera Capture", width=200)
                
                with col_preview2:
                    # Show image metadata if available
                    st.write("**📊 Capture Info:**")
                    st.write(f"📐 Format: {camera_photo.type}")
                    st.write(f"📏 Size: {camera_photo.size} bytes")
                    st.write(f"🕒 Captured: Just now")
                    
                    if auto_analyze:
                        st.info("🔄 Auto-analysis enabled - results will appear below")
            else:
                uploaded_file = None
    
    # Handle export functionality
    if st.session_state.get('show_export', False):
        st.info("📊 Export functionality - Feature coming soon!")
        if st.button("Close", key="close_btn"):
            st.session_state.show_export = False
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    if uploaded_file is not None:
        # Clear previous results when new image is uploaded
        if 'current_image' not in st.session_state or st.session_state.current_image != uploaded_file:
            st.session_state.show_results = False
            st.session_state.analysis_result = None
            st.session_state.analysis_error = None
            st.session_state.current_image = uploaded_file
        
        # Load and display original image
        try:
            # Handle sample images vs uploaded files
            if uploaded_file == "SAMPLE_IMAGE":
                # Load from stored sample path
                import os
                sample_path = st.session_state.get('sample_image_path')
                if sample_path and os.path.exists(sample_path):
                    image = Image.open(sample_path)
                else:
                    st.error("❌ Sample image path not found")
                    return
            elif hasattr(uploaded_file, 'read'):
                # This is a file upload object
                image = Image.open(uploaded_file)
            else:
                # This is already a PIL Image object
                image = uploaded_file
        except Exception as e:
            st.error(f"❌ Error loading image: {str(e)}")
            return
        
        # Apply image enhancement if enabled
        enhance_image = st.session_state.get('enhance_image', True)
        if enhance_image:
            # Simple image enhancement
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # Slightly increase contrast
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)  # Slightly increase sharpness
        
        with col1:
            st.subheader("📷 Original Image")
            if enhance_image:
                st.caption("✨ Image enhanced for better analysis")
            
            # Show detection mode info
            detection_mode = st.session_state.get('detection_mode', '⚖️ Balanced')
            mode_info = {
                "🔍 Precise": "High confidence required for determinations",
                "⚖️ Balanced": "Standard analysis with balanced criteria", 
                "🔬 Thorough": "Detailed analysis, may flag minor concerns"
            }
            st.caption(f"🎚️ {detection_mode}: {mode_info.get(detection_mode, '')}")
            
            # Show product category if selected
            product_category = st.session_state.get('product_category', '🔍 Auto-Detect')
            if product_category != '🔍 Auto-Detect':
                st.caption(f"📂 Category Focus: {product_category}")
            
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        with col2:
            st.subheader("📊 Analysis Results")
            
            # Show results if available
            if st.session_state.get('show_results', False):
                api_result = st.session_state.get('analysis_result')
                api_error = st.session_state.get('analysis_error')
                
                if api_error:
                    st.error("⚠️ AI analysis temporarily unavailable")
                    st.info("💡 Please try again or check your internet connection")
                else:
                    # Display main result
                    status = api_result.get('authenticity_status', 'unknown')
                    confidence = api_result.get('confidence_score', 0.0)
                    
                    # Status display with color coding
                    if status == 'authentic':
                        st.success(f"✅ **AUTHENTIC** (Confidence: {confidence:.1%})")
                    elif status == 'fake':
                        st.error(f"🚨 **FAKE/COUNTERFEIT** (Confidence: {confidence:.1%})")
                    else:
                        st.warning(f"⚠️ **UNCERTAIN** (Confidence: {confidence:.1%})")
                    
                    # Display comprehensive analysis
                    if api_result:
                        st.markdown("---")
                        st.subheader("🔬 Detailed Analysis")
                        display_comprehensive_analysis(api_result)
                        
                # Clear results button
                if st.button("🗑️ Clear Results", key="clear_results_btn1"):
                    st.session_state.show_results = False
                    st.session_state.analysis_result = None
                    st.session_state.analysis_error = None
                    st.rerun()
            else:
                st.info("📷 Upload an image and click 'Analyze' to see results")
        
        # MAIN ANALYZE BUTTON - Outside columns for maximum visibility
        st.markdown("---")
        st.markdown("## 🎯 Ready to Analyze Your Product!")
        
        col_analyze1, col_analyze2 = st.columns([3, 1])
        
        with col_analyze1:
            if st.button("🚀 **ANALYZE PRODUCT AUTHENTICITY**", key="main_analyze_btn", type="primary", use_container_width=True):
                # Run AI analysis with progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔍 Initializing analysis...")
                progress_bar.progress(20)
                
                with st.spinner("🤖 AI analyzing product authenticity..."):
                    status_text.text("📸 Processing image...")
                    progress_bar.progress(40)
                    
                    status_text.text("🧠 Running AI analysis...")
                    progress_bar.progress(60)
                    
                    api_result, api_error = st.session_state.detector.analyze_with_ai_api(image)
                    
                    status_text.text("📊 Generating report...")
                    progress_bar.progress(80)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Clear progress indicators after a moment
                import time
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # Store results in session state for persistent display
                st.session_state.analysis_result = api_result
                st.session_state.analysis_error = api_error
                st.session_state.show_results = True
                
                # Save results to history
                if api_result and not api_error:
                    from datetime import datetime
                    result_entry = {
                        'timestamp': datetime.now().strftime("%H:%M"),
                        'status': api_result.get('authenticity_status', 'unknown'),
                        'confidence': api_result.get('confidence_score', 0.0)
                    }
                    if 'results_history' not in st.session_state:
                        st.session_state.results_history = []
                    st.session_state.results_history.append(result_entry)
                    # Keep only last 10 results
                    if len(st.session_state.results_history) > 10:
                        st.session_state.results_history = st.session_state.results_history[-10:]
                
                # Force page refresh to show results
                st.rerun()
        
        with col_analyze2:
            # API test button for debugging
            if st.button("🔧 Test API", key="api_test_btn", use_container_width=True):
                with st.spinner("Testing API..."):
                    # Simple test without image
                    import requests
                    import json
                    
                    try:
                        test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={st.session_state.detector.gemini_api_key}"
                        test_payload = {
                            "contents": [{
                                "parts": [{"text": "Hello, can you respond with 'API test successful'?"}]
                            }]
                        }
                        
                        response = requests.post(test_url, headers={'Content-Type': 'application/json'}, json=test_payload, timeout=10)
                        
                        if response.status_code == 200:
                            st.success("✅ API Connected!")
                        else:
                            st.error(f"❌ API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ API Test Failed: {str(e)}")
        
        # Add API test button
        col_test1, col_test2 = st.columns(2)
        
        with col_test1:
            # Simple, clear analyze button
            if st.button("🚀 Analyze Product Authenticity", key="analyze_btn_duplicate", type="primary", use_container_width=True):
                # Run AI analysis with progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔍 Initializing analysis...")
                progress_bar.progress(20)
                
                with st.spinner("🤖 AI analyzing product authenticity..."):
                    status_text.text("📸 Processing image...")
                    progress_bar.progress(40)
                    
                    status_text.text("🧠 Running AI analysis...")
                    progress_bar.progress(60)
                    
                    api_result, api_error = st.session_state.detector.analyze_with_ai_api(image)
                    
                    status_text.text("📊 Generating report...")
                    progress_bar.progress(80)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Show debug info
                st.write(f"DEBUG: API Result: {api_result is not None}")
                st.write(f"DEBUG: API Error: {api_error}")
                
                # Clear progress indicators after a moment
                import time
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # Store results in session state for persistent display
                st.session_state.analysis_result = api_result
                st.session_state.analysis_error = api_error
                st.session_state.show_results = True
                
                # Save results to history
                if api_result and not api_error:
                    from datetime import datetime
                    result_entry = {
                        'timestamp': datetime.now().strftime("%H:%M"),
                        'status': api_result.get('authenticity_status', 'unknown'),
                        'confidence': api_result.get('confidence_score', 0.0)
                    }
                    if 'results_history' not in st.session_state:
                        st.session_state.results_history = []
                    st.session_state.results_history.append(result_entry)
                    # Keep only last 10 results
                    if len(st.session_state.results_history) > 10:
                        st.session_state.results_history = st.session_state.results_history[-10:]
                
                # Force page refresh to show results
                st.rerun()
        
        with col_test2:
            # API test button for debugging
            if st.button("🔧 Test API Connection", key="api_test_btn_duplicate", use_container_width=True):
                with st.spinner("Testing API..."):
                    # Simple test without image
                    import requests
                    import json
                    
                    try:
                        test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={st.session_state.detector.gemini_api_key}"
                        test_payload = {
                            "contents": [{
                                "parts": [{"text": "Hello, can you respond with 'API test successful'?"}]
                            }]
                        }
                        
                        response = requests.post(test_url, headers={'Content-Type': 'application/json'}, json=test_payload, timeout=10)
                        
                        if response.status_code == 200:
                            st.success("✅ API Connection Successful!")
                            st.write(f"Response: {response.json()}")
                        else:
                            st.error(f"❌ API Test Failed: {response.status_code}")
                            st.write(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ API Test Error: {str(e)}")
        
        # Display Results Section (persistent display using session state)
        if st.session_state.get('show_results', False):
            api_result = st.session_state.get('analysis_result')
            api_error = st.session_state.get('analysis_error')
            
            st.markdown("---")
            st.subheader("📊 Analysis Results")
            
            if api_error:
                st.error("⚠️ AI analysis temporarily unavailable")
                st.info("💡 Please try again or check your internet connection")
            else:
                # Display main result
                status = api_result.get('authenticity_status', 'unknown')
                confidence = api_result.get('confidence_score', 0.0)
                
                # Status display with color coding
                if status == 'authentic':
                    st.success(f"✅ **AUTHENTIC** (Confidence: {confidence:.1%})")
                elif status == 'fake':
                    st.error(f"🚨 **FAKE/COUNTERFEIT** (Confidence: {confidence:.1%})")
                else:
                    st.warning(f"⚠️ **UNCERTAIN** (Confidence: {confidence:.1%})")
                
                # Display comprehensive analysis
                if api_result:
                    st.markdown("---")
                    st.subheader("🔬 Detailed Analysis")
                    display_comprehensive_analysis(api_result)
                    
            # Clear results button
            if st.button("🗑️ Clear Results", key="clear_results_btn2"):
                st.session_state.show_results = False
                st.session_state.analysis_result = None
                st.session_state.analysis_error = None
                st.rerun()
        
        else:
            # Show instruction when no analysis has been run
            st.markdown("---")
            st.info("� Upload an image and click 'Analyze Product Authenticity' to see results")
            st.info("📸 **Image uploaded successfully!** Click the 'Analyze Product Authenticity' button above to start the analysis.")

def display_comprehensive_analysis(api_result):
    """Display comprehensive analysis from Gemini API"""
    if not api_result:
        return
    
    # Product Details Section
    product_details = api_result.get('product_details', {})
    if product_details:
        st.subheader("🏷️ Product Information")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if product_details.get('type'):
                st.metric("📦 Product Type", product_details['type'])
            if product_details.get('brand'):
                st.metric("🏭 Brand", product_details['brand'])
        
        with col2:
            if product_details.get('model'):
                st.metric("🔖 Model", product_details['model'])
            if product_details.get('color'):
                st.metric("🎨 Color", product_details['color'])
        
        with col3:
            if product_details.get('estimated_price_range'):
                st.metric("💰 Est. Price Range", product_details['estimated_price_range'])
    
    # Key metrics overview
    st.subheader("🎯 Authenticity Assessment")
    col1, col2, col3 = st.columns(3)
    
    status = api_result.get('authenticity_status', 'unknown')
    confidence = api_result.get('confidence_score', 0.0)
    
    with col1:
        status_emoji = {"authentic": "✅", "fake": "🚨", "uncertain": "⚠️"}.get(status, "❓")
        st.metric("🎯 Authenticity Status", f"{status_emoji} {status.upper()}")
    
    with col2:
        st.metric("📊 AI Confidence", f"{confidence:.1%}")
    
    with col3:
        quality = api_result.get('quality_assessment', {})
        overall_quality = quality.get('overall_craftsmanship', 'unknown')
        st.metric("🔍 Overall Quality", overall_quality.title())
    
    # Detailed Analysis Sections
    detailed_analysis = api_result.get('detailed_analysis', {})
    if detailed_analysis:
        st.subheader("🔬 Detailed Component Analysis")
        
        analysis_tabs = st.tabs(["🏷️ Logo", "🧵 Material", "🔨 Construction", "⚙️ Hardware", "📦 Packaging"])
        
        with analysis_tabs[0]:  # Logo Analysis
            logo_analysis = detailed_analysis.get('logo_analysis', 'No logo analysis available')
            # Truncate if too long
            if len(logo_analysis) > 150:
                logo_analysis = logo_analysis[:150] + "..."
            st.write(logo_analysis)
        
        with analysis_tabs[1]:  # Material Analysis
            material_analysis = detailed_analysis.get('material_analysis', 'No material analysis available')
            if len(material_analysis) > 150:
                material_analysis = material_analysis[:150] + "..."
            st.write(material_analysis)
        
        with analysis_tabs[2]:  # Construction Analysis
            construction_analysis = detailed_analysis.get('construction_analysis', 'No construction analysis available')
            if len(construction_analysis) > 150:
                construction_analysis = construction_analysis[:150] + "..."
            st.write(construction_analysis)
        
        with analysis_tabs[3]:  # Hardware Analysis
            hardware_analysis = detailed_analysis.get('hardware_analysis', 'No hardware analysis available')
            if len(hardware_analysis) > 150:
                hardware_analysis = hardware_analysis[:150] + "..."
            st.write(hardware_analysis)
        
        with analysis_tabs[4]:  # Packaging Analysis
            packaging_analysis = detailed_analysis.get('packaging_analysis', 'No packaging analysis available')
            if len(packaging_analysis) > 150:
                packaging_analysis = packaging_analysis[:150] + "..."
            st.write(packaging_analysis)
    
    # Quality breakdown with enhanced details
    st.subheader("🔬 Quality Analysis Breakdown")
    
    quality_data = []
    quality_assessment = api_result.get('quality_assessment', {})
    
    for aspect, rating in quality_assessment.items():
        quality_data.append({
            'Aspect': aspect.replace('_', ' ').title(),
            'Rating': rating.title(),
            'Status': "🟢" if rating in ["excellent", "good"] else "🟡" if rating == "poor" else "🔴" if rating == "missing" else "⚪"
        })
    
    if quality_data:
        df_quality = pd.DataFrame(quality_data)
        st.dataframe(df_quality, use_container_width=True, hide_index=True)
    
    # Issues and positive indicators
    col_issues, col_positive = st.columns(2)
    
    with col_issues:
        issues = api_result.get('detected_issues', [])
        if issues:
            st.subheader("⚠️ Issues Detected")
            for issue in issues:
                st.write(f"🔴 {issue}")
        else:
            st.subheader("✅ No Issues Detected")
            st.write("AI analysis found no major authenticity concerns")
    
    with col_positive:
        positive_indicators = api_result.get('positive_indicators', [])
        if positive_indicators:
            st.subheader("✅ Positive Indicators")
            for indicator in positive_indicators:
                st.write(f"🟢 {indicator}")
        else:
            st.subheader("ℹ️ No Specific Positives")
            st.write("No specific authentic features highlighted")
    
    # Recommendations section
    recommendations = api_result.get('recommendations', {})
    if recommendations:
        st.subheader("💡 Expert Recommendations")
        
        rec_tabs = st.tabs(["🎯 Verdict", "💰 Purchase Advice", "🔍 Verification Tips"])
        
        with rec_tabs[0]:
            verdict = recommendations.get('authenticity_verdict', 'No verdict available')
            if len(verdict) > 100:
                verdict = verdict[:100] + "..."
            st.write(verdict)
        
        with rec_tabs[1]:
            purchase_advice = recommendations.get('purchase_advice', 'No purchase advice available')
            if len(purchase_advice) > 100:
                purchase_advice = purchase_advice[:100] + "..."
            st.write(purchase_advice)
        
        with rec_tabs[2]:
            verification_tips = recommendations.get('verification_tips', 'No verification tips available')
            if len(verification_tips) > 100:
                verification_tips = verification_tips[:100] + "..."
            st.write(verification_tips)
    
    # Analysis summary and expert notes
    summary = api_result.get('analysis_summary', '')
    expert_notes = api_result.get('expert_notes', '')
    
    if summary or expert_notes:
        st.subheader("📝 Key Findings")
        
        if summary:
            # Limit summary to first 200 characters if too long
            if len(summary) > 200:
                summary = summary[:200] + "..."
            st.write(summary)
        
        if expert_notes:
            # Show expert notes in a more compact format
            st.info(f"💡 {expert_notes}")

def display_yolo_results(detections, compact=False):
    """Display YOLO detection results"""
    if not detections:
        st.warning("No objects detected")
        return
    
    if not compact:
        st.markdown("---")
        st.subheader("📊 YOLO Detection Summary")
    
    # Metrics
    fake_count = sum(1 for d in detections if d['class'] == 'fake')
    real_count = sum(1 for d in detections if d['class'] == 'real')
    total_count = len(detections)
    
    if compact:
        st.write(f"**Total:** {total_count} | **Fake:** {fake_count} | **Real:** {real_count}")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🚨 Fake Products", fake_count)
        with col2:
            st.metric("✅ Real Products", real_count)
        with col3:
            st.metric("📦 Total Detections", total_count)
    
    # Results table
    if not compact:
        df = pd.DataFrame(detections)
        st.dataframe(df, use_container_width=True)

def display_analysis_results(api_result, compact=False):
    """Display AI analysis results"""
    if not api_result:
        st.warning("No analysis results")
        return
    
    if not compact:
        st.markdown("---")
        st.subheader("📊 AI Model Detection")
    
    # Main status
    status = api_result.get('authenticity_status', 'unknown')
    confidence = api_result.get('confidence_score', 0.0)
    
    # Status styling
    if status == 'authentic':
        status_color = "🟢"
        status_text = "AUTHENTIC"
    elif status == 'fake':
        status_color = "🔴"
        status_text = "FAKE/COUNTERFEIT"
    else:
        status_color = "🟡"
        status_text = "UNCERTAIN"
    
    st.markdown(f"### {status_color} **{status_text}**")
    st.markdown(f"**Confidence:** {confidence:.1%}")
    
    # Quality assessment
    quality = api_result.get('quality_assessment', {})
    if quality and not compact:
        st.markdown("#### 🔍 Quality Assessment:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Logo Quality:** {quality.get('logo_quality', 'unknown')}")
        with col2:
            st.write(f"**Material Quality:** {quality.get('material_quality', 'unknown')}")
        with col3:
            st.write(f"**Construction:** {quality.get('construction_quality', 'unknown')}")
    
    # Issues found
    issues = api_result.get('detected_issues', [])
    if issues and not compact:
        st.markdown("#### ⚠️ Issues Detected:")
        for issue in issues:
            st.write(f"• {issue}")
    
    # Recommendation
    recommendation = api_result.get('recommendation', '')
    if recommendation:
        if compact:
            st.write(f"**Recommendation:** {recommendation}")
        else:
            st.markdown(f"#### 💡 **Recommendation:** {recommendation}")
    
    # Analysis summary
    summary = api_result.get('analysis_summary', '')
    if summary and not compact:
        st.markdown("#### 📝 Analysis Summary:")
        st.write(summary)

def display_comparison_results(yolo_detections, gemini_result):
    """Display comparison between YOLO and Gemini results"""
    st.markdown("### 🔄 AI Analysis Comparison")
    
    # YOLO summary
    yolo_fake_count = sum(1 for d in yolo_detections if d['class'] == 'fake')
    yolo_verdict = "FAKE DETECTED" if yolo_fake_count > 0 else "NO FAKES DETECTED"
    
    # Gemini summary
    gemini_status = gemini_result.get('authenticity_status', 'unknown')
    gemini_verdict = {
        'authentic': 'AUTHENTIC',
        'fake': 'FAKE/COUNTERFEIT', 
        'uncertain': 'UNCERTAIN'
    }.get(gemini_status, 'UNKNOWN')
    
    # Comparison table
    comparison_data = {
        'Analysis Type': ['🎯 YOLO Model', '🤖 Gemini AI'],
        'Verdict': [yolo_verdict, gemini_verdict],
        'Confidence': [
            f"{max([d['confidence'] for d in yolo_detections], default=0):.1%}" if yolo_detections else "N/A",
            f"{gemini_result.get('confidence_score', 0):.1%}"
        ],
        'Details': [
            f"{len(yolo_detections)} objects detected",
            f"Quality assessment completed"
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
    
    # Agreement analysis
    yolo_says_fake = yolo_fake_count > 0
    gemini_says_fake = gemini_status == 'fake'
    
    if yolo_says_fake and gemini_says_fake:
        st.error("🚨 **Both AI systems agree: LIKELY FAKE**")
    elif not yolo_says_fake and gemini_status == 'authentic':
        st.success("✅ **Both AI systems agree: LIKELY AUTHENTIC**")
    elif yolo_says_fake and gemini_status == 'authentic':
        st.warning("⚠️ **Disagreement: Detection model vs AI analysis**")
    elif not yolo_says_fake and gemini_says_fake:
        st.warning("⚠️ **Disagreement: Different AI assessments**")
    else:
        st.info("ℹ️ **Results inconclusive - manual review recommended**")

def metrics_page():
    """Performance metrics page"""
    st.header("📈 Model Performance Metrics")
    
    # Check if training results exist
    results_path = "runs/fake_product_detector27/results.csv"
    
    if os.path.exists(results_path):
        # Load training results
        df = pd.read_csv(results_path)
        
        # Training progress
        st.subheader("📊 Training Progress")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Loss curves
            fig_loss = go.Figure()
            if 'train/box_loss' in df.columns:
                fig_loss.add_trace(go.Scatter(
                    x=df.index, y=df['train/box_loss'],
                    mode='lines', name='Box Loss'
                ))
            if 'train/cls_loss' in df.columns:
                fig_loss.add_trace(go.Scatter(
                    x=df.index, y=df['train/cls_loss'],
                    mode='lines', name='Class Loss'
                ))
            fig_loss.update_layout(title="Training Loss", xaxis_title="Epoch", yaxis_title="Loss")
            st.plotly_chart(fig_loss, use_container_width=True)
        
        with col2:
            # mAP curves
            fig_map = go.Figure()
            if 'metrics/mAP50(B)' in df.columns:
                fig_map.add_trace(go.Scatter(
                    x=df.index, y=df['metrics/mAP50(B)'],
                    mode='lines', name='mAP50'
                ))
            if 'metrics/mAP50-95(B)' in df.columns:
                fig_map.add_trace(go.Scatter(
                    x=df.index, y=df['metrics/mAP50-95(B)'],
                    mode='lines', name='mAP50-95'
                ))
            fig_map.update_layout(title="mAP Metrics", xaxis_title="Epoch", yaxis_title="mAP")
            st.plotly_chart(fig_map, use_container_width=True)
        
        # Final metrics summary
        st.subheader("📋 Final Training Metrics")
        final_metrics = df.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Box Loss", f"{final_metrics.get('train/box_loss', 0):.4f}")
        with col2:
            st.metric("Class Loss", f"{final_metrics.get('train/cls_loss', 0):.4f}")
        with col3:
            st.metric("mAP50", f"{final_metrics.get('metrics/mAP50(B)', 0):.4f}")
        with col4:
            st.metric("mAP50-95", f"{final_metrics.get('metrics/mAP50-95(B)', 0):.4f}")
        
        # Training images
        st.subheader("🖼️ Training Visualizations")
        
        viz_files = [
            ("Training Results", "runs/fake_product_detector27/results.png"),
            ("Confusion Matrix", "runs/fake_product_detector27/confusion_matrix.png"),
            ("PR Curve", "runs/fake_product_detector27/BoxPR_curve.png"),
            ("Training Batch", "runs/fake_product_detector27/train_batch0.jpg")
        ]
        
        cols = st.columns(2)
        for i, (title, path) in enumerate(viz_files):
            if os.path.exists(path):
                with cols[i % 2]:
                    st.image(path, caption=title)
    else:
        st.warning("📊 Training results not found. Please complete model training first.")

def batch_processing_page(conf_threshold):
    """Batch processing page"""
    st.header("📸 Batch Processing")
    
    uploaded_files = st.file_uploader(
        "Choose multiple images...",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Upload multiple images for batch processing",
        key="batch_file_uploader"
    )
    
    if uploaded_files:
        st.write(f"📁 Processing {len(uploaded_files)} images...")
        
        # Progress bar
        progress_bar = st.progress(0)
        results_container = st.container()
        
        all_detections = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Process image
            image = Image.open(uploaded_file)
            results, error = st.session_state.detector.detect_products(image, conf_threshold)
            
            if not error:
                annotated_image, detections = st.session_state.detector.draw_detections(image, results)
                
                # Store results
                for detection in detections:
                    detection['filename'] = uploaded_file.name
                all_detections.extend(detections)
                
                # Display results
                with results_container:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(image, caption=f"Original: {uploaded_file.name}", width=300)
                    with col2:
                        st.image(annotated_image, caption=f"Detected: {uploaded_file.name}", width=300)
        
        # Summary statistics
        if all_detections:
            st.markdown("---")
            st.subheader("📊 Batch Processing Summary")
            
            df = pd.DataFrame(all_detections)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                total_fake = len(df[df['class'] == 'fake'])
                st.metric("🚨 Total Fake Products", total_fake)
            with col2:
                total_real = len(df[df['class'] == 'real'])
                st.metric("✅ Total Real Products", total_real)
            with col3:
                avg_confidence = df['confidence'].mean()
                st.metric("📊 Average Confidence", f"{avg_confidence:.3f}")
            
            # Detailed results
            st.subheader("📋 Detailed Results")
            st.dataframe(df, use_container_width=True)
            
            # Download results
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download Results as CSV",
                data=csv,
                file_name="detection_results.csv",
                mime="text/csv"
            )

def model_info_page():
    """Model information page"""
    st.header("ℹ️ Model Information")
    
    # Model details
    st.subheader("🏋️ Model Details")
    
    if st.session_state.detector.model:
        model_info = {
            "Model Path": st.session_state.detector.model_path,
            "Model Type": "YOLOv8",
            "Classes": list(st.session_state.detector.model.names.values()),
            "Input Size": "640x640",
            "Framework": "PyTorch"
        }
        
        for key, value in model_info.items():
            st.write(f"**{key}:** {value}")
    
    # Training dataset info
    st.subheader("📊 Dataset Information")
    dataset_info = {
        "Training Images": "5 (limited dataset)",
        "Validation Images": "5",
        "Classes": ["real", "fake"],
        "Format": "YOLO format (.txt annotations)"
    }
    
    for key, value in dataset_info.items():
        st.write(f"**{key}:** {value}")
    
    # Performance notes
    st.subheader("⚠️ Performance Notes")
    st.warning("""
    **Current Limitations:**
    - Very small training dataset (only 5 images)
    - mAP50 = 0.0000 (low performance)
    - Recommended: Gather 100+ labeled images per class
    
    **Improvement Suggestions:**
    1. Collect more diverse training data
    2. Verify annotation quality
    3. Consider data augmentation
    4. Retrain with larger dataset
    """)
    
    # Usage instructions
    st.subheader("📖 Usage Instructions")
    st.markdown("""
    1. **Single Detection**: Upload one image in the Detection tab
    2. **Batch Processing**: Upload multiple images for bulk analysis
    3. **Adjust Threshold**: Use sidebar to modify confidence threshold
    4. **View Metrics**: Check training performance in Metrics tab
    5. **Download Results**: Save detection results as CSV
    """)

def display_batch_analysis_results(all_results):
    """Display results from batch AI analysis"""
    if not all_results:
        return
    
    # Summary statistics
    st.markdown("---")
    st.subheader("📊 Batch Analysis Summary")
    
    # Calculate metrics
    successful_analyses = [r for r in all_results if not r['api_error']]
    failed_analyses = [r for r in all_results if r['api_error']]
    
    authentic_count = 0
    fake_count = 0
    uncertain_count = 0
    
    for result in successful_analyses:
        if result['api_result']:
            status = result['api_result'].get('authenticity_status', 'uncertain')
            if status == 'authentic':
                authentic_count += 1
            elif status == 'fake':
                fake_count += 1
            else:
                uncertain_count += 1
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✅ Authentic", authentic_count)
    with col2:
        st.metric("🚨 Fake/Counterfeit", fake_count)
    with col3:
        st.metric("⚠️ Uncertain", uncertain_count)
    with col4:
        st.metric("❌ Failed Analysis", len(failed_analyses))
    
    # Results table
    st.subheader("📋 Detailed Results")
    
    table_data = []
    for result in all_results:
        if result['api_error']:
            table_data.append({
                'Filename': result['filename'],
                'Status': '❌ Error',
                'Authenticity': 'Analysis Failed',
                'Confidence': 'N/A',
                'Issues': result['api_error']
            })
        elif result['api_result']:
            api_result = result['api_result']
            status_emoji = {
                'authentic': '✅',
                'fake': '🚨',
                'uncertain': '⚠️'
            }.get(api_result.get('authenticity_status', 'uncertain'), '❓')
            
            issues = api_result.get('detected_issues', [])
            issues_text = ', '.join(issues[:2]) if issues else 'None detected'
            if len(issues) > 2:
                issues_text += f' (+{len(issues)-2} more)'
            
            table_data.append({
                'Filename': result['filename'],
                'Status': f"{status_emoji} Success",
                'Authenticity': api_result.get('authenticity_status', 'unknown').title(),
                'Confidence': f"{api_result.get('confidence_score', 0):.1%}",
                'Issues': issues_text
            })
    
    if table_data:
        df_results = pd.DataFrame(table_data)
        st.dataframe(df_results, use_container_width=True, hide_index=True)
    
    # Individual image results
    st.subheader("🖼️ Individual Image Analysis")
    
    for result in all_results:
        with st.expander(f"📷 {result['filename']} - Analysis Details"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(result['image'], caption=result['filename'], use_column_width=True)
            
            with col2:
                if result['api_error']:
                    st.error(f"Analysis failed: {result['api_error']}")
                elif result['api_result']:
                    display_analysis_results(result['api_result'], compact=True)
                else:
                    st.warning("No analysis result available")

if __name__ == "__main__":
    main()