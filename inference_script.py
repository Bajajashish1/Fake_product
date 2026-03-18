
from ultralytics import YOLO
import cv2

def detect_fake_products(image_path, weights_path="runs\fake_product_detector28\weights\best.pt"):
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
                
                print(f"Detected: {class_name} (confidence: {conf:.3f})")
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                print(f"Location: x1={x1:.0f}, y1={y1:.0f}, x2={x2:.0f}, y2={y2:.0f}")
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
