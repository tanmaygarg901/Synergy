#!/bin/bash

# Quick script to wipe and re-seed the database

echo "🔄 Resetting ChromaDB..."
echo ""

echo "🗑️  Step 1/2: Wiping database..."
python3 wipe_db.py --force

echo ""
echo "🌱 Step 2/2: Re-seeding with fresh profiles..."
python3 seed_db.py

echo ""
echo "✅ Database reset complete!"
echo "   - 92 diverse collaborators ready"
echo "   - No duplicate 'User' entries"
echo ""
echo "💡 To add Slack intros manually:"
echo "   1. Go to http://localhost:3000"
echo "   2. Paste the Slack intro in the chat"
echo "   3. Answer any follow-up questions"
echo "   4. They'll be added to the database automatically!"
echo ""
echo "Or use: python add_slack_intro.py \"intro text here\""
