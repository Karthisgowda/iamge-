import os
import json
import uuid
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, jsonify, abort, Response
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import app, db
from forms import RegistrationForm, LoginForm, ImageUploadForm
from models import User, ImageResult
from image_recognition import analyze_image, analyze_image_with_groq, get_visualization_data
import logging

# Ensure uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    )

def extract_top_tags(recognition_result, limit=10):
    try:
        tags = recognition_result['data']['result']['tags']
        top_tags = sorted(tags, key=lambda x: x['confidence'], reverse=True)[:limit]
        return [
            {
                'name': tag['tag']['en'],
                'confidence': round(float(tag['confidence']), 2)
            }
            for tag in top_tags
        ]
    except (KeyError, TypeError, ValueError):
        return []

def build_user_stats(user_id):
    total = ImageResult.query.filter_by(user_id=user_id).count()
    latest = ImageResult.query.filter_by(user_id=user_id)\
        .order_by(ImageResult.timestamp.desc())\
        .first()
    return {
        'total': total,
        'latest': latest.timestamp.strftime('%b %d, %Y at %H:%M:%S') if latest else 'No uploads yet',
        'groq_enabled': bool(app.config.get('GROQ_API_KEY')),
        'max_upload_mb': int(app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024))
    }

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

        if not original_filename or not allowed_file(original_filename):
            flash('Please upload a JPG, JPEG, PNG, or GIF image.', 'danger')
            return redirect(url_for('dashboard'))
        
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
        
        # Also process with Groq API for enhanced analysis
        try:
            logging.debug(f"Starting Groq API analysis for {file_path}")
            openai_analysis = analyze_image_with_groq(file_path)
            logging.debug(f"Groq API analysis result: {openai_analysis.get('success')}")
            
            # If Groq API analysis failed but we have basic recognition data,
            # add more detailed information about the image itself
            if not openai_analysis.get('success', False) and recognition_result.get('success', False):
                # Get file info for additional details
                image_size = os.path.getsize(file_path)
                image_size_kb = round(image_size / 1024, 2)
                file_extension = os.path.splitext(file_path)[1].lower().replace('.', '')
                
                # Add enhanced details to the description
                if 'description' not in openai_analysis or not openai_analysis['description']:
                    openai_analysis['description'] = f"""
**IMAGE DETAILS**

This image was uploaded as "{original_filename}" ({image_size_kb} KB, {file_extension.upper()} format).

**BASIC RECOGNITION RESULTS**

Based on our analysis, this image contains the following elements:
"""
                    # Add top tags to the description
                    if 'data' in recognition_result and 'result' in recognition_result['data']:
                        tags = recognition_result['data']['result']['tags']
                        top_tags = sorted(tags, key=lambda x: x['confidence'], reverse=True)[:10]
                        
                        for i, tag in enumerate(top_tags):
                            confidence = tag['confidence']
                            tag_name = tag['tag']['en']
                            confidence_star = "*" * int(confidence / 20) + "-" * (5 - int(confidence / 20))
                            openai_analysis['description'] += f"\n- **{tag_name}** ({confidence:.1f}% confidence) <span class=\"confidence-stars\">{confidence_star}</span>"
                    
                    # Add more information and suggestions
                    openai_analysis['description'] += """

**TECHNICAL INFORMATION**

The image has been successfully processed through our basic recognition system.
For a more detailed AI analysis, please try again later when our Groq enhanced analysis service is available.

**SUGGESTIONS**

- View the chart below to see confidence levels for each detected element
- Try different images or image types for varied results
- Check your history page to compare with previous uploads
"""
                
                # Ensure the success flag is true even though we're using fallback content
                openai_analysis['success'] = True
                openai_analysis['is_fallback'] = True
        except Exception as e:
            logging.error(f"Error in Groq API analysis: {str(e)}")
            openai_analysis = {
                'success': False,
                'error': f"Error in Groq API analysis: {str(e)}",
                'description': "An error occurred while analyzing the image with Groq API."
            }
        
        # Combine results
        combined_result = {
            **recognition_result,
            'openai_analysis': openai_analysis,
            'file_info': {
                'original_name': original_filename,
                'size': os.path.getsize(file_path),
                'type': os.path.splitext(file_path)[1].lower().replace('.', ''),
                'upload_time': datetime.utcnow().strftime('%b %d, %Y at %H:%M:%S')
            }
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
        top_tags = extract_top_tags(recognition_result)
        
        # Return result for display
        result = {
            'id': image_result.id,
            'filename': unique_filename,
            'original_filename': original_filename,
            'timestamp': image_result.timestamp.strftime('%b %d, %Y at %H:%M:%S'),
            'visualization_data': visualization_data,
            'top_tags': top_tags,
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
        recent_results=recent_results,
        stats=build_user_stats(current_user.id)
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
    top_tags = extract_top_tags(recognition_result)
    
    # Extract enhanced AI analysis if it exists.
    openai_analysis = recognition_result.get('openai_analysis', {})
    
    # For backward compatibility with existing database records that might have lama_analysis
    if not openai_analysis and 'lama_analysis' in recognition_result:
        # Convert lama_analysis to openai_analysis for backward compatibility
        openai_analysis = recognition_result.get('lama_analysis', {})
        # Log for debugging
        logging.debug(f"Converting lama_analysis to openai_analysis for result_id: {result_id}")
    
    view_data = {
        'id': result.id,
        'filename': result.filename,
        'original_filename': result.original_filename,
        'timestamp': result.timestamp.strftime('%b %d, %Y at %H:%M:%S'),
        'visualization_data': visualization_data,
        'top_tags': top_tags,
        'success': recognition_result['success'],
        'error': recognition_result.get('error', None),
        'simulated': recognition_result.get('simulated', False),
        'openai_analysis': openai_analysis
    }
    
    recent_results = ImageResult.query.filter_by(user_id=current_user.id)\
        .order_by(ImageResult.timestamp.desc())\
        .limit(5).all()

    return render_template(
        'dashboard.html',
        title='Result',
        form=ImageUploadForm(),
        result=view_data,
        recent_results=recent_results,
        stats=build_user_stats(current_user.id)
    )

@app.route('/result/<int:result_id>/download')
@login_required
def download_result(result_id):
    """Download a saved recognition result as JSON."""
    result = ImageResult.query.get_or_404(result_id)
    if result.user_id != current_user.id:
        abort(403)

    payload = {
        'id': result.id,
        'filename': result.filename,
        'original_filename': result.original_filename,
        'timestamp': result.timestamp.isoformat(),
        'recognition_data': json.loads(result.recognition_data or '{}')
    }
    return Response(
        json.dumps(payload, indent=2),
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment; filename=analysis-{result.id}.json'
        }
    )

@app.route('/result/<int:result_id>/delete', methods=['POST'])
@login_required
def delete_result(result_id):
    """Delete a saved result and its uploaded image."""
    result = ImageResult.query.get_or_404(result_id)
    if result.user_id != current_user.id:
        abort(403)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], result.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(result)
    db.session.commit()
    flash('Analysis deleted successfully.', 'success')
    return redirect(url_for('history'))

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
        parsed = json.loads(item.recognition_data or '{}')
        top_tags = extract_top_tags(parsed, limit=3)
        results.append({
            'id': item.id,
            'filename': item.filename,
            'original_filename': item.original_filename,
            'timestamp': item.timestamp.strftime('%b %d, %Y at %H:%M:%S'),
            'recognition_data': item.recognition_data,
            'top_tags': top_tags,
            'ai_enhanced': bool(parsed.get('openai_analysis') or parsed.get('lama_analysis'))
        })
    
    return render_template('history.html', title='History', results=results, stats=build_user_stats(current_user.id))

@app.route('/api/status')
def api_status():
    """Small health endpoint for local checks and demos."""
    return jsonify({
        'status': 'ok',
        'app': 'Image Recognition',
        'database': 'connected',
        'groq_enabled': bool(app.config.get('GROQ_API_KEY')),
        'max_upload_mb': int(app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)),
        'allowed_extensions': sorted(app.config['ALLOWED_EXTENSIONS'])
    })
