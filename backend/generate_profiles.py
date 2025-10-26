"""
Automated profile generator for diverse collaborators.
Generates realistic profiles without manual entry.
"""

import random
import json

# Profile templates by role
ROLES = {
    "Software Engineer": {
        "skills": [
            ["Python", "Django", "PostgreSQL", "Redis"],
            ["JavaScript", "Vue.js", "Node.js", "MongoDB"],
            ["Go", "gRPC", "Kubernetes", "Docker"],
            ["Rust", "WebAssembly", "Systems Programming"],
            ["Ruby", "Rails", "Sidekiq", "Heroku"],
            ["Elixir", "Phoenix", "LiveView", "Distributed Systems"],
            ["Swift", "SwiftUI", "Combine", "Core Data"],
            ["Kotlin", "Jetpack Compose", "Coroutines", "Room"],
            ["TypeScript", "Angular", "RxJS", "NgRx"],
            ["PHP", "Laravel", "MySQL", "Redis"],
        ],
        "bios": [
            "Full-stack developer with {years} years building scalable web applications.",
            "Backend specialist focused on performance and reliability.",
            "Frontend engineer who loves crafting pixel-perfect UIs.",
            "Mobile-first developer shipping apps to millions of users.",
            "Systems programmer optimizing for speed and efficiency.",
            "Polyglot engineer comfortable across the stack.",
            "API architect designing developer-friendly interfaces.",
            "Indie hacker who's shipped {projects} side projects.",
        ]
    },
    "Designer": {
        "skills": [
            ["Figma", "Prototyping", "Design Systems", "User Testing"],
            ["Adobe XD", "Illustration", "Brand Identity", "Typography"],
            ["Sketch", "InVision", "Wireframing", "UI Animation"],
            ["Framer", "Motion Design", "Micro-interactions", "CSS"],
            ["User Research", "Journey Mapping", "Personas", "A/B Testing"],
            ["Visual Design", "Color Theory", "Layout", "Composition"],
            ["3D Design", "Blender", "3D Modeling", "Rendering"],
            ["Design Ops", "Documentation", "Design Tokens", "Collaboration"],
        ],
        "bios": [
            "Product designer passionate about creating intuitive user experiences.",
            "Visual designer with an eye for detail and storytelling.",
            "UX researcher who loves uncovering user needs through data.",
            "Design systems architect building scalable component libraries.",
            "Motion designer adding delight through animation.",
            "Brand designer crafting memorable identities.",
            "Accessibility-first designer ensuring products work for everyone.",
            "Design lead who's mentored {people} designers.",
        ]
    },
    "Product Manager": {
        "skills": [
            ["Product Strategy", "Roadmapping", "Metrics", "Prioritization"],
            ["User Research", "Customer Interviews", "Market Analysis", "Competitive Analysis"],
            ["A/B Testing", "Analytics", "SQL", "Data-Driven Decisions"],
            ["Agile", "Scrum", "Sprint Planning", "Backlog Management"],
            ["Technical Writing", "PRDs", "User Stories", "Documentation"],
            ["Go-to-Market", "Launch Strategy", "Marketing", "Positioning"],
            ["Stakeholder Management", "Communication", "Alignment", "Influence"],
            ["Growth", "Activation", "Retention", "Monetization"],
        ],
        "bios": [
            "Product manager turning ambiguous problems into shipped features.",
            "Data-driven PM obsessed with metrics and user outcomes.",
            "Technical PM who can code and ship prototypes.",
            "Growth PM focused on activation and retention loops.",
            "Platform PM building tools that other teams love.",
            "B2B PM who understands enterprise customer needs.",
            "Consumer PM shipping products to millions of users.",
            "AI/ML PM translating research into product value.",
        ]
    },
    "Data Scientist": {
        "skills": [
            ["Python", "Pandas", "NumPy", "Scikit-learn", "Jupyter"],
            ["TensorFlow", "Keras", "Deep Learning", "Neural Networks"],
            ["PyTorch", "Computer Vision", "CNNs", "Transfer Learning"],
            ["NLP", "Transformers", "BERT", "LLMs", "RAG"],
            ["SQL", "PostgreSQL", "Data Warehousing", "ETL"],
            ["R", "Statistics", "Hypothesis Testing", "Causal Inference"],
            ["Spark", "Big Data", "Distributed Computing", "Scala"],
            ["MLOps", "Model Deployment", "Monitoring", "A/B Testing"],
        ],
        "bios": [
            "Data scientist turning messy data into actionable insights.",
            "ML engineer deploying models that drive business value.",
            "Research scientist pushing the boundaries of what's possible.",
            "Applied scientist solving real-world problems with ML.",
            "Computer vision specialist working on perception systems.",
            "NLP engineer building language understanding systems.",
            "Data engineer building reliable data pipelines.",
            "MLOps engineer making ML systems production-ready.",
        ]
    },
    "Marketing & Growth": {
        "skills": [
            ["Content Marketing", "SEO", "Copywriting", "Blogging"],
            ["Growth Hacking", "Viral Loops", "Referrals", "Experiments"],
            ["Paid Acquisition", "Google Ads", "Facebook Ads", "CAC"],
            ["Email Marketing", "Automation", "Drip Campaigns", "Mailchimp"],
            ["Social Media", "Community", "Engagement", "Brand Voice"],
            ["Analytics", "Google Analytics", "Mixpanel", "Amplitude"],
            ["Product Marketing", "Positioning", "Messaging", "GTM"],
            ["Influencer Marketing", "Partnerships", "Collaborations", "Outreach"],
        ],
        "bios": [
            "Growth marketer who's scaled {number} companies from 0 to $1M+ ARR.",
            "Content strategist building organic acquisition engines.",
            "Performance marketer optimizing every dollar of ad spend.",
            "Community builder growing engaged audiences of {number}+ members.",
            "Product marketer who makes complex products simple to understand.",
            "Brand marketer crafting memorable stories that resonate.",
            "Influencer marketer who's run {number} successful campaigns.",
            "Lifecycle marketer optimizing onboarding to retention.",
        ]
    },
    "Sales & Business Development": {
        "skills": [
            ["Enterprise Sales", "MEDDIC", "Solution Selling", "Demos"],
            ["Outbound", "Cold Email", "Prospecting", "Lead Generation"],
            ["Partnerships", "Channel Sales", "Alliances", "Co-selling"],
            ["Customer Success", "Onboarding", "Retention", "Upselling"],
            ["Sales Ops", "CRM", "Salesforce", "Pipeline Management"],
            ["Negotiation", "Closing", "Contract Review", "Pricing"],
            ["Account Management", "Relationship Building", "Customer Advocacy"],
            ["Sales Enablement", "Training", "Playbooks", "Documentation"],
        ],
        "bios": [
            "Enterprise AE who's closed {number} six-figure deals.",
            "SDR turned AE with {years} years of quota crushing.",
            "Partnerships lead who's built {number} strategic alliances.",
            "Customer success manager with {percent}% retention rate.",
            "Sales engineer who demos and closes technical deals.",
            "Revenue leader who's built teams from 0 to {number} reps.",
            "Inbound sales specialist converting high-intent leads.",
            "Account executive specializing in mid-market SaaS.",
        ]
    }
}

