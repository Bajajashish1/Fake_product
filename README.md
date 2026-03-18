# Counterfeit Product Detection System

A robust system for detecting counterfeit products using computer vision and machine learning.

## Project Structure

```
├── config/              # Configuration files
├── data/               # Data storage
│   ├── dataset/        # Training and validation datasets
│   └── models/         # Model files
├── docs/               # Documentation
├── product_history/    # Analysis history and database
├── src/               # Source code
│   ├── core/          # Core functionality
│   └── utils/         # Utility functions
├── tests/             # Test files
└── mobile-app/        # Mobile application
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the environment:
```bash
python setup.py
```

3. Start the dashboard:
```bash
streamlit run src/core/dashboard.py
```

## Features

- Product authenticity analysis
- Image-based counterfeit detection
- Historical analysis tracking
- Mobile app integration
- Database management
- Export and reporting capabilities

## Directory Contents

- `src/core/`: Main application code
  - `dashboard.py`: Main web interface
  - `database_manager.py`: Database operations
  - `model_manager.py`: ML model operations

- `src/utils/`: Helper functions and utilities
  - `image_utils.py`: Image processing
  - `data_utils.py`: Data handling

- `config/`: Configuration files
  - `app_config.py`: Application settings
  - `model_config.yaml`: Model parameters

## Usage

1. Launch the dashboard
2. Upload product images
3. View analysis results
4. Access history and reports

## Mobile App

The mobile app component is in the `mobile-app/` directory.

## Documentation

Detailed documentation is available in the `docs/` directory.