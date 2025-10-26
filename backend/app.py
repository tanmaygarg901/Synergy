from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import time
import traceback
import os
import httpx
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
    logger.info(f"📥 {request.method} {request.path}")

@app.after_request
def log_response_info(response):
    """Log response details and request duration."""
    duration = time.time() - request.start_time
    logger.info(f"📤 {response.status_code} - {duration:.3f}s\n")
    return response

# Store chat history per session (in production, use proper session management)
chat_sessions = {}
processed_slack_messages = set()  # (channel_id, message_ts)
recent_text_cache = {}  # {(channel_id, normalized_text): last_ts}


def _post_slack_thread_message(channel_id: str, thread_ts: str, text: str) -> bool:
    """Post a message to a Slack thread if SLACK_BOT_TOKEN is configured.
    Returns True on success, False otherwise. Never raises to avoid impacting MVP.
    """
    token = os.getenv('SLACK_BOT_TOKEN', '').strip()
    if not token:
        return False
    try:
        resp = httpx.post(
            'https://slack.com/api/chat.postMessage',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={
                'channel': channel_id,
                'thread_ts': thread_ts,
                'text': text
            },
            timeout=8.0
        )
        ok = resp.json().get('ok', False)
        if not ok:
            logging.warning(f"Slack postMessage failed: {resp.text}")
        return bool(ok)
    except Exception as e:
        logging.warning(f"Slack postMessage error: {e}")
        return False


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
        
        # Determine trigger: exact phrase OR server-side extraction shows enough info (skills+interests)
        phrase_trigger = "Great, I have everything I need!" in response
        extracted_trigger = False
        try:
            augmented_history = chat_history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
            transcript_lines = []
            for m in augmented_history:
                role = m.get("role", "assistant")
                prefix = "User" if role == "user" else "Assistant"
                transcript_lines.append(f"{prefix}: {m.get('content', '')}")
            transcript_str = "\n".join(transcript_lines)

            extracted_profile = ai_core.extract_user_profile(transcript_str)
            skills = extracted_profile.get("skills") or []
            interests = extracted_profile.get("interests") or []
            skills_ok = isinstance(skills, list) and len(skills) > 0 and skills != ["General"]
            interests_ok = isinstance(interests, list) and len(interests) > 0 and interests != ["Collaboration"]
            extracted_trigger = bool(skills_ok and interests_ok)
            logger.info(f"   🔎 Auto-trigger check: skills_ok={skills_ok}, interests_ok={interests_ok}")
        except Exception as trigger_err:
            logger.warning(f"   ⚠️ Auto-trigger check failed: {trigger_err}")
            extracted_trigger = False

        is_trigger = phrase_trigger or extracted_trigger
        if is_trigger:
            if not phrase_trigger:
                response = "Great, I have everything I need!"
            logger.info("   🎯 TRIGGER CONFIRMED - Proceeding to matching")
        
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
        
        user_profile = ai_core.extract_user_profile(chat_transcript)
        matches = ai_core.find_collaborators(user_profile)
        team_suggestions = ai_core.build_team_suggestions(user_profile, matches)
        user_id = ai_core.save_user_profile(user_profile)
        
        # Clear session
        if session_id in chat_sessions:
            del chat_sessions[session_id]
        
        logger.info(f"   ✅ Found {len(matches)} matches, saved user {user_id}")
        return jsonify({
            "your_profile": user_profile,
            "matches": matches,
            "user_id": user_id,  # Return the saved user ID
            "team_suggestions": team_suggestions
        })
    except Exception as e:
        logger.error(f"❌ ERROR in /find-collaborators: {str(e)}")
        logger.error(traceback.format_exc())
        
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


