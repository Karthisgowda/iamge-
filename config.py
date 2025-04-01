import os

class Config:
    """Application configuration settings"""
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Image recognition API configuration
    # Default to a free tier key for the Imagga API - should be replaced with actual API key
    IMAGE_RECOGNITION_API_KEY = os.environ.get('IMAGE_RECOGNITION_API_KEY', 'default_key')
    IMAGE_RECOGNITION_API_SECRET = os.environ.get('IMAGE_RECOGNITION_API_SECRET', 'default_secret')
    # Using Imagga API for image recognition
    IMAGE_RECOGNITION_API_URL = 'https://api.imagga.com/v2/tags'
    
    # OpenAI API configuration for enhanced image analysis
    # Use the OpenAI API key for detailed image analysis
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # File upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
