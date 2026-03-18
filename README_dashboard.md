# 🔍 Fake Product Detector Dashboard

A comprehensive web-based dashboard for detecting fake products using YOLO object detection.

## 🚀 Quick Start

### 1. Launch the Dashboard
```bash
python launch_dashboard.py
```

### 2. Open in Browser
The dashboard will automatically open at: `http://localhost:8501`

## 📱 Features

### 🔍 **Single Image Detection**
- Upload individual images for product detection
- Real-time confidence scoring
- Visual bounding box annotations
- Detailed detection results

### 📸 **Batch Processing**
- Upload multiple images simultaneously
- Bulk detection analysis
- Downloadable CSV results
- Summary statistics

### 📈 **Performance Metrics**
- Training loss curves
- mAP (Mean Average Precision) metrics
- Confusion matrices
- Training visualization samples

### ℹ️ **Model Information**
- Model specifications
- Dataset details
- Performance notes
- Usage instructions

## 🎯 Dashboard Navigation

### Main Pages:
1. **🔍 Detection** - Single image analysis
2. **📈 Performance Metrics** - Training results and charts
3. **📸 Batch Processing** - Multiple image processing
4. **ℹ️ Model Info** - Model and dataset information

### Sidebar Controls:
- **Model Status** - Current model loading status
- **Confidence Threshold** - Adjust detection sensitivity (0.0 - 1.0)
- **Navigation Menu** - Switch between different pages

## 📊 How to Use

### Single Image Detection:
1. Navigate to "🔍 Detection" page
2. Click "Choose an image..." to upload
3. View original vs detected results
4. Check detection summary and confidence scores

### Batch Processing:
1. Go to "📸 Batch Processing" page
2. Upload multiple images at once
3. Monitor processing progress
4. Download results as CSV file

### View Training Metrics:
1. Visit "📈 Performance Metrics" page
2. Analyze training curves and final metrics
3. Review confusion matrices and PR curves

## ⚙️ Configuration

### Confidence Threshold:
- **Low (0.1-0.3)**: More detections, may include false positives
- **Medium (0.3-0.7)**: Balanced detection accuracy
- **High (0.7-1.0)**: Only high-confidence detections

### Supported File Formats:
- **Images**: JPG, JPEG, PNG
- **Batch Size**: No limit (processing time increases with more images)

## 🔧 Technical Details

### Model Information:
- **Architecture**: YOLOv8 (You Only Look Once v8)
- **Classes**: Real, Fake
- **Input Size**: 640x640 pixels
- **Framework**: PyTorch via Ultralytics

### Performance Notes:
- Current model trained on limited dataset (5 images)
- mAP50 = 0.0000 (indicates need for more training data)
- Recommended: 100+ labeled images per class for production use

## 🚨 Troubleshooting

### Dashboard Won't Start:
```bash
# Install missing packages
pip install streamlit opencv-python plotly ultralytics

# Check if all files exist
ls dashboard.py launch_dashboard.py
```

### Model Not Found:
- Ensure training completed successfully
- Check that `runs/fake_product_detector27/weights/best.pt` exists
- Re-run training if model is missing

### Low Detection Accuracy:
- Increase training dataset size
- Verify label quality
- Adjust confidence threshold
- Consider retraining with more epochs

### Browser Issues:
- Try different browser (Chrome, Firefox, Edge)
- Clear browser cache
- Check if port 8501 is available
- Restart dashboard if needed

## 📝 Future Improvements

### Recommended Enhancements:
1. **More Training Data**: Collect 100+ images per class
2. **Data Augmentation**: Improve model robustness
3. **Real-time Processing**: Add webcam support
4. **API Integration**: REST API for external applications
5. **Mobile Support**: Responsive design for mobile devices

## 🔗 Additional Resources

- **YOLO Documentation**: https://docs.ultralytics.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Model Training Guide**: See `train_yolo.py` and training scripts

## 🎉 Happy Detecting!

Your fake product detection dashboard is ready to use. Upload images and start detecting fake products with confidence!

---

**Note**: This dashboard is built for the fake product detection model. Ensure your model is properly trained before using for production applications.