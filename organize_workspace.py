import os
import shutil
from pathlib import Path

def organize_workspace():
    # Define essential files and their destinations
    file_structure = {
        'src/core/': [
            'dashboard.py',
            'database_manager.py',
            'enhanced_shoe_detector.py'
        ],
        'src/utils/': [
            'image_utils.py',
            'data_utils.py'
        ],
        'config/': [
            'app_config.py',
            'model_config.yaml'
        ],
        'tests/': [
            'test_model.py',
            'test_database.py'
        ],
        'docs/': [
            'API_INTEGRATION_GUIDE.md',
            'SHOE_DETECTION_GUIDE.md',
            'DATABASE_INTEGRATION_COMPLETE.md'
        ],
        'data/models/': [
            'yolov8m.pt'
        ]
    }

    # Files to keep in root directory
    root_files = [
        'README.md',
        'requirements.txt',
        'setup.py'
    ]

    # Create directories
    for directory in file_structure.keys():
        os.makedirs(directory, exist_ok=True)
    
    os.makedirs('data/dataset', exist_ok=True)
    
    # Move files to their new locations
    for dest_dir, files in file_structure.items():
        for file in files:
            if os.path.exists(file):
                try:
                    shutil.move(file, os.path.join(dest_dir, file))
                except Exception as e:
                    print(f"Error moving {file}: {str(e)}")

    # Move dataset files
    if os.path.exists('dataset'):
        try:
            shutil.move('dataset', 'data/dataset')
        except Exception as e:
            print(f"Error moving dataset: {str(e)}")

    # Clean up temporary and backup files
    cleanup_patterns = [
        '*_backup*',
        'temp_*',
        '*copy*',
        '*.pyc',
        'test_result_*.jpg'
    ]

    # Remove temporary files
    for pattern in cleanup_patterns:
        for file in Path('.').glob(pattern):
            try:
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)
            except Exception as e:
                print(f"Error removing {file}: {str(e)}")

    print("✨ Workspace organized successfully!")

if __name__ == "__main__":
    organize_workspace()