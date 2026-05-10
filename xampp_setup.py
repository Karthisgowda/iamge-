"""
XAMPP Setup Script for Image Recognition Application
---------------------------------------------------
This script helps set up the Image Recognition application for use with XAMPP.

It will:
1. Check for required Python packages and install missing ones
2. Test MySQL connection through XAMPP
3. Create the database if it doesn't exist
4. Verify upload folder permissions
5. Set up environment variables
"""

import os
import sys
import subprocess
import importlib.util

def check_package_installed(package_name):
    """Check if a Python package is installed"""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name):
    """Install a Python package using pip"""
    print(f"Installing {package_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# Required packages
required_packages = [
    "flask", 
    "flask-login", 
    "flask-sqlalchemy", 
    "flask-wtf", 
    "pymysql", 
    "email-validator", 
    "markdown", 
    "markupsafe", 
    "python-dotenv",
    "werkzeug",
    "requests"
]

optional_packages = []

print("\n===== Image Recognition App XAMPP Setup =====\n")

print("Step 1: Checking and installing required packages...\n")
for package in required_packages:
    if not check_package_installed(package):
        try:
            install_package(package)
            print(f"✓ {package} installed successfully")
        except Exception as e:
            print(f"✗ Failed to install {package}: {e}")
            print(f"  Please run: pip install {package}")
    else:
        print(f"✓ {package} already installed")

print("\nChecking optional packages...")
for package in optional_packages:
    if not check_package_installed(package):
        print(f"? {package} is not installed (optional for advanced features)")
        install = input(f"Would you like to install {package}? (y/n): ")
        if install.lower() == 'y':
            try:
                install_package(package)
                print(f"✓ {package} installed successfully")
            except Exception as e:
                print(f"✗ Failed to install {package}: {e}")
    else:
        print(f"✓ {package} already installed")

print("\nStep 2: Setting up environment variables...\n")

# Create .env file if it doesn't exist
if not os.path.exists('.env'):
    print("Creating .env file for environment variables...")
    
    secret_key = os.urandom(24).hex()
    
    with open('.env', 'w') as f:
        f.write(f"SESSION_SECRET={secret_key}\n")
        f.write("MYSQL_USER=root\n")
        f.write("MYSQL_PASSWORD=\n")  # Default empty for XAMPP
        f.write("MYSQL_HOST=localhost\n")
        f.write("MYSQL_PORT=3306\n")
        f.write("MYSQL_DATABASE=image_recognition_db\n")
        
        # Add a placeholder for Groq API key
        f.write("# Set your Groq API key here for advanced image analysis\n")
        f.write("# GROQ_API_KEY=your_key_here\n")
        f.write("GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct\n")
    
    print("✓ .env file created with default settings")
else:
    print("✓ .env file already exists")

print("\nStep 3: Testing MySQL connection through XAMPP...\n")
print("Please make sure XAMPP is running with MySQL started.")
input("Press Enter to continue...")

try:
    import pymysql
    
    # Try to connect with default settings
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE 'image_recognition_db'")
        result = cursor.fetchone()
        
        if not result:
            print("Creating database 'image_recognition_db'...")
            cursor.execute("CREATE DATABASE image_recognition_db")
            connection.commit()
            print("✓ Database created successfully")
        else:
            print("✓ Database 'image_recognition_db' already exists")
        
        connection.close()
        print("✓ MySQL connection successful")
        
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        print("\nPossible issues:")
        print("1. XAMPP MySQL service might not be running")
        print("2. MySQL password might be different from default (empty)")
        print("3. MySQL port might be different from default (3306)")
        print("\nPlease update the .env file with correct MySQL settings.")
        
except ImportError:
    print("✗ pymysql module not found. Please install it with:")
    print("  pip install pymysql")

print("\nStep 4: Checking upload directory...\n")

if not os.path.exists("uploads"):
    os.makedirs("uploads")
    print("✓ Created 'uploads' directory")
else:
    print("✓ 'uploads' directory already exists")

# Try to write a test file to ensure permissions are correct
try:
    with open("uploads/test_write.txt", "w") as f:
        f.write("Test write permission")
    os.remove("uploads/test_write.txt")
    print("✓ Upload directory has write permissions")
except Exception as e:
    print(f"✗ Upload directory permission issue: {e}")
    print("  Please ensure the 'uploads' directory is writable.")

print("\n===== Setup Complete =====")
print("""
To run the application:
1. Ensure XAMPP is running with MySQL started
2. Run the application with: python app.py
3. Access the application at: http://localhost:5000

For Groq image analysis:
- Edit the .env file and uncomment the GROQ_API_KEY line
- Add your API key from https://console.groq.com/keys
""")
