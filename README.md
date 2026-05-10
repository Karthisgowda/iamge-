# Image Recognition Application

An interactive web application for image recognition using machine learning to provide detailed visual analysis. Features user accounts, image upload, recognition results visualization, and history tracking.

## XAMPP Setup Instructions

### Prerequisites

1. **XAMPP**: Install [XAMPP](https://www.apachefriends.org/index.html) for your operating system
2. **Python 3.9+**: Install [Python](https://www.python.org/downloads/) (3.9 or newer)
3. **Git** (optional): For cloning the repository

### Easiest Method (New!)

1. **Start XAMPP**:
   - Launch XAMPP Control Panel
   - Start Apache and MySQL services

2. **Download Application**:
   - Download the project files to your computer
   - Extract to a folder of your choice (doesn't need to be in htdocs)

3. **Run the Batch File**:
   - Double-click `start_app.bat` in the project folder
   - This will automatically:
     - Check for required directories
     - Configure the database connection
     - Start the application
     - Open your browser to the correct URL

4. **Troubleshooting**:
   - If you encounter any issues, see `XAMPP_TROUBLESHOOTING.md`
   - The troubleshooting guide covers common connection and navigation problems

### Run From VS Code Terminal

If you see `can't open file ... app.py: [Errno 2] No such file or directory`, your terminal is not in the folder that contains `app.py`.

Run these commands from PowerShell:

```powershell
cd path\to\image-recognization--main
dir app.py
python -m pip install -r local-requirements.txt
python app.py
```

If `dir app.py` says the file is missing, open the folder that contains the project files or download the latest code again from GitHub.

### Alternative Manual Setup

1. **Start XAMPP**:
   - Launch XAMPP Control Panel
   - Start Apache and MySQL services

2. **Download Application**:
   - Download the project files to your computer
   - Extract to a folder of your choice

3. **Run Setup Script**:
   ```
   cd path/to/your/project
   python xampp_setup.py
   ```
   This script will:
   - Install required Python packages
   - Test MySQL connection
   - Create the database if needed
   - Set up environment variables
   
   **Alternative**: Install packages manually:
   ```
   pip install -r local-requirements.txt
   ```

4. **Start the Application**:
   ```
   python run_xampp.py
   ```
   Or use the original method:
   ```
   python app.py
   ```

5. **Access the Application**:
   - Open your browser
   - Visit: http://localhost:5000

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Start XAMPP** with Apache and MySQL

2. **Create Database**:
   - Open phpMyAdmin (http://localhost/phpmyadmin/)
   - Create a new database named "image_recognition_db"

3. **Install Required Packages**:
   ```
   pip install flask flask-login flask-sqlalchemy flask-wtf pymysql email-validator markdown markupsafe werkzeug requests
   ```

4. **Create Environment Variables**:
   - Create a file named `.env` in the project root
   - Add:
     ```
     SESSION_SECRET=your_random_string
     MYSQL_USER=root
     MYSQL_PASSWORD=
     MYSQL_DATABASE=image_recognition_db
     GROQ_API_KEY=your_groq_api_key_here
     ```

5. **Start the Application**:
   ```
   python app.py
   ```

## Advanced Features

### Groq Image Analysis

For detailed AI-powered image analysis:

1. Get an API key from [Groq](https://console.groq.com/keys)
2. Add to your `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
   ```

### Apache Integration (Advanced)

For deeper integration with XAMPP Apache:

1. Review the included `apache_config_sample.conf` file 
2. Copy configuration to your XAMPP httpd-vhosts.conf
3. Update paths to match your system
4. Enable required Apache modules
5. Restart Apache in XAMPP Control Panel

This allows you to access the app directly through Apache at http://image-recognition.local

## Troubleshooting

For detailed troubleshooting steps, please see our [XAMPP Troubleshooting Guide](XAMPP_TROUBLESHOOTING.md).

### Common Database Connection Issues

- **MySQL Not Running**: Make sure MySQL is started in XAMPP Control Panel
- **Wrong Credentials**: Default is username "root" with no password
- **Port Conflict**: Check if MySQL is running on a non-standard port
- **Database Missing**: Ensure "image_recognition_db" exists in phpMyAdmin

### Common Application Errors

- **Missing Packages**: Run `pip install -r local-requirements.txt`
- **Upload Issues**: Ensure "uploads" folder exists and is writable
- **Browser Cache**: Try Ctrl+F5 to refresh with cache clear
- **Navigation Issues**: See our troubleshooting guide for page interconnection problems

## Running in Production

For development and testing only. For production deployment, consider:

1. Using a production-ready server like Gunicorn
2. Setting up proper SSL/TLS encryption
3. Implementing additional security measures
