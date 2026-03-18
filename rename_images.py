import os
import glob

# Path to training images
train_path = "dataset/images/train/"

# Get all files starting with .trashed
files = glob.glob(train_path + ".trashed*")

# Rename files to a sequential number
for i, file in enumerate(files, 1):
    # Get file extension
    ext = os.path.splitext(file)[1]
    # Create new name
    new_name = os.path.join(train_path, f"image_{i:06d}{ext}")
    # Rename file
    os.rename(file, new_name)
    print(f"Renamed {file} to {new_name}")