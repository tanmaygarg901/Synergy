from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import time
import traceback
from datetime import datetime
import ai_core

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS to allow frontend communication
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Request logging middleware
@app.before_request
def log_request_info():
    """Log incoming request details."""
    request.start_time = time.time()
    logger.info(f"\n{'='*80}")
    logger.info(f"📥 Incoming Request: {request.method} {request.path}")
    logger.info(f"   Client IP: {request.remote_addr}")
    logger.info(f"   Headers: {dict(request.headers)}")
    if request.is_json:
        # Log request body but truncate if too long
        data = request.get_json()
        data_str = str(data)
        if len(data_str) > 500:
            data_str = data_str[:500] + "... (truncated)"
        logger.info(f"   Request Body: {data_str}")

@app.after_request
def log_response_info(response):
    """Log response details and request duration."""
    duration = time.time() - request.start_time
    logger.info(f"📤 Response: {response.status_code} {response.status}")
    logger.info(f"   Duration: {duration:.3f}s")
    logger.info(f"{'='*80}\n")
    return response

# Store chat history per session (in production, use proper session management)
chat_sessions = {}


# Validation helpers
def validate_chat_request(data):
    """Validate /chat endpoint request data."""
    if not data:
        return "Request body is required", 400
    
    message = data.get('message', '').strip()
    session_id = data.get('session_id', '').strip()
    
    if not message:
        return "Message is required and cannot be empty", 400
    
    if len(message) > 1000:
        return "Message is too long (max 1000 characters)", 400
    
    if not session_id:
        return "Session ID is required", 400
    
    if len(session_id) > 100:
        return "Session ID is too long (max 100 characters)", 400
    
    return None, None


def validate_find_collaborators_request(data):
    """Validate /find-collaborators endpoint request data."""
    if not data:
        return "Request body is required", 400
    
    chat_transcript = data.get('chat_transcript', '').strip()
    session_id = data.get('session_id', '').strip()
    
    if not chat_transcript:
        return "Chat transcript is required and cannot be empty", 400
    
    if len(chat_transcript) < 50:
        return "Chat transcript is too short (minimum 50 characters)", 400
    
    if len(chat_transcript) > 10000:
        return "Chat transcript is too long (max 10000 characters)", 400
    
    if not session_id:
        return "Session ID is required", 400
    
    return None, None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    logger.info("✅ Health check requested")
    return jsonify({"status": "ok"})


@app.route('/chat', methods=['POST'])
def chat():
    """
    Real-time chat endpoint using Groq llama3-8b.
    """
    try:
        logger.info("💬 Processing chat request")
        
        # Validate request
        data = request.get_json(silent=True)
        error_msg, status_code = validate_chat_request(data)
        if error_msg:
            logger.warning(f"   ⚠️  Validation failed: {error_msg}")
            return jsonify({"error": error_msg}), status_code
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        logger.info(f"   Session ID: {session_id}")
        logger.info(f"   User Message: {message[:100]}..." if len(message) > 100 else f"   User Message: {message}")
        
        # Get or create chat history for this session
        if session_id not in chat_sessions:
            logger.info(f"   Creating new session: {session_id}")
            chat_sessions[session_id] = []
        else:
            logger.info(f"   Existing session with {len(chat_sessions[session_id])} messages")
        
        chat_history = chat_sessions[session_id]
        
        # Get AI response
        logger.info("   🤖 Calling Groq API for chat response...")
        ai_start = time.time()
        response = ai_core.get_chat_response(message, chat_history)
        ai_duration = time.time() - ai_start
        logger.info(f"   ✅ Groq API response received in {ai_duration:.3f}s")
        logger.info(f"   AI Response: {response[:100]}..." if len(response) > 100 else f"   AI Response: {response}")
        
        # Check for trigger phrase
        is_trigger = "Great, I have a clear picture!" in response
        if is_trigger:
            logger.info("   🎯 TRIGGER PHRASE DETECTED - Moving to profile extraction")
        
        # Update chat history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response})
        chat_sessions[session_id] = chat_history
        
        logger.info(f"   ✅ Chat completed successfully")
        return jsonify({
            "response": response,
            "is_trigger": is_trigger
        })
    except Exception as e:
        logger.error(f"❌ ERROR in /chat endpoint:")
        logger.error(f"   Error Type: {type(e).__name__}")
        logger.error(f"   Error Message: {str(e)}")
        logger.error(f"   Stack Trace:\n{traceback.format_exc()}")
        
        # Return user-friendly error messages
        error_msg = "An unexpected error occurred"
        if "rate" in str(e).lower() or "quota" in str(e).lower():
            error_msg = "AI service is temporarily unavailable. Please try again in a moment."
        elif "connection" in str(e).lower() or "timeout" in str(e).lower():
            error_msg = "Unable to connect to AI service. Please check your internet connection."
        elif "api_key" in str(e).lower() or "authentication" in str(e).lower():
            error_msg = "Service configuration error. Please contact support."
        
        return jsonify({"error": error_msg}), 500


