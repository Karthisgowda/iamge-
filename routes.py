import os
import json
import uuid
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import app, db
from forms import RegistrationForm, LoginForm, ImageUploadForm
from models import User, ImageResult
from image_recognition import analyze_image, analyze_image_with_openai, get_visualization_data
import logging

# Home route
@app.route('/')
def home():
    """Render the home page"""
    return render_template('home.html', title='Home')

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
            
    return render_template('login.html', title='Login', form=form)

# User logout
@app.route('/logout')
def logout():
    """Log user out and redirect to home page"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """User dashboard for image upload and recognition"""
    form = ImageUploadForm()
    result = None
    
    if form.validate_on_submit():
        # Save the uploaded file
        file = form.image.data
        original_filename = secure_filename(file.filename)
        
        # Generate unique filename to prevent overwrites
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        file.save(file_path)
        
        # Process the image with basic recognition
        try:
            logging.debug(f"Starting basic image recognition for {file_path}")
            recognition_result = analyze_image(file_path)
            logging.debug(f"Basic recognition result: {recognition_result.get('success')}")
        except Exception as e:
            logging.error(f"Error in basic image recognition: {str(e)}")
            recognition_result = {
                'success': False,
                'error': f"Error in basic image recognition: {str(e)}"
            }
        
        # Also process with OpenAI for enhanced analysis
        try:
            logging.debug(f"Starting OpenAI analysis for {file_path}")
            openai_analysis = analyze_image_with_openai(file_path)
            logging.debug(f"OpenAI analysis result: {openai_analysis.get('success')}")
        except Exception as e:
            logging.error(f"Error in OpenAI analysis: {str(e)}")
            openai_analysis = {
                'success': False,
                'error': f"Error in OpenAI analysis: {str(e)}",
                'description': "An error occurred while analyzing the image with OpenAI."
            }
        
        # Combine results
        combined_result = {
            **recognition_result,
            'openai_analysis': openai_analysis
        }
        
        # Store result in database
        image_result = ImageResult(
            filename=unique_filename,
            original_filename=original_filename,
            user_id=current_user.id,
            recognition_data=json.dumps(combined_result)
        )
        db.session.add(image_result)
        db.session.commit()
        
        # Prepare visualization data
        visualization_data = get_visualization_data(recognition_result)
        
        # Return result for display
        result = {
            'id': image_result.id,
            'filename': unique_filename,
            'original_filename': original_filename,
            'timestamp': image_result.timestamp.strftime('%b %d, %Y at %H:%M:%S'),
            'visualization_data': visualization_data,
            'success': recognition_result['success'],
            'error': recognition_result.get('error', None),
            'simulated': recognition_result.get('simulated', False),
            'openai_analysis': openai_analysis
        }
        
    # Get 5 most recent results for quick access
    recent_results = ImageResult.query.filter_by(user_id=current_user.id)\
        .order_by(ImageResult.timestamp.desc())\
        .limit(5).all()
    
    return render_template(
        'dashboard.html',
        title='Dashboard',
        form=form,
        result=result,
        recent_results=recent_results
    )

# View a specific image result
@app.route('/result/<int:result_id>')
@login_required
def view_result(result_id):
    """View a specific image recognition result"""
    result = ImageResult.query.get_or_404(result_id)
    
    # Check if the result belongs to the current user
    if result.user_id != current_user.id:
        abort(403)  # Forbidden
    
    # Parse the stored recognition data
    recognition_result = json.loads(result.recognition_data)
    visualization_data = get_visualization_data(recognition_result)
    
    # Extract OpenAI analysis if it exists
    openai_analysis = recognition_result.get('openai_analysis', {})
    
    view_data = {
        'id': result.id,
        'filename': result.filename,
        'original_filename': result.original_filename,
        'timestamp': result.timestamp.strftime('%b %d, %Y at %H:%M:%S'),
        'visualization_data': visualization_data,
        'success': recognition_result['success'],
        'error': recognition_result.get('error', None),
        'simulated': recognition_result.get('simulated', False),
        'openai_analysis': openai_analysis
    }
    
    return render_template('dashboard.html', title='Result', result=view_data)

# History page showing all user's image results
@app.route('/history')
@login_required
def history():
    """Display all image recognition results for the current user"""
    # Get all image results from the database
    db_results = ImageResult.query.filter_by(user_id=current_user.id)\
        .order_by(ImageResult.timestamp.desc()).all()
    
    # Format results with proper timestamp string
    results = []
    for item in db_results:
        results.append({
            'id': item.id,
            'filename': item.filename,
            'original_filename': item.original_filename,
            'timestamp': item.timestamp.strftime('%b %d, %Y at %H:%M:%S'),
            'recognition_data': item.recognition_data
        })
    
    return render_template('history.html', title='History', results=results)