# Interest categories with specific topics
INTERESTS = {
    "Tech Verticals": [
        "AI/ML", "Healthcare", "FinTech", "EdTech", "Climate Tech",
        "Legal Tech", "Real Estate Tech", "Agriculture", "Supply Chain",
        "Robotics", "Drones", "Space Tech", "Quantum Computing"
    ],
    "Consumer": [
        "E-commerce", "Social Media", "Gaming", "Creator Economy",
        "Fitness", "Wellness", "Mental Health", "Food Tech",
        "Travel", "Hospitality", "Entertainment", "Music"
    ],
    "Enterprise": [
        "B2B SaaS", "Developer Tools", "Security", "Privacy",
        "Infrastructure", "DevOps", "Data Tools", "Analytics",
        "Productivity", "Collaboration", "Workflow Automation"
    ],
    "Impact": [
        "Nonprofit", "Social Good", "Education", "Accessibility",
        "Diversity", "Sustainability", "Open Source", "Democracy",
        "Public Health", "Policy", "Community", "Economic Justice"
    ]
}

# Names pool (diverse, international)
FIRST_NAMES = [
    # More names added for diversity
    "Aiden", "Aria", "Chen", "Diana", "Ethan", "Fatima", "Gabriel", "Hana",
    "Ibrahim", "Jade", "Kai", "Leila", "Marco", "Nadia", "Oscar", "Priya",
    "Quinn", "Rafael", "Sofia", "Tomas", "Uma", "Viktor", "Wei", "Xiao",
    "Yuki", "Zara", "Ahmed", "Bianca", "Carlos", "Darius", "Elena", "Felix",
    "Greta", "Hassan", "Isla", "Jorge", "Kenji", "Lucia", "Malik", "Nina",
    "Oliver", "Petra", "Quincy", "Rosa", "Sven", "Tara", "Ulrich", "Vera",
    "Winston", "Xander", "Yasmin", "Zane"
]

