import os
import re
import shutil

# Direct execution without function
labels_dir = r"d:\newww\dataset\labels\train"

# Get all trashed files
trashed_files = [f for f in os.listdir(labels_dir) if f.startswith('.trashed-')]

print(f"Found {len(trashed_files)} trashed label files")

restored_count = 0
for trashed_file in trashed_files:
    # Extract the original filename from the trashed filename
    # Pattern: .trashed-timestamp-originalname.txt
    match = re.search(r'\.trashed-\d+-(.+)\.txt$', trashed_file)
    if match:
        original_name = match.group(1)
        
        # Handle special case for scaled images
        if original_name.startswith('scal_'):
            original_name = original_name.replace('scal_', 'image_')
        elif not original_name.startswith('image_'):
            original_name = f'image_{original_name}'
        
        # Ensure proper format (image_000001.txt)
        if not original_name.startswith('image_'):
            continue
            
        new_filename = f"{original_name}.txt"
        
        old_path = os.path.join(labels_dir, trashed_file)
        new_path = os.path.join(labels_dir, new_filename)
        
        # Only restore if we don't already have a file with this name
        if not os.path.exists(new_path):
            try:
                shutil.copy2(old_path, new_path)
                print(f"Restored: {trashed_file} -> {new_filename}")
                restored_count += 1
            except Exception as e:
                print(f"Error restoring {trashed_file}: {e}")
        else:
            print(f"Skipped {trashed_file} - {new_filename} already exists")

print(f"Restoration complete. Restored {restored_count} files.")