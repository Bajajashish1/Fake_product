"""
Enhanced Shoe Detection System
Combines multiple approaches for better shoe analysis
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import plotly.express as px
import plotly.graph_objects as go
from ultralytics import YOLO
import pandas as pd
import base64
import io

class EnhancedShoeDetector:
    def __init__(self):
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load the trained model with fallback options"""
        model_paths = [
            "runs/fake_product_detector27/weights/best.pt",
            "runs/fake_product_detector26/weights/best.pt", 
            "runs/fake_product_detector25/weights/best.pt",
            "yolov8m.pt"  # Fallback to pretrained model
        ]
        
        for path in model_paths:
            try:
                self.model = YOLO(path)
                st.success(f"✅ Model loaded: {path}")
                return
            except Exception as e:
                continue
        
        st.error("❌ Could not load any model")
        
    def analyze_shoe_image(self, image, conf_threshold=0.3):
        """Comprehensive shoe image analysis"""
        results = {
            'detections': [],
            'image_analysis': {},
            'quality_score': 0,
            'recommendations': []
        }
        
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_cv = img_array
            
        # 1. YOLO Detection
        yolo_results = self.run_yolo_detection(image, conf_threshold)
        results['detections'].extend(yolo_results)
        
        # 2. Image Quality Analysis
        quality_analysis = self.analyze_image_quality(img_cv)
        results['image_analysis'] = quality_analysis
        results['quality_score'] = quality_analysis['overall_score']
        
        # 3. Color and Texture Analysis
        color_analysis = self.analyze_colors_and_textures(img_cv)
        results['image_analysis'].update(color_analysis)
        
        # 4. Generate Recommendations
        results['recommendations'] = self.generate_recommendations(results)
        
        return results
    
    def run_yolo_detection(self, image, conf_threshold):
        """Run YOLO detection with enhanced result processing"""
        detections = []
        
        if self.model is None:
            return [{
                'class': 'unknown',
                'confidence': 0.0,
                'bbox': [0, 0, 100, 100],
                'status': 'Model not loaded',
                'source': 'YOLO'
            }]
        
        try:
            # Run prediction
            results = self.model(image, conf=conf_threshold)
            
            if len(results) > 0 and len(results[0].boxes) > 0:
                boxes = results[0].boxes
                
                for box in boxes:
                    # Get detection info
                    conf = float(box.conf.cpu().numpy()[0])
                    cls = int(box.cls.cpu().numpy()[0])
                    bbox = box.xyxy.cpu().numpy()[0].astype(int)
                    
                    # Map class to name
                    class_names = ['real', 'fake']
                    class_name = class_names[cls] if cls < len(class_names) else 'unknown'
                    
                    # Determine authenticity status
                    if class_name == 'fake':
                        status = 'LIKELY FAKE - High Risk' if conf > 0.7 else 'POTENTIALLY FAKE - Medium Risk'
                        risk_level = 'high' if conf > 0.7 else 'medium'
                    else:
                        status = 'AUTHENTIC - Low Risk' if conf > 0.7 else 'POSSIBLY AUTHENTIC - Low Risk'
                        risk_level = 'low'
                    
                    detections.append({
                        'class': class_name,
                        'confidence': conf,
                        'bbox': bbox.tolist(),
                        'status': status,
                        'risk_level': risk_level,
                        'source': 'YOLO'
                    })
            else:
                # No detections found - provide helpful feedback
                detections.append({
                    'class': 'no_detection',
                    'confidence': 0.0,
                    'bbox': [0, 0, 50, 50],
                    'status': 'No products detected - try adjusting confidence or retaking photo',
                    'risk_level': 'unknown',
                    'source': 'YOLO'
                })
                
        except Exception as e:
            detections.append({
                'class': 'error',
                'confidence': 0.0,
                'bbox': [0, 0, 50, 50],
                'status': f'Detection error: {str(e)}',
                'risk_level': 'unknown',
                'source': 'YOLO'
            })
        
        return detections
    
    def analyze_image_quality(self, img_cv):
        """Analyze image quality factors important for shoe detection"""
        analysis = {}
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # 1. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 100, 10) / 10  # Normalize to 0-1
        
        # 2. Brightness
        brightness = np.mean(gray) / 255
        
        # 3. Contrast
        contrast = gray.std() / 255
        
        # 4. Image size
        height, width = img_cv.shape[:2]
        size_score = min(min(height, width) / 300, 1)  # Prefer images >= 300px
        
        # 5. Overall quality score
        overall_score = np.mean([sharpness_score, 
                               1 - abs(brightness - 0.5) * 2,  # Prefer moderate brightness
                               contrast,
                               size_score]) * 100
        
        analysis.update({
            'sharpness': round(sharpness_score * 100, 1),
            'brightness': round(brightness * 100, 1),
            'contrast': round(contrast * 100, 1),
            'size_quality': round(size_score * 100, 1),
            'overall_score': round(overall_score, 1),
            'dimensions': f"{width}x{height}"
        })
        
        return analysis
    
    def analyze_colors_and_textures(self, img_cv):
        """Analyze color distribution and texture patterns"""
        analysis = {}
        
        # Color analysis
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        
        # Dominant colors
        pixels = img_rgb.reshape(-1, 3)
        
        # Calculate color statistics
        mean_color = np.mean(pixels, axis=0)
        color_variance = np.var(pixels, axis=0)
        
        # Color diversity (simplified)
        unique_colors = len(np.unique(pixels.view(np.dtype((np.void, pixels.dtype.itemsize * pixels.shape[1])))))
        color_diversity = min(unique_colors / 1000, 1) * 100  # Normalize
        
        analysis.update({
            'dominant_color_rgb': mean_color.astype(int).tolist(),
            'color_variance': color_variance.tolist(),
            'color_diversity': round(color_diversity, 1)
        })
        
        return analysis
    
    def generate_recommendations(self, results):
        """Generate helpful recommendations based on analysis"""
        recommendations = []
        
        quality = results['image_analysis']
        detections = results['detections']
        
        # Quality-based recommendations
        if quality['overall_score'] < 50:
            recommendations.append("📸 Image quality is low - try better lighting and focus")
        
        if quality['sharpness'] < 30:
            recommendations.append("🔍 Image appears blurry - ensure camera is steady and focused")
        
        if quality['brightness'] < 20:
            recommendations.append("💡 Image is too dark - increase lighting")
        elif quality['brightness'] > 80:
            recommendations.append("☀️ Image is too bright - reduce lighting or use diffused light")
        
        if quality['contrast'] < 20:
            recommendations.append("🌈 Low contrast - try different background or lighting angle")
        
        # Detection-based recommendations
        if len(detections) == 0 or detections[0]['class'] == 'no_detection':
            recommendations.extend([
                "🎯 No products detected - ensure shoes are clearly visible",
                "📏 Try zooming in on the shoes or getting closer",
                "🔄 Lower the confidence threshold if objects are partially visible"
            ])
        
        # Specific shoe recommendations
        recommendations.extend([
            "👟 For best results with shoes: show the whole shoe including sole",
            "🏷️ Include any brand labels or logos in the image",
            "📐 Take photos from multiple angles for comprehensive analysis"
        ])
        
        return recommendations
    
    def create_annotated_image(self, image, detections):
        """Create annotated image with detection boxes and labels"""
        img_annotated = image.copy()
        draw = ImageDraw.Draw(img_annotated)
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        colors = {
            'real': '#10b981',      # Green for authentic
            'fake': '#ef4444',      # Red for fake
            'no_detection': '#94a3b8',  # Gray for no detection
            'error': '#f59e0b'      # Orange for errors
        }
        
        for detection in detections:
            if detection['class'] in ['no_detection', 'error']:
                continue
                
            bbox = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            # Draw bounding box
            color = colors.get(class_name, '#6b7280')
            draw.rectangle(bbox, outline=color, width=3)
            
            # Draw label
            label = f"{class_name.upper()}: {confidence:.1%}"
            label_bbox = draw.textbbox((bbox[0], bbox[1] - 25), label, font=font)
            draw.rectangle(label_bbox, fill=color)
            draw.text((bbox[0], bbox[1] - 25), label, fill='white', font=font)
        
        return img_annotated