LAST_NAMES = [
    "Anderson", "Brown", "Chen", "Davis", "Evans", "Fischer", "Garcia", "Hassan",
    "Ivanov", "Johnson", "Kim", "Lopez", "Martinez", "Nguyen", "O'Brien", "Patel",
    "Quinn", "Rodriguez", "Smith", "Thompson", "Usman", "Vargas", "Wang", "Xu",
    "Yang", "Zhang", "Abbas", "Berg", "Costa", "Diallo", "Ellis", "Fernandez",
    "Green", "Hughes", "Ibrahim", "Jones", "Kumar", "Lee", "Miller", "Nelson",
    "Okafor", "Park", "Qureshi", "Ramos", "Santos", "Taylor", "Uddin", "Vega",
    "Wilson", "Yamamoto", "Zhao"
]

AVAILABILITY = ["Available", "Available", "Available", "Part-time", "Contract", "Advisory"]

def generate_profile(id_num):
    """Generate a single realistic profile."""
    # Pick role
    role = random.choice(list(ROLES.keys()))
    role_data = ROLES[role]
    
    # Generate name
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    
    # Pick skills for this role
    skills = random.choice(role_data["skills"])
    
    # Pick 2-3 interests from different categories
    interest_cats = random.sample(list(INTERESTS.keys()), k=random.randint(2, 3))
    interests = []
    for cat in interest_cats:
        interests.append(random.choice(INTERESTS[cat]))
    
    # Generate bio
    bio_template = random.choice(role_data["bios"])
    bio = bio_template.format(
        years=random.randint(2, 8),
        projects=random.randint(3, 12),
        people=random.randint(5, 20),
        number=random.choice(["3", "5", "10", "50", "100"]),
        percent=random.choice(["90", "92", "95", "97"])
    )
    
    # Generate availability
    availability = random.choice(AVAILABILITY)
    
    return {
        "id": f"collab_{id_num}",
        "name": name,
        "role": role,
        "skills": skills,
        "interests": interests,
        "bio": bio,
        "availability": availability
    }

def generate_profiles(count, start_id=93):
    """Generate multiple profiles."""
    profiles = []
    for i in range(count):
        profile = generate_profile(start_id + i)
        profiles.append(profile)
    return profiles

def format_for_seed_file(profiles):
    """Format profiles for seed_db.py"""
    output = []
    for p in profiles:
        formatted = f'''    {{
        "id": "{p["id"]}",
        "name": "{p["name"]}",
        "role": "{p["role"]}",
        "skills": {json.dumps(p["skills"])},
        "interests": {json.dumps(p["interests"])},
        "bio": "{p["bio"]}",
        "availability": "{p["availability"]}"
    }}'''
        output.append(formatted)
    return ",\n".join(output)

if __name__ == "__main__":
    import sys
    
    # Get count from command line or default to 20
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    
    print(f"🤖 Generating {count} diverse profiles...")
    profiles = generate_profiles(count)
    
    print(f"\n✅ Generated {len(profiles)} profiles")
    print(f"\nRole distribution:")
    role_counts = {}
    for p in profiles:
        role_counts[p["role"]] = role_counts.get(p["role"], 0) + 1
    for role, count in sorted(role_counts.items()):
        print(f"  - {role}: {count}")
    
    print(f"\n📋 Copy-paste this into seed_db.py collaborators list:\n")
    print("    # === Auto-generated profiles ===")
    print(format_for_seed_file(profiles))
    
    # Also save to JSON file for reference
    with open("generated_profiles.json", "w") as f:
        json.dump(profiles, f, indent=2)
    print(f"\n💾 Also saved to generated_profiles.json")