@app.route('/collaborators', methods=['GET'])
def get_collaborators():
    """
    Get all collaborators or filter by role.
    Query params: ?role=Software%20Engineer
    """
    try:
        role = request.args.get('role')
        
        if role:
            logger.info(f"🔍 Getting collaborators with role: {role}")
            collaborators = ai_core.get_collaborators_by_role(role)
        else:
            logger.info("🔍 Getting all collaborators")
            collaborators = ai_core.get_all_collaborators()
        
        return jsonify({
            "count": len(collaborators),
            "collaborators": collaborators
        })
    except Exception as e:
        logger.error(f"❌ ERROR in /collaborators endpoint: {e}")
        return jsonify({"error": "Failed to retrieve collaborators"}), 500


@app.route('/collaborators/<collab_id>', methods=['GET'])
def get_collaborator(collab_id):
    """
    Get a single collaborator by ID.
    """
    try:
        logger.info(f"🔍 Getting collaborator: {collab_id}")
        collaborator = ai_core.get_collaborator_by_id(collab_id)
        
        if collaborator:
            return jsonify(collaborator)
        else:
            return jsonify({"error": "Collaborator not found"}), 404
    except Exception as e:
        logger.error(f"❌ ERROR in /collaborators/<id> endpoint: {e}")
        return jsonify({"error": "Failed to retrieve collaborator"}), 500


@app.route('/search/skills', methods=['POST'])
def search_skills():
    """
    Search for collaborators by skills.
    Body: {"skills": ["Python", "React"]}
    """
    try:
        data = request.get_json(silent=True)
        if not data or 'skills' not in data:
            return jsonify({"error": "Skills list is required"}), 400
        
        skills = data.get('skills', [])
        logger.info(f"🔍 Searching by skills: {skills}")
        
        matches = ai_core.search_by_skills(skills)
        return jsonify({
            "count": len(matches),
            "matches": matches
        })
    except Exception as e:
        logger.error(f"❌ ERROR in /search/skills endpoint: {e}")
        return jsonify({"error": "Failed to search by skills"}), 500


