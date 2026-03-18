# Deployment Guide

This guide will help you deploy the Counterfeit Product Detection System to a production environment.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- A production server or cloud platform (Heroku, AWS, GCP, etc.)
- SQLite3

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/your-username/counterfeit-detection.git
cd counterfeit-detection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.template` to `.env`
   - Update the variables in `.env` with your production values

4. Database setup:
   - Ensure the database directory exists and has proper permissions
   - Initialize the database by running:
   ```bash
   python setup_database.py
   ```

5. Model setup:
   - Download the YOLOv8 model file to the project root
   - Verify the model path in your `.env` file

## Deployment Options

### Option 1: Heroku Deployment

1. Install Heroku CLI
2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Set environment variables:
```bash
heroku config:set $(cat .env)
```

5. Deploy:
```bash
git push heroku master
```

### Option 2: Docker Deployment

1. Build the Docker image:
```bash
docker build -t counterfeit-detection .
```

2. Run the container:
```bash
docker run -p 8501:8501 --env-file .env counterfeit-detection
```

## Important Notes

1. Database Persistence:
   - For Heroku: Use PostgreSQL add-on instead of SQLite
   - For Docker: Use a volume mount for SQLite or external database

2. File Storage:
   - Configure cloud storage for uploaded images in production
   - Update paths to use environment variables

3. Security:
   - Ensure SSL/HTTPS is enabled
   - Set strong SECRET_KEY in production
   - Review and restrict access as needed

4. Monitoring:
   - Set up logging
   - Configure error tracking
   - Monitor system resources

## Troubleshooting

Common issues and solutions:

1. Database errors:
   - Check file permissions
   - Verify connection strings
   - Ensure proper initialization

2. Model loading issues:
   - Verify model file exists
   - Check path configurations
   - Ensure sufficient memory

3. Image processing errors:
   - Check OpenCV installation
   - Verify image file permissions
   - Monitor memory usage

## Support

For issues or questions:
- Open an issue on GitHub
- Contact support at your-email@example.com

## Updates and Maintenance

1. Regular updates:
   - Check for dependency updates
   - Update model files as needed
   - Monitor system logs

2. Backup procedures:
   - Regular database backups
   - Configuration backups
   - Model file versioning