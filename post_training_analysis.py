import os
import pandas as pd
import matplotlib.pyplot as plt
from ultralytics import YOLO
import cv2
import numpy as np

def analyze_training_results(run_path="runs/fake_product_detector27"):
    """
    Analyze the results after YOLO training completion
    """
    print("=" * 60)
    print("🎯 POST-TRAINING ANALYSIS")
    print("=" * 60)
    
    # 1. Check if training completed successfully
    weights_path = os.path.join(run_path, "weights")
    if not os.path.exists(weights_path):
        print("❌ Training weights not found. Training may not have completed.")
        return
    
    # Check for best and last weights
    best_weights = os.path.join(weights_path, "best.pt")
    last_weights = os.path.join(weights_path, "last.pt")
    
    print(f"📁 Training Results Directory: {run_path}")
    print(f"✅ Best weights: {'Found' if os.path.exists(best_weights) else 'Missing'}")
    print(f"✅ Last weights: {'Found' if os.path.exists(last_weights) else 'Missing'}")
    
    # 2. Load and display training metrics
    results_csv = os.path.join(run_path, "results.csv")
    if os.path.exists(results_csv):
        print("\n📊 TRAINING METRICS:")
        df = pd.read_csv(results_csv)
        print(f"   Total epochs trained: {len(df)}")
        
        # Get final metrics
        final_metrics = df.iloc[-1]
        print(f"   Final Box Loss: {final_metrics.get('train/box_loss', 'N/A'):.4f}")
        print(f"   Final Class Loss: {final_metrics.get('train/cls_loss', 'N/A'):.4f}")
        print(f"   Final mAP50: {final_metrics.get('metrics/mAP50(B)', 'N/A'):.4f}")
        print(f"   Final mAP50-95: {final_metrics.get('metrics/mAP50-95(B)', 'N/A'):.4f}")
        
        # Show best metrics
        if 'metrics/mAP50(B)' in df.columns:
            best_map50 = df['metrics/mAP50(B)'].max()
            best_epoch = df['metrics/mAP50(B)'].idxmax() + 1
            print(f"   Best mAP50: {best_map50:.4f} (Epoch {best_epoch})")
    
    # 3. List generated visualization files
    print("\n🖼️ GENERATED VISUALIZATIONS:")
    viz_files = [
        "results.png", "confusion_matrix.png", "BoxPR_curve.png", 
        "labels.jpg", "train_batch0.jpg"
    ]
    
    for viz_file in viz_files:
        viz_path = os.path.join(run_path, viz_file)
        if os.path.exists(viz_path):
            print(f"   ✅ {viz_file}")
        else:
            print(f"   ❌ {viz_file}")
    
    return best_weights if os.path.exists(best_weights) else None

def test_trained_model(weights_path, test_image_path=None):
    """
    Test the trained model on sample images
    """
    print("\n" + "=" * 60)
    print("🔬 MODEL TESTING")
    print("=" * 60)
    
    if not os.path.exists(weights_path):
        print(f"❌ Weights file not found: {weights_path}")
        return
    
    # Load the trained model
    print(f"📦 Loading model from: {weights_path}")
    model = YOLO(weights_path)
    
    # Test on training images if no specific test image provided
    if test_image_path is None:
        train_images_dir = "dataset/images/train"
        if os.path.exists(train_images_dir):
            test_images = [f for f in os.listdir(train_images_dir) if f.endswith('.jpg')][:5]
            print(f"🖼️ Testing on {len(test_images)} training images...")
            
            for img_file in test_images:
                img_path = os.path.join(train_images_dir, img_file)
                print(f"   Testing: {img_file}")
                
                # Run inference
                results = model(img_path)
                
                # Print detections
                for i, result in enumerate(results):
                    boxes = result.boxes
                    if boxes is not None:
                        print(f"     Detected {len(boxes)} objects")
                        for box in boxes:
                            conf = float(box.conf[0])
                            cls = int(box.cls[0])
                            class_name = model.names[cls]
                            print(f"       - {class_name}: {conf:.3f}")
                    else:
                        print(f"     No objects detected")
    
    return model

def create_inference_script(weights_path):
    """
    Create a script for easy inference on new images
    """
    inference_script = f'''
from ultralytics import YOLO
import cv2

def detect_fake_products(image_path, weights_path="{weights_path}"):
    """
    Detect fake products in an image using the trained YOLO model
    """
    # Load the trained model
    model = YOLO(weights_path)
    
    # Run inference
    results = model(image_path)
    
    # Process results
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Get detection details
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                
                print(f"Detected: {{class_name}} (confidence: {{conf:.3f}})")
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                print(f"Location: x1={{x1:.0f}}, y1={{y1:.0f}}, x2={{x2:.0f}}, y2={{y2:.0f}}")
        else:
            print("No objects detected")
    
    return results

# Example usage:
if __name__ == "__main__":
    # Test on a single image
    image_path = "path/to/your/test/image.jpg"
    results = detect_fake_products(image_path)
    
    # Save results with annotations
    results[0].save("detection_results.jpg")
    print("Results saved to detection_results.jpg")
'''
    
    script_path = "inference_script.py"
    with open(script_path, 'w') as f:
        f.write(inference_script)
    
    print(f"\n📝 Created inference script: {script_path}")
    return script_path

def main():
    """
    Main function to run complete post-training analysis
    """
    # Find the most recent training run
    runs_dir = "runs"
    if os.path.exists(runs_dir):
        run_folders = [f for f in os.listdir(runs_dir) if f.startswith("fake_product_detector")]
        if run_folders:
            # Sort by modification time to get the most recent
            run_folders.sort(key=lambda x: os.path.getmtime(os.path.join(runs_dir, x)), reverse=True)
            latest_run = os.path.join(runs_dir, run_folders[0])
            
            print(f"🔍 Analyzing latest training run: {latest_run}")
            
            # Analyze training results
            best_weights = analyze_training_results(latest_run)
            
            if best_weights:
                # Test the trained model
                model = test_trained_model(best_weights)
                
                # Create inference script
                create_inference_script(best_weights)
                
                print("\n" + "=" * 60)
                print("🎉 NEXT STEPS RECOMMENDATIONS:")
                print("=" * 60)
                print("1. 📊 Review the training plots in the results directory")
                print("2. 🔬 Test the model on new images using inference_script.py")
                print("3. 📈 If performance is low, consider:")
                print("   - Adding more labeled training data")
                print("   - Adjusting hyperparameters")
                print("   - Training for more epochs")
                print("4. 🚀 Deploy the model for production use")
                print("5. 📱 Integrate into your application")
                
                return best_weights
            else:
                print("❌ No valid model weights found. Training may have failed.")
        else:
            print("❌ No training runs found in the runs directory.")
    else:
        print("❌ No runs directory found. Have you completed training?")
    
    return None

if __name__ == "__main__":
    main()