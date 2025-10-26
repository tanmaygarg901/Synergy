# Synergy Backend

AI-powered collaborator matching system using Groq and ChromaDB.

## 🚀 Quick Start (New Setup)

**Important:** Get your Groq API key from: https://console.groq.com/keys
(Ask your team lead for the shared key)

```bash
# 1. Make scripts executable (first time only)
chmod +x setup.sh start.sh

# 2. Run setup (first time only)
./setup.sh
# You'll be prompted to enter the Groq API key

# 3. Seed the database (first time only)
source venv/bin/activate
export GROQ_API_KEY=$(cat .env | grep GROQ_API_KEY | cut -d '=' -f2)
python seed_db.py

# 4. Start the server
./start.sh
```

## 🔄 Daily Usage (After Setup)

```bash
cd backend
./start.sh
```

That's it! The script handles:
- ✅ Activating virtual environment
- ✅ Loading API key from .env
- ✅ Starting Flask server on port 5001

## 📋 Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# 4. Seed database
export GROQ_API_KEY=$(cat .env | grep GROQ_API_KEY | cut -d '=' -f2)
python seed_db.py

# 5. Start server
python app.py
```

## 🧪 Testing Endpoints

### Health Check
```bash
curl http://localhost:5001/health
```

### Chat
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi, my name is Sarah", "session_id": "test1"}'
```

### Find Collaborators
```bash
curl -X POST http://localhost:5001/find-collaborators \
  -H "Content-Type: application/json" \
  -d '{
    "chat_transcript": "User: Hi, I am Sarah\nAssistant: Nice to meet you!\nUser: I have skills in Python and React\nUser: I am interested in HealthTech\nUser: Looking for a Designer",
    "session_id": "test1"
  }'
```

## 📁 Project Structure

```
backend/
├── app.py              # Flask API server with logging
├── ai_core.py          # Groq AI and ChromaDB logic
├── seed_db.py          # Database seeding script
├── start.sh            # Server startup script
├── setup.sh            # First-time setup script
├── requirements.txt    # Python dependencies
├── .env                # API keys (not in git)
├── venv/               # Virtual environment (not in git)
└── chroma_db/          # ChromaDB storage (not in git)
```

## 🔧 Environment Variables

Create a `.env` file in the backend folder:

```
GROQ_API_KEY=your_groq_api_key_here
```

**Note:** The `.env` file is gitignored. Each team member creates their own.

## 🐛 Troubleshooting

### Port 5000 Already in Use
We use port 5001 to avoid conflicts with macOS AirPlay Receiver.

### NumPy Compatibility Error
Already fixed in `requirements.txt` with `numpy<2.0`.

### Groq API Key Not Found
Make sure `.env` file exists and contains the API key.

### Database Not Found
Run `python seed_db.py` to create and populate the database.

## 🎯 API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

### `POST /chat`
Real-time chat using Groq llama-3.1-8b-instant.

**Request:**
```json
{
  "message": "Hi, my name is Sarah",
  "session_id": "unique_session_id"
}
```

**Response:**
```json
{
  "response": "Nice to meet you, Sarah! What skills do you have?",
  "is_trigger": false
}
```

### `POST /find-collaborators`
Extract profile and find matches using Groq + ChromaDB.

**Request:**
```json
{
  "chat_transcript": "User: Hi...\nAssistant: ...",
  "session_id": "unique_session_id"
}
```

**Response:**
```json
{
  "your_profile": {
    "name": "Sarah",
    "skills": ["Python", "React"],
    "interests": ["HealthTech"],
    "looking_for": "Designer"
  },
  "matches": [
    {
      "name": "Jane Smith",
      "role": "Designer",
      "bio": "...",
      "skills": ["UI/UX", "Figma"],
      "interests": ["HealthTech"],
      "availability": "Part-time"
    }
  ]
}
```

## 📝 Logging

All requests and responses are logged with:
- 📥 Request details (method, path, body)
- 💬 Processing steps
- 🤖 AI API calls with timing
- ✅/❌ Success/error status
- 📤 Response status and duration

Check the terminal where the server is running to see logs.

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Test locally before committing
3. Commit with descriptive messages
4. Push and create a pull request

## 📚 Tech Stack

- **Flask** - Web framework
- **Groq** - LLM API (llama-3.1-8b-instant, llama-3.1-70b-versatile)
- **ChromaDB** - Vector database for semantic search
- **Sentence Transformers** - Text embeddings
- **Python 3.9+** - Programming language
