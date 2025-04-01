import os
import json
import requests
import base64
import logging
import base64
from openai import OpenAI
from flask import current_app

def analyze_image(image_path):
    """
    Process an image using the image recognition API
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Recognition results or error information
    """
    api_key = current_app.config['IMAGE_RECOGNITION_API_KEY']
    api_secret = current_app.config['IMAGE_RECOGNITION_API_SECRET']
    api_url = current_app.config['IMAGE_RECOGNITION_API_URL']
    
    if api_key == 'default_key' or api_secret == 'default_secret':
        # In a real application, you'd want to log this and handle accordingly
        logging.warning("Using default API credentials - image recognition will be simulated")
        return simulate_recognition_results()
    
    try:
        # Prepare authentication
        auth = (api_key, api_secret)
        
        # Open the image file
        with open(image_path, 'rb') as image_file:
            # Send to API
            files = {'image': image_file}
            response = requests.post(api_url, auth=auth, files=files)
            
            # Check if request was successful
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                logging.error(f"API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"API responded with status code {response.status_code}"
                }
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return {
            'success': False,
            'error': f"Error processing image: {str(e)}"
        }

def simulate_recognition_results():
    """
    Create simulated results for testing when real API is not available
    This is only used when no API key is provided
    """
    return {
        'success': True,
        'data': {
            'result': {
                'tags': [
                    {'confidence': 85.5, 'tag': {'en': 'nature'}},
                    {'confidence': 80.2, 'tag': {'en': 'landscape'}},
                    {'confidence': 75.1, 'tag': {'en': 'forest'}},
                    {'confidence': 65.8, 'tag': {'en': 'tree'}},
                    {'confidence': 60.4, 'tag': {'en': 'outdoor'}},
                ]
            }
        },
        'simulated': True
    }

def analyze_image_with_openai(image_path):
    """
    Process an image using OpenAI's Vision model for detailed analysis
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Detailed analysis of the image content
    """
    openai_api_key = current_app.config['OPENAI_API_KEY']
    
    if not openai_api_key:
        logging.warning("OpenAI API key not provided - detailed analysis unavailable")
        return {
            'success': False,
            'error': "OpenAI API key not provided",
            'description': "Unable to generate detailed description without an API key."
        }
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Encode image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Call OpenAI API with the image
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                             # do not change this unless explicitly requested by the user
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Provide a comprehensive analysis of this image with the following structure. Format each section header with **bold** markdown:\n\n**IMAGE OVERVIEW**\nA brief summary of what's in the image (1-2 sentences).\n\n**MAIN ELEMENTS**\nDetailed description of the primary objects, people, or focal points in the image.\n\n**CONTEXT & SETTING**\nAnalysis of the environment, location, time of day, season, etc.\n\n**MOOD & ATMOSPHERE**\nThe emotional tone, lighting, colors, and overall feel of the image.\n\n**COMPOSITION & TECHNICAL ASPECTS**\nNotes on framing, perspective, focus, depth of field, etc.\n\n**SUBJECT DETAILS**\nMore specific information about the subjects in the image, their appearance, positioning, etc.\n\n**POSSIBLE INTERPRETATIONS**\nPotential meanings, story, or significance of the image content.\n\n**POSSIBLE CATEGORIES**\nList 3-5 categories this image could fall under (e.g., nature photography, portrait, urban landscape).\n\nMake sure to use markdown **bold** for all section headers, and provide detailed analysis in each section."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        # Extract the detailed description from the response
        detailed_description = response.choices[0].message.content
        
        return {
            'success': True,
            'description': detailed_description
        }
        
    except Exception as e:
        logging.error(f"Error in OpenAI image analysis: {str(e)}")
        return {
            'success': False,
            'error': f"Error in OpenAI image analysis: {str(e)}",
            'description': "An error occurred while generating the detailed description."
        }

def get_visualization_data(recognition_result):
    """
    Transform API results into a format suitable for Chart.js visualization
    
    Args:
        recognition_result (dict): The recognition results from the API
        
    Returns:
        dict: Formatted data for visualization
    """
    # Check if we have valid data
    if not recognition_result['success']:
        return {
            'labels': ['Error'],
            'data': [100],
            'error': True
        }
        
    # Extract tags and confidence levels
    try:
        tags = recognition_result['data']['result']['tags']
        
        # Get top 10 tags for visualization
        top_tags = sorted(tags, key=lambda x: x['confidence'], reverse=True)[:10]
        
        labels = [tag['tag']['en'] for tag in top_tags]
        data = [tag['confidence'] for tag in top_tags]
        
        return {
            'labels': labels,
            'data': data,
            'error': False
        }
    except (KeyError, IndexError) as e:
        logging.error(f"Error formatting visualization data: {str(e)}")
        return {
            'labels': ['Error'],
            'data': [100],
            'error': True
        }
