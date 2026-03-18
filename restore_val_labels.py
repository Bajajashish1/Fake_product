import os
import re
import shutil
from collections import defaultdict

def restore_validation_labels():
    """Restore all trashed label files for validation set"""
    labels_dir = r"d:\newww\dataset\labels\val"
    images_dir = r"d:\newww\dataset\images\val"
    
    # Get all image files
    image_files = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
    image_names = [os.path.splitext(f)[0] for f in image_files]
    print(f"Found {len(image_files)} validation images")
    
    # Get all trashed files
    trashed_files = [f for f in os.listdir(labels_dir) if f.startswith('.trashed-')]
    print(f"Found {len(trashed_files)} trashed label files")
    
    # Group trashed files by their original names
    label_groups = defaultdict(list)
    
    for trashed_file in trashed_files:
        # Extract the original filename from the trashed filename
        match = re.search(r'\.trashed-\d+-(.*?)\.txt$', trashed_file)
        if match:
            original_name = match.group(1)
            
            # Handle different naming patterns
            if original_name.startswith('scal_'):
                # Remove 'scal_' prefix
                clean_name = original_name.replace('scal_', '')
                if not clean_name.startswith('image_'):
                    clean_name = f'image_{clean_name}'
            elif not original_name.startswith('image_'):
                clean_name = f'image_{original_name}'
            else:
                clean_name = original_name
            
            label_groups[clean_name].append(trashed_file)
    
    print(f"Found labels for {len(label_groups)} different image names")
    
    restored_count = 0
    for image_name in image_names:
        label_filename = f"{image_name}.txt"
        label_path = os.path.join(labels_dir, label_filename)
        
        # Skip if label already exists
        if os.path.exists(label_path):
            continue
            
        # Try to find a corresponding trashed label
        if image_name in label_groups:
            # Use the first available trashed file for this image
            trashed_file = label_groups[image_name][0]
            old_path = os.path.join(labels_dir, trashed_file)
            
            try:
                shutil.copy2(old_path, label_path)
                print(f"Restored: {trashed_file} -> {label_filename}")
                restored_count += 1
            except Exception as e:
                print(f"Error restoring {trashed_file}: {e}")
    
    print(f"Restoration complete. Restored {restored_count} new files.")
    
    # Final count
    final_label_count = len([f for f in os.listdir(labels_dir) if f.startswith('image_') and f.endswith('.txt')])
    print(f"Total validation label files now: {final_label_count}")

if __name__ == "__main__":
    restore_validation_labels()