@app.route('/find-collaborators', methods=['POST'])
def find_collaborators():
    """
    Extract user profile from chat transcript and find matching collaborators.
    Uses Groq llama3-70b for extraction and ChromaDB for matching.
    """
    try:
        logger.info("🔍 Processing find-collaborators request")
        
        # Validate request
        data = request.get_json(silent=True)
        error_msg, status_code = validate_find_collaborators_request(data)
        if error_msg:
            logger.warning(f"   ⚠️  Validation failed: {error_msg}")
            return jsonify({"error": error_msg}), status_code
        
        chat_transcript = data.get('chat_transcript', '').strip()
        session_id = data.get('session_id', 'default')
        
        logger.info(f"   Session ID: {session_id}")
        logger.info(f"   Transcript length: {len(chat_transcript)} characters")
        
        # Extract structured profile using Groq 70b
        logger.info("   🤖 Extracting user profile with Groq 70b...")
        extract_start = time.time()
        user_profile = ai_core.extract_user_profile(chat_transcript)
        extract_duration = time.time() - extract_start
        logger.info(f"   ✅ Profile extracted in {extract_duration:.3f}s")
        logger.info(f"   Profile: {user_profile}")
        
        # Run mock enrichment
        logger.info("   🔧 Running mock data enrichment...")
        user_profile = ai_core.mock_bright_data_enrichment(user_profile)
        logger.info(f"   ✅ Enriched profile: {user_profile}")
        
        # Find matching collaborators
        logger.info("   🔎 Searching ChromaDB for matching collaborators...")
        search_start = time.time()
        matches = ai_core.find_collaborators(user_profile)
        search_duration = time.time() - search_start
        logger.info(f"   ✅ Found {len(matches)} matches in {search_duration:.3f}s")
        
        if matches:
            for i, match in enumerate(matches, 1):
                logger.info(f"   Match {i}: {match.get('name', 'Unknown')} - {match.get('role', 'Unknown')}")
        else:
            logger.warning("   ⚠️  No matches found!")
        
        # Clear session
        if session_id in chat_sessions:
            logger.info(f"   🗑️  Clearing session: {session_id}")
            del chat_sessions[session_id]
        
        logger.info("   ✅ Find-collaborators completed successfully")
        return jsonify({
            "your_profile": user_profile,
            "matches": matches
        })
    except Exception as e:
        logger.error(f"❌ ERROR in /find-collaborators endpoint:")
        logger.error(f"   Error Type: {type(e).__name__}")
        logger.error(f"   Error Message: {str(e)}")
        logger.error(f"   Stack Trace:\n{traceback.format_exc()}")
        
        # Return user-friendly error messages
        error_msg = "An unexpected error occurred while finding collaborators"
        if "rate" in str(e).lower() or "quota" in str(e).lower():
            error_msg = "AI service is temporarily unavailable. Please try again in a moment."
        elif "connection" in str(e).lower() or "timeout" in str(e).lower():
            error_msg = "Unable to connect to services. Please check your internet connection."
        elif "collection" in str(e).lower() or "database" in str(e).lower():
            error_msg = "Database not found. Please ensure the database is seeded."
        elif "api_key" in str(e).lower() or "authentication" in str(e).lower():
            error_msg = "Service configuration error. Please contact support."
        
        return jsonify({"error": error_msg}), 500


if __name__ == '__main__':
    logger.info("\n" + "="*80)
    logger.info("🚀 Starting Synergy Backend Server")
    logger.info("   Port: 5001")
    logger.info("   Debug Mode: True")
    logger.info("   Endpoints:")
    logger.info("      GET  /health")
    logger.info("      POST /chat")
    logger.info("      POST /find-collaborators")
    logger.info("="*80 + "\n")
    app.run(debug=True, port=5001)