def main():
    st.set_page_config(
        page_title="Enhanced Shoe Detector",
        page_icon="👟",
        layout="wide"
    )
    
    st.title("👟 Enhanced Shoe Authentication System")
    st.markdown("**Comprehensive analysis for footwear authenticity detection**")
    
    # Initialize detector
    if 'shoe_detector' not in st.session_state:
        st.session_state.shoe_detector = EnhancedShoeDetector()
    
    # Sidebar controls
    st.sidebar.header("⚙️ Detection Settings")
    conf_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.3, 0.05)
    show_quality_analysis = st.sidebar.checkbox("Show Quality Analysis", True)
    show_color_analysis = st.sidebar.checkbox("Show Color Analysis", True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a shoe image", 
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of shoes for authenticity analysis"
    )
    
    if uploaded_file:
        # Load and display original image
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📷 Original Image")
            st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
        
        # Run analysis
        with st.spinner("🔍 Analyzing shoe authenticity..."):
            results = st.session_state.shoe_detector.analyze_shoe_image(image, conf_threshold)
        
        with col2:
            st.subheader("🎯 Detection Results")
            
            # Create annotated image
            annotated_img = st.session_state.shoe_detector.create_annotated_image(image, results['detections'])
            st.image(annotated_img, caption="Detected Objects", use_column_width=True)
        
        # Results Analysis
        st.markdown("---")
        st.subheader("📊 Analysis Report")
        
        # Detection Summary
        detections = results['detections']
        if detections and detections[0]['class'] not in ['no_detection', 'error']:
            # Summary metrics
            fake_count = sum(1 for d in detections if d['class'] == 'fake')
            real_count = sum(1 for d in detections if d['class'] == 'real')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Total Detections", len(detections))
            with col2:
                st.metric("✅ Authentic", real_count)
            with col3:
                st.metric("🚨 Suspicious", fake_count)
            
            # Detailed results table
            df_data = []
            for detection in detections:
                df_data.append({
                    'Class': detection['class'].title(),
                    'Confidence': f"{detection['confidence']:.1%}",
                    'Status': detection['status'],
                    'Risk Level': detection['risk_level'].title()
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        else:
            # No valid detections
            st.warning("⚠️ No shoes detected in the image")
            if detections:
                st.info(f"ℹ️ {detections[0]['status']}")
        
        # Quality Analysis
        if show_quality_analysis:
            st.subheader("🔬 Image Quality Analysis")
            quality = results['image_analysis']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📐 Overall Quality", f"{quality['overall_score']:.1f}%")
            with col2:
                st.metric("🔍 Sharpness", f"{quality['sharpness']:.1f}%")
            with col3:
                st.metric("💡 Brightness", f"{quality['brightness']:.1f}%")
            with col4:
                st.metric("🌈 Contrast", f"{quality['contrast']:.1f}%")
            
            # Quality chart
            quality_metrics = ['Sharpness', 'Brightness', 'Contrast', 'Size Quality']
            quality_values = [quality['sharpness'], quality['brightness'], quality['contrast'], quality['size_quality']]
            
            fig = px.bar(
                x=quality_metrics,
                y=quality_values,
                title="Image Quality Metrics",
                color=quality_values,
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Color Analysis
        if show_color_analysis:
            st.subheader("🎨 Color Analysis")
            color_info = results['image_analysis']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🌈 Color Diversity", f"{color_info['color_diversity']:.1f}%")
                st.metric("📏 Dimensions", color_info['dimensions'])
            
            with col2:
                # Display dominant color
                rgb = color_info['dominant_color_rgb']
                st.markdown(f"**Dominant Color:** RGB({rgb[0]}, {rgb[1]}, {rgb[2]})")
                st.markdown(
                    f'<div style="width: 100px; height: 50px; background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border: 1px solid #ccc;"></div>',
                    unsafe_allow_html=True
                )
        
        # Recommendations
        st.subheader("💡 Recommendations")
        recommendations = results['recommendations']
        
        for rec in recommendations:
            st.markdown(f"• {rec}")
    
    else:
        # Instructions for users
        st.info("👆 Upload a shoe image to start analysis")
        
        st.subheader("📋 How to get the best results:")
        st.markdown("""
        **📸 Photography Tips:**
        - Use good lighting (natural light preferred)
        - Ensure shoes are in focus and clearly visible
        - Include the entire shoe in the frame
        - Avoid shadows and reflections
        
        **🎯 Detection Tips:**
        - Show brand labels and logos clearly
        - Capture details like stitching and materials
        - Take photos from multiple angles if possible
        - Use a neutral background for better contrast
        
        **⚙️ Settings:**
        - Adjust confidence threshold if needed
        - Lower values detect more objects (may include false positives)
        - Higher values are more selective (may miss some objects)
        """)

if __name__ == "__main__":
    main()