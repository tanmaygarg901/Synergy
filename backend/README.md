# 🤝 Synergy Backend

AI-powered co-founder matching with team management.

## ⚡ Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set API key
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Seed database
python seed_db.py

# 4. Start
./start.sh

# 5. Test
python chat_terminal.py
```

---

## 🎯 Features

### **Fast AI Chat** (3-4 messages)
- Extracts name, skills, interests, role needed
- Concise responses (max 25 words)

### **Semantic Matching**
- ChromaDB vector search
- Filters by role & availability
- Top 5 matches

### **Team Management** ⭐
- Form teams → Users hidden from search
- View all teams
- Dissolve teams → Users available again

### **Auto Storage**
- Profiles saved automatically
- Users searchable by others

---

## 🔌 API Endpoints

### Chat & Match
```bash
POST /chat
POST /find-collaborators
```

### Teams
```bash
POST /team/create
GET  /team/all
POST /team/dissolve/<id>
GET  /users/available
```

### Database
```bash
GET /health
GET /collaborators
GET /stats
POST /search/skills
```

---

## 🧪 Testing

```bash
# Interactive chat
python chat_terminal.py

# Team system
./test_team_system.sh

# API tests
python test_api.py
```

---

## 🏗️ How It Works

```
Chat → Extract Profile → Save (Available) → Show Matches
                              ↓
                         Form Team
                              ↓
                    Mark "In Team" → Hide from search
                              ↓
                    (Optional) Dissolve → "Available" again
```

---

## 💾 Database

```python
{
    "name": "Alice",
    "role": "Software Engineer",
    "skills": "Python, React",
    "interests": "HealthTech",
    "availability": "Available",  # or "In Team"
    "team_id": "None",           # or "team_123"
    "looking_for": "Designer"
}
```

---

## 🚀 Tech Stack

- Flask - Web framework
- Groq - Llama 3.1 & 3.3
- ChromaDB - Vector database
- sentence-transformers - Embeddings

---

## 📝 Environment

```bash
GROQ_API_KEY=gsk_...  # Required
```

---

## 🐛 Troubleshooting

```bash
# Module errors
source venv/bin/activate
pip install -r requirements.txt

# Collection not found
python seed_db.py

# Port in use
lsof -ti:5001 | xargs kill -9
```

---

## 📁 Structure

```
backend/
├── app.py               # Flask server
├── ai_core.py          # AI & database
├── seed_db.py          # Initial data
├── chat_terminal.py    # Test interface
├── test_team_system.sh # Team tests
├── requirements.txt    # Dependencies
└── .env                # API keys
```

---

## ✅ Ready

- [x] Conversational AI
- [x] Profile extraction
- [x] Semantic matching
- [x] User storage
- [x] Team management
- [x] Availability filtering
- [x] Complete API

**Deploy it!** 🚀
