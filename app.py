import os
import logging
from flask import Flask, render_template
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Try to load environment variables from .env file if dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file if it exists
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv not installed. Using system environment variables only.")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Ensure URLs are generated correctly when behind a proxy or running under XAMPP
app.config['PREFERRED_URL_SCHEME'] = 'http'
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME')  # Only set if specified in environment

# Database Configuration - Optimized for XAMPP MySQL
# Default to MySQL with XAMPP configuration

# Check if we're running on Replit with PostgreSQL
if os.environ.get('DATABASE_URL'):
    # Replit environment with PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # XAMPP MySQL configuration
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')  # Default empty password for XAMPP
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')
    mysql_db = os.environ.get('MYSQL_DATABASE', 'image_recognition_db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}'
    
    # Fallback to SQLite if MySQL connection fails
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///image_recognition.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize paths
upload_folder = os.path.join("static", "uploads")
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)
app.config['UPLOAD_FOLDER'] = upload_folder

# Config for image recognition and Groq API
app.config['IMAGE_RECOGNITION_API_KEY'] = os.environ.get('IMAGE_RECOGNITION_API_KEY', 'default_key')
app.config['IMAGE_RECOGNITION_API_SECRET'] = os.environ.get('IMAGE_RECOGNITION_API_SECRET', 'default_secret')
app.config['IMAGE_RECOGNITION_API_URL'] = 'https://api.imagga.com/v2/tags'
app.config['GROQ_API_KEY'] = os.environ.get('GROQ_API_KEY')
app.config['GROQ_MODEL'] = os.environ.get('GROQ_MODEL', 'meta-llama/llama-4-scout-17b-16e-instruct')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Add custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to <br> tags"""
    if not text:
        return ""
    return Markup(text.replace('\n', '<br>'))

@app.template_filter('markdown')
def markdown_filter(text):
    """Convert markdown to HTML"""
    if not text:
        return ""
    import markdown
    return Markup(markdown.markdown(text, extensions=['extra']))

# Create database tables within app context
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    from models import User, ImageResult
    db.create_all()

# Import routes
from routes import *

# Configure error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Reset any failed database transactions
    return render_template('error.html', error_code=500, message="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