@app.route('/slack/ingest', methods=['POST'])
def slack_ingest():
    """Ingest Slack channel messages via Composio. Minimal and isolated.

    Expects JSON body:
      {
        "text": "intro message",
        "channel_id": "C123",
        "message_ts": "1730000000.000100",
        "user_id": "U123",
        "thread_ts": "1730000000.000100"  # optional
      }

    Auth: Send header Authorization: Bearer <SLACK_INGEST_TOKEN>
    """
    try:
        # Simple bearer token verification (keeps MVP untouched)
        authz = request.headers.get('Authorization', '')
        token = authz.split('Bearer ' ,1)[1].strip() if 'Bearer ' in authz else ''
        expected = os.getenv('SLACK_INGEST_TOKEN', '')
        if not expected or token != expected:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(silent=True) or {}
        text = (data.get('text') or '').strip()
        channel_id = (data.get('channel_id') or '').strip()
        message_ts = (data.get('message_ts') or '').strip()
        user_id = (data.get('user_id') or '').strip()

        # Validate minimal fields
        if not text or not channel_id or not message_ts:
            return jsonify({"error": "Missing required fields: text, channel_id, message_ts"}), 400

        # Optional: channel allowlist
        allowed = os.getenv('SLACK_CHANNEL_ALLOWLIST', '')  # comma-separated channel IDs
        if allowed:
            allow = {c.strip() for c in allowed.split(',') if c.strip()}
            if channel_id not in allow:
                return jsonify({"ok": True, "skipped": True, "reason": "channel_not_allowed"})

        # Idempotency: skip if we've already processed
        key = (channel_id, message_ts)
        if key in processed_slack_messages:
            return jsonify({"ok": True, "deduped": True})

        logger.info("🤖 Ingesting Slack intro from %s in %s", user_id or "unknown", channel_id)

        # Build transcript and extract profile
        transcript = f"User: {text}"
        profile = ai_core.extract_user_profile(transcript) or {}

        # Save profile and compute matches
        saved_user_id = ai_core.save_user_profile(profile)
        matches = ai_core.find_collaborators(profile) or []

        # Keep only top 3 for Slack summary
        top_matches = []
        for m in matches[:3]:
            top_matches.append({
                "name": m.get("name"),
                "role": m.get("role"),
                "score": m.get("score"),
                "availability": m.get("availability")
            })

        # Mark processed
        processed_slack_messages.add(key)

        # Short summary for Composio to post in thread
        summary = {
            "ok": True,
            "saved_user_id": saved_user_id,
            "profile": {
                "name": profile.get("name"),
                "role": profile.get("role"),
                "skills": profile.get("skills", []),
                "interests": profile.get("interests", []),
                "looking_for": profile.get("looking_for")
            },
            "top_matches": top_matches
        }

        return jsonify(summary)
    except Exception as e:
        logger.error("❌ ERROR in /slack/ingest: %s", e)
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to ingest Slack message"}), 500


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """Slack Events API adapter.

    - Responds to URL verification by echoing the challenge
    - For message events, reuses the same profile extraction + matching pipeline
    """
    try:
        data = request.get_json(silent=True) or {}

        # 1) URL verification handshake
        if data.get('type') == 'url_verification':
            challenge = data.get('challenge')
            return jsonify({"challenge": challenge})

        # 2) Event callbacks
        if data.get('type') == 'event_callback':
            event = data.get('event', {})
            # Only handle plain channel messages
            if event.get('type') == 'message' and not event.get('subtype'):
                text = (event.get('text') or '').strip()
                channel_id = (event.get('channel') or '').strip()
                message_ts = (event.get('ts') or '').strip()
                user_id = (event.get('user') or '').strip()

                if not text or not channel_id or not message_ts:
                    return jsonify({"ok": True, "skipped": True, "reason": "missing_fields"})

                # Ignore messages from bots (avoid reply loops)
                if event.get('bot_id'):
                    return jsonify({"ok": True, "skipped": True, "reason": "bot_message"})
                bot_user_id = os.getenv('SLACK_BOT_USER_ID', '').strip()
                if bot_user_id and user_id == bot_user_id:
                    return jsonify({"ok": True, "skipped": True, "reason": "self_message"})

                # Optional: channel allowlist
                allowed = os.getenv('SLACK_CHANNEL_ALLOWLIST', '')
                if allowed:
                    allow = {c.strip() for c in allowed.split(',') if c.strip()}
                    if channel_id not in allow:
                        return jsonify({"ok": True, "skipped": True, "reason": "channel_not_allowed"})

                # Idempotency
                key = (channel_id, message_ts)
                if key in processed_slack_messages:
                    return jsonify({"ok": True, "deduped": True})

                # Soft dedupe: ignore identical text from same channel within 2 minutes
                try:
                    import time as _t
                    norm = ' '.join(text.lower().split())
                    tkey = (channel_id, norm)
                    now = _t.time()
                    last = recent_text_cache.get(tkey, 0)
                    if now - last < 120:  # 2 minutes
                        return jsonify({"ok": True, "deduped_text": True})
                    recent_text_cache[tkey] = now
                except Exception:
                    pass

                logger.info("📨 Slack event message from %s in %s", user_id or "unknown", channel_id)

                # Reuse pipeline
                transcript = f"User: {text}"
                profile = ai_core.extract_user_profile(transcript) or {}
                saved_user_id = ai_core.save_user_profile(profile)
                matches = ai_core.find_collaborators(profile) or []

                top_matches = []
                for m in matches[:3]:
                    top_matches.append({
                        "name": m.get("name"),
                        "role": m.get("role"),
                        "score": m.get("score"),
                        "availability": m.get("availability")
                    })

                processed_slack_messages.add(key)

                # Optionally reply in Slack thread (guarded by SLACK_BOT_TOKEN)
                summary_lines = [
                    f"✅ Profile added: *{(profile.get('role') or 'Unknown')}*",
                    f"• Skills: {', '.join(profile.get('skills') or []) or '—'}",
                    f"• Interests: {', '.join(profile.get('interests') or []) or '—'}",
                    "",
                ]
                if top_matches:
                    summary_lines.append("Top matches:")
                    for i, tm in enumerate(top_matches, start=1):
                        name = tm.get('name') or tm.get('role') or 'Candidate'
                        role = tm.get('role') or '—'
                        score = tm.get('score')
                        score_str = f" ({int(round(score))}%)" if isinstance(score, (int, float)) else ""
                        summary_lines.append(f"{i}) {name} — {role}{score_str}")
                else:
                    summary_lines.append("No strong matches yet. Try adding 1–2 more skills or interests.")
                summary_text = "\n".join(summary_lines)

                _post_slack_thread_message(channel_id, message_ts, summary_text)

                return jsonify({
                    "ok": True,
                    "saved_user_id": saved_user_id,
                    "profile": {
                        "name": profile.get("name"),
                        "role": profile.get("role"),
                        "skills": profile.get("skills", []),
                        "interests": profile.get("interests", []),
                        "looking_for": profile.get("looking_for")
                    },
                    "top_matches": top_matches
                })

        # For other events, just ack
        return jsonify({"ok": True})
    except Exception as e:
        logger.error("❌ ERROR in /slack/events: %s", e)
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to handle Slack event"}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Get database statistics.
    """
    try:
        logger.info("📊 Getting database statistics")
        stats = ai_core.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"❌ ERROR in /stats endpoint: {e}")
        return jsonify({"error": "Failed to retrieve statistics"}), 500


@app.route('/team/create', methods=['POST'])
def create_team():
    """Create a team from user IDs"""
    try:
        data = request.json
        user_ids = data.get('user_ids', [])
        team_name = data.get('team_name', 'Unnamed Team')
        
        if not user_ids or len(user_ids) < 2:
            return jsonify({"error": "Need at least 2 user IDs to form a team"}), 400
        
        team_id = ai_core.create_team(user_ids, team_name)
        
        if team_id:
            return jsonify({
                "message": f"Team '{team_name}' created successfully",
                "team_id": team_id,
                "members": user_ids
            })
        else:
            return jsonify({"error": "Failed to create team"}), 500
            
    except Exception as e:
        logger.error(f"❌ ERROR in /team/create: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/team/all', methods=['GET'])
def get_all_teams():
    """Get all formed teams"""
    try:
        teams = ai_core.get_teams()
        return jsonify({"teams": teams})
    except Exception as e:
        logger.error(f"❌ ERROR in /team/all: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/team/dissolve/<team_id>', methods=['POST'])
def dissolve_team(team_id):
    """Dissolve a team and make members available again"""
    try:
        success = ai_core.dissolve_team(team_id)
        if success:
            return jsonify({"message": f"Team {team_id} dissolved successfully"})
        else:
            return jsonify({"error": "Failed to dissolve team"}), 500
    except Exception as e:
        logger.error(f"❌ ERROR in /team/dissolve: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/users/available', methods=['GET'])
def get_available():
    """Get users who are still available (not in a team)"""
    try:
        available = ai_core.get_available_users()
        return jsonify({
            "available_users": available,
            "count": len(available)
        })
    except Exception as e:
        logger.error(f"❌ ERROR in /users/available: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logger.info("\n" + "="*80)
    logger.info("🚀 Starting Synergy Backend Server")
    logger.info("   Port: 5001")
    logger.info("   Debug Mode: True")
    logger.info("   Endpoints:")
    logger.info("      GET  /health")
    logger.info("      POST /chat")
    logger.info("      POST /find-collaborators")
    logger.info("      POST /slack/ingest")
    logger.info("      POST /slack/events")
    logger.info("      GET  /collaborators")
    logger.info("      GET  /collaborators/<id>")
    logger.info("      POST /search/skills")
    logger.info("      GET  /stats")
    logger.info("="*80 + "\n")
    app.run(debug=True, port=5001)
