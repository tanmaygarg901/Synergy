/**
 * API client for connecting to Synergy backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

/**
 * Generate a unique session ID for the chat
 */
export function generateSessionId() {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Send a chat message to the backend
 */
export async function sendChatMessage(sessionId, message) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

/**
 * Trigger the matching algorithm to find collaborators
 */
export async function findCollaborators(sessionId, chatTranscript) {
  try {
    const response = await fetch(`${API_BASE_URL}/find-collaborators`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        chat_transcript: chatTranscript,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error finding collaborators:', error);
    throw error;
  }
}

/**
 * Get all collaborators from the database
 */
export async function getAllCollaborators(role = null) {
  try {
    const url = role 
      ? `${API_BASE_URL}/collaborators?role=${encodeURIComponent(role)}`
      : `${API_BASE_URL}/collaborators`;
    
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting collaborators:', error);
    throw error;
  }
}

/**
 * Health check to verify backend connection
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.status === 'ok';
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
}
