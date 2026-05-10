# XAMPP Troubleshooting Guide

This guide provides solutions for common issues when running the Image Recognition App with XAMPP.

## Navigation Issues (Pages Not Interconnected)

### Problem: Clicking links doesn't navigate properly or buttons don't work

**Solutions:**

1. **Use the Provided Start Script**
   - Double-click `start_app.bat` file to launch the application
   - This ensures all paths are properly configured

2. **Check URL Settings**
   - If you're not using our provided scripts, edit `.env` file and add:
   ```
   SERVER_NAME=localhost:5000
   ```

3. **Clear Browser Cache**
   - Press Ctrl+F5 to force reload the page
   - Or clear your browser history/cache completely

4. **Check for JavaScript Errors**
   - Open browser developer tools (F12) and check Console tab for errors

## Database Connection Issues

### Problem: "Cannot connect to MySQL database"

**Solutions:**

1. **Verify XAMPP is Running**
   - Open XAMPP Control Panel
   - Ensure MySQL service shows "Running" (green)
   - If not, click "Start" button next to MySQL

2. **Check Database Name**
   - Ensure database `image_recognition_db` exists in phpMyAdmin
   - If not, create it manually or run `python xampp_setup.py`

3. **Password Issues**
   - Default XAMPP MySQL password is blank (empty)
   - If you've set a custom password, update `.env` file:
   ```
   MYSQL_PASSWORD=your_password_here
   DATABASE_URL=mysql+pymysql://root:your_password_here@localhost/image_recognition_db
   ```

4. **Non-Standard Port**
   - If MySQL is running on a custom port, update `.env` file:
   ```
   MYSQL_PORT=your_port_number
   DATABASE_URL=mysql+pymysql://root:@localhost:your_port_number/image_recognition_db
   ```

## Package Installation Issues

### Problem: "Module not found" errors

**Solutions:**

1. **Install Required Packages**
   - Run this command:
   ```
   pip install -r local-requirements.txt
   ```

2. **Verify Python Environment**
   - Ensure you're using the correct Python environment
   - Check Python version with: `python --version`
   - Recommended: Python 3.8 or newer

3. **pymysql Specific Issues**
   - If you see an error about pymysql, install it specifically:
   ```
   pip install pymysql
   ```

## File Upload Issues

### Problem: "Permission denied" when uploading images

**Solutions:**

1. **Check Directory Permissions**
   - Ensure the `uploads` and `static/uploads` directories exist
   - Ensure your user account has write permissions to these folders

2. **Create Directories Manually**
   ```
   mkdir -p uploads
   mkdir -p static/uploads
   ```

## Groq API Issues

### Problem: Groq analysis not working

**Solutions:**

1. **API Key Configuration**
   - Ensure you have a Groq API key
   - Add it to `.env` file:
   ```
   GROQ_API_KEY=your_api_key_here
   GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
   ```

2. **Install Requests Package**
   - Install the requests package:
   ```
   pip install requests
   ```

## Advanced: Running Behind Apache

If you want to run the application through Apache instead of directly:

1. **Install the Apache module mod_proxy**:
   - In XAMPP Control Panel, click "Config" for Apache
   - Select "httpd.conf"
   - Uncomment these lines (remove the # at the beginning):
     ```
     LoadModule proxy_module modules/mod_proxy.so
     LoadModule proxy_http_module modules/mod_proxy_http.so
     ```

2. **Add a VirtualHost configuration**:
   - Copy the contents of `apache_config_sample.conf` to your XAMPP's `conf/extra/httpd-vhosts.conf` file
   - Or create a new configuration file and include it

3. **Update your hosts file**:
   - Add this line to your hosts file (C:\Windows\System32\drivers\etc\hosts on Windows):
     ```
     127.0.0.1 image-recognition.local
     ```

4. **Restart Apache** in the XAMPP Control Panel

5. **Access the application** at http://image-recognition.local
