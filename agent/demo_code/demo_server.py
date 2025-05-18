from flask import Flask, request, jsonify, render_template
import os
import sys
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the parent directory to path so we can import pharmacy_bot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# FastAPI server URL from environment variable
FASTAPI_URL = os.getenv('FASTAPI_URL', 'http://localhost:8000')
logger.info(f"Using FastAPI URL: {FASTAPI_URL}")


@app.route('/')
def index():
    """Serve the demo page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Forward the request to the FastAPI endpoint"""
    try:
        data = request.json
        conversation_hash = data.get('conversation_hash')
        message = data.get('message')
        request_timestamp = data.get('request_timestamp')
        
        logger.info(f"Forwarding request to FastAPI: {message}")
        
        # Forward request to FastAPI endpoint
        response = requests.post(
            f"{FASTAPI_URL}/agent",
            json={
                "conversation_hash": conversation_hash,
                "request_timestamp": request_timestamp,
                "customer_message": message
            },
            timeout=30  # Add timeout
        )
        
        if response.status_code == 200:
            logger.info("Received successful response from FastAPI")
            return jsonify(response.json())
        else:
            logger.error(f"FastAPI returned error status: {response.status_code}")
            return jsonify({
                "response": "I apologize, but I'm having trouble processing your request. Please try again later."
            }), 500

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with FastAPI: {str(e)}")
        return jsonify({
            "response": f"I apologize, but I'm having trouble processing your request. Error: {str(e)}"
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "response": f"I apologize, but I'm having trouble processing your request. Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(debug=True, load_dotenv=True, port=8080, host='0.0.0.0') 