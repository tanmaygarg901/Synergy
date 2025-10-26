import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB client (disable telemetry to avoid noisy PostHog errors)
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)

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
    },
    {
        "id": "collab_5",
        "name": "Priya Nair",
        "role": "Product Manager",
        "skills": ["Roadmapping", "User Interviews", "A/B Testing", "Analytics", "Stakeholder Management"],
        "interests": ["Marketplace platforms", "Creator economy", "B2B SaaS"],
        "bio": "PM with 6+ years shipping data-informed features across web and mobile.",
        "availability": "Full-time"
    },
    {
        "id": "collab_6",
        "name": "Diego Alvarez",
        "role": "Marketing",
        "skills": ["Growth", "Content Strategy", "SEO", "Paid Acquisition", "Email Marketing"],
        "interests": ["DevTools", "Open source", "Community building"],
        "bio": "Growth marketer who scaled two developer communities from 0 to 50k+.",
        "availability": "Part-time"
    },
    {
        "id": "collab_7",
        "name": "Lisa Wong",
        "role": "Sales",
        "skills": ["Enterprise Sales", "Discovery", "Negotiation", "CRM", "MEDDIC"],
        "interests": ["AI for healthcare", "Compliance", "B2B"],
        "bio": "Account executive with 8 years in healthcare SaaS, $5M+ ARR closed.",
        "availability": "Full-time"
    },
    {
        "id": "collab_8",
        "name": "Ethan Brooks",
        "role": "Data Scientist",
        "skills": ["Python", "PyTorch", "NLP", "Time Series", "MLOps"],
        "interests": ["Climate tech", "Forecasting", "Recommender systems"],
        "bio": "DS with a research background in NLP and deploying production ML pipelines.",
        "availability": "Part-time"
    },
    {
        "id": "collab_9",
        "name": "Ava Johnson",
        "role": "Designer",
        "skills": ["Design Systems", "Prototyping", "Illustration", "Accessibility", "Figma"],
        "interests": ["FinTech", "Education", "Inclusive design"],
        "bio": "Senior product designer focused on design systems and rapid prototyping.",
        "availability": "Contract"
    },
    {
        "id": "collab_10",
        "name": "Markus Schaefer",
        "role": "Software Engineer",
        "skills": ["Go", "Distributed Systems", "Kubernetes", "PostgreSQL", "gRPC"],
        "interests": ["Infra", "Observability", "High availability"],
        "bio": "Backend engineer building reliable distributed systems at scale.",
        "availability": "Full-time"
    },
    {
        "id": "collab_11",
        "name": "Nina Park",
        "role": "Software Engineer",
        "skills": ["React", "TypeScript", "Next.js", "Tailwind", "Accessibility"],
        "interests": ["Creator tools", "E-commerce", "Design systems"],
        "bio": "Frontend engineer crafting fast, accessible web apps and component libraries.",
        "availability": "Full-time"
    },
    {
        "id": "collab_12",
        "name": "Rohan Mehta",
        "role": "Product Manager",
        "skills": ["Prioritization", "Experimentation", "PRD Writing", "Pricing", "Go-to-Market"],
        "interests": ["AI productivity", "SaaS", "Collaboration"],
        "bio": "PM who loves turning ambiguous problems into measurable outcomes.",
        "availability": "Part-time"
    },
    {
        "id": "collab_13",
        "name": "Sofia Marin",
        "role": "Designer",
        "skills": ["User Research", "Interaction Design", "Visual Design", "Motion", "Prototyping"],
        "interests": ["Healthtech", "Social impact", "Onboarding"],
        "bio": "Product designer focused on zero-to-one experiences with a research-first approach.",
        "availability": "Full-time"
    },
    {
        "id": "collab_14",
        "name": "Omar El-Sayed",
        "role": "Finance Expert",
        "skills": ["FP&A", "Fundraising", "Unit Economics", "Investor Relations", "Modeling"],
        "interests": ["Marketplaces", "Sustainability", "FinOps"],
        "bio": "Startup finance lead who helped 2 teams navigate seed to Series B.",
        "availability": "Advisory"
    },
    {
        "id": "collab_15",
        "name": "Grace Kim",
        "role": "DevOps Engineer",
        "skills": ["AWS", "Terraform", "CI/CD", "Docker", "Prometheus"],
        "interests": ["Platform engineering", "Cost optimization", "Security"],
        "bio": "DevOps engineer automating infrastructure and improving developer velocity.",
        "availability": "Contract"
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
            metadatas.append({
                "id": collab["id"],
                "name": collab["name"],
                "role": collab["role"],
                "skills": ", ".join(collab.get("skills", [])),
                "interests": ", ".join(collab.get("interests", [])),
                "bio": collab["bio"],
                "availability": collab["availability"],
            })
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