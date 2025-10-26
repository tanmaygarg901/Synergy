"""
Integration tests for Synergy Backend API
Run with: pytest test_api.py -v
Or manually: python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_health_endpoint():
    """Test health check endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ Health check passed")

def test_chat_validation_empty_message():
    """Test chat endpoint rejects empty message"""
    print("Testing empty message validation...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "", "session_id": "test"}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["error"].lower()
    print("✅ Empty message validation passed")

def test_chat_validation_missing_session():
    """Test chat endpoint requires session_id"""
    print("Testing missing session_id validation...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Hi"}
    )
    assert response.status_code == 400
    assert "session" in response.json()["error"].lower()
    print("✅ Session ID validation passed")

def test_chat_validation_message_too_long():
    """Test chat endpoint rejects messages that are too long"""
    print("Testing message length validation...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "a" * 1001, "session_id": "test"}
    )
    assert response.status_code == 400
    assert "long" in response.json()["error"].lower()
    print("✅ Message length validation passed")

def test_chat_valid_request():
    """Test chat endpoint with valid request"""
    print("Testing valid chat request...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "Hi, my name is Test User", "session_id": "pytest_session"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "is_trigger" in data
    assert isinstance(data["is_trigger"], bool)
    assert len(data["response"]) > 0
    print(f"✅ Chat endpoint passed - Got response: {data['response'][:50]}...")

def test_find_collaborators_validation_short_transcript():
    """Test find-collaborators rejects short transcript"""
    print("Testing short transcript validation...")
    response = requests.post(
        f"{BASE_URL}/find-collaborators",
        json={"chat_transcript": "Hi", "session_id": "test"}
    )
    assert response.status_code == 400
    assert "short" in response.json()["error"].lower()
    print("✅ Short transcript validation passed")

def test_find_collaborators_validation_missing_transcript():
    """Test find-collaborators requires transcript"""
    print("Testing missing transcript validation...")
    response = requests.post(
        f"{BASE_URL}/find-collaborators",
        json={"session_id": "test"}
    )
    assert response.status_code == 400
    print("✅ Missing transcript validation passed")

def test_find_collaborators_full_flow():
    """Test complete find-collaborators flow"""
    print("Testing full find-collaborators flow...")
    transcript = """
    User: Hi, my name is Sarah
    Assistant: Nice to meet you, Sarah!
    User: I have skills in Python, React, and UI/UX design
    Assistant: Great skills!
    User: I'm interested in HealthTech and AI technologies
    Assistant: Awesome!
    User: I'm looking for a Software Engineer to collaborate with on my startup
    """
    
    response = requests.post(
        f"{BASE_URL}/find-collaborators",
        json={"chat_transcript": transcript, "session_id": "pytest_full_flow"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "your_profile" in data
    assert "matches" in data
    assert isinstance(data["matches"], list)
    
    # Verify profile extraction worked
    profile = data["your_profile"]
    assert "name" in profile
    assert "skills" in profile
    assert "interests" in profile
    assert "looking_for" in profile
    
    print(f"✅ Find-collaborators passed - Found {len(data['matches'])} matches")
    print(f"   Profile: {profile}")
    if data['matches']:
        print(f"   First match: {data['matches'][0].get('name', 'Unknown')}")

def test_cors_headers():
    """Test CORS headers are present"""
    print("Testing CORS headers...")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "test", "session_id": "cors_test"},
        headers={"Origin": "http://localhost:3000"}
    )
    assert "Access-Control-Allow-Origin" in response.headers
    print("✅ CORS headers present")

def run_all_tests():
    """Run all tests manually"""
    print("\n" + "="*60)
    print("🧪 Running Synergy Backend Integration Tests")
    print("="*60 + "\n")
    
    try:
        test_health_endpoint()
        test_chat_validation_empty_message()
        test_chat_validation_missing_session()
        test_chat_validation_message_too_long()
        test_chat_valid_request()
        test_find_collaborators_validation_short_transcript()
        test_find_collaborators_validation_missing_transcript()
        test_find_collaborators_full_flow()
        test_cors_headers()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED! 🎉")
        print("="*60 + "\n")
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server at http://localhost:5001")
        print("Make sure the backend server is running!")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
