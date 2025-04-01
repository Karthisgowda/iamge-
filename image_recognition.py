import os
import json
import requests
import base64
import logging
from datetime import datetime
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
    Process an image using OpenAI API for detailed analysis
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Detailed analysis of the image content
    """
    api_key = current_app.config['OPENAI_API_KEY']  # Using the OpenAI API key
    
    if not api_key:
        logging.warning("OpenAI API key not provided - detailed analysis unavailable")
        return {
            'success': False,
            'error': "OpenAI API key not provided",
            'description': "Unable to generate detailed description without an API key."
        }
    
    try:
        logging.debug(f"Starting OpenAI analysis for image: {image_path}")
        
        # Ensure the image file exists
        if not os.path.exists(image_path):
            logging.error(f"Image file not found: {image_path}")
            return {
                'success': False,
                'error': f"Image file not found: {image_path}",
                'description': "The image file could not be found."
            }
        
        # Get file size
        file_size = os.path.getsize(image_path)
        logging.debug(f"Image file size: {file_size} bytes")
        
        # Prepare to send the request to OpenAI API
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Read the image file and encode as base64
        image_file = None
        try:
            image_file = open(image_path, 'rb')
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare the request payload for OpenAI Chat API with image
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image in detail. Describe what you see including: the main elements, subjects, any notable features, colors, composition, context, and technical details if visible. Provide a comprehensive analysis suitable for visualization and data presentation."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 800
            }
            
            logging.debug("Calling OpenAI API...")
            response = requests.post(api_url, headers=headers, json=payload)
            logging.debug(f"OpenAI API response status code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # Extract text content from OpenAI response
                    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    # Get current time for the analysis timestamp
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Format the content into a more structured format
                    description = f"""# Image Analysis Results

## Detailed Description
{content}

## Technical Details
* File Size: {file_size} bytes
* File Path: {image_path}
* Analysis Time: {current_time}

## Note
This analysis was generated using OpenAI's vision model."""
                    
                    return {
                        'success': True,
                        'description': description
                    }
                except Exception as json_error:
                    logging.error(f"Error parsing OpenAI API response: {str(json_error)}")
                    return {
                        'success': False,
                        'error': f"Error parsing API response: {str(json_error)}",
                        'description': "There was a problem understanding the analysis results."
                    }
            elif response.status_code == 401:
                logging.error("OpenAI API authentication error: Invalid API key")
                return {
                    'success': False,
                    'error': "OpenAI API authentication failed",
                    'description': """# Enhanced Image Analysis Unavailable

The OpenAI API authentication failed. This could be due to an invalid or expired API key.

## What you can see instead:
* Basic image recognition tags are still available
* Chart visualization of detected elements
* Image preview and technical data

## How to fix:
Please check your API key and make sure it's valid and active."""
                }
            elif response.status_code == 429:
                logging.error("OpenAI API rate limit exceeded")
                return {
                    'success': False,
                    'error': "OpenAI API rate limit exceeded",
                    'description': """# Enhanced Image Analysis Unavailable

We're currently experiencing high demand for our AI-powered image analysis feature. The OpenAI service has temporarily limited access due to rate limiting.

## What you can see instead:
* Basic image recognition tags are still available
* Chart visualization of detected elements
* Image preview and technical data

## When to try again:
API quota typically refreshes after a short period. Please try again in a few minutes, or contact support if this issue persists."""
                }
            else:
                logging.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"OpenAI API error: {response.status_code}",
                    'description': "There was a problem communicating with the OpenAI service. Please try again later."
                }
        except Exception as request_error:
            logging.error(f"Error making OpenAI API request: {str(request_error)}")
            return {
                'success': False,
                'error': f"Error making API request: {str(request_error)}",
                'description': "There was a problem sending the image for analysis."
            }
        finally:
            # Make sure to close the file if it was opened
            if image_file is not None:
                try:
                    image_file.close()
                except Exception as close_error:
                    logging.error(f"Error closing image file: {str(close_error)}")
        
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
