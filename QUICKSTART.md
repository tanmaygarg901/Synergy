# Quick Start Guide - Synergy

Get Synergy up and running in 5 minutes!

## 🚀 Quick Setup

### 1. Get a Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up/login
3. Create an API key
4. Copy it for the next step

### 2. Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your Groq API key

# Seed database with fake collaborators
python seed_db.py

# Start server
python app.py
```

Backend runs at: `http://localhost:5000`

### 3. Frontend Setup (2 minutes)

Open a NEW terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: `http://localhost:3000`

## ✅ Test It Out

1. Open http://localhost:3000 in your browser
2. Chat with Synergy AI:
   - Enter your name
   - Describe your skills (e.g., "Python, React, AI")
   - Share your interests (e.g., "EdTech, Sustainability")
   - Say what collaborator you need (e.g., "Designer")
3. When the AI says "Great, I have a clear picture!", it will find matches
4. View your profile and matched collaborators!

## 🐛 Troubleshooting

**Backend won't start?**
- Make sure you added your Groq API key to `.env`
- Check Python version: `python --version` (need 3.8+)
- Verify virtual environment is activated

**Frontend won't start?**
- Check Node version: `node --version` (need 18+)
- Try deleting `node_modules` and running `npm install` again
- Make sure backend is running first

**No matches found?**
- Database might not be seeded. Run `python seed_db.py` in backend
- Check backend logs for errors

**CSS warnings in IDE?**
- The `@tailwind` and `@apply` warnings are expected
- These are TailwindCSS directives that work correctly at build time
- You can safely ignore them

## 📦 Project Structure

```
calhacks 12.0/
├── backend/
│   ├── app.py              # Flask API server
│   ├── ai_core.py          # Groq AI + ChromaDB logic
│   ├── seed_db.py          # Database seeding
│   ├── requirements.txt    # Python packages
│   └── .env               # Your API keys (create this)
│
└── frontend/
    ├── app/
    │   ├── page.js         # Main app (3 states)
    │   └── globals.css     # Tailwind + custom styles
    ├── components/
    │   ├── ui/            # shadcn components
    │   ├── chatbot/       # Chatbot config
    │   └── UserCard.jsx   # Match display
    └── package.json       # Node packages
```

## 🎯 Key Features to Demo

1. **Real-time Chat**: Uses Groq's ultra-fast llama3-8b
2. **Smart Extraction**: llama3-70b extracts structured data from conversation
3. **Vector Search**: ChromaDB finds semantically similar collaborators
4. **Mock Enrichment**: Try saying your name is "Bob" - you'll get an extra "SEO" skill!
5. **Beautiful UI**: Modern design with shadcn/ui components

## 🔗 Useful Links

- Groq Console: https://console.groq.com
- Groq Docs: https://console.groq.com/docs
- ChromaDB Docs: https://docs.trychroma.com
- shadcn/ui: https://ui.shadcn.com

## 💡 Tips for Hackathon

- **Demo Flow**: "Hi I'm [name]" → skills → interests → "looking for a [role]"
- **Best Test**: Say you're looking for a "Software Engineer" or "Designer"
- **Easter Egg**: Name yourself "Bob" to see enrichment in action
- **Fast Iteration**: Backend auto-reloads, frontend has fast refresh

## 🚀 Ready to Ship?

When ready to deploy:
- Frontend: Deploy to Vercel (automatic Next.js support)
- Backend: Deploy to Render, Railway, or Heroku
- Don't forget to set environment variables on your hosting platform!

---

**Need help?** Check the main README.md for detailed information.

Good luck at CalHacks! 🎉
