# Image Recognition Application

An interactive web application for image recognition using machine learning to provide detailed visual analysis. Features user accounts, image upload, recognition results visualization, and history tracking.

Repository: https://github.com/Karthisgowda/iamge-.git

## Final Feature Set

- User registration, login, logout, and protected dashboard pages
- Drag-and-drop image upload with server-side file type validation
- Basic recognition tags with confidence chart visualization
- Groq-powered detailed AI image analysis when `GROQ_API_KEY` is configured
- Automatic basic fallback mode when no API key is available
- User analysis history with previews, top tags, and timestamps
- Download any analysis as JSON
- Delete saved analyses and uploaded images
- Local SQLite database by default, so XAMPP/MySQL is not required
- `/api/status` health endpoint for quick localhost checks

## Local Setup Instructions

### Prerequisites

1. **Python 3.9+**: Install [Python](https://www.python.org/downloads/) and enable "Add Python to PATH"
2. **Git** (optional): For cloning the repository

### Easiest Method With npm

1. **Clone or open the project**:
   ```powershell
   git clone https://github.com/Karthisgowda/iamge-.git
   cd iamge-
   ```

2. **Run from PowerShell**:
   ```powershell
   dir app.py
   npm install
   npm run setup
   npm start
   ```

3. **Open the app**:
   - Visit http://localhost:5000
   - Visit http://localhost:5000/api/status to confirm the backend is healthy

The npm scripts run the Python Flask app and use a local SQLite database automatically. XAMPP/MySQL is not required.

If PowerShell blocks `npm`, use `npm.cmd`:

```powershell
npm.cmd install
npm.cmd run setup
npm.cmd start
```

If you previously ran the XAMPP version and have an old `.env` file, you do not need to delete it. `npm start` forces local SQLite automatically.

4. **Troubleshooting**:
   - If you encounter any issues, see `XAMPP_TROUBLESHOOTING.md`
   - The troubleshooting guide covers common connection and navigation problems

### Run From VS Code Terminal

If you see `can't open file ... app.py: [Errno 2] No such file or directory`, your terminal is not in the folder that contains `app.py`.

Open VS Code, choose **File > Open Folder**, select the folder that contains `app.py`, then open the integrated terminal with **Terminal > New Terminal** and run:

```powershell
dir app.py
npm install
npm run setup
npm start
```

If `dir app.py` says the file is missing, open the folder that contains the project files or download the latest code again from GitHub.

### Optional Groq Key

The app runs without a Groq key, but detailed AI image analysis needs one.

1. **Create Environment Variables**:
   - Create a file named `.env` in the project root
   - Add:
     ```
     SESSION_SECRET=your_random_string
     GROQ_API_KEY=your_groq_api_key_here
     GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
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
