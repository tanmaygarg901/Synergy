import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Fake collaborators data
collaborators = [
    {
        "id": "collab_1",
        "name": "Alex Chen",
        "role": "Software Engineer",
        "skills": ["Python", "React", "Node.js", "AI/ML"],
        "interests": ["Building AI tools", "Web3", "EdTech"],
        "bio": "Full-stack engineer with 5 years experience. Love building products that solve real problems.",
        "availability": "Part-time"
    },
    {
        "id": "collab_2",
        "name": "Maya Patel",
        "role": "Designer",
        "skills": ["UI/UX Design", "Figma", "Brand Identity", "User Research"],
        "interests": ["Healthcare tech", "Accessibility", "Design systems"],
        "bio": "Product designer passionate about creating inclusive experiences. Previously at startup and FAANG.",
        "availability": "Full-time"
    },
    {
        "id": "collab_3",
        "name": "Jordan Lee",
        "role": "Finance Expert",
        "skills": ["Financial Modeling", "Fundraising", "P&L Management", "VC Relations"],
        "interests": ["FinTech", "Sustainable business", "Market analysis"],
        "bio": "Former investment banker turned startup CFO. Helped 3 companies raise Series A.",
        "availability": "Advisory"
    },
    {
        "id": "collab_4",
        "name": "Sam Rivera",
        "role": "Software Engineer",
        "skills": ["Mobile Development", "Flutter", "Swift", "Firebase"],
        "interests": ["Consumer apps", "Gaming", "AR/VR"],
        "bio": "Mobile-first developer who loves creating delightful user experiences. Indie game dev on weekends.",
        "availability": "Part-time"
    }
]


def create_embedding(text):
    """Create embedding for text."""
    return embedding_model.encode(text).tolist()


def seed_database():
    """Seed ChromaDB with fake collaborators."""
    try:
        # Delete existing collection if it exists
        try:
            chroma_client.delete_collection(name="collaborators")
            print("Deleted existing collection")
        except:
            pass
        
        # Create new collection
        collection = chroma_client.create_collection(
            name="collaborators",
            metadata={"description": "Collaborator profiles"}
        )
        
        # Prepare data for insertion
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for collab in collaborators:
            # Create searchable text from profile
            searchable_text = f"{collab['role']} {' '.join(collab['skills'])} {' '.join(collab['interests'])} {collab['bio']}"
            
            # Create embedding
            embedding = create_embedding(searchable_text)
            
            # Prepare data
            ids.append(collab['id'])
            embeddings.append(embedding)
            metadatas.append(collab)
            documents.append(searchable_text)
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        print(f"✅ Successfully seeded {len(collaborators)} collaborators to ChromaDB")
        
        # Verify
        count = collection.count()
        print(f"📊 Collection now contains {count} items")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")


if __name__ == "__main__":
    print("🌱 Seeding database...")
    seed_database()
