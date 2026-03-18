from ultralytics import YOLO
import os
import cv2

def test_trained_model():
    """
    Test the trained YOLO model on sample images
    """
    print("🔬 Testing Trained YOLO Model")
    print("=" * 50)
    
    # Path to your best trained model
    model_path = "runs/fake_product_detector27/weights/best.pt"
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        print("Please check if training completed successfully.")
        return
    
    # Load the trained model
    print(f"📦 Loading model from: {model_path}")
    model = YOLO(model_path)
    
    # Test on training images
    test_images_dir = "dataset/images/train"
    test_images = [f for f in os.listdir(test_images_dir) if f.endswith('.jpg')][:5]
    
    print(f"\n🖼️ Testing on {len(test_images)} sample images:")
    print("-" * 50)
    
    for i, img_file in enumerate(test_images, 1):
        img_path = os.path.join(test_images_dir, img_file)
        print(f"\n{i}. Testing: {img_file}")
        
        # Run inference
        results = model(img_path, verbose=False)
        
        # Process and display results
        for result in results:
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                print(f"   ✅ Detected {len(boxes)} objects:")
                for j, box in enumerate(boxes):
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = model.names[cls]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    print(f"      {j+1}. {class_name}: {conf:.3f} confidence")
                    print(f"         Location: ({x1:.0f},{y1:.0f}) to ({x2:.0f},{y2:.0f})")
            else:
                print(f"   ❌ No objects detected")
        
        # Save annotated result
        output_path = f"test_result_{i}.jpg"
        results[0].save(output_path)
        print(f"   💾 Saved annotated image: {output_path}")
    
    print("\n" + "=" * 50)
    print("🎯 TESTING COMPLETE")
    print("=" * 50)
    print("📊 Summary:")
    print("• Check the saved test_result_*.jpg files to see detections")
    print("• Low confidence scores indicate the model needs more training data")
    print("• If no objects are detected, the model may need retraining")
    
    return model

def inference_example(image_path):
    """
    Example of how to use the trained model for inference
    """
    model_path = "runs/fake_product_detector27/weights/best.pt"
    model = YOLO(model_path)
    
    print(f"\n🔍 Running inference on: {image_path}")
    results = model(image_path)
    
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                print(f"Detected: {class_name} (confidence: {conf:.3f})")
        else:
            print("No objects detected")
    
    # Save result
    results[0].save("inference_result.jpg")
    print("Result saved as inference_result.jpg")
    
    return results

if __name__ == "__main__":
    # Test the model
    model = test_trained_model()
    
    print("\n🚀 Next Steps:")
    print("1. Check the test_result_*.jpg files for visual results")
    print("2. If performance is poor, gather more training data")
    print("3. Consider retraining with a larger dataset")
    print("4. Use inference_example() function for new images")
    
    # Example usage for new images:
    print("\n📝 To test on a new image:")
    print("inference_example('path/to/your/image.jpg')")