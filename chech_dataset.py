import os
import shutil
from pathlib import Path
import random

def setup_dataset():
    # Create required directories
    dataset_dirs = [
        'dataset/images/train',
        'dataset/images/val',
        'dataset/labels/train',
        'dataset/labels/val'
    ]
    for d in dataset_dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        
    # Get all images from train directory
    train_images = list(Path('dataset/images/train').glob('*.*'))
    print(f"Found {len(train_images)} images in train directory")
    
    # Split into train/val sets
    random.shuffle(train_images)
    val_size = int(len(train_images) * 0.2)  # 20% for validation
    val_images = train_images[:val_size]
    
    # Move validation images and their labels
    for img_path in val_images:
        # Move image to val folder
        dst_img = Path('dataset/images/val') / img_path.name
        shutil.move(str(img_path), str(dst_img))
        
        # Move corresponding label if it exists
        label_path = Path('dataset/labels/train') / (img_path.stem + '.txt')
        if label_path.exists():
            dst_label = Path('dataset/labels/val') / (img_path.stem + '.txt')
            shutil.move(str(label_path), str(dst_label))
    
    print(f"Moved {len(val_images)} images to validation set")

if __name__ == "__main__":
    setup_dataset()