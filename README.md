# Synergy - AI-Powered Co-Founder Matching Platform

**CalHacks 12.0 Project**

Synergy is an intelligent co-founder matching platform that uses conversational AI to understand your skills, interests, and needs, then matches you with complementary team members. Through natural conversation, Synergy learns about you and suggests both individual collaborators and complete team combinations.

## ✨ Key Features

- 🤖 **Conversational AI** - Natural chat interface powered by Groq's Llama 3.1
- 🎯 **Smart Matching** - Vector similarity search with semantic understanding
- 👥 **Team Suggestions** - AI-generated team combinations, not just individual matches
- 📊 **Compatibility Scores** - See how well each match fits your needs (85-100%)
- ✨ **Beautiful UI** - Modern, animated interface with smooth transitions
- 🚀 **Fast & Real-time** - Instant responses with sub-second inference
- 🔄 **Adaptive Conversation** - AI asks follow-up questions only when needed

## Tech Stack

### Frontend
- **Next.js 14** - React framework
- **shadcn/ui** - Modern UI components
- **Tailwind CSS** - Styling
- **react-chatbot-kit** - Chat interface
- **Lucide Icons** - Icon system

### Backend
- **Flask** - Python web framework with CORS support
- **Groq AI** - Ultra-fast LLM inference
  - `llama-3.1-8b-instant` for real-time chat (200ms response time)
  - `llama-3.1-70b-versatile` for profile extraction & team reasoning
- **ChromaDB** - Vector database for semantic search
- **sentence-transformers** - Local embeddings (all-MiniLM-L6-v2)
- **Python 3.9+** - Modern Python with type hints

## Project Structure

```
calhacks 12.0/
├── frontend/              # Next.js application
│   ├── app/              # App router pages
│   ├── components/       # React components
│   │   ├── ui/          # shadcn/ui components
│   │   └── chatbot/     # Chatbot configuration
│   └── lib/             # Utilities
└── backend/              # Flask API
    ├── app.py           # Flask routes
    ├── ai_core.py       # AI logic & ChromaDB
    ├── seed_db.py       # Database seeding
    └── requirements.txt  # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** and npm
- **Python 3.9+** (3.8+ works but 3.9+ recommended)
- **Groq API Key** - [Get one free here](https://console.groq.com)
  - Sign up for Groq Cloud
  - Navigate to API Keys section
  - Create a new API key
  - Copy the key (you'll need it in step 5)

---

## 📦 Installation

### Backend Setup

**1. Navigate to backend directory:**
```bash
cd backend
```

**2. Create and activate virtual environment:**
```bash
python3 -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**3. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

This installs:
- Flask & Flask-CORS
- Groq SDK
- ChromaDB
- sentence-transformers
- python-dotenv

**4. Create environment file:**
```bash
cp .env.example .env
```

**5. Add your Groq API key to `.env`:**
```env
GROQ_API_KEY=gsk_your_actual_api_key_here
```

**6. Seed the database with sample profiles:**
```bash
python seed_db.py
```

This creates 20+ diverse collaborator profiles in ChromaDB with:
- Software Engineers
- Designers
- Product Managers
- Data Scientists
- And more!

**7. Start the Flask backend server:**

**Option A - Using the start script (recommended):**
```bash
./start.sh
```

**Option B - Direct Python:**
```bash
python app.py
```

✅ Backend will run on `http://localhost:5001`

You should see:
```
================================================================================
🚀 Starting Synergy Backend Server
   Port: 5001
   Debug Mode: True
   Endpoints:
      GET  /health
      POST /chat
      POST /find-collaborators
      ...
================================================================================
```

---

### Frontend Setup

**1. Navigate to frontend directory:**
```bash
cd frontend
```

**2. Install Node dependencies:**
```bash
npm install
```

This installs:
- Next.js 14
- React 18
- Tailwind CSS
- shadcn/ui components
- react-chatbot-kit
- Lucide icons

**3. Start the Next.js development server:**
```bash
npm run dev
```

✅ Frontend will run on `http://localhost:3000`

You should see:
```
▲ Next.js 14.2.33
- Local:        http://localhost:3000
✓ Ready in 800ms
```

---

## 🎯 Running the Application

**1. Make sure both servers are running:**
- Backend: `http://localhost:5001` ✅
- Frontend: `http://localhost:3000` ✅

**2. Open your browser and go to:**
```
http://localhost:3000
```

**3. You should see:**
- Beautiful landing page with gradient background
- Large input box at the top
- "Connected" status indicator (green dot) in navbar

**4. Try the demo:**

**Option A - Complete prompt (instant matching):**
```
Product designer with fintech experience. Want to build a B2B payments 
platform, need an engineer who knows backend systems.
```

