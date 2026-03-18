from ultralytics import YOLO
import os
from pathlib import Path

def verify_dataset():
    train_path = Path("dataset/images/train")
    val_path = Path("dataset/images/val")
    
    if not train_path.exists() or not val_path.exists():
        raise FileNotFoundError("Dataset directories not found. Run setup_dataset.py first")
        
    train_images = list(train_path.glob("*.*"))
    val_images = list(val_path.glob("*.*"))
    
    if len(train_images) == 0 or len(val_images) == 0:
        raise ValueError(f"Not enough images found. Train: {len(train_images)}, Val: {len(val_images)}")

def train_model():
    verify_dataset()
    
    # Load pre-trained model
    model = YOLO("yolov8m.pt")
    
    # Train the model
    model.train(
        data="dataset/data.yaml",
        epochs=50,
        imgsz=640,
        batch=16,
        name="fake_product_detector2",
        project="runs",
        patience=50,
        save=True,
        device='cpu'  # Change to 'cuda' if you have a GPU
    )

if __name__ == "__main__":
    train_model()