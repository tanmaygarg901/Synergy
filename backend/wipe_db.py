#!/usr/bin/env python3
"""
Wipe ChromaDB completely and start fresh.
Run this before re-seeding with seed_db.py
"""

import chromadb
import os
import shutil
import sys

def wipe_chromadb():
    """Delete the entire ChromaDB directory."""
    db_path = "./chroma_db"
    
    if os.path.exists(db_path):
        print(f"🗑️  Deleting ChromaDB at {db_path}...")
        shutil.rmtree(db_path)
        print("✅ ChromaDB wiped successfully!")
    else:
        print("ℹ️  No ChromaDB found at ./chroma_db")
    
    print("\n📝 Next steps:")
    print("   1. Run: python seed_db.py")
    print("   2. Or add manual entries from Slack via the frontend")

if __name__ == "__main__":
    # Check if --force flag is passed (for scripting)
    if "--force" in sys.argv:
        wipe_chromadb()
    else:
        confirm = input("⚠️  This will DELETE all data in ChromaDB. Continue? (yes/no): ")
        
        if confirm.lower() in ['yes', 'y']:
            wipe_chromadb()
        else:
            print("❌ Aborted.")
