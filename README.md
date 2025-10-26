# Synergy - AI Collaborator Finder

**CalHacks 12.0 Project**

Synergy is an AI-powered platform that helps you find the perfect collaborator for your next project. Chat with our AI assistant to describe your skills and needs, then get matched with complementary team members.

## Tech Stack

### Frontend
- **Next.js 14** - React framework
- **shadcn/ui** - Modern UI components
- **Tailwind CSS** - Styling
- **react-chatbot-kit** - Chat interface
- **Lucide Icons** - Icon system

### Backend
- **Flask** - Python web framework
- **Groq AI** - Fast LLM inference
  - llama3-8b for real-time chat
  - llama3-70b for profile extraction
- **ChromaDB** - Vector database for matching
- **sentence-transformers** - Local embeddings

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

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com))

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_actual_api_key_here
```

6. Seed the database:
```bash
python seed_db.py
```

7. Start the Flask server:
```bash
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## How It Works

1. **Chat State**: Users chat with Synergy AI about their skills, interests, and what kind of collaborator they're looking for

2. **Trigger Detection**: When the AI detects it has enough information (trigger phrase: "Great, I have a clear picture!"), it transitions to the loading state

3. **Profile Extraction**: 
   - Uses Groq's llama3-70b in JSON mode to extract structured profile
   - Runs mock Bright Data enrichment (adds "SEO" skill if name is "Bob")
   - Creates embedding from user's needs using sentence-transformers

4. **Matching**: 
   - Queries ChromaDB with the user's profile embedding
   - Filters by role if specified
   - Returns top 3 matches

5. **Results Display**: Shows user's enriched profile and matched collaborators with beautiful UI cards

## API Endpoints

- `GET /health` - Health check
- `POST /chat` - Send chat message, get AI response
- `POST /find-collaborators` - Extract profile and find matches

## Features

- ✨ Real-time AI chat with Groq's fast llama3-8b
- 🎯 Intelligent profile extraction using llama3-70b
- 🔍 Vector similarity search with ChromaDB
- 💼 Pre-seeded with diverse collaborator profiles
- 🎨 Beautiful, modern UI with shadcn/ui
- 📱 Responsive design
- 🚀 Fast and efficient

## Mock Data

The database is pre-seeded with 4 collaborators:
- **Alex Chen** - Software Engineer (AI/ML, Web3)
- **Maya Patel** - Designer (Healthcare, Accessibility)
- **Jordan Lee** - Finance Expert (FinTech, Fundraising)
- **Sam Rivera** - Mobile Developer (Consumer apps, Gaming)

## Future Enhancements

- Real Bright Data integration for profile enrichment
- User authentication and saved matches
- Direct messaging between matched users
- More sophisticated matching algorithms
- Larger collaborator database
- Match explanations (why you matched)

## Team

Built with ❤️ for CalHacks 12.0

## License

MIT
