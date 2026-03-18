import streamlit as st
import cv2
import numpy as np
from PIL import Image
import requests
import json
import base64
import io
import time
import os
import pandas as pd
import plotly.graph_objects as go
from ultralytics import YOLO
from pathlib import Path
import pickle
from datetime import datetime
import plotly.express as px
from database_manager import DatabaseManager

# Database-powered History Management
class HistoryManager:
    def __init__(self):
        """Initialize with SQLite database backend"""
        self.db_manager = DatabaseManager()
    
    def save_analysis(self, analysis_data, image_data=None, image_filename=None):
        """Save analysis to database"""
        try:
            analysis_id = self.db_manager.save_analysis(analysis_data, image_data, image_filename)
            if analysis_id:
                return True
            return False
        except Exception as e:
            st.error(f"Error saving analysis: {str(e)}")
            return False
    
    def load_history(self, limit=100, filter_by=None):
        """Load analysis history from database"""
        try:
            return self.db_manager.get_analysis_history(limit=limit, filter_by=filter_by)
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")
            return []
    
    def get_analysis_by_id(self, analysis_id):
        """Get specific analysis by ID"""
        try:
            return self.db_manager.get_analysis_by_id(analysis_id)
        except Exception as e:
            st.error(f"Error loading analysis: {str(e)}")
            return None
    
    def update_analysis(self, analysis_id, updates):
        """Update analysis (favorite, flagged, notes, etc.)"""
        try:
            return self.db_manager.update_analysis(analysis_id, updates)
        except Exception as e:
            st.error(f"Error updating analysis: {str(e)}")
            return False
    
    def delete_analysis(self, analysis_id):
        """Delete analysis by ID"""
        try:
            return self.db_manager.delete_analysis(analysis_id)
        except Exception as e:
            st.error(f"Error deleting analysis: {str(e)}")
            return False
    
    def load_favorites(self):
        """Load favorite analyses"""
        try:
            return self.db_manager.get_analysis_history(filter_by={'is_favorite': True})
        except Exception as e:
            st.error(f"Error loading favorites: {str(e)}")
            return []
    
    def load_flagged(self):
        """Load flagged analyses"""
        try:
            return self.db_manager.get_analysis_history(filter_by={'is_flagged': True})
        except Exception as e:
            st.error(f"Error loading flagged products: {str(e)}")
            return []
    
    def get_statistics(self, days=30):
        """Get analysis statistics"""
        try:
            return self.db_manager.get_statistics(days=days)
        except Exception as e:
            st.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def export_all_data(self):
        """Export all data to file"""
        try:
            export_file = self.db_manager.export_data()
            return Path(export_file) if export_file else None
        except Exception as e:
            st.error(f"Error exporting data: {str(e)}")
            return None
    
    def get_storage_info(self):
        """Get database information"""
        try:
            db_info = self.db_manager.get_database_size()
            stats = self.db_manager.get_statistics(days=365)  # All-time stats
            
            info = {
                'history_count': stats.get('total_analyses', 0),
                'favorites_count': len(self.load_favorites()),
                'flagged_count': len(self.load_flagged()),
                'storage_location': str(self.db_manager.db_path.absolute()),
                'database_size_mb': db_info.get('database_size_mb', 0),
                'database_type': 'SQLite Database',
                'total_records': db_info.get('analysis_history_count', 0)
            }
            return info
        except Exception as e:
            st.error(f"Error getting storage info: {str(e)}")
            return {}

    def import_data(self, backup_file_path):
        """Import data from backup file"""
        try:
            import json
            with open(backup_file_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Handle different backup formats
            if isinstance(backup_data, list):
                # Old format - direct list of analyses
                analyses_data = backup_data
            elif isinstance(backup_data, dict):
                # New format - structured backup with metadata
                analyses_data = backup_data.get('analyses', backup_data.get('data', []))
            else:
                st.error("Invalid backup file format")
                return False
            
            # Import each analysis
            imported_count = 0
            for analysis in analyses_data:
                if self.db_manager.save_analysis(analysis):
                    imported_count += 1
            
            if imported_count > 0:
                st.success(f"✅ Successfully imported {imported_count} analyses from backup")
                return True
            else:
                st.warning("No valid analyses found in backup file")
                return False
                
        except Exception as e:
            st.error(f"Error importing backup: {str(e)}")
            return False

# Helper functions for compatibility between old and new data formats
def get_analysis_status(analysis_record):
    """Get status from analysis record, handling both old and new formats"""
    return analysis_record.get('status', analysis_record.get('authenticity_status', 'unknown'))

def get_analysis_confidence(analysis_record):
    """Get confidence from analysis record, handling both old and new formats"""
    return analysis_record.get('confidence', analysis_record.get('confidence_score', 0.0))

def get_analysis_brand(analysis_record):
    """Get brand from analysis record, handling both old and new formats"""
    return analysis_record.get('brand', 'Unknown')

def get_analysis_product(analysis_record):
    """Get product name from analysis record, handling both old and new formats"""
    return analysis_record.get('product', f"{get_analysis_brand(analysis_record)} {analysis_record.get('model', 'Unknown')}")

# Configure page
st.set_page_config(
    page_title="🔍 Fake Product Detector ",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Attractive CSS Styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Header Styles */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Mobile Navigation Styles */
    .mobile-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .nav-tabs {
        display: flex;
        justify-content: space-around;
        background: linear-gradient(135deg, #ffffff, #f8f9ff);
        border-radius: 25px;
        padding: 0.8rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .nav-tab {
        flex: 1;
        text-align: center;
        padding: 0.8rem 1rem;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 500;
        color: #64748b;
    }
    
    .nav-tab.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .nav-tab:hover {
        transform: translateY(-1px);
        background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
    }
    
    /* Card Styles */
    .mobile-card {
        background: linear-gradient(135deg, #ffffff, #fafbff);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    .mobile-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
    }
    
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Metric Containers */
    .metric-container {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
        margin: 0.8rem 0;
        border: 1px solid rgba(102, 126, 234, 0.08);
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8, #6b46c1);
    }
    
    /* File Uploader */
    .stFileUploader > div > div {
        background: linear-gradient(135deg, #f0f4ff, #e0e7ff) !important;
        border-radius: 15px !important;
        border: 2px dashed rgba(102, 126, 234, 0.3) !important;
        padding: 2rem !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
    }
    
    .stFileUploader > div > div:hover {
        border-color: rgba(102, 126, 234, 0.6) !important;
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15) !important;
    }
    
    .stFileUploader > div > div > div {
        color: #667eea !important;
        font-weight: 500 !important;
    }
    
    .stFileUploader label {
        color: #4c51bf !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Drag and drop zone styling */
    .stFileUploader > div > div[data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(135deg, #f0f4ff, #e0e7ff) !important;
        border: 3px dashed rgba(102, 126, 234, 0.4) !important;
        border-radius: 20px !important;
        padding: 3rem 2rem !important;
        text-align: center !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stFileUploader > div > div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(102, 126, 234, 0.8) !important;
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stFileUploader > div > div[data-testid="stFileUploaderDropzone"]::before {
        content: '📁' !important;
        font-size: 3rem !important;
        display: block !important;
        margin-bottom: 1rem !important;
        opacity: 0.7 !important;
    }
    
    /* Drag over state */
    .stFileUploader > div > div[data-testid="stFileUploaderDropzone"][data-drag-over="true"] {
        border-color: rgba(102, 126, 234, 1) !important;
        background: linear-gradient(135deg, #c7d2fe, #a5b4fc) !important;
        transform: scale(1.05) !important;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* File upload button */
    .stFileUploader button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        transition: all 0.3s ease !important;
        margin-top: 1rem !important;
    }
    
    .stFileUploader button:hover {
        background: linear-gradient(135deg, #5a67d8, #6b46c1) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Uploaded file display */
    .uploadedFile {
        background: linear-gradient(135deg, #f0f4ff, #e0e7ff);
        border-radius: 15px;
        border: 2px dashed rgba(102, 126, 234, 0.3);
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        border-color: rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
    }
    
    /* Additional drag and drop enhancements */
    .stFileUploader > div {
        position: relative !important;
    }
    
    .stFileUploader small {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
    }
    
    /* Animation for successful upload */
    @keyframes uploadSuccess {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .upload-success {
        animation: uploadSuccess 0.6s ease-in-out !important;
        border-color: rgba(34, 197, 94, 0.8) !important;
        background: linear-gradient(135deg, #dcfce7, #bbf7d0) !important;
    }
    
    /* Pulse animation for drag over */
    @keyframes dragPulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    
    .drag-over {
        animation: dragPulse 1.5s infinite !important;
    }
    
    /* Expander Styles */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.1);
        padding: 1rem;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background: linear-gradient(135deg, #ffffff, #fafbff);
        border-radius: 0 0 12px 12px;
        border: 1px solid rgba(102, 126, 234, 0.08);
        border-top: none;
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #ffffff, #f8faff);
        border-radius: 0 20px 20px 0;
    }
    
    /* Progress Bar */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
        height: 10px;
    }
    
    /* Selectbox and Input Styles */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        border-radius: 12px;
        border-left: 4px solid #10b981;
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border-radius: 12px;
        border-left: 4px solid #ef4444;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7, #fed7aa);
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
    }
    
    /* Image Styles */
    .stImage {
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    
    /* Metric Value Styles */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border: 1px solid rgba(102, 126, 234, 0.1);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Custom Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .mobile-card, .metric-container, .stat-card {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Scrollbar Styles */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8, #6b46c1);
    }
    
    /* Loading Spinner Custom */
    .stSpinner {
        border: 4px solid rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
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
                    return None, "Failed to process image"
                
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
                    print(f"DEBUG: Full response structure: {result.keys()}")
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        print(f"DEBUG: Candidate structure: {candidate.keys()}")
                        
                        # Handle different response structures
                        content = None
                        if 'content' in candidate:
                            if 'parts' in candidate['content']:
                                content = candidate['content']['parts'][0]['text']
                            elif 'text' in candidate['content']:
                                content = candidate['content']['text']
                            else:
                                print(f"DEBUG: Unexpected content structure: {candidate['content']}")
                                content = str(candidate['content'])
                        elif 'text' in candidate:
                            content = candidate['text']
                        else:
                            print(f"DEBUG: No recognizable content field in candidate")
                            return None, "❌ Unexpected API response structure"
                        
                        if content:
                            print(f"DEBUG: Got content from API: {content[:100]}...")
                            
                            try:
                                # Parse JSON response
                                parsed_result = json.loads(content)
                                print(f"DEBUG: Successfully parsed JSON response")
                                return parsed_result, None
                            except json.JSONDecodeError as e:
                                print(f"DEBUG: JSON parse error: {str(e)}")
                                print(f"DEBUG: Raw content: {content[:500]}")
                                # Try to parse as text response
                                return self.parse_text_response(content), None
                        else:
                            return None, "❌ No text content in API response"
                    else:
                        print(f"DEBUG: No candidates in response or empty candidates")
                        return None, "❌ No response from AI analysis"
                        
                elif response.status_code == 503:
                    # Handle 503 Service Unavailable - API overloaded
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"DEBUG: Service unavailable, retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return None, "🔄 AI service temporarily overloaded. Please try again in a few minutes."
                        
                elif response.status_code == 429:
                    # Handle 429 Too Many Requests - Rate limiting
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"DEBUG: Rate limited, retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return None, "⏱️ Rate limit exceeded. Please wait a moment and try again."
                        
                else:
                    # Other HTTP errors
                    error_msg = f"API request failed: {response.status_code}"
                    if response.text:
                        try:
                            error_detail = response.json()
                            error_msg += f" - {error_detail}"
                        except:
                            error_msg += f" - {response.text[:200]}"
                    return None, error_msg
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"DEBUG: Timeout, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None, "⏱️ Request timeout. Please check your connection and try again."
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"DEBUG: Request error, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None, f"🌐 Network error: {str(e)}"
                    
            except Exception as e:
                print(f"DEBUG: Unexpected error in attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"DEBUG: Retrying after error...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"DEBUG: All retries failed, providing fallback analysis")
                    # Provide a fallback analysis instead of complete failure
                    return self.get_fallback_analysis(), None
        
        # If we reach here, all retries failed
        print(f"DEBUG: All retries exhausted, providing fallback analysis")
        return self.get_fallback_analysis(), None
    
    def get_fallback_analysis(self):
        """Provide a basic fallback analysis when API fails"""
        return {
            "product_details": {
                "type": "Product",
                "brand": "Unknown", 
                "model": "Unknown",
                "color": "Unknown",
                "estimated_price_range": "Unknown"
            },
            "authenticity_status": "uncertain",
            "confidence_score": 0.3,
            "detailed_analysis": {
                "logo_analysis": "Unable to perform detailed logo analysis - API temporarily unavailable",
                "material_analysis": "Material analysis requires AI processing - please try again later",
                "construction_analysis": "Construction quality assessment pending",
                "hardware_analysis": "Hardware evaluation not available",
                "packaging_analysis": "Packaging analysis could not be completed"
            },
            "detected_issues": ["AI analysis temporarily unavailable", "Manual inspection recommended"],
            "positive_indicators": ["Image successfully uploaded and processed"],
            "quality_assessment": {
                "logo_quality": "unknown",
                "material_quality": "unknown", 
                "construction_quality": "unknown",
                "overall_craftsmanship": "unknown"
            },
            "recommendations": {
                "authenticity_verdict": "Analysis could not be completed due to technical issues",
                "purchase_advice": "Consider manual inspection or try analysis again later",
                "verification_tips": "Seek professional authentication for valuable items"
            },
            "analysis_summary": "Technical analysis temporarily unavailable. Basic image processing completed successfully. Please try again later for full AI analysis.",
            "expert_notes": "System is experiencing temporary API connectivity issues. Image was processed but detailed analysis could not be performed."
        }
    
    def parse_text_response(self, text_response):
        """Parse a text response when JSON parsing fails"""
        print(f"DEBUG: Parsing text response: {text_response[:200]}...")
        
        # Try to extract useful information from the text
        text_lower = text_response.lower()
        
        # Determine authenticity status
        if "authentic" in text_lower and "fake" not in text_lower:
            status = "authentic"
            confidence = 0.7
        elif "fake" in text_lower or "counterfeit" in text_lower:
            status = "fake"
            confidence = 0.7
        elif "uncertain" in text_lower or "unsure" in text_lower:
            status = "uncertain"
            confidence = 0.5
        else:
            # Default to uncertain if we can't determine
            status = "uncertain"
            confidence = 0.4
        
        # Extract basic product info
        product_type = "Product"
        brand = "Unknown"
        
        # Simple brand detection
        brands = ["nike", "adidas", "puma", "gucci", "louis vuitton", "chanel", "rolex", "apple", "samsung"]
        for brand_name in brands:
            if brand_name in text_lower:
                brand = brand_name.title()
                break
        
        # Product type detection
        types = ["shoe", "sneaker", "bag", "handbag", "watch", "phone", "clothing", "shirt", "jacket"]
        for product_name in types:
            if product_name in text_lower:
                product_type = product_name.title()
                break
        
        # Extract basic issues
        issues = []
        if "poor quality" in text_lower or "low quality" in text_lower:
            issues.append("Poor quality detected")
        if "logo" in text_lower and ("poor" in text_lower or "incorrect" in text_lower or "wrong" in text_lower):
            issues.append("Logo quality concerns")
        if "material" in text_lower and ("poor" in text_lower or "cheap" in text_lower):
            issues.append("Material quality issues")
        if "stitching" in text_lower and ("poor" in text_lower or "uneven" in text_lower):
            issues.append("Stitching quality concerns")
        
        # If no specific issues found
        if not issues:
            if status == "fake":
                issues = ["Counterfeit indicators detected"]
            else:
                issues = ["No specific issues detected"]
        
        # Generate positive indicators
        positive_indicators = []
        if "good quality" in text_lower or "high quality" in text_lower:
            positive_indicators.append("Good quality materials detected")
        if "authentic" in text_lower:
            positive_indicators.append("Authentic features identified")
        if "original" in text_lower:
            positive_indicators.append("Original product characteristics")
        
        # Default positive indicator
        if not positive_indicators:
            positive_indicators = ["Visual analysis completed"]
        
        # Create comprehensive response
        return {
            "product_details": {
                "type": product_type,
                "brand": brand,
                "model": "Unknown",
                "color": "Unknown",
                "estimated_price_range": "Unknown"
            },
            "authenticity_status": status,
            "confidence_score": confidence,
            "detailed_analysis": {
                "logo_analysis": f"Logo analysis completed for {brand} product",
                "material_analysis": f"Material quality assessment performed",
                "construction_analysis": f"Construction quality evaluated",
                "hardware_analysis": f"Hardware components checked",
                "packaging_analysis": f"Packaging elements reviewed"
            },
            "detected_issues": issues,
            "positive_indicators": positive_indicators,
            "quality_assessment": {
                "logo_quality": "good" if status == "authentic" else "poor" if status == "fake" else "fair",
                "material_quality": "good" if status == "authentic" else "poor" if status == "fake" else "fair",
                "construction_quality": "good" if status == "authentic" else "poor" if status == "fake" else "fair",
                "overall_craftsmanship": "good" if status == "authentic" else "poor" if status == "fake" else "fair"
            },
            "recommendations": {
                "authenticity_verdict": f"Based on visual analysis, this product appears to be {status}",
                "purchase_advice": "Proceed with purchase" if status == "authentic" else "Exercise caution" if status == "uncertain" else "Avoid purchase",
                "verification_tips": "Consider professional authentication for high-value items"
            },
            "analysis_summary": f"AI visual analysis indicates this {product_type} from {brand} is {status} with {confidence:.0%} confidence based on available visual information.",
            "expert_notes": f"Analysis completed using visual inspection. Confidence level: {confidence:.0%}"
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

def main():
    # Enhanced Mobile-Style Header with Attractive Navigation
    st.markdown("""
        <div class="mobile-header">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
                🔍 Product Authentication
            </h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                Professional Product Authenticity Analysis
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .enhanced-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        }
        .nav-tabs {
            display: flex;
            justify-content: space-around;
            background: linear-gradient(135deg, #ffffff, #f8f9ff);
            border-radius: 25px;
            padding: 0.8rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .nav-tab {
            flex: 1;
            text-align: center;
            padding: 0.5rem;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .nav-tab.active {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .mobile-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Mobile-style header
    st.markdown("""
        <div class="mobile-header">
            <h1>🔍 Counterfeit Product Detection</h1>
            <p>AI-Powered Mobile & Web Analysis Platform</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Mobile-style navigation tabs with attractive design
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 'scan'
    
    # Create attractive tab navigation
    st.markdown("""
        <div class="nav-tabs">
            <div class="nav-tab {}" onclick="setTab('scan')">
                <div style="font-size: 1.5rem;">🔍</div>
                <div>Smart Scan</div>
            </div>
            <div class="nav-tab {}" onclick="setTab('history')">
                <div style="font-size: 1.5rem;">📋</div>
                <div>History</div>
            </div>
            <div class="nav-tab {}" onclick="setTab('analytics')">
                <div style="font-size: 1.5rem;">📊</div>
                <div>Analytics</div>
            </div>
            <div class="nav-tab {}" onclick="setTab('settings')">
                <div style="font-size: 1.5rem;">⚙️</div>
                <div>Settings</div>
            </div>
        </div>
    """.format(
        "active" if st.session_state.current_tab == 'scan' else "",
        "active" if st.session_state.current_tab == 'history' else "",
        "active" if st.session_state.current_tab == 'analytics' else "",
        "active" if st.session_state.current_tab == 'settings' else ""
    ), unsafe_allow_html=True)
    
    # Tab buttons (fallback for interaction)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("� Smart Scan", use_container_width=True, type="primary" if st.session_state.current_tab == 'scan' else "secondary"):
            st.session_state.current_tab = 'scan'
    
    with col2:
        if st.button("� History", use_container_width=True, type="primary" if st.session_state.current_tab == 'history' else "secondary"):
            st.session_state.current_tab = 'history'
    
    with col3:
        if st.button("📊 Analytics", use_container_width=True, type="primary" if st.session_state.current_tab == 'analytics' else "secondary"):
            st.session_state.current_tab = 'analytics'
    
    with col4:
        if st.button("⚙️ Settings", use_container_width=True, type="primary" if st.session_state.current_tab == 'settings' else "secondary"):
            st.session_state.current_tab = 'settings'
    
    st.markdown("---")
    
    # Initialize detector
    if 'detector' not in st.session_state:
        st.session_state.detector = FakeProductDetector()
    
    # Initialize History Manager
    if 'history_manager' not in st.session_state:
        st.session_state.history_manager = HistoryManager()
    
    # Initialize session state variables with persistent storage
    if 'analysis_history' not in st.session_state:
        # Load from persistent storage
        st.session_state.analysis_history = st.session_state.history_manager.load_history()
    if 'product_database' not in st.session_state:
        st.session_state.product_database = st.session_state.analysis_history.copy()
    if 'favorite_products' not in st.session_state:
        # Load favorites from persistent storage
        st.session_state.favorite_products = st.session_state.history_manager.load_favorites()
    if 'flagged_products' not in st.session_state:
        # Load flagged products from persistent storage
        st.session_state.flagged_products = st.session_state.history_manager.load_flagged()
    if 'confidence_threshold' not in st.session_state:
        st.session_state.confidence_threshold = 0.7
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'auto_save' not in st.session_state:
        st.session_state.auto_save = True
    
    # Enhanced Sidebar
    with st.sidebar:
        # Quick Actions
        st.markdown("### ⚡ **Quick Actions**")
        
        if st.button("� New Scan", use_container_width=True, type="primary"):
            st.session_state.current_tab = 'scan'
            st.rerun()
        
        if st.button("�📊 View Analytics", use_container_width=True):
            st.session_state.current_tab = 'analytics'
            st.rerun()
        
        # Live Stats Widget
        st.markdown("### 📊 **Live Statistics**")
        total_analyses = len(st.session_state.analysis_history)
        
        if total_analyses > 0:
            # Handle both old format (status) and new database format (authenticity_status)
            authentic_count = sum(1 for h in st.session_state.analysis_history 
                                if get_analysis_status(h) == 'authentic')
            fake_count = sum(1 for h in st.session_state.analysis_history 
                           if get_analysis_status(h) in ['fake', 'counterfeit'])
            
            # Mobile-style compact stats
            st.markdown(f"""
                <div style="background: #4CAF50; color: white; padding: 0.5rem; border-radius: 5px; margin: 0.2rem 0; text-align: center;">
                    <strong>✅ Authentic: {authentic_count}</strong>
                </div>
                <div style="background: #F44336; color: white; padding: 0.5rem; border-radius: 5px; margin: 0.2rem 0; text-align: center;">
                    <strong>🚨 Counterfeit: {fake_count}</strong>
                </div>
                <div style="background: #2196F3; color: white; padding: 0.5rem; border-radius: 5px; margin: 0.2rem 0; text-align: center;">
                    <strong>📈 Total: {total_analyses}</strong>
                </div>
            """, unsafe_allow_html=True)
            
            if total_analyses > 0:
                avg_confidence = sum(get_analysis_confidence(h) for h in st.session_state.analysis_history) / total_analyses
                st.markdown(f"""
                    <div style="background: #FF9800; color: white; padding: 0.5rem; border-radius: 5px; margin: 0.2rem 0; text-align: center;">
                        <strong>🎯 Accuracy: {avg_confidence:.1%}</strong>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📊 Start scanning to see statistics!")
        
        st.markdown("---")
        
        # Analysis Settings
        st.markdown("### 🎚️ Analysis Settings")
        
        # Confidence threshold
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.confidence_threshold,
            step=0.05,
            help="Minimum confidence for reliable results"
        )
        st.session_state.confidence_threshold = confidence_threshold
        
        # Analysis mode
        analysis_mode = st.selectbox(
            "🔍 Analysis Mode",
            ["🔬 Comprehensive", "⚡ Quick Scan", "🎯 Focused"],
            help="Choose analysis depth and speed"
        )
        
        # Product category filter
        product_filter = st.selectbox(
            "📦 Product Category",
            ["🔍 Auto-Detect", "👟 Footwear", "👜 Handbags", "⌚ Watches", "👕 Clothing", "🕶️ Accessories"],
            help="Focus analysis on specific product type"
        )
        
        st.markdown("---")
        
        st.markdown("---")
        
        # Enhanced Product History Section
        st.markdown("### 📚 Product History & Database")
        
        # History navigation tabs
        history_tab = st.selectbox(
            "� View History",
            ["�📋 Recent Analysis", "⭐ Favorites", "🚨 Flagged Products", "🔍 Search History", "📊 All Products"],
            key="history_tab_selector"
        )
        
        if history_tab == "📋 Recent Analysis":
            if st.session_state.analysis_history:
                # Show last 5 analyses with enhanced details
                recent_analyses = st.session_state.analysis_history[-5:]
                for i, analysis in enumerate(reversed(recent_analyses)):
                    status = get_analysis_status(analysis)
                    status_emoji = {"authentic": "✅", "fake": "🚨", "uncertain": "⚠️", "counterfeit": "🚨"}.get(status, "❓")
                    
                    with st.expander(f"{status_emoji} {analysis.get('timestamp', 'Unknown')} - {get_analysis_brand(analysis)}", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Product:** {get_analysis_product(analysis)}")
                            st.write(f"**Status:** {status.title()}")
                            st.write(f"**Confidence:** {get_analysis_confidence(analysis):.1%}")
                        with col2:
                            st.write(f"**Brand:** {analysis.get('brand', 'Unknown')}")
                            st.write(f"**Category:** {analysis.get('category', 'Unknown')}")
                            
                            # Action buttons for each product
                            action_col1, action_col2 = st.columns(2)
                            with action_col1:
                                # Check if analysis has database ID (new format) or is legacy format
                                is_favorite = analysis.get('is_favorite', False) if 'id' in analysis else analysis in st.session_state.favorite_products
                                fav_label = "💖" if is_favorite else "⭐"
                                if st.button(fav_label, key=f"fav_{i}", help="Toggle favorite"):
                                    if 'id' in analysis:
                                        # New database format
                                        new_status = not analysis.get('is_favorite', False)
                                        success = st.session_state.history_manager.update_analysis(
                                            analysis['id'], 
                                            {'is_favorite': new_status}
                                        )
                                        if success:
                                            analysis['is_favorite'] = new_status
                                            st.success("Favorite updated!" if new_status else "Removed from favorites!")
                                        else:
                                            st.error("Failed to update favorite status")
                                    else:
                                        # Legacy format
                                        if analysis not in st.session_state.favorite_products:
                                            st.session_state.favorite_products.append(analysis)
                                            st.success("Added to favorites!")
                                        else:
                                            st.session_state.favorite_products.remove(analysis)
                                            st.success("Removed from favorites!")
                                    st.rerun()
                            with action_col2:
                                is_flagged = analysis.get('is_flagged', False) if 'id' in analysis else analysis in st.session_state.flagged_products
                                flag_label = "🔴" if is_flagged else "🚨"
                                if st.button(flag_label, key=f"flag_{i}", help="Toggle flag"):
                                    if 'id' in analysis:
                                        # New database format
                                        new_status = not analysis.get('is_flagged', False)
                                        success = st.session_state.history_manager.update_analysis(
                                            analysis['id'], 
                                            {'is_flagged': new_status}
                                        )
                                        if success:
                                            analysis['is_flagged'] = new_status
                                            st.warning("Product flagged!" if new_status else "Flag removed!")
                                        else:
                                            st.error("Failed to update flag status")
                                    else:
                                        # Legacy format
                                        if analysis not in st.session_state.flagged_products:
                                            st.session_state.flagged_products.append(analysis)
                                            st.warning("Product flagged!")
                                        else:
                                            st.session_state.flagged_products.remove(analysis)
                                            st.warning("Flag removed!")
                                    st.rerun()
                
                # Clear history button
                if st.button("🗑️ Clear Recent History", use_container_width=True):
                    st.session_state.analysis_history = []
                    st.rerun()
            else:
                st.info("No recent analysis history")
        
        elif history_tab == "⭐ Favorites":
            if st.session_state.favorite_products:
                st.write(f"**{len(st.session_state.favorite_products)} Favorite Products**")
                for i, fav in enumerate(st.session_state.favorite_products):
                    status = get_analysis_status(fav)
                    status_emoji = {"authentic": "✅", "fake": "🚨", "uncertain": "⚠️", "counterfeit": "🚨"}.get(status, "❓")
                    with st.expander(f"{status_emoji} {get_analysis_brand(fav)} - {status.title()}", expanded=False):
                        st.write(f"**Product:** {get_analysis_product(fav)}")
                        st.write(f"**Date:** {fav.get('timestamp', 'Unknown')}")
                        st.write(f"**Confidence:** {get_analysis_confidence(fav):.1%}")
                        
                        if st.button("❌ Remove from favorites", key=f"remove_fav_{i}"):
                            st.session_state.favorite_products.remove(fav)
                            st.rerun()
                
                if st.button("🗑️ Clear All Favorites", use_container_width=True):
                    st.session_state.favorite_products = []
                    st.rerun()
            else:
                st.info("No favorite products yet")
        
        elif history_tab == "🚨 Flagged Products":
            if st.session_state.flagged_products:
                st.write(f"**{len(st.session_state.flagged_products)} Flagged Products**")
                for i, flagged in enumerate(st.session_state.flagged_products):
                    status = get_analysis_status(flagged)
                    with st.expander(f"🚨 {get_analysis_brand(flagged)} - {status.title()}", expanded=False):
                        st.write(f"**Product:** {get_analysis_product(flagged)}")
                        st.write(f"**Date:** {flagged.get('timestamp', 'Unknown')}")
                        st.write(f"**Reason:** {status} detection")
                        st.write(f"**Confidence:** {get_analysis_confidence(flagged):.1%}")
                        
                        if st.button("✅ Remove flag", key=f"unflag_{i}"):
                            st.session_state.flagged_products.remove(flagged)
                            st.rerun()
                
                if st.button("🗑️ Clear All Flags", use_container_width=True):
                    st.session_state.flagged_products = []
                    st.rerun()
            else:
                st.info("No flagged products")
        
        elif history_tab == "🔍 Search History":
            st.text_input("🔍 Search products", key="product_search", placeholder="Search by brand, product name...")
            
            if st.session_state.get('product_search', ''):
                search_term = st.session_state.product_search.lower()
                
                # Search through all analysis history
                search_results = []
                for analysis in st.session_state.analysis_history:
                    if (search_term in analysis.get('product', '').lower() or 
                        search_term in analysis.get('brand', '').lower() or
                        search_term in analysis.get('category', '').lower()):
                        search_results.append(analysis)
                
                if search_results:
                    st.write(f"**Found {len(search_results)} results for '{search_term}'**")
                    for result in search_results[-10:]:  # Show last 10 results
                        status_emoji = {"authentic": "✅", "fake": "🚨", "uncertain": "⚠️"}.get(result['status'], "❓")
                        with st.expander(f"{status_emoji} {result.get('brand', 'Unknown')} - {result['timestamp'][-8:]}", expanded=False):
                            st.write(f"**Product:** {result['product']}")
                            st.write(f"**Status:** {result['status'].title()}")
                            st.write(f"**Confidence:** {result['confidence']:.1%}")
                else:
                    st.info(f"No products found matching '{search_term}'")
            else:
                st.info("Enter a search term to find products")
        
        elif history_tab == "📊 All Products":
            total_products = len(st.session_state.analysis_history)
            if total_products > 0:
                st.write(f"**Total Products Analyzed: {total_products}**")
                
                # Product statistics
                authentic_products = [p for p in st.session_state.analysis_history if get_analysis_status(p) == 'authentic']
                fake_products = [p for p in st.session_state.analysis_history if get_analysis_status(p) == 'fake']
                uncertain_products = [p for p in st.session_state.analysis_history if get_analysis_status(p) == 'uncertain']
                
                st.write(f"✅ Authentic: {len(authentic_products)}")
                st.write(f"🚨 Fake: {len(fake_products)}")
                st.write(f"⚠️ Uncertain: {len(uncertain_products)}")
                
                # Brand breakdown
                brands = {}
                for product in st.session_state.analysis_history:
                    brand = product.get('brand', 'Unknown')
                    brands[brand] = brands.get(brand, 0) + 1
                
                if len(brands) > 1:
                    st.write("**Top Brands Analyzed:**")
                    sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)
                    for brand, count in sorted_brands[:5]:
                        st.write(f"• {brand}: {count} products")
                
                # Filter options
                filter_status = st.selectbox("Filter by status:", ["All", "Authentic", "Fake", "Uncertain"])
                
                filtered_products = st.session_state.analysis_history
                if filter_status != "All":
                    filtered_products = [p for p in st.session_state.analysis_history if get_analysis_status(p) == filter_status.lower()]
                
                # Show filtered products (last 10)
                for product in filtered_products[-10:]:
                    status = get_analysis_status(product)
                    status_emoji = {"authentic": "✅", "fake": "🚨", "counterfeit": "🚨", "uncertain": "⚠️"}.get(status, "❓")
                    st.write(f"{status_emoji} {get_analysis_brand(product)} - {get_analysis_confidence(product):.1%}")
            else:
                st.info("No products in database yet")
        
        st.markdown("---")
        
        # Storage Management
        st.markdown("### 💾 Storage Management")
        
        # Auto-save toggle
        auto_save = st.checkbox(
            "🔄 Auto-save to disk",
            value=st.session_state.auto_save,
            help="Automatically save analysis history to disk"
        )
        st.session_state.auto_save = auto_save
        
        # Storage info
        storage_info = st.session_state.history_manager.get_storage_info()
        
        st.write(f"**📊 Stored Data:**")
        st.write(f"• Analysis History: {storage_info['history_count']} products")
        st.write(f"• Favorites: {storage_info['favorites_count']} products")
        st.write(f"• Flagged: {storage_info['flagged_count']} products")
        
        # Storage location
        with st.expander("📂 Storage Location"):
            st.code(storage_info['storage_location'])
            st.write("**Database Info:**")
            st.write(f"✅ Database Type: {storage_info.get('database_type', 'SQLite Database')}")
            st.write(f"📊 Total Records: {storage_info.get('total_records', 0)}")
            st.write(f"💾 Database Size: {storage_info.get('database_size_mb', 0)} MB")
        
        # Manual save/load buttons
        save_col1, save_col2 = st.columns(2)
        
        with save_col1:
            if st.button("💾 Export Database", use_container_width=True):
                export_file = st.session_state.history_manager.export_all_data()
                if export_file:
                    st.success(f"✅ Database exported to: {export_file}")
                else:
                    st.error("❌ Export failed")
        
        with save_col2:
            if st.button("🔄 Reload Database", use_container_width=True):
                st.session_state.analysis_history = st.session_state.history_manager.load_history()
                st.session_state.favorite_products = st.session_state.history_manager.load_favorites()
                st.session_state.flagged_products = st.session_state.history_manager.load_flagged()
                st.success("✅ Data reloaded from database!")
                st.rerun()
        
        # Backup and restore
        backup_col1, backup_col2 = st.columns(2)
        
        with backup_col1:
            if st.button("📦 Create Backup", use_container_width=True):
                backup_file = st.session_state.history_manager.export_all_data()
                if backup_file:
                    st.success(f"✅ Backup created!")
                    st.info(f"📁 {backup_file.name}")
        
        with backup_col2:
            # File uploader for restore
            uploaded_backup = st.file_uploader(
                "🔄 Restore Backup",
                type=['json'],
                help="Upload a backup file to restore data",
                key="backup_uploader"
            )
            
            if uploaded_backup:
                if st.button("🔄 Restore", use_container_width=True):
                    # Save uploaded file temporarily
                    temp_file = f"temp_backup_{int(time.time())}.json"
                    with open(temp_file, 'wb') as f:
                        f.write(uploaded_backup.getvalue())
                    
                    # Import data
                    if st.session_state.history_manager.import_data(temp_file):
                        st.success("✅ Backup restored successfully!")
                        # Clean up temp file
                        os.remove(temp_file)
                        st.rerun()
                    else:
                        st.error("❌ Error restoring backup")
                        os.remove(temp_file)
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Export Data", use_container_width=True):
                if st.session_state.analysis_history:
                    df = pd.DataFrame(st.session_state.analysis_history)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"analysis_history_{int(time.time())}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data to export")
        
        with col2:
            if st.button("🔄 Reset All", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key not in ['detector']:  # Keep detector initialized
                        del st.session_state[key]
                st.rerun()
        
        st.markdown("---")
        
        # Help & Tips
        with st.expander("💡 Tips & Help"):
            st.markdown("""
            **📸 Best Photo Practices:**
            • Good lighting (natural preferred)
            • Clear, focused images
            • Include brand logos/labels
            • Multiple angles helpful
            
            **🎯 Understanding Results:**
            • 90-100%: Very confident
            • 70-89%: High confidence  
            • 50-69%: Moderate confidence
            • <50%: Low confidence
            
            **🔍 What We Analyze:**
            • Logo quality & placement
            • Material texture & finish
            • Stitching patterns
            • Hardware quality
            • Overall craftsmanship
            """)
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Fake Product Detector v2.0**
            
            Advanced AI-powered authenticity detection using:
            • Google Gemini 2.5 Flash Preview
            • Computer vision analysis
            • Machine learning algorithms
            
            Built with Streamlit & Python
            """)
    
    # Main content area
    st.header("🤖 AI-Powered Product Authenticity Detection")
    
    # Handle batch processing
    if st.session_state.get('run_batch_analysis', False) or st.session_state.get('run_batch', False):
        st.markdown("### � Batch Analysis Results")
        
        # Get batch files from either source
        batch_files = st.session_state.get('batch_files', [])
        if not batch_files:
            st.error("❌ No files found for batch processing")
            st.session_state.run_batch_analysis = False
            st.session_state.run_batch = False
            st.rerun()
        
        st.markdown(f"**🔄 Processing {len(batch_files)} images...**")
        
        # Create progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            batch_results = []
            
            for i, file in enumerate(batch_files):
                current_progress = (i + 1) / len(batch_files)
                progress_bar.progress(current_progress)
                status_text.markdown(f"**🔍 Analyzing: {file.name}** ({i+1}/{len(batch_files)})")
                
                try:
                    image = Image.open(file)
                    
                    # Convert to base64 for API
                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    image_base64 = base64.b64encode(buffer.getvalue()).decode()
                    
                    # Analyze with AI API
                    api_result, api_error = st.session_state.detector.analyze_with_ai_api(image)
                    
                    if api_result and not api_error:
                        # Extract data for history
                        product_details = api_result.get('product_details', {})
                        status = api_result.get('authenticity_status', 'unknown')
                        confidence = api_result.get('confidence_score', 0.0)
                        
                        # Create product entry for database
                        product_entry = {
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'authenticity_status': status,
                            'confidence_score': confidence,
                            'product': f"{product_details.get('brand', 'Unknown')} {product_details.get('model', 'Unknown')}",
                            'brand': product_details.get('brand', 'Unknown'),
                            'model': product_details.get('model', 'Unknown'),
                            'category': product_details.get('type', 'Unknown'),
                            'color': product_details.get('color', 'Unknown'),
                            'price_range': product_details.get('estimated_price_range', 'Unknown'),
                            'analysis_summary': api_result.get('analysis_summary', ''),
                            'detailed_analysis': api_result.get('detailed_analysis', {}),
                            'recommendations': api_result.get('recommendations', {}),
                            'image_filename': file.name
                        }
                        
                        # Save to database
                        st.session_state.history_manager.save_analysis(product_entry, image_base64, file.name)
                        
                        batch_results.append({
                            'filename': file.name,
                            'status': status,
                            'confidence': f"{confidence:.1%}",
                            'brand': product_details.get('brand', 'Unknown'),
                            'product': f"{product_details.get('brand', 'Unknown')} {product_details.get('model', 'Unknown')}",
                            'error': None
                        })
                    else:
                        batch_results.append({
                            'filename': file.name,
                            'status': 'error',
                            'confidence': '0%',
                            'brand': 'Unknown',
                            'product': 'Analysis Failed',
                            'error': api_error or 'Unknown error'
                        })
                        
                except Exception as e:
                    batch_results.append({
                        'filename': file.name,
                        'status': 'error',
                        'confidence': '0%',
                        'brand': 'Unknown',
                        'product': 'Processing Error',
                        'error': str(e)
                    })
                
                # Small delay to show progress
                time.sleep(0.1)
            
            # Complete processing
            progress_bar.progress(1.0)
            status_text.markdown("**✅ Batch analysis complete!**")
            
        # Display batch results
        st.markdown("---")
        st.markdown("### 📊 **Analysis Results Summary**")
        
        if batch_results:
            # Create DataFrame for display
            df = pd.DataFrame(batch_results)
            
            # Display results table
            st.dataframe(
                df[['filename', 'status', 'confidence', 'brand', 'product']],
                use_container_width=True,
                column_config={
                    'filename': 'File Name',
                    'status': 'Authenticity Status',
                    'confidence': 'Confidence',
                    'brand': 'Brand',
                    'product': 'Product'
                }
            )
            
            # Batch summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Processed", len(batch_results))
            with col2:
                authentic_count = len([r for r in batch_results if r['status'] == 'authentic'])
                st.metric("✅ Authentic", authentic_count)
            with col3:
                fake_count = len([r for r in batch_results if r['status'] == 'fake'])
                st.metric("🚨 Fake", fake_count)
            with col4:
                error_count = len([r for r in batch_results if r['status'] == 'error'])
                st.metric("❌ Errors", error_count)
            
            # Show error details if any
            errors = [r for r in batch_results if r['error']]
            if errors:
                with st.expander(f"⚠️ View Errors ({len(errors)})"):
                    for error in errors:
                        st.error(f"**{error['filename']}**: {error['error']}")
            
            # Download results option
            st.markdown("### 📥 **Export Results**")
            csv_data = pd.DataFrame(batch_results).to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_data,
                file_name=f"batch_analysis_{int(time.time())}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Reset batch processing flags
        st.session_state.run_batch_analysis = False
        st.session_state.run_batch = False
        
        # Reload analysis history
        st.session_state.analysis_history = st.session_state.history_manager.load_history()
        
        # Show button to return to scanner
        st.markdown("---")
        if st.button("🔄 **Process More Images**", type="primary", use_container_width=True):
            st.rerun()
    
    # Mobile-app-like navigation content
    if st.session_state.current_tab == 'scan':
        # Enhanced Scan Tab with Modern Design
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        
        # Attractive header with icons and description
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem; margin: 0;">
                    � AI Product Scanner
                </h2>
                <p style="color: #64748b; margin: 0.5rem 0; font-size: 1.1rem;">
                    Professional authenticity analysis powered by advanced AI
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Enhanced scanner mode selection with radio buttons
        st.markdown("#### 🎯 Choose Your Analysis Method")
        
        scanner_mode = st.radio(
            "Select scanning method:",
            ["📁 Upload Image", "📷 Camera Capture"],
            horizontal=True,
            help="Choose how you want to scan your product"
        )
        
        if scanner_mode == "📁 Upload Image":
            # Upload mode selection
            st.markdown("---")
            upload_mode = st.radio(
                "Upload Mode:",
                ["📷 Single Image", "📂 Multiple Images (Batch Analysis)"],
                horizontal=True,
                help="Choose single or multiple image upload"
            )
            
            if upload_mode == "📷 Single Image":
                # Single file upload with enhanced design
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #f0f4ff, #e0e7ff); padding: 2rem; border-radius: 15px; border: 2px dashed rgba(102, 126, 234, 0.3); text-align: center; margin: 1rem 0; position: relative; overflow: hidden;">
                        <div style="position: relative; z-index: 2;">
                            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.8;">📁</div>
                            <h4 style="color: #667eea; margin: 0; font-weight: 600;">Upload Product Image</h4>
                            <p style="color: #64748b; margin: 0.5rem 0; font-size: 1.1rem;">Drag & drop your image here or click to browse</p>
                            <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">Supported formats: JPG, PNG, JPEG • Max size: 10MB</p>
                        </div>
                        <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(102, 126, 234, 0.05) 0%, transparent 70%); pointer-events: none;"></div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Multiple files upload design
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #fff1f2, #fce7f3); padding: 2rem; border-radius: 15px; border: 2px dashed rgba(236, 72, 153, 0.3); text-align: center; margin: 1rem 0; position: relative; overflow: hidden;">
                        <div style="position: relative; z-index: 2;">
                            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.8;">📂</div>
                            <h4 style="color: #ec4899; margin: 0; font-weight: 600;">Batch Upload - Multiple Images</h4>
                            <p style="color: #64748b; margin: 0.5rem 0; font-size: 1.1rem;">Select multiple product images for batch analysis</p>
                            <p style="color: #94a3b8; margin: 0; font-size: 0.9rem;">Supported formats: JPG, PNG, JPEG • Max 10MB each • Up to 20 images</p>
                        </div>
                        <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(236, 72, 153, 0.05) 0%, transparent 70%); pointer-events: none;"></div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Enhanced file uploader with better error handling
            try:
                # Initialize variables
                uploaded_files = []
                valid_files = []
                
                if upload_mode == "📷 Single Image":
                    # Single file uploader
                    uploaded_file = st.file_uploader(
                        "Choose an image file (JPG, PNG, JPEG)",
                        type=['jpg', 'jpeg', 'png'],
                        help="Upload a clear photo of the product you want to authenticate",
                        key="single_file_uploader",
                        label_visibility="collapsed"
                    )
                    uploaded_files = [uploaded_file] if uploaded_file else []
                else:
                    # Multiple files uploader
                    uploaded_files = st.file_uploader(
                        "Choose image files (JPG, PNG, JPEG)",
                        type=['jpg', 'jpeg', 'png'],
                        help="Select multiple product images for batch analysis",
                        key="multiple_files_uploader",
                        label_visibility="collapsed",
                        accept_multiple_files=True
                    )
                    if uploaded_files is None:
                        uploaded_files = []
                
                # Filter out None values to get valid files
                valid_files = [f for f in uploaded_files if f is not None]
                
                if valid_files and len(valid_files) > 0:
                    if upload_mode == "📷 Single Image":
                        # Single image processing
                        uploaded_file = valid_files[0]
                        st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
                        
                        # File size check
                        file_size = len(uploaded_file.getvalue())
                        if file_size > 10 * 1024 * 1024:  # 10MB limit
                            st.warning("⚠️ File is quite large. Processing may take longer.")
                        
                        try:
                            image = Image.open(uploaded_file)
                            
                            # Image validation
                            if image.size[0] < 50 or image.size[1] < 50:
                                st.error("❌ Image is too small. Please upload a larger image.")
                            else:
                                # Create columns for compact image display
                                col1, col2, col3 = st.columns([1, 2, 1])
                                
                                with col2:
                                    st.markdown("### 📷 **Uploaded Product Image**")
                                    st.image(image, caption=f"📁 {uploaded_file.name}", width=400)
                                    st.info(f"📏 Image size: {image.size[0]}×{image.size[1]} pixels")
                        
                        except Exception as img_error:
                            st.error(f"❌ Error processing uploaded image: {str(img_error)}")
                            st.info("💡 Please try uploading a different image file")
                    
                    else:
                        # Multiple images processing
                        st.success(f"✅ {len(valid_files)} files uploaded successfully!")
                        
                        # Show file information
                        total_size = sum(len(f.getvalue()) for f in valid_files)
                        st.info(f"📊 Total files: {len(valid_files)} • Total size: {total_size / (1024*1024):.1f} MB")
                        
                        # Display uploaded images in grid
                        st.markdown("### 📂 **Uploaded Images Preview**")
                        
                        # Create grid layout for images
                        cols_per_row = 4
                        for i in range(0, len(valid_files), cols_per_row):
                            cols = st.columns(cols_per_row)
                            for j in range(cols_per_row):
                                if i + j < len(valid_files):
                                    file = valid_files[i + j]
                                    try:
                                        image = Image.open(file)
                                        with cols[j]:
                                            st.image(image, caption=f"📁 {file.name}", width=150)
                                    except Exception as e:
                                        with cols[j]:
                                            st.error(f"❌ Error: {file.name}")
                        
                        # Batch analysis options
                        st.markdown("---")
                        st.markdown("### 🚀 **Batch Analysis Options**")
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.info(f"🎯 Ready to analyze {len(valid_files)} images simultaneously")
                        
                        with col2:
                            if st.button("🚀 **Start Batch Analysis**", type="primary", use_container_width=True):
                                st.session_state.batch_files = valid_files
                                st.session_state.run_batch_analysis = True
                                st.rerun()
                
            except Exception as upload_error:
                st.error(f"❌ Upload error: {str(upload_error)}")
                st.info("💡 Please refresh the page and try again")
            
            # Show analyze button if file(s) are uploaded and valid
            if valid_files and len(valid_files) > 0:
                if upload_mode == "📷 Single Image" and len(valid_files) == 1:
                    uploaded_file = valid_files[0]
                    try:
                        # Validate image can be opened
                        test_image = Image.open(uploaded_file)
                        
                        # Enhanced analyze button with attractive styling
                        st.markdown("---")
                        st.markdown("""
                            <div style="text-align: center; margin: 1.5rem 0;">
                                <p style="color: #64748b; margin: 0 0 1rem 0; font-size: 1rem;">
                                    🤖 Ready to analyze with advanced AI technology
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🚀 **START AI ANALYSIS**", key="analyze_btn", type="primary", use_container_width=True):
                            image = Image.open(uploaded_file)
                        # Enhanced analysis progress with attractive design
                        with st.spinner("🤖 AI analyzing product authenticity..."):
                            # Create attractive progress container
                            progress_container = st.container()
                            with progress_container:
                                st.markdown("""
                                    <div style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
                                        <h4 style="text-align: center; color: #667eea; margin: 0 0 1rem 0;">
                                            🤖 AI Analysis in Progress
                                        </h4>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Initialize progress tracking
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                status_text.markdown("**🔍 Initializing neural networks...**")
                                progress_bar.progress(20)
                                time.sleep(0.5)
                                
                                status_text.markdown("**📸 Processing image data...**")
                                progress_bar.progress(40)
                                time.sleep(0.5)
                                
                                status_text.markdown("**🧠 Running authenticity analysis...**")
                                progress_bar.progress(60)
                                time.sleep(0.5)
                                
                                status_text.markdown("**🔬 Generating detailed report...**")
                                progress_bar.progress(80)
                            
                            # Run analysis
                            api_result, api_error = st.session_state.detector.analyze_with_ai_api(image)
                        
                            # Automatically save to history if analysis was successful
                            if api_result and not api_error:
                                # Extract data for history
                                product_details = api_result.get('product_details', {})
                                quality = api_result.get('quality_assessment', {})
                                detailed_analysis = api_result.get('detailed_analysis', {})
                                recommendations = api_result.get('recommendations', {})
                                summary = api_result.get('analysis_summary', '')
                                status = api_result.get('authenticity_status', 'unknown')
                                confidence = api_result.get('confidence_score', 0.0)
                            
                                # Create detailed product entry
                                product_entry = {
                                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                    'status': status,
                                    'confidence': confidence,
                                    'product': f"{product_details.get('brand', 'Unknown')} {product_details.get('model', 'Unknown')}",
                                    'brand': product_details.get('brand', 'Unknown'),
                                    'model': product_details.get('model', 'Unknown'),
                                    'category': product_details.get('type', 'Unknown'),
                                    'color': product_details.get('color', 'Unknown'),
                                    'price_range': product_details.get('estimated_price_range', 'Unknown'),
                                    'logo_quality': quality.get('logo_quality', 'N/A'),
                                    'material_quality': quality.get('material_quality', 'N/A'),
                                    'construction_quality': quality.get('construction_quality', 'N/A'),
                                    'overall_quality': quality.get('overall_craftsmanship', 'N/A'),
                                    'detected_issues': api_result.get('detected_issues', []),
                                    'positive_indicators': api_result.get('positive_indicators', []),
                                    'analysis_summary': summary,
                                    'expert_notes': api_result.get('expert_notes', ''),
                                    'detailed_analysis': detailed_analysis,
                                    'recommendations': recommendations
                                }
                            
                                # Save to database
                                image_bytes = None
                                if uploaded_file:
                                    uploaded_file.seek(0)  # Reset file pointer
                                    image_bytes = uploaded_file.read()
                                
                                # Save analysis to database
                                analysis_saved = st.session_state.history_manager.save_analysis(
                                    api_result, 
                                    image_bytes, 
                                    uploaded_file.name if uploaded_file else None
                                )
                                
                                if analysis_saved:
                                    # Reload history to include the new analysis
                                    st.session_state.analysis_history = st.session_state.history_manager.load_history()
                                    st.success("✅ Analysis saved to database successfully!")
                                else:
                                    st.error("❌ Failed to save analysis to database")
                                
                                # Also keep in session state for immediate display (convert to old format for compatibility)
                                if 'analysis_history' not in st.session_state:
                                    st.session_state.analysis_history = []
                                # Add to session state for immediate access (will be overwritten by database load on next run)
                                st.session_state.analysis_history.insert(0, product_entry)  # Add to beginning for latest-first
                            
                            status_text.text("📊 Generating report...")
                            progress_bar.progress(80)
                            progress_bar.progress(100)
                            status_text.text("✅ Analysis complete!")
                            
                            # Clear progress indicators
                            time.sleep(1)
                            progress_bar.empty()
                            status_text.empty()
                        
                        # Show results
                        st.markdown("---")
                        st.subheader("📊 **ANALYSIS RESULTS**")
                        
                        # Add small reference image thumbnail
                        ref_col1, ref_col2 = st.columns([4, 1])
                        with ref_col2:
                            st.markdown("**📷 Analyzed Image:**")
                            st.image(image, width=150, caption="Reference")
                        
                        with ref_col1:
                            if api_error:
                                st.error(f"⚠️ Analysis error: {api_error}")
                                st.info("💡 Please try again in a few moments")
                            else:
                                if api_result:
                                    status = api_result.get('authenticity_status', 'unknown')
                                    confidence = api_result.get('confidence_score', 0.0)
                            
                            # Main Status Display with enhanced styling
                            col_status1, col_status2, col_status3 = st.columns([2, 1, 1])
                            
                            with col_status1:
                                # Status display with color coding
                                if status == 'authentic':
                                    st.success(f"✅ **AUTHENTIC PRODUCT**")
                                    st.markdown(f"🎯 **Confidence Level:** {confidence:.1%}")
                                elif status == 'fake':
                                    st.error(f"🚨 **FAKE/COUNTERFEIT DETECTED**")
                                    st.markdown(f"🎯 **Confidence Level:** {confidence:.1%}")
                                else:
                                    st.warning(f"⚠️ **AUTHENTICITY UNCERTAIN**")
                                    st.markdown(f"🎯 **Confidence Level:** {confidence:.1%}")
                            
                            with col_status2:
                                # Risk Assessment
                                if confidence >= 0.8:
                                    risk_level = "🟢 Low Risk"
                                elif confidence >= 0.6:
                                    risk_level = "🟡 Medium Risk" 
                                else:
                                    risk_level = "🔴 High Risk"
                                st.metric("🚨 Risk Level", risk_level)
                            
                            with col_status3:
                                # Quick Action
                                if status == 'authentic' and confidence >= 0.8:
                                    recommendation = "✅ Proceed"
                                elif status == 'fake':
                                    recommendation = "❌ Avoid"
                                else:
                                    recommendation = "⚠️ Caution"
                                st.metric("💡 Recommendation", recommendation)
                            
                            # DETAILED ANALYSIS SECTION - Always visible below authenticity
                            st.markdown("---")
                            st.subheader("🔬 **DETAILED ANALYSIS**")
                            
                            # Product Information Card
                            with st.container():
                                st.markdown("### 🏷️ Product Information")
                                product_details = api_result.get('product_details', {})
                                
                                prod_col1, prod_col2, prod_col3 = st.columns(3)
                                with prod_col1:
                                    st.metric("📦 Product Type", product_details.get('type', 'Unknown'))
                                    st.metric("🏭 Brand", product_details.get('brand', 'Unknown'))
                                with prod_col2:
                                    st.metric("🔖 Model", product_details.get('model', 'Unknown'))
                                    st.metric("🎨 Color", product_details.get('color', 'Unknown'))
                                with prod_col3:
                                    st.metric("💰 Est. Price", product_details.get('estimated_price_range', 'Unknown'))
                            
                            # Quality Assessment Grid
                            st.markdown("### ⭐ Quality Assessment")
                            quality = api_result.get('quality_assessment', {})
                            
                            qual_col1, qual_col2, qual_col3, qual_col4 = st.columns(4)
                            with qual_col1:
                                logo_quality = quality.get('logo_quality', 'N/A')
                                logo_color = "🟢" if logo_quality in ["excellent", "good"] else "🟡" if logo_quality == "poor" else "🔴"
                                st.metric(f"{logo_color} Logo Quality", logo_quality.title())
                            
                            with qual_col2:
                                material_quality = quality.get('material_quality', 'N/A')
                                material_color = "🟢" if material_quality in ["excellent", "good"] else "🟡" if material_quality == "poor" else "🔴"
                                st.metric(f"{material_color} Material", material_quality.title())
                            
                            with qual_col3:
                                construction_quality = quality.get('construction_quality', 'N/A')
                                construction_color = "🟢" if construction_quality in ["excellent", "good"] else "🟡" if construction_quality == "poor" else "🔴"
                                st.metric(f"{construction_color} Construction", construction_quality.title())
                            
                            with qual_col4:
                                overall_quality = quality.get('overall_craftsmanship', 'N/A')
                                overall_color = "🟢" if overall_quality in ["excellent", "good"] else "🟡" if overall_quality == "poor" else "🔴"
                                st.metric(f"{overall_color} Overall", overall_quality.title())
                            
                            # Component Analysis Tabs
                            st.markdown("### 🔍 Component Analysis")
                            detailed_analysis = api_result.get('detailed_analysis', {})
                            
                            analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4, analysis_tab5 = st.tabs([
                                "🏷️ Logo", "🧵 Material", "🔨 Construction", "⚙️ Hardware", "� Packaging"
                            ])
                            
                            with analysis_tab1:
                                st.write("**Logo Analysis:**")
                                st.info(detailed_analysis.get('logo_analysis', 'No logo analysis available'))
                            
                            with analysis_tab2:
                                st.write("**Material Analysis:**")
                                st.info(detailed_analysis.get('material_analysis', 'No material analysis available'))
                            
                            with analysis_tab3:
                                st.write("**Construction Analysis:**")
                                st.info(detailed_analysis.get('construction_analysis', 'No construction analysis available'))
                            
                            with analysis_tab4:
                                st.write("**Hardware Analysis:**")
                                st.info(detailed_analysis.get('hardware_analysis', 'No hardware analysis available'))
                            
                            with analysis_tab5:
                                st.write("**Packaging Analysis:**")
                                st.info(detailed_analysis.get('packaging_analysis', 'No packaging analysis available'))
                            
                            # Issues and Positive Indicators
                            st.markdown("### ⚖️ Findings Summary")
                            findings_col1, findings_col2 = st.columns(2)
                            
                            with findings_col1:
                                st.markdown("#### ⚠️ Issues Detected")
                                issues = api_result.get('detected_issues', [])
                                if issues and any(issue != "No specific issues detected" for issue in issues):
                                    for issue in issues:
                                        if issue != "No specific issues detected":
                                            st.error(f"🔴 {issue}")
                                else:
                                    st.success("✅ No major issues detected")
                            
                            with findings_col2:
                                st.markdown("#### ✅ Positive Indicators")
                                positives = api_result.get('positive_indicators', [])
                                if positives and len(positives) > 0:
                                    for positive in positives:
                                        st.success(f"🟢 {positive}")
                                else:
                                    st.info("ℹ️ No specific positive indicators noted")
                            
                            # Expert Recommendations
                            st.markdown("### 💡 Expert Recommendations")
                            recommendations = api_result.get('recommendations', {})
                            
                            rec_col1, rec_col2 = st.columns(2)
                            with rec_col1:
                                st.markdown("**🎯 Authenticity Verdict:**")
                                verdict = recommendations.get('authenticity_verdict', 'No verdict available')
                                st.write(verdict)
                                
                                st.markdown("**💰 Purchase Advice:**")
                                purchase_advice = recommendations.get('purchase_advice', 'No advice available')
                                st.write(purchase_advice)
                            
                            with rec_col2:
                                st.markdown("**🔍 Verification Tips:**")
                                verification_tips = recommendations.get('verification_tips', 'No tips available')
                                st.write(verification_tips)
                            
                            # Analysis Summary
                            summary = api_result.get('analysis_summary', '')
                            expert_notes = api_result.get('expert_notes', '')
                            
                            if summary or expert_notes:
                                st.markdown("### 📄 Analysis Summary")
                                if summary:
                                    st.info(f"📝 {summary}")
                                if expert_notes:
                                    st.success(f"👨‍🔬 Expert Notes: {expert_notes}")
                            
                            # Additional Features Section
                            st.markdown("---")
                            st.markdown("### 🚀 Additional Features")
                            
                            feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)
                            
                            with feature_col1:
                                if st.button("📄 Generate Report", use_container_width=True):
                                    st.session_state.show_report = True
                            
                            with feature_col2:
                                if st.button("📊 Compare Similar", use_container_width=True):
                                    st.session_state.show_comparison = True
                            
                            with feature_col3:
                                if st.button("💾 Save Analysis", use_container_width=True):
                                    st.session_state.save_analysis = True
                            
                            with feature_col4:
                                if st.button("📤 Share Results", use_container_width=True):
                                    st.session_state.share_results = True
                            
                            # Feature implementations
                            if st.session_state.get('show_report', False):
                                with st.expander("📄 Detailed Report", expanded=True):
                                    st.markdown("**PRODUCT AUTHENTICITY REPORT**")
                                    st.markdown(f"**Analysis Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
                                    st.markdown(f"**Product:** {product_details.get('brand', 'Unknown')} {product_details.get('model', 'Unknown')}")
                                    st.markdown(f"**Status:** {status.upper()}")
                                    st.markdown(f"**Confidence:** {confidence:.1%}")
                                    st.markdown("**Summary:** " + summary)
                                    
                                    # Download button for report
                                    report_data = f"""
PRODUCT AUTHENTICITY REPORT
Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
Product: {product_details.get('brand', 'Unknown')} {product_details.get('model', 'Unknown')}
Status: {status.upper()}
Confidence: {confidence:.1%}
Summary: {summary}
                                    """
                                    st.download_button(
                                        label="📥 Download Report",
                                        data=report_data,
                                        file_name=f"authenticity_report_{int(time.time())}.txt",
                                        mime="text/plain"
                                    )
                                
                                if st.button("❌ Close Report"):
                                    st.session_state.show_report = False
                                    st.rerun()
                            
                            if st.session_state.get('save_analysis', False):
                                st.success("💾 Analysis already saved automatically to history!")
                                st.info("ℹ️ All analyses are now automatically saved to your product history.")
                                st.session_state.save_analysis = False
                            
                            if st.session_state.get('share_results', False):
                                st.info("📤 Share functionality - Copy the analysis summary below:")
                                share_text = f"Product Analysis: {status.upper()} ({confidence:.1%} confidence) - {summary}"
                                st.code(share_text)
                                st.session_state.share_results = False
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.subheader("📝 **Product Details**")
                                    product_details = api_result.get('product_details', {})
                                    if product_details:
                                        st.write(f"**Type:** {product_details.get('type', 'Unknown')}")
                                        st.write(f"**Brand:** {product_details.get('brand', 'Unknown')}")
                                        st.write(f"**Model:** {product_details.get('model', 'Unknown')}")
                                        st.write(f"**Color:** {product_details.get('color', 'Unknown')}")
                                
                                with col2:
                                    st.subheader("⭐ **Quality Assessment**")
                                    quality = api_result.get('quality_assessment', {})
                                    if quality:
                                        st.write(f"**Logo Quality:** {quality.get('logo_quality', 'N/A')}")
                                        st.write(f"**Material Quality:** {quality.get('material_quality', 'N/A')}")
                                        st.write(f"**Construction Quality:** {quality.get('construction_quality', 'N/A')}")
                                
                                # Issues and recommendations
                                issues = api_result.get('detected_issues', [])
                                if issues:
                                    st.subheader("⚠️ **Detected Issues**")
                                    for issue in issues:
                                        if issue != "No specific issues detected":
                                            st.warning(f"• {issue}")
                                
                                # Summary
                                summary = api_result.get('analysis_summary', '')
                                if summary:
                                    st.subheader("📄 **Summary**")
                                    st.write(summary)
                            else:
                                st.info("Analysis completed but no detailed results available")
                                
                    except Exception as e:
                        st.error(f"❌ Error loading image: {str(e)}")
                
                elif upload_mode == "📂 Multiple Images (Batch Analysis)" and len(valid_files) > 1:
                    st.info("📂 Use the 'Start Batch Analysis' button above to analyze all images")
                
                else:
                    # Show appropriate message based on mode
                    if upload_mode == "📂 Multiple Images (Batch Analysis)":
                        if len(valid_files) == 1:
                            st.info("📂 Please upload at least 2 images for batch analysis, or switch to Single Image mode")
                        else:
                            st.info("📂 No images uploaded yet")
                    else:
                        st.info("📎 No file uploaded yet")
        
        elif scanner_mode == "📷 Camera Capture":
            # Enhanced camera interface with attractive design
            st.markdown("---")
            st.markdown("""
                <div style="background: linear-gradient(135deg, #e0f2fe, #b3e5fc); padding: 2rem; border-radius: 15px; border: 2px dashed rgba(33, 150, 243, 0.3); text-align: center; margin: 1rem 0;">
                    <h4 style="color: #0277bd; margin: 0;">📷 Camera Capture</h4>
                    <p style="color: #64748b; margin: 0.5rem 0;">Position your product and take a clear photo</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Camera input with improved error handling
            try:
                camera_photo = st.camera_input(
                    "📸 Take a picture of the product",
                    help="Position the product clearly in view and take a photo",
                    key="main_camera_input"
                )
                
                if camera_photo is not None:
                    st.success("📷 Photo captured successfully!")
                    
                    try:
                        image = Image.open(camera_photo)
                        
                        # Create columns for compact image display
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col2:
                            st.markdown("### 📷 **Captured Product Image**")
                            st.image(image, caption="📸 Camera Capture", width=400)
                    
                    except Exception as img_error:
                        st.error(f"❌ Error processing camera image: {str(img_error)}")
                        st.info("💡 Please try capturing the image again")
                
            except Exception as camera_error:
                st.error(f"❌ Camera error: {str(camera_error)}")
                st.info("💡 Camera might not be available in this browser. Please use file upload instead.")
            
            # Auto-analyze for camera if image is captured
            if 'camera_photo' in locals() and camera_photo is not None:
                try:
                    image = Image.open(camera_photo)
                    
                    # Auto-analyze for camera
                    with st.spinner("🤖 AI analyzing captured photo..."):
                        api_result, api_error = st.session_state.detector.analyze_with_ai_api(image)
                
                    # Automatically save to history if analysis was successful
                    if api_result and not api_error:
                        # Extract data for history
                        product_details = api_result.get('product_details', {})
                        quality = api_result.get('quality_assessment', {})
                        detailed_analysis = api_result.get('detailed_analysis', {})
                        recommendations = api_result.get('recommendations', {})
                        summary = api_result.get('analysis_summary', '')
                        status = api_result.get('authenticity_status', 'unknown')
                        confidence = api_result.get('confidence_score', 0.0)
                        
                        # Create detailed product entry
                        product_entry = {
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'status': status,
                            'confidence': confidence,
                            'product': f"{product_details.get('brand', 'Unknown')} {product_details.get('model', 'Unknown')}",
                            'brand': product_details.get('brand', 'Unknown'),
                            'model': product_details.get('model', 'Unknown'),
                            'category': product_details.get('type', 'Unknown'),
                            'color': product_details.get('color', 'Unknown'),
                            'price_range': product_details.get('estimated_price_range', 'Unknown'),
                            'logo_quality': quality.get('logo_quality', 'N/A'),
                            'material_quality': quality.get('material_quality', 'N/A'),
                            'construction_quality': quality.get('construction_quality', 'N/A'),
                            'overall_quality': quality.get('overall_craftsmanship', 'N/A'),
                            'detected_issues': api_result.get('detected_issues', []),
                            'positive_indicators': api_result.get('positive_indicators', []),
                            'analysis_summary': summary,
                            'expert_notes': api_result.get('expert_notes', ''),
                            'detailed_analysis': detailed_analysis,
                            'recommendations': recommendations
                        }
                        
                        # Save to database  
                        image_bytes = None
                        try:
                            # Convert camera photo to bytes
                            img_buffer = io.BytesIO()
                            image.save(img_buffer, format='PNG')
                            image_bytes = img_buffer.getvalue()
                        except Exception as img_conv_error:
                            st.warning(f"⚠️ Could not convert image for storage: {str(img_conv_error)}")
                        
                        # Save analysis to database
                        analysis_saved = st.session_state.history_manager.save_analysis(
                            product_entry, 
                            image_bytes, 
                            f"camera_capture_{int(time.time())}.png"
                        )
                        
                        if analysis_saved:
                            # Reload history to include the new analysis
                            st.session_state.analysis_history = st.session_state.history_manager.load_history()
                            st.success("✅ Analysis saved to database successfully!")
                        else:
                            st.error("❌ Failed to save analysis to database")
                        
                        # Also keep in session state for immediate display
                        if 'analysis_history' not in st.session_state:
                            st.session_state.analysis_history = []
                        st.session_state.analysis_history.insert(0, product_entry)  # Add to beginning
                        
                        # Also add to product database
                        if 'product_database' not in st.session_state:
                            st.session_state.product_database = []
                        st.session_state.product_database.append(product_entry)
                    
                    # Show results
                    st.markdown("---")
                    st.subheader("📊 **ANALYSIS RESULTS**")
                    
                    if api_error:
                        st.error(f"⚠️ Analysis error: {api_error}")
                        st.info("💡 Please try again")
                    else:
                        if api_result:
                            status = api_result.get('authenticity_status', 'unknown')
                            confidence = api_result.get('confidence_score', 0.0)
                            
                            # Status display
                            if status == 'authentic':
                                st.success(f"✅ **AUTHENTIC** (Confidence: {confidence:.1%})")
                            elif status == 'fake':
                                st.error(f"🚨 **FAKE/COUNTERFEIT** (Confidence: {confidence:.1%})")
                            else:
                                st.warning(f"⚠️ **UNCERTAIN** (Confidence: {confidence:.1%})")
                            
                            # Quick summary
                            summary = api_result.get('analysis_summary', '')
                            if summary:
                                st.write(summary)
                                
                except Exception as e:
                    st.error(f"❌ Error processing camera image: {str(e)}")
    
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_tab == 'history':
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.header("📚 Comprehensive Product History & Analytics")
        
        # History Dashboard
        if not st.session_state.analysis_history:
            st.info("🔍 No product history yet. Analyze some products to build your database!")
            st.markdown("""
            ### 🚀 Get Started:
            1. Upload product images in the **Upload Image** tab
            2. Use the **Live Camera** feature to capture products
            3. Build your comprehensive product database
            4. Track authenticity patterns over time
            """)
        else:
            # Analytics Overview
            st.markdown("### 📊 Analytics Overview")
            
            # Get statistics from database
            stats = st.session_state.history_manager.get_statistics(days=30)
            all_time_stats = st.session_state.history_manager.get_statistics(days=365)
            
            # Use database statistics if available, fallback to session state for compatibility
            total_products = all_time_stats.get('total_analyses', len(st.session_state.analysis_history))
            authenticity_counts = all_time_stats.get('authenticity_counts', {})
            authentic_count = authenticity_counts.get('authentic', sum(1 for p in st.session_state.analysis_history if p.get('status') == 'authentic'))
            fake_count = authenticity_counts.get('counterfeit', sum(1 for p in st.session_state.analysis_history if p.get('status') in ['fake', 'counterfeit']))
            uncertain_count = authenticity_counts.get('uncertain', sum(1 for p in st.session_state.analysis_history if p.get('status') == 'uncertain'))
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📦 Total Products", total_products)
            with col2:
                percentage = f"{(authentic_count/total_products)*100:.1f}%" if total_products > 0 else "0%"
                st.metric("✅ Authentic", authentic_count, percentage)
            with col3:
                percentage = f"{(fake_count/total_products)*100:.1f}%" if total_products > 0 else "0%"
                st.metric("🚨 Counterfeit", fake_count, percentage)
            with col4:
                percentage = f"{(uncertain_count/total_products)*100:.1f}%" if total_products > 0 else "0%"
                st.metric("⚠️ Uncertain", uncertain_count, percentage)
            
            # Advanced Analytics
            st.markdown("### 📈 Advanced Analytics")
            
            analytics_col1, analytics_col2 = st.columns(2)
            
            with analytics_col1:
                # Brand Analysis
                st.markdown("#### 🏭 Brand Analysis")
                brands = {}
                brand_authenticity = {}
                
                for product in st.session_state.analysis_history:
                    brand = product.get('brand', 'Unknown')
                    brands[brand] = brands.get(brand, 0) + 1
                    
                    if brand not in brand_authenticity:
                        brand_authenticity[brand] = {'authentic': 0, 'fake': 0, 'counterfeit': 0, 'uncertain': 0}
                    status = get_analysis_status(product)
                    # Normalize status names
                    if status == 'fake':
                        status = 'counterfeit'
                    if status in brand_authenticity[brand]:
                        brand_authenticity[brand][status] += 1
                
                if len(brands) > 0:
                    # Top brands
                    sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)
                    for brand, count in sorted_brands[:5]:
                        auth_rate = (brand_authenticity[brand]['authentic'] / count) * 100
                        st.write(f"**{brand}:** {count} products ({auth_rate:.1f}% authentic)")
                
                # Quality Trends
                st.markdown("#### ⭐ Quality Trends")
                quality_metrics = {}
                for product in st.session_state.analysis_history:
                    for metric in ['logo_quality', 'material_quality', 'construction_quality']:
                        quality = product.get(metric, 'N/A')
                        if quality != 'N/A':
                            if metric not in quality_metrics:
                                quality_metrics[metric] = {}
                            quality_metrics[metric][quality] = quality_metrics[metric].get(quality, 0) + 1
                
                for metric, values in quality_metrics.items():
                    st.write(f"**{metric.replace('_', ' ').title()}:**")
                    for quality, count in values.items():
                        percentage = (count / total_products) * 100
                        st.write(f"  • {quality.title()}: {count} ({percentage:.1f}%)")
            
            with analytics_col2:
                # Category Analysis
                st.markdown("#### 📦 Category Analysis")
                categories = {}
                for product in st.session_state.analysis_history:
                    category = product.get('category', 'Unknown')
                    categories[category] = categories.get(category, 0) + 1
                
                if len(categories) > 0:
                    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                    for category, count in sorted_categories:
                        percentage = (count / total_products) * 100
                        st.write(f"**{category}:** {count} products ({percentage:.1f}%)")
                
                # Confidence Analysis
                st.markdown("#### 🎯 Confidence Analysis")
                high_conf = sum(1 for p in st.session_state.analysis_history if get_analysis_confidence(p) >= 0.8)
                med_conf = sum(1 for p in st.session_state.analysis_history if 0.5 <= get_analysis_confidence(p) < 0.8)
                low_conf = sum(1 for p in st.session_state.analysis_history if get_analysis_confidence(p) < 0.5)
                
                st.write(f"**High Confidence (≥80%):** {high_conf} ({(high_conf/total_products)*100:.1f}%)")
                st.write(f"**Medium Confidence (50-79%):** {med_conf} ({(med_conf/total_products)*100:.1f}%)")
                st.write(f"**Low Confidence (<50%):** {low_conf} ({(low_conf/total_products)*100:.1f}%)")
                
                # Average confidence by status
                avg_conf_authentic = sum(get_analysis_confidence(p) for p in st.session_state.analysis_history if get_analysis_status(p) == 'authentic') / max(authentic_count, 1)
                avg_conf_fake = sum(get_analysis_confidence(p) for p in st.session_state.analysis_history if get_analysis_status(p) == 'fake') / max(fake_count, 1)
                
                st.write(f"**Avg Confidence - Authentic:** {avg_conf_authentic:.1%}")
                st.write(f"**Avg Confidence - Fake:** {avg_conf_fake:.1%}")
            
            st.markdown("---")
            
            # Detailed Product History
            st.markdown("### 📋 Detailed Product History")
            
            # Filters and sorting
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                status_filter = st.selectbox("Filter by Status:", ["All", "Authentic", "Fake", "Uncertain"], key="status_filter")
            
            with filter_col2:
                brand_filter = st.selectbox("Filter by Brand:", ["All"] + list(set(p.get('brand', 'Unknown') for p in st.session_state.analysis_history)), key="brand_filter")
            
            with filter_col3:
                sort_by = st.selectbox("Sort by:", ["Newest First", "Oldest First", "Highest Confidence", "Lowest Confidence"], key="sort_filter")
            
            # Apply filters
            filtered_products = st.session_state.analysis_history.copy()
            
            if status_filter != "All":
                filtered_products = [p for p in filtered_products if get_analysis_status(p) == status_filter.lower()]
            
            if brand_filter != "All":
                filtered_products = [p for p in filtered_products if p.get('brand', 'Unknown') == brand_filter]
            
            # Apply sorting
            if sort_by == "Newest First":
                filtered_products = sorted(filtered_products, key=lambda x: x['timestamp'], reverse=True)
            elif sort_by == "Oldest First":
                filtered_products = sorted(filtered_products, key=lambda x: x['timestamp'])
            elif sort_by == "Highest Confidence":
                filtered_products = sorted(filtered_products, key=lambda x: x['confidence'], reverse=True)
            elif sort_by == "Lowest Confidence":
                filtered_products = sorted(filtered_products, key=lambda x: x['confidence'])
            
            # Display products
            st.write(f"**Showing {len(filtered_products)} of {total_products} products**")
            
            for i, product in enumerate(filtered_products):
                status = get_analysis_status(product)
                status_emoji = {"authentic": "✅", "fake": "🚨", "counterfeit": "🚨", "uncertain": "⚠️"}.get(status, "❓")
                
                with st.expander(f"{status_emoji} {get_analysis_brand(product)} {product.get('model', 'Unknown')} - {product.get('timestamp', 'Unknown')}", expanded=False):
                    # Product overview
                    overview_col1, overview_col2, overview_col3 = st.columns(3)
                    
                    with overview_col1:
                        st.write("**📦 Product Info:**")
                        st.write(f"Brand: {product.get('brand', 'Unknown')}")
                        st.write(f"Model: {product.get('model', 'Unknown')}")
                        st.write(f"Category: {product.get('category', 'Unknown')}")
                        st.write(f"Color: {product.get('color', 'Unknown')}")
                    
                    with overview_col2:
                        st.write("**🎯 Analysis Results:**")
                        st.write(f"Status: {get_analysis_status(product).title()}")
                        st.write(f"Confidence: {get_analysis_confidence(product):.1%}")
                        st.write(f"Date: {product['timestamp']}")
                        st.write(f"Price Range: {product.get('price_range', 'Unknown')}")
                    
                    with overview_col3:
                        st.write("**⭐ Quality Scores:**")
                        st.write(f"Logo: {product.get('logo_quality', 'N/A')}")
                        st.write(f"Material: {product.get('material_quality', 'N/A')}")
                        st.write(f"Construction: {product.get('construction_quality', 'N/A')}")
                        st.write(f"Overall: {product.get('overall_quality', 'N/A')}")
                    
                    # Detailed analysis
                    if st.button("📋 View Full Analysis", key=f"view_analysis_{i}"):
                        st.markdown("**🔬 Detailed Analysis:**")
                        detailed = product.get('detailed_analysis', {})
                        for component, analysis in detailed.items():
                            st.write(f"**{component.replace('_', ' ').title()}:** {analysis}")
                        
                        st.markdown("**⚠️ Issues Detected:**")
                        issues = product.get('detected_issues', [])
                        for issue in issues:
                            st.write(f"• {issue}")
                        
                        st.markdown("**✅ Positive Indicators:**")
                        positives = product.get('positive_indicators', [])
                        for positive in positives:
                            st.write(f"• {positive}")
                        
                        if product.get('analysis_summary'):
                            st.markdown("**📄 Summary:**")
                            st.info(product['analysis_summary'])
                    
                    # Action buttons
                    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                    
                    with action_col1:
                        if st.button("⭐ Favorite", key=f"fav_main_{i}"):
                            if product not in st.session_state.favorite_products:
                                st.session_state.favorite_products.append(product)
                                if st.session_state.auto_save:
                                    st.session_state.history_manager.save_favorites(st.session_state.favorite_products)
                                st.success("Added to favorites!")
                                st.rerun()
                    
                    with action_col2:
                        if st.button("🚨 Flag", key=f"flag_main_{i}"):
                            if product not in st.session_state.flagged_products:
                                st.session_state.flagged_products.append(product)
                                if st.session_state.auto_save:
                                    st.session_state.history_manager.save_flagged(st.session_state.flagged_products)
                                st.warning("Product flagged!")
                                st.rerun()
                    
                    with action_col3:
                        if st.button("📤 Export", key=f"export_main_{i}"):
                            product_data = json.dumps(product, indent=2, default=str)
                            st.download_button(
                                label="📥 Download JSON",
                                data=product_data,
                                file_name=f"product_analysis_{product['timestamp'].replace(':', '-').replace(' ', '_')}.json",
                                mime="application/json",
                                key=f"download_main_{i}"
                            )
                    
                    with action_col4:
                        if st.button("🗑️ Delete", key=f"delete_main_{i}"):
                            st.session_state.analysis_history.remove(product)
                            st.success("Product deleted!")
                            st.rerun()
            
            # Bulk actions
            st.markdown("---")
            st.markdown("### 🔧 Bulk Actions")
            
            bulk_col1, bulk_col2, bulk_col3 = st.columns(3)
            
            with bulk_col1:
                if st.button("📊 Export All Data", use_container_width=True):
                    df = pd.DataFrame(st.session_state.analysis_history)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"product_history_{int(time.time())}.csv",
                        mime="text/csv"
                    )
            
            with bulk_col2:
                if st.button("🗑️ Clear All History", use_container_width=True):
                    if st.checkbox("⚠️ Confirm deletion", key="confirm_delete_all"):
                        st.session_state.analysis_history = []
                        st.session_state.product_database = []
                        st.session_state.favorite_products = []
                        st.session_state.flagged_products = []
                        st.success("All history cleared!")
                        st.rerun()
            
            with bulk_col3:
                if st.button("📈 Generate Report", use_container_width=True):
                    st.session_state.show_full_report = True
            
            # Full analytics report
            if st.session_state.get('show_full_report', False):
                st.markdown("---")
                st.markdown("### 📊 Comprehensive Analytics Report")
                
                report_data = f"""
# Product Analysis Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Total Products Analyzed: {total_products}
- Authentic Products: {authentic_count} ({(authentic_count/total_products)*100:.1f}%)
- Counterfeit Products: {fake_count} ({(fake_count/total_products)*100:.1f}%)
- Uncertain Products: {uncertain_count} ({(uncertain_count/total_products)*100:.1f}%)

## Brand Analysis
{chr(10).join([f'- {brand}: {count} products' for brand, count in sorted_brands[:10]])}

## Category Analysis  
{chr(10).join([f'- {category}: {count} products' for category, count in sorted_categories[:10]])}

## Confidence Analysis
- High Confidence (≥80%): {high_conf} products ({(high_conf/total_products)*100:.1f}%)
- Medium Confidence (50-79%): {med_conf} products ({(med_conf/total_products)*100:.1f}%)
- Low Confidence (<50%): {low_conf} products ({(low_conf/total_products)*100:.1f}%)
                """
                
                st.markdown(report_data)
                
                st.download_button(
                    label="📥 Download Full Report",
                    data=report_data,
                    file_name=f"analytics_report_{int(time.time())}.md",
                    mime="text/markdown"
                )
                
                if st.button("❌ Close Report"):
                    st.session_state.show_full_report = False
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_tab == 'analytics':
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.header("📊 Advanced Analytics Dashboard")
        
        if st.session_state.analysis_history:
            total_products = len(st.session_state.analysis_history)
            authentic_count = sum(1 for p in st.session_state.analysis_history if get_analysis_status(p) == 'authentic')
            fake_count = sum(1 for p in st.session_state.analysis_history if get_analysis_status(p) == 'fake')
            uncertain_count = total_products - authentic_count - fake_count
            
            # Mobile-style stats cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="stat-card">
                        <h3>📊 {total_products}</h3>
                        <p>Total Scans</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="stat-card">
                        <h3>✅ {authentic_count}</h3>
                        <p>Authentic</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="stat-card">
                        <h3>🚨 {fake_count}</h3>
                        <p>Counterfeit</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                accuracy = (authentic_count + fake_count) / total_products * 100 if total_products > 0 else 0
                st.markdown(f"""
                    <div class="stat-card">
                        <h3>🎯 {accuracy:.1f}%</h3>
                        <p>Accuracy</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Interactive charts
            st.markdown("### 📈 **Analysis Trends**")
            
            # Authenticity distribution pie chart
            if total_products > 0:
                fig_pie = px.pie(
                    values=[authentic_count, fake_count, uncertain_count],
                    names=['Authentic', 'Counterfeit', 'Uncertain'],
                    title="Product Authenticity Distribution",
                    color_discrete_map={
                        'Authentic': '#4CAF50',
                        'Counterfeit': '#F44336',
                        'Uncertain': '#FF9800'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Timeline analysis
            try:
                df = pd.DataFrame(st.session_state.analysis_history)
                if not df.empty:
                    # Debug: Show available columns
                    st.write("Debug - Available columns:", df.columns.tolist())
                    
                    if 'timestamp' in df.columns:
                        df['date'] = pd.to_datetime(df['timestamp']).dt.date
                        
                        # Create status column using helper function
                        df['status'] = df.apply(lambda row: get_analysis_status(row), axis=1)
                        
                        # Debug: Show sample data
                        st.write("Debug - Sample data with status:", df[['date', 'status']].head())
                        
                        daily_counts = df.groupby(['date', 'status']).size().reset_index(name='count')
                        
                        if not daily_counts.empty:
                            fig_timeline = px.line(
                                daily_counts, 
                                x='date', 
                                y='count', 
                                color='status',
                                title="Daily Analysis Activity",
                                color_discrete_map={
                                    'authentic': '#4CAF50',
                                    'fake': '#F44336',
                                    'uncertain': '#FF9800'
                                }
                            )
                            st.plotly_chart(fig_timeline, use_container_width=True)
                        else:
                            st.info("📈 Not enough data for timeline analysis")
                    else:
                        st.warning("⚠️ Timeline data format issue - missing timestamp")
                        st.write("Available columns:", df.columns.tolist())
                elif df.empty:
                    st.info("📈 No historical data available for timeline")
            except Exception as e:
                st.error(f"Error creating timeline chart: {str(e)}")
                st.write("Debug error details:", str(e))
                if 'df' in locals():
                    st.write("DataFrame info:", df.info() if not df.empty else "Empty DataFrame")
                st.info("📈 Timeline analysis temporarily unavailable")
        else:
            st.info("📊 No data available for analytics. Start scanning products to see insights!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.current_tab == 'settings':
        st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
        st.header("⚙️ App Settings & Configuration")
        
        # API Configuration
        st.markdown("### 🔑 **API Configuration**")
        
        # Load current API key if exists
        current_api_key = st.session_state.get('gemini_api_key', '')
        
        api_key = st.text_input(
            "Google Gemini API Key",
            value=current_api_key,
            type="password",
            help="Enter your Google Gemini API key for AI analysis"
        )
        
        if api_key != current_api_key:
            st.session_state.gemini_api_key = api_key
            if api_key:
                st.success("✅ API key updated successfully!")
            else:
                st.warning("⚠️ API key cleared")
        
        # App Preferences
        st.markdown("### 📱 **App Preferences**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_save = st.checkbox(
                "🔄 Auto-save results",
                value=st.session_state.get('auto_save', True),
                help="Automatically save analysis results to history"
            )
            st.session_state.auto_save = auto_save
            
            confidence_threshold = st.slider(
                "🎯 Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get('confidence_threshold', 0.7),
                step=0.1,
                help="Minimum confidence for positive identification"
            )
            st.session_state.confidence_threshold = confidence_threshold
        
        with col2:
            notifications = st.checkbox(
                "🔔 Enable notifications",
                value=True,
                help="Show analysis completion notifications"
            )
            
            dark_mode = st.checkbox(
                "🌙 Dark mode (Coming Soon)",
                value=False,
                disabled=True,
                help="Switch to dark theme"
            )
        
        # Data Management
        st.markdown("### 📊 **Data Management**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export Data", use_container_width=True):
                if st.session_state.history_manager:
                    export_data = st.session_state.history_manager.export_all_data()
                    st.download_button(
                        label="💾 Download Export",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"product_analysis_export_{int(time.time())}.json",
                        mime="application/json"
                    )
        
        with col2:
            if st.button("🗑️ Clear History", use_container_width=True):
                if st.checkbox("⚠️ Confirm deletion"):
                    st.session_state.analysis_history = []
                    st.session_state.favorite_products = []
                    st.session_state.flagged_products = []
                    st.success("✅ All data cleared!")
                    st.rerun()
        
        with col3:
            if st.button("🔄 Reset Settings", use_container_width=True):
                if st.checkbox("⚠️ Confirm reset"):
                    st.session_state.confidence_threshold = 0.7
                    st.session_state.auto_save = True
                    st.success("✅ Settings reset to defaults!")
                    st.rerun()
        
        # App Information
        st.markdown("### ℹ️ **About**")
        st.info("""
        **Product Authentication System v2.0**
        
        🔍 AI-powered authenticity analysis  
        📱 Mobile-optimized interface  
        🤖 Google Gemini integration  
        📊 Advanced analytics  
        🔐 Privacy-focused design  
        
        Built with Streamlit & React Native
        """)

if __name__ == "__main__":
    main()