**Option B - Conversational flow:**
```
User: "Need a technical co-founder for my startup idea."
Bot: "What skills do you have?"
User: "Python and Java"
Bot: "What domains interest you most?"
User: "Finance and healthcare"
Bot: "Great, I have everything I need!"
```

**5. Watch the magic:**
- ⏳ Loading indicator appears (1.5 seconds)
- 👥 5-6 match cards appear with compatibility scores (85-100%)
- 🎯 2-3 team suggestions appear below
- ✨ Smooth animations throughout

---

## 🔧 How It Works

### 1. **Conversational Input** 
- User types their information in the main input box OR uses the chatbot
- Can provide complete information upfront or answer follow-up questions
- AI adapts to the level of detail provided

### 2. **Smart Trigger Detection**
The backend uses dual-trigger logic:
- **Phrase Detection**: AI says "Great, I have everything I need!"
- **Auto-Extraction**: Analyzes transcript for skills AND interests
- **Combined Logic**: Triggers when BOTH conditions are met

```python
# Backend checks:
skills_ok = has_valid_skills(profile)  # Python, React, etc.
interests_ok = has_valid_interests(profile)  # FinTech, Healthcare, etc.
is_trigger = phrase_trigger OR (skills_ok AND interests_ok)
```

### 3. **Profile Extraction**
Using Groq's `llama-3.1-70b-versatile`:
```python
{
  "name": "User",
  "skills": ["Product Design", "Fintech", "UI/UX"],
  "interests": ["B2B Payments", "Financial Technology"],
  "role": "Designer",
  "looking_for": "Software Engineer"
}
```

### 4. **Vector Embedding & Semantic Search**
- Profile → text → embedding using `sentence-transformers`
- Query ChromaDB for similar profiles
- Returns top 5-7 matches based on cosine similarity

### 5. **Re-ranking Algorithm**
Matches are scored based on:
```python
score = 0.0

# Role complementarity (highest weight)
if candidate_role in target_roles:
    score += 10.0  # Explicitly requested role
elif candidate_role in complement_roles:
    score += 6.0   # Complementary role
    
# Domain overlap
shared_interests = user_interests ∩ candidate_interests
score += 3.0 * (overlap_ratio)

# Final sorting by score
```

### 6. **Team Building**
AI generates 2-3 different team suggestions:
- **Balanced Team**: Designer + PM (early-stage focus)
- **Technical Powerhouse**: 2 technical roles (infrastructure focus)
- **Product-Led Team**: PM + executor (user-centric focus)

Each team gets AI-generated reasoning using Groq.

### 7. **Results Display**
- **Match Cards**: 5-6 individuals with compatibility scores
- **Team Suggestions**: 2-3 pre-formed teams with reasoning
- **Animations**: Staggered slide-up animations (100ms delays)
- **Auto-scroll**: Smooth scroll to results section

---

## 📡 API Endpoints

### `GET /health`
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2025-10-26T05:00:00Z"
}
```

### `POST /chat`
Send a chat message, get AI response with trigger detection

**Request:**
```json
{
  "session_id": "session_123",
  "message": "I'm a Python developer interested in healthcare"
}
```

**Response:**
```json
{
  "response": "What domains interest you most?",
  "is_trigger": false
}
```

When trigger is detected:
```json
{
  "response": "Great, I have everything I need!",
  "is_trigger": true
}
```

### `POST /find-collaborators`
Extract profile and find matches

**Request:**
```json
{
  "session_id": "session_123",
  "chat_transcript": "User: I'm a Python developer...\nAssistant: ..."
}
```

**Response:**
```json
{
  "matches": [
    {
      "name": "Maya Patel",
      "role": "Designer",
      "skills": ["UI/UX", "Figma", "Healthcare"],
      "interests": ["Medical Tech", "Accessibility"],
      "bio": "Product designer...",
      "availability": "Available",
      "score": 92
    }
  ],
  "team_suggestions": [
    {
      "members": [
        { "name": "Maya Patel", "role": "Designer" },
        { "name": "Alex Chen", "role": "Product Manager" }
      ],
      "reasoning": "A balanced team combining Designer and Product Manager skills..."
    }
  ],
  "your_profile": { ... }
}
```

---

## 🎨 UI/UX Features

### Animations
- **Slide-up entrance** for match cards (staggered 100ms delays)
- **Fade-in** for team suggestions
- **Pulse animation** on chatbot icon (sparkle ✨)
- **Hover effects** on cards (scale, shadow, translate)
- **Smooth scrolling** to results section
- **Loading spinner** with minimum 1.5s display time

### Design System
- **Color Palette**: Purple/Blue gradients (#726BFF → #5E82FF)
- **Typography**: Space Grotesk (headings), Plus Jakarta Sans (body)
- **Glass Morphism**: Backdrop blur effects throughout
- **Responsive**: Mobile-first design, scales to desktop

### Interactive Elements
- **Compatibility Badges**: Color-coded scores (Green 90%+, Blue 80-89%, Purple 75-79%)
- **Suggested Prompts**: Quick-start options with different detail levels
- **Debug Panel**: Bottom-right real-time state indicator (removable)
- **Status Indicator**: Green dot shows backend connection

---

## 📊 Sample Data

The database includes 20+ diverse collaborators:
- **Software Engineers** (Python, JavaScript, Full-stack, Mobile)
- **Designers** (UI/UX, Product Design, Brand)
- **Product Managers** (Technical PM, Growth PM)
- **Data Scientists** (ML, AI, Analytics)
- **Business Developers** (Sales, Marketing, Fundraising)

Each profile includes:
- Skills, interests, role, bio, availability
- Pre-computed embeddings for fast matching
- Realistic backgrounds and expertise areas

---

## 🚨 Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**"GROQ_API_KEY not found":**
```bash
# Check .env file exists and has your key
cat .env

