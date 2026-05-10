"""
Local startup script for the Image Recognition application.

By default this uses SQLite so the app runs without XAMPP/MySQL. If you want
MySQL, set USE_MYSQL=1 and provide the MYSQL_* variables in .env.
"""

import os
import sys
import webbrowser
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()  
    print("Environment variables loaded from .env file")
except ImportError:
    print("Warning: python-dotenv not installed. Run: pip install python-dotenv")
    print("Will continue with system environment variables only.")

# Ensure we're using absolute paths for XAMPP environment
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# Create uploads folder if it doesn't exist
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"Created upload folder: {UPLOAD_FOLDER}")

# Ensure we have a .env file with local settings
ENV_FILE = os.path.join(BASE_DIR, ".env")
if not os.path.exists(ENV_FILE):
    # Generate a random secret key
    import secrets
    secret_key = secrets.token_hex(16)
    
    # Create the .env file with default settings
    with open(ENV_FILE, "w") as f:
        f.write(f"SESSION_SECRET={secret_key}\n")
        f.write("# Local default uses SQLite. Uncomment USE_MYSQL to use XAMPP MySQL.\n")
        f.write("# USE_MYSQL=1\n")
        f.write("# MYSQL_USER=root\n")
        f.write("# MYSQL_PASSWORD=\n")
        f.write("# MYSQL_HOST=localhost\n")
        f.write("# MYSQL_PORT=3306\n")
        f.write("# MYSQL_DATABASE=image_recognition_db\n")
        f.write("# GROQ_API_KEY=your_key_here\n")
        f.write("GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct\n")
    print(f"Created .env file with default settings: {ENV_FILE}")
else:
    print(f"Using existing .env file: {ENV_FILE}")

if os.environ.get("USE_MYSQL") == "1":
    print("\nUSE_MYSQL=1 detected. Checking MySQL connection...")
    try:
        import pymysql
        conn = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            port=int(os.environ.get("MYSQL_PORT", 3306))
        )
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE 'image_recognition_db'")
            if not cursor.fetchone():
                print("Creating database: image_recognition_db")
                cursor.execute("CREATE DATABASE image_recognition_db")
                conn.commit()
        conn.close()
        print("MySQL connection successful!")
    except Exception as e:
        print(f"MySQL connection error: {e}")
        print("Remove USE_MYSQL=1 from .env to use SQLite instead.")
        sys.exit(1)
else:
    print("\nUsing local SQLite database. XAMPP/MySQL is not required.")

# Print information about the application
print("\n===============================================")
print("Image Recognition App - Local Edition")
print("===============================================")
print("Starting the application...")
print("URL: http://localhost:5000")
print("Press Ctrl+C to stop the application")
print("===============================================\n")

# Open browser automatically
webbrowser.open("http://localhost:5000")

# Run the application
os.environ["FLASK_APP"] = "main.py"
os.environ["FLASK_ENV"] = "development"
os.environ["FLASK_DEBUG"] = "1"

# Use Flask's run method for better compatibility with XAMPP
if __name__ == "__main__":
    try:
        from flask import Flask
        from app import app
        app.run(host="0.0.0.0", port=5000, debug=True)
    except ImportError:
        print("Error: Flask not installed. Run: pip install flask")
        sys.exit(1)  # Exit with error
