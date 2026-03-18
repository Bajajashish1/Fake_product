from ultralytics import YOLO

# Load the trained model
model = YOLO("runs/fake_product_detector/weights/best.pt")

# Test on your validation images
results = model.predict(source="dataset/fake_product_detection/images/val", conf=0.4, save=True)

print("✅ Detection complete! Check the 'runs/detect/predict' folder for output images.")
