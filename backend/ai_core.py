import os
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import json

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def get_chat_response(message, chat_history):
    """
    Get a real-time chat response using Groq's llama-3.1-8b-instant model.
    Optimized to gather info in 3-4 messages max.
    """
    messages = [
        {
            "role": "system",
            "content": """You are a friendly AI assistant helping users find collaborators. Your goal is to gather 4 key pieces of information efficiently:

1. Name
2. Skills (technical or professional abilities)
3. Interests (industries, topics, or areas they care about)
4. What type of collaborator they're looking for (role: developer, designer, PM, etc.)

Guidelines:
- Ask for multiple pieces of info per message when possible
- Keep responses under 30 words
- Be conversational but efficient
- After you have all 4 pieces of info, say EXACTLY: "Great, I have a clear picture!"
- Don't ask for info they already provided

Examples:
- "Hi! I'm here to help you find collaborators. What's your name and what are your main skills?"
- "Nice! What industries or topics interest you, and what type of collaborator are you looking for?"
"""
        }
    ]
    
    # Add chat history
    messages.extend(chat_history)
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.5,  # Lower for more focused responses
            max_tokens=80  # Shorter responses for efficiency
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in chat response: {e}")
        return "I'm having trouble responding right now. Could you try again?"


def extract_user_profile(chat_transcript):
    """
    Extract structured profile from chat transcript using Groq's llama-3.1-70b-versatile model with JSON mode.
    """
    prompt = f"""Based on this conversation, extract the user's profile in JSON format with these exact keys:
- name: string
- skills: array of strings
- interests: array of strings  
- looking_for: string (the type of collaborator they want, e.g., "Software Engineer", "Designer", "Finance Expert")

Conversation:
{chat_transcript}

Return ONLY valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a JSON extraction expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        profile = json.loads(response.choices[0].message.content)
        return profile
    except Exception as e:
        print(f"Error extracting profile: {e}")
        return {
            "name": "User",
            "skills": ["General"],
            "interests": ["Collaboration"],
            "looking_for": "Software Engineer"
        }


def mock_bright_data_enrichment(profile):
    """
    Mock Bright Data enrichment - adds hardcoded skill if name is Bob.
    """
    if profile.get("name", "").lower() == "bob":
        if "skills" not in profile:
            profile["skills"] = []
        profile["skills"].append("SEO")
    
    return profile


def create_embedding(text):
    """
    Create embedding using sentence-transformers.
    """
    return embedding_model.encode(text).tolist()


def find_collaborators(user_profile):
    """
    Find matching collaborators from ChromaDB based on user profile.
    """
    try:
        # Get or create collection
        collection = chroma_client.get_collection(name="collaborators")
        
        # Create query embedding from looking_for field
        query_text = f"{user_profile.get('looking_for', 'collaborator')} {' '.join(user_profile.get('interests', []))}"
        query_embedding = create_embedding(query_text)
        
        # Build where clause if looking_for is specified
        where_clause = None
        looking_for = user_profile.get('looking_for', '').strip()
        if looking_for:
            where_clause = {"role": {"$eq": looking_for}}
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where=where_clause if where_clause else None
        )
        
        matches = []
        if results and results['metadatas'] and len(results['metadatas'][0]) > 0:
            for metadata in results['metadatas'][0]:
                matches.append(metadata)
        
        return matches
    except Exception as e:
        print(f"Error finding collaborators: {e}")
        return []
