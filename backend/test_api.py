import sys
import threading
import time
from pathlib import Path
from typing import List, Dict

import pytest
import requests
from werkzeug.serving import make_server


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# Provide a lightweight ai_core stub so tests do not depend on external services.
import types

fake_ai_core = types.ModuleType("ai_core")
_TRIGGER_PHRASE = "Great, I have a clear picture!"


def _fake_chat_response(message: str, chat_history: List[Dict[str, str]]) -> str:
    if not message or not message.strip():
        raise ValueError("Empty message")
    if "trigger" in message.lower():
        return _TRIGGER_PHRASE
    return f"Echo: {message}"


def _fake_extract_profile(chat_transcript: str) -> Dict[str, object]:
    if not chat_transcript or not chat_transcript.strip():
        raise ValueError("Empty transcript")
    return {
        "name": "Jordan Test",
        "skills": ["Product Management", "User Research"],
        "interests": ["AI Collaboration"],
        "looking_for": "Software Engineer",
    }


def _fake_enrichment(profile: Dict[str, object]) -> Dict[str, object]:
    profile = dict(profile)
    if profile.get("name", "").lower() == "bob":
        profile.setdefault("skills", []).append("SEO")
    return profile


def _fake_find_collaborators(profile: Dict[str, object]) -> List[Dict[str, object]]:
    return [
        {
            "id": "match_1",
            "name": "Alex Collaborator",
            "role": "Software Engineer",
            "skills": ["Python", "LLM Integration"],
            "interests": ["Hackathons"],
        }
    ]


fake_ai_core.get_chat_response = _fake_chat_response
fake_ai_core.extract_user_profile = _fake_extract_profile
fake_ai_core.mock_bright_data_enrichment = _fake_enrichment
fake_ai_core.find_collaborators = _fake_find_collaborators

sys.modules["ai_core"] = fake_ai_core


from app import app, chat_sessions  # noqa: E402  pylint: disable=wrong-import-position


@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    server = make_server("127.0.0.1", 5000, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    _wait_for_server("http://127.0.0.1:5000/health")

    yield

    server.shutdown()
    thread.join(timeout=2)


def _wait_for_server(url: str, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=0.5)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.1)
    raise RuntimeError("Server did not start in time")


@pytest.fixture(autouse=True)
def clear_sessions():
    chat_sessions.clear()
    yield
    chat_sessions.clear()


@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:5000"


def test_health_endpoint_returns_200(base_url):
    response = requests.get(f"{base_url}/health", timeout=2)
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "ok"


def test_chat_with_valid_message_returns_response(base_url):
    payload = {"message": "Hello there", "session_id": "session-valid"}
    response = requests.post(f"{base_url}/chat", json=payload, timeout=2)
    assert response.status_code == 200
    body = response.json()
    assert body.get("response") == "Echo: Hello there"
    assert body.get("is_trigger") is False


def test_chat_with_empty_message_returns_400(base_url):
    payload = {"message": "", "session_id": "empty-message"}
    response = requests.post(f"{base_url}/chat", json=payload, timeout=2)
    assert response.status_code == 400


def test_find_collaborators_with_valid_transcript_returns_matches(base_url):
    transcript = "User: My name is Jordan\nAssistant: Nice to meet you!\nUser: I need a developer."
    payload = {"chat_transcript": transcript, "session_id": "session-find"}
    response = requests.post(f"{base_url}/find-collaborators", json=payload, timeout=2)
    assert response.status_code == 200
    body = response.json()
    assert body["your_profile"]["name"] == "Jordan Test"
    assert isinstance(body.get("matches"), list)
    assert body["matches"], "Expected at least one collaborator match"


def test_find_collaborators_with_empty_transcript_returns_error(base_url):
    payload = {"chat_transcript": "", "session_id": "empty-transcript"}
    response = requests.post(f"{base_url}/find-collaborators", json=payload, timeout=2)
    assert response.status_code == 400


def test_session_management_clears_on_results(base_url):
    session_id = "session-management"

    payload = {"message": "Testing sessions", "session_id": session_id}
    first_response = requests.post(f"{base_url}/chat", json=payload, timeout=2)
    assert first_response.status_code == 200
    assert session_id in chat_sessions
    assert len(chat_sessions[session_id]) == 2  # user + assistant

    transcript = "User: Testing session flow"
    final_payload = {"chat_transcript": transcript, "session_id": session_id}
    final_response = requests.post(f"{base_url}/find-collaborators", json=final_payload, timeout=2)
    assert final_response.status_code == 200
    assert session_id not in chat_sessions


def test_trigger_phrase_detection_returns_true(base_url):
    payload = {"message": "Please trigger the phrase", "session_id": "trigger-session"}
    response = requests.post(f"{base_url}/chat", json=payload, timeout=2)
    assert response.status_code == 200
    body = response.json()
    assert body.get("response") == _TRIGGER_PHRASE
    assert body.get("is_trigger") is True
