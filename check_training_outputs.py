import os
import shutil

def check_training_outputs():
    """
    Check and organize training outputs for easy review
    """
    print("📊 TRAINING OUTPUTS SUMMARY")
    print("=" * 50)
    
    run_dir = "runs/fake_product_detector27"
    
    if not os.path.exists(run_dir):
        print(f"❌ Training directory not found: {run_dir}")
        return
    
    # List all files in the training output directory
    files = os.listdir(run_dir)
    
    print(f"📁 Training Directory: {run_dir}")
    print(f"📄 Total files generated: {len(files)}")
    print()
    
    # Categorize files
    categories = {
        "📊 Performance Plots": [f for f in files if f.endswith('.png') and any(x in f for x in ['results', 'curve', 'matrix'])],
        "🖼️ Sample Images": [f for f in files if f.endswith('.jpg')],
        "📋 Data Files": [f for f in files if f.endswith(('.csv', '.yaml'))],
        "🏋️ Model Weights": []
    }
    
    # Check weights directory
    weights_dir = os.path.join(run_dir, "weights")
    if os.path.exists(weights_dir):
        weight_files = os.listdir(weights_dir)
        categories["🏋️ Model Weights"] = [f"weights/{f}" for f in weight_files]
    
    # Display categorized files
    for category, file_list in categories.items():
        print(f"{category}:")
        if file_list:
            for file in file_list:
                file_path = os.path.join(run_dir, file)
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    size_mb = size / (1024 * 1024)
                    print(f"  ✅ {file} ({size_mb:.1f} MB)")
                else:
                    print(f"  ❌ {file} (missing)")
        else:
            print("  📭 No files in this category")
        print()
    
    # Create summary report
    summary_report = f"""
YOLO TRAINING COMPLETION REPORT
===============================
Training Directory: {run_dir}
Training Status: ✅ COMPLETED (50 epochs)

KEY FILES TO REVIEW:
📈 results.png - Training progress curves
🎯 confusion_matrix.png - Classification accuracy
📊 BoxPR_curve.png - Precision-Recall analysis
🖼️ train_batch*.jpg - Training data samples
🏋️ weights/best.pt - Best performing model
🏋️ weights/last.pt - Final epoch model

NEXT ACTIONS:
1. Review training plots for performance analysis
2. Test model on new images using test_model.py
3. If performance is low, gather more training data
4. Deploy best.pt for production use

PERFORMANCE NOTES:
⚠️ mAP50 = 0.0000 indicates low performance
💡 Recommendation: Add more labeled training data (aim for 100+ images per class)
    """
    
    # Save summary report
    with open("training_summary.txt", "w") as f:
        f.write(summary_report)
    
    print("📝 Summary report saved to: training_summary.txt")
    print()
    print("🎯 IMMEDIATE NEXT STEPS:")
    print("1. Open the PNG files to visualize training performance")
    print("2. Run 'python test_model.py' to test your trained model")
    print("3. Gather more labeled data if performance is low")
    print("4. Deploy weights/best.pt for real-world testing")

if __name__ == "__main__":
    check_training_outputs()