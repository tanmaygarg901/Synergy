from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import ai_core

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Store chat history per session (in production, use proper session management)
chat_sessions = {}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route('/chat', methods=['POST'])
def chat():
    """
    Real-time chat endpoint using Groq llama3-8b.
    """
    try:
        data = request.get_json(silent=True) or {}
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')

        if not message or not message.strip():
            return jsonify({"error": "Message must not be empty"}), 400
        
        # Get or create chat history for this session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        chat_history = chat_sessions[session_id]
        
        # Get AI response
        response = ai_core.get_chat_response(message, chat_history)
        
        # Update chat history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response})
        chat_sessions[session_id] = chat_history
        
        return jsonify({
            "response": response,
            "is_trigger": "Great, I have a clear picture!" in response
        })
    except Exception as e:
        print(f"Error in /chat: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/find-collaborators', methods=['POST'])
def find_collaborators():
    """
    Extract user profile from chat transcript and find matching collaborators.
    Uses Groq llama3-70b for extraction and ChromaDB for matching.
    """
    try:
        data = request.get_json(silent=True) or {}
        chat_transcript = data.get('chat_transcript', '')
        session_id = data.get('session_id', 'default')

        if not chat_transcript or not chat_transcript.strip():
            return jsonify({"error": "Chat transcript must not be empty"}), 400
        
        # Extract structured profile using Groq 70b
        user_profile = ai_core.extract_user_profile(chat_transcript)
        
        # Run mock enrichment
        user_profile = ai_core.mock_bright_data_enrichment(user_profile)
        
        # Find matching collaborators
        matches = ai_core.find_collaborators(user_profile)
        
        # Clear session
        if session_id in chat_sessions:
            del chat_sessions[session_id]
        
        return jsonify({
            "your_profile": user_profile,
            "matches": matches
        })
    except Exception as e:
        print(f"Error in /find-collaborators: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