# Should show:
GROQ_API_KEY=gsk_your_key_here

# If not, add it:
echo "GROQ_API_KEY=gsk_your_key_here" > .env
```

**Port 5001 already in use:**
```bash
# Find and kill the process
lsof -ti:5001 | xargs kill -9

# Or change port in app.py:
app.run(host='0.0.0.0', port=5002, debug=True)
```

**ChromaDB warnings:**
- These are normal! ChromaDB shows warnings about telemetry but works fine
- Safe to ignore: "Failed to send telemetry event"

### Frontend Issues

**"Module not found" in Next.js:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**"Failed to fetch" errors:**
- Make sure backend is running on port 5001
- Check backend status indicator (should be green)
- Open browser console and check for CORS errors

**Chatbot not showing:**
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Clear browser cache
- Check browser console for errors

---

## ⚡ Performance Notes

- **Response Time**: Chat responses in ~200ms with Groq
- **Matching Time**: Profile extraction + matching in ~500-800ms
- **Database**: ChromaDB loads instantly with pre-computed embeddings
- **First Load**: ~1s for Next.js initial page load
- **Animations**: 60fps smooth animations using CSS transforms

---

## 🎯 Future Enhancements

### Short Term
- [ ] Add user authentication (Auth0/Clerk)
- [ ] Save match history to database
- [ ] Email notifications for new matches
- [ ] Export matches to PDF/CSV
- [ ] More detailed match explanations

### Long Term
- [ ] Real Bright Data integration for LinkedIn enrichment
- [ ] Direct messaging between matched users
- [ ] Video chat integration
- [ ] Advanced filtering (location, availability, equity split)
- [ ] Machine learning to improve matching over time
- [ ] Mobile apps (React Native)

---

## 🏗️ Architecture Decisions

### Why Groq?
- **Speed**: 200ms response time vs 2-3s with other providers
- **Cost**: Free tier with generous limits
- **Quality**: Llama 3.1 matches GPT-4 quality at 10x speed

### Why ChromaDB?
- **Local-first**: No external dependencies
- **Fast**: In-memory operations with persistence
- **Simple**: Minimal setup, works out of the box
- **Free**: No API costs or limits

### Why Next.js?
- **Performance**: Server-side rendering + static generation
- **Developer Experience**: Hot reload, TypeScript support
- **Ecosystem**: Rich component libraries (shadcn/ui)
- **Production Ready**: Vercel deployment in one click

---

## 📝 Development Notes

### Adding New Profiles
```bash
# Edit seed_db.py and add to profiles list:
{
    "name": "New Person",
    "role": "Software Engineer",
    "skills": ["Python", "React"],
    "interests": ["AI", "Web3"],
    "bio": "Description here",
    "availability": "Available"
}

# Re-run seeding:
python seed_db.py
```

### Modifying Matching Algorithm
See `backend/ai_core.py` → `find_collaborators()` function:
- Adjust role weights (lines 450-455)
- Change domain overlap calculation (lines 460-465)
- Modify team building logic (lines 665-725)

### Customizing UI
- Colors: `frontend/app/globals.css` (CSS variables)
- Animations: `frontend/app/globals.css` (@keyframes)
- Chatbot styling: `frontend/app/chatbot.css`
- Components: `frontend/components/`

---

## 👥 Team

Built with ❤️ for **CalHacks 12.0**

---

## 📄 License

MIT License - Feel free to use this project for learning, hackathons, or personal projects!

---

## 🙏 Acknowledgments

- **Groq** for lightning-fast LLM inference
- **CalHacks** for the amazing hackathon experience
- **ChromaDB** for the elegant vector database
- **Vercel** for Next.js and incredible dev tools
- **shadcn** for beautiful, accessible UI components

---

**Happy Matching! 🚀✨**
