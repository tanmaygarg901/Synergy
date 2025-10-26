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
        "role": "Finance & Operations",
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
        "role": "Marketing & Growth",
        "skills": ["Growth", "Content Strategy", "SEO", "Paid Acquisition", "Email Marketing"],
        "interests": ["DevTools", "Open source", "Community building"],
        "bio": "Growth marketer who scaled two developer communities from 0 to 50k+.",
        "availability": "Part-time"
    },
    {
        "id": "collab_7",
        "name": "Lisa Wong",
        "role": "Sales & Business Development",
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
        "role": "Finance & Operations",
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

# Additional enriched demo profiles
collaborators.extend([
    {
        "id": "collab_16",
        "name": "Zoe Park",
        "role": "Software Engineer",
        "skills": ["PyTorch", "RAG", "LLMs", "LangChain", "Vector DBs"],
        "interests": ["AI agents", "Knowledge search", "Developer tools"],
        "bio": "AI engineer building retrieval-augmented agents with LangChain and vector databases.",
        "availability": "Full-time"
    },
    {
        "id": "collab_17",
        "name": "David Kim",
        "role": "Software Engineer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Celery"],
        "interests": ["Healthcare data", "Privacy", "Security"],
        "bio": "Backend engineer experienced in secure data pipelines and async processing.",
        "availability": "Full-time"
    },
    {
        "id": "collab_18",
        "name": "Aria Singh",
        "role": "Software Engineer",
        "skills": ["Kotlin", "SwiftUI", "Flutter", "Firebase"],
        "interests": ["Fitness", "Behavior change", "Wearables"],
        "bio": "Mobile engineer shipping polished iOS/Android apps with fast iteration.",
        "availability": "Part-time"
    },
    {
        "id": "collab_19",
        "name": "Ben Torres",
        "role": "Software Engineer",
        "skills": ["ROS2", "C++", "SLAM", "Computer Vision"],
        "interests": ["Robotics", "Drones", "Assistive tech"],
        "bio": "Robotics engineer focused on perception and autonomy.",
        "availability": "Contract"
    },
    {
        "id": "collab_20",
        "name": "Jing Li",
        "role": "Product Manager",
        "skills": ["PRDs", "Experimentation", "Metrics", "User Research"],
        "interests": ["AI productivity", "Collaboration", "SaaS"],
        "bio": "ML PM turning ambiguous ideas into measurable impact.",
        "availability": "Full-time"
    },
    {
        "id": "collab_21",
        "name": "Carla Gomez",
        "role": "Marketing",
        "skills": ["Growth loops", "SEO", "Content", "Paid Social"],
        "interests": ["Creator tools", "Community", "PLG"],
        "bio": "Growth marketer who bootstrapped communities to 100k+.",
        "availability": "Part-time"
    },
    {
        "id": "collab_22",
        "name": "Omar Farouk",
        "role": "Data Scientist",
        "skills": ["Spark", "Airflow", "dbt", "Snowflake", "Kafka"],
        "interests": ["Real-time analytics", "Observability", "Streaming"],
        "bio": "Data engineer/scientist building reliable streaming pipelines.",
        "availability": "Full-time"
    },
    {
        "id": "collab_23",
        "name": "Helena Schultz",
        "role": "Data Scientist",
        "skills": ["NLP", "Prompt engineering", "Evaluation", "OpenAI", "Groq"],
        "interests": ["Safety", "Alignment", "Eval harnesses"],
        "bio": "Researcher designing robust LLM evaluation harnesses.",
        "availability": "Advisory"
    },
    {
        "id": "collab_24",
        "name": "Priyanka Rao",
        "role": "Designer",
        "skills": ["UI Motion", "Prototyping", "Design Systems", "Figma"],
        "interests": ["HealthTech onboarding", "Accessibility", "Patient UX"],
        "bio": "Product designer focused on accessibility and motion clarity.",
        "availability": "Full-time"
    },
    {
        "id": "collab_25",
        "name": "Marco Alvarez",
        "role": "Software Engineer",
        "skills": ["Next.js", "React", "Node", "GraphQL", "Tailwind"],
        "interests": ["EdTech", "Learning", "Knowledge graphs"],
        "bio": "Full-stack engineer building modern web apps end-to-end.",
        "availability": "Full-time"
    },
    {
        "id": "collab_26",
        "name": "Noura Hassan",
        "role": "Security Engineer",
        "skills": ["Threat modeling", "OAuth", "JWT", "CSP", "SAST"],
        "interests": ["FinSec", "Privacy", "Compliance"],
        "bio": "Security engineer helping teams ship safely.",
        "availability": "Part-time"
    },
    {
        "id": "collab_27",
        "name": "Andre Williams",
        "role": "Software Engineer",
        "skills": ["Unity", "Unreal", "C#", "OpenXR"],
        "interests": ["AR/VR", "Serious games", "Edutainment"],
        "bio": "Game dev bringing playful experiences to learning and health.",
        "availability": "Contract"
    },
    {
        "id": "collab_28",
        "name": "Yuki Tanaka",
        "role": "DevOps Engineer",
        "skills": ["Kubernetes", "Terraform", "Prometheus", "Grafana", "ArgoCD"],
        "interests": ["Reliability", "Cost", "DX"],
        "bio": "SRE improving reliability and developer experience.",
        "availability": "Full-time"
    },
    {
        "id": "collab_29",
        "name": "Fatima Zahra",
        "role": "Data Scientist",
        "skills": ["Signal processing", "Time series", "Deep learning", "Python"],
        "interests": ["Diagnostics", "Wearables", "Health monitoring"],
        "bio": "Biomedical ML researcher focusing on signals and wearables.",
        "availability": "Part-time"
    },
    {
        "id": "collab_30",
        "name": "Tom Laurent",
        "role": "Sales",
        "skills": ["Partnerships", "Fundraising", "Pitching", "BD"],
        "interests": ["GovTech", "Public services", "Civic tech"],
        "bio": "Founder-minded operator who unlocks partnerships and capital.",
        "availability": "Advisory"
    },
])

# More Slack-style, non-coding inclusive demo profiles
collaborators.extend([
    {
        "id": "collab_31",
        "name": "Nina Alvarez",
        "role": "Product Manager",
        "skills": ["Zero-to-one", "User interviews", "PRDs", "Prioritization"],
        "interests": ["Productivity", "Collaboration", "AI agents"],
        "bio": "Founder-minded PM who loves turning napkin ideas into shipped products.",
        "availability": "Full-time"
    },
    {
        "id": "collab_32",
        "name": "Dr. Maya Singh",
        "role": "Data Scientist",
        "skills": ["Clinical research", "Statistics", "Python", "R"],
        "interests": ["Healthcare", "Medical imaging", "Patient outcomes"],
        "bio": "Healthcare researcher bridging clinics and data-driven insights.",
        "availability": "Part-time"
    },
    {
        "id": "collab_33",
        "name": "Leo Martins",
        "role": "Marketing & Growth",
        "skills": ["Community building", "Content", "SEO", "Events"],
        "interests": ["Open source", "Developer tools", "Education"],
        "bio": "Community manager who grew OSS projects from 0 to 100k+.",
        "availability": "Part-time"
    },
    {
        "id": "collab_34",
        "name": "Aisha Rahman",
        "role": "Finance & Operations",
        "skills": ["Compliance", "Risk", "Legal reviews", "Vendor management"],
        "interests": ["FinTech", "Security", "Healthcare"],
        "bio": "Ops/compliance lead who keeps the ship steady in regulated spaces.",
        "availability": "Full-time"
    },
    {
        "id": "collab_35",
        "name": "Kenji Watanabe",
        "role": "Designer",
        "skills": ["UX Research", "Prototyping", "Usability testing", "Figma"],
        "interests": ["Education", "HealthTech", "Onboarding"],
        "bio": "UX researcher turning user pain into simple journeys.",
        "availability": "Full-time"
    },
    {
        "id": "collab_36",
        "name": "Rachel Green",
        "role": "Sales & Business Development",
        "skills": ["Prospecting", "Discovery", "Pitching", "Partnerships"],
        "interests": ["SaaS", "Healthcare", "Security"],
        "bio": "BD operator who opens doors and closes complex deals.",
        "availability": "Full-time"
    },
    {
        "id": "collab_37",
        "name": "Arjun Patel",
        "role": "Product Manager",
        "skills": ["Roadmapping", "User research", "MVP scoping", "Data analysis"],
        "interests": ["FinTech", "AI", "Climate"],
        "bio": "Student founder looking to co-build something ambitious this hackathon.",
        "availability": "Part-time"
    },
    {
        "id": "collab_38",
        "name": "Elena Sokolov",
        "role": "Security Engineer",
        "skills": ["Threat modeling", "Identity", "OAuth", "OWASP"],
        "interests": ["Privacy", "Compliance", "Healthcare"],
        "bio": "Security engineer focused on practical safeguards for early-stage products.",
        "availability": "Contract"
    },
    {
        "id": "collab_39",
        "name": "Miguel Ortega",
        "role": "Product Manager",
        "skills": ["Curriculum design", "Research partnerships", "User testing"],
        "interests": ["Education", "Assessment", "Accessibility"],
        "bio": "Educator-turned-PM crafting tools for learning at scale.",
        "availability": "Part-time"
    },
    {
        "id": "collab_40",
        "name": "Sara Ahmed",
        "role": "Marketing & Growth",
        "skills": ["Content strategy", "Narratives", "Social", "Email"],
        "interests": ["HealthTech", "FinTech", "Community"],
        "bio": "Storyteller who turns products into movements.",
        "availability": "Part-time"
    },
])

collaborators.extend([
    {
        "id": "collab_41",
        "name": "Tara Nguyen",
        "role": "Marketing & Growth",
        "skills": ["Community", "Content", "SEO", "Analytics"],
        "interests": ["HealthTech", "Mental health", "Community"],
        "bio": "Community manager who grows authentic user bases through content and events.",
        "availability": "Part-time"
    },
    {
        "id": "collab_42",
        "name": "Jason Patel",
        "role": "Sales & Business Development",
        "skills": ["Customer Success", "Onboarding", "Renewals", "Playbooks"],
        "interests": ["SaaS", "Healthcare", "Security"],
        "bio": "Customer success lead focused on retention and expansion.",
        "availability": "Full-time"
    },
    {
        "id": "collab_43",
        "name": "Emily Chen",
        "role": "Finance & Operations",
        "skills": ["Clinical ops", "IRB", "HIPAA", "Coordination"],
        "interests": ["Healthcare", "Clinical research", "Compliance"],
        "bio": "Clinical research coordinator who navigates approvals and operations.",
        "availability": "Part-time"
    },
    {
        "id": "collab_44",
        "name": "Marcus Lee",
        "role": "Sales & Business Development",
        "skills": ["Partnerships", "Pitching", "Outbound", "Negotiation"],
        "interests": ["FinTech", "Developer tools", "AI"],
        "bio": "Partnerships lead connecting early teams with design partners.",
        "availability": "Full-time"
    },
    {
        "id": "collab_45",
        "name": "Hannah Brooks",
        "role": "Designer",
        "skills": ["UX Writing", "Information architecture", "Prototyping", "Figma"],
        "interests": ["Education", "Healthcare", "Accessibility"],
        "bio": "UX writer who clarifies complex flows with simple language.",
        "availability": "Contract"
    },
    {
        "id": "collab_46",
        "name": "Derek Wong",
        "role": "Marketing & Growth",
        "skills": ["Content strategy", "Social", "Email", "Lifecycle"],
        "interests": ["Productivity", "SaaS", "Remote work"],
        "bio": "Lifecycle marketer crafting narratives that convert.",
        "availability": "Part-time"
    },
    {
        "id": "collab_47",
        "name": "Amara Yusuf",
        "role": "Biomedical Engineer",
        "skills": ["Signal processing", "Prototyping", "Python", "Wearables"],
        "interests": ["Diagnostics", "Health monitoring", "Accessibility"],
        "bio": "Biomedical engineer prototyping patient-centered devices.",
        "availability": "Contract"
    },
    {
        "id": "collab_48",
        "name": "Victor Huang",
        "role": "Hardware Engineer",
        "skills": ["PCB", "Firmware", "C", "BLE"],
        "interests": ["IoT", "Robotics", "Wearables"],
        "bio": "Hardware engineer building connected products end-to-end.",
        "availability": "Part-time"
    },
    {
        "id": "collab_49",
        "name": "Jasmine Shah",
        "role": "QA Engineer",
        "skills": ["Manual QA", "Cypress", "Playwright", "Test plans"],
        "interests": ["Healthcare", "Finance", "Compliance"],
        "bio": "QA engineer ensuring quality in regulated environments.",
        "availability": "Full-time"
    },
    {
        "id": "collab_50",
        "name": "Diego Ramos",
        "role": "Data Engineer",
        "skills": ["Airflow", "dbt", "Snowflake", "Kafka", "Python"],
        "interests": ["Analytics", "Streaming", "Observability"],
        "bio": "Data engineer building reliable pipelines and metrics.",
        "availability": "Full-time"
    },
    {
        "id": "collab_51",
        "name": "Natalie Perez",
        "role": "Finance & Operations",
        "skills": ["Clinical trials", "Site onboarding", "Budgeting", "Vendor mgmt"],
        "interests": ["Healthcare", "Compliance", "Patient outcomes"],
        "bio": "Clinical trial coordinator aligning sites and sponsors.",
        "availability": "Part-time"
    },
    {
        "id": "collab_52",
        "name": "Owen Carter",
        "role": "Marketing & Growth",
        "skills": ["Community", "Events", "Content", "Ambassador programs"],
        "interests": ["Open source", "Education", "HealthTech"],
        "bio": "Community organizer building programs that activate users.",
        "availability": "Part-time"
    },
    {
        "id": "collab_53",
        "name": "Rita Gomez",
        "role": "Finance & Operations",
        "skills": ["Grant writing", "Budgets", "Reporting", "Compliance"],
        "interests": ["Nonprofit", "Social impact", "Healthcare"],
        "bio": "Grant writer helping early teams fund their missions.",
        "availability": "Contract"
    },
    {
        "id": "collab_54",
        "name": "Alan Wright",
        "role": "Finance & Operations",
        "skills": ["Contracts", "Privacy", "Terms", "Risk"],
        "interests": ["Security", "Healthcare", "FinTech"],
        "bio": "Legal counsel simplifying contracts for startups.",
        "availability": "Advisory"
    },
    {
        "id": "collab_55",
        "name": "Lina Torres",
        "role": "Marketing & Growth",
        "skills": ["Content", "PR", "Narratives", "Video"],
        "interests": ["Climate", "HealthTech", "Community"],
        "bio": "Journalist-turned-marketer crafting credible stories.",
        "availability": "Part-time"
    },
    {
        "id": "collab_56",
        "name": "Ravi Iyer",
        "role": "Product Manager",
        "skills": ["Program mgmt", "Roadmaps", "Metrics", "Stakeholders"],
        "interests": ["Education", "AI", "SaaS"],
        "bio": "Program manager turning strategy into execution.",
        "availability": "Full-time"
    },
    {
        "id": "collab_57",
        "name": "Noah Brooks",
        "role": "Product Manager",
        "skills": ["Zero-to-one", "Research", "User testing", "MVPs"],
        "interests": ["Social impact", "Community", "HealthTech"],
        "bio": "Nonprofit founder exploring tech for impact.",
        "availability": "Part-time"
    },
    {
        "id": "collab_58",
        "name": "Amina Ali",
        "role": "Data Scientist",
        "skills": ["Research", "Python", "Stats", "Surveys"],
        "interests": ["Public policy", "HealthTech", "Education"],
        "bio": "Research assistant translating data into insight.",
        "availability": "Part-time"
    },
    {
        "id": "collab_59",
        "name": "Peter Zhang",
        "role": "Sales & Business Development",
        "skills": ["Outreach", "Cold email", "Discovery", "CRM"],
        "interests": ["SaaS", "Community", "DevTools"],
        "bio": "Outbound specialist booking meetings for early teams.",
        "availability": "Contract"
    },
    {
        "id": "collab_60",
        "name": "Camila Rivera",
        "role": "Finance & Operations",
        "skills": ["Community health", "Outreach", "Coordination", "Surveys"],
        "interests": ["Healthcare", "Public health", "Policy"],
        "bio": "Community health worker connecting with underserved populations.",
        "availability": "Part-time"
    },
    # === More Diverse Profiles for Richer Demo ===
    # Climate Tech
    {
        "id": "collab_61",
        "name": "Sofia Martinez",
        "role": "Product Manager",
        "skills": ["Sustainability metrics", "Carbon accounting", "Product strategy"],
        "interests": ["Climate tech", "Carbon markets", "Circular economy"],
        "bio": "Climate-focused PM helping companies measure carbon footprint.",
        "availability": "Available"
    },
    {
        "id": "collab_62",
        "name": "Chen Wei",
        "role": "Data Scientist",
        "skills": ["Geospatial analysis", "Climate modeling", "Python"],
        "interests": ["Climate change", "Environmental monitoring", "Satellite data"],
        "bio": "Using satellite data and ML to track environmental impacts.",
        "availability": "Available"
    },
    # Legal Tech
    {
        "id": "collab_63",
        "name": "Priya Sharma",
        "role": "Product Manager",
        "skills": ["Legal workflows", "Compliance", "B2B SaaS"],
        "interests": ["Legal tech", "Access to justice", "Automation"],
        "bio": "Former paralegal building tools to democratize legal services.",
        "availability": "Available"
    },
    # Agriculture Tech
    {
        "id": "collab_64",
        "name": "Amara Okafor",
        "role": "Data Scientist",
        "skills": ["Computer vision", "Crop monitoring", "IoT", "ML"],
        "interests": ["Agriculture", "Food security", "Precision farming"],
        "bio": "Building AI systems to help farmers optimize yields.",
        "availability": "Available"
    },
    {
        "id": "collab_65",
        "name": "Lucas Silva",
        "role": "Hardware Engineer",
        "skills": ["Sensors", "Embedded systems", "LoRaWAN"],
        "interests": ["Agriculture", "IoT", "Sustainability"],
        "bio": "Designing low-power IoT sensors for farm monitoring.",
        "availability": "Available"
    },
    # Mental Health Tech
    {
        "id": "collab_66",
        "name": "Dr. Sarah Cohen",
        "role": "Product Manager",
        "skills": ["Clinical psychology", "Digital therapeutics", "User research"],
        "interests": ["Mental health", "Therapy", "Wellness"],
        "bio": "Licensed psychologist building evidence-based mental health tools.",
        "availability": "Available"
    },
    {
        "id": "collab_67",
        "name": "Kevin Nguyen",
        "role": "Designer",
        "skills": ["UX research", "Accessibility", "Design for health"],
        "interests": ["Mental wellness", "Healthcare", "Inclusive design"],
        "bio": "Designing compassionate interfaces for sensitive health topics.",
        "availability": "Available"
    },
    # Supply Chain
    {
        "id": "collab_68",
        "name": "Fatou Diallo",
        "role": "Software Engineer",
        "skills": ["Logistics optimization", "Python", "GraphQL"],
        "interests": ["Supply chain", "Last-mile delivery", "Automation"],
        "bio": "Built route optimization for 10K+ deliveries/day.",
        "availability": "Available"
    },
    # Creator Economy
    {
        "id": "collab_69",
        "name": "Emma Rodriguez",
        "role": "Product Manager",
        "skills": ["Creator tools", "Monetization", "Community"],
        "interests": ["Creator economy", "Social media", "Influencers"],
        "bio": "Building tools to help creators monetize their audience.",
        "availability": "Available"
    },
    {
        "id": "collab_70",
        "name": "Tyler Chen",
        "role": "Software Engineer",
        "skills": ["Video processing", "CDN", "Streaming", "React"],
        "interests": ["Content creation", "Live streaming", "Media"],
        "bio": "Built live streaming infrastructure for millions of creators.",
        "availability": "Available"
    },
    # GovTech
    {
        "id": "collab_71",
        "name": "Maria Santos",
        "role": "Product Manager",
        "skills": ["Civic engagement", "Public policy", "Accessibility"],
        "interests": ["GovTech", "Democracy", "Public services"],
        "bio": "Designing digital services to make government accessible.",
        "availability": "Available"
    },
    # Space Tech
    {
        "id": "collab_72",
        "name": "Dr. Zara Patel",
        "role": "Data Scientist",
        "skills": ["Satellite imagery", "Signal processing", "Python"],
        "interests": ["Space", "Earth observation", "Remote sensing"],
        "bio": "Using satellite data for climate and disaster response.",
        "availability": "Available"
    },
    {
        "id": "collab_73",
        "name": "Alex Ivanov",
        "role": "Hardware Engineer",
        "skills": ["Aerospace", "CubeSats", "Embedded C", "RF"],
        "interests": ["Space exploration", "Satellites", "NewSpace"],
        "bio": "Designed avionics for 3 successful CubeSat missions.",
        "availability": "Available"
    },
    # Construction Tech
    {
        "id": "collab_74",
        "name": "Omar Hassan",
        "role": "Product Manager",
        "skills": ["Construction management", "BIM", "Workflows"],
        "interests": ["Construction", "Real estate", "PropTech"],
        "bio": "Former contractor building software for construction.",
        "availability": "Available"
    },
    # Music Tech
    {
        "id": "collab_75",
        "name": "Marcus Thompson",
        "role": "Software Engineer",
        "skills": ["Audio processing", "DSP", "C++"],
        "interests": ["Music production", "Audio tools", "Creators"],
        "bio": "Built audio plugins used by thousands of producers.",
        "availability": "Available"
    },
    # Insurance Tech
    {
        "id": "collab_76",
        "name": "Ahmed El-Sayed",
        "role": "Data Scientist",
        "skills": ["Actuarial science", "Risk modeling", "ML"],
        "interests": ["InsurTech", "Risk assessment", "Healthcare"],
        "bio": "Using ML to make insurance pricing fair and accurate.",
        "availability": "Available"
    },
    # Travel Tech
    {
        "id": "collab_77",
        "name": "Carlos Mendez",
        "role": "Software Engineer",
        "skills": ["Booking systems", "Payments", "React", "Node.js"],
        "interests": ["Travel", "Tourism", "Hospitality"],
        "bio": "Built booking platforms for hotels and tour operators.",
        "availability": "Available"
    },
    # Gaming
    {
        "id": "collab_78",
        "name": "Jake Morrison",
        "role": "Software Engineer",
        "skills": ["Unity", "Game design", "Multiplayer", "C#"],
        "interests": ["Gaming", "eSports", "Game dev"],
        "bio": "Indie game dev with 3 titles and 500K+ downloads.",
        "availability": "Available"
    },
    {
        "id": "collab_79",
        "name": "Aisha Bakare",
        "role": "Designer",
        "skills": ["Character design", "Animation", "3D modeling"],
        "interests": ["Gaming", "Art", "Interactive media"],
        "bio": "Game artist passionate about inclusive character design.",
        "availability": "Available"
    },
    # Nonprofit / Social Impact
    {
        "id": "collab_80",
        "name": "Rashid Abdullah",
        "role": "Product Manager",
        "skills": ["Social impact", "Community organizing", "Strategy"],
        "interests": ["Nonprofit", "Social good", "Education"],
        "bio": "Former nonprofit director building tech for social impact.",
        "availability": "Available"
    },
    # Web3 
    {
        "id": "collab_81",
        "name": "Kofi Mensah",
        "role": "Software Engineer",
        "skills": ["Solidity", "Smart contracts", "Web3.js", "DeFi"],
        "interests": ["Blockchain", "DeFi", "Financial inclusion"],
        "bio": "Building DeFi tools for underserved communities.",
        "availability": "Available"
    },
    {
        "id": "collab_82",
        "name": "Isabella Rossi",
        "role": "Product Manager",
        "skills": ["Tokenomics", "Community", "Web3 UX"],
        "interests": ["Web3", "DAOs", "Creator economy"],
        "bio": "Designing crypto products that make sense to normal people.",
        "availability": "Available"
    },
    # Specialized roles
    {
        "id": "collab_83",
        "name": "Sarah Johnson",
        "role": "Marketing & Growth",
        "skills": ["Technical writing", "Documentation", "DevRel"],
        "interests": ["Developer tools", "Open source", "Education"],
        "bio": "Technical writer making complex products understandable.",
        "availability": "Available"
    },
    {
        "id": "collab_84",
        "name": "Michael O'Brien",
        "role": "Sales & Business Development",
        "skills": ["Customer success", "Onboarding", "Retention"],
        "interests": ["B2B SaaS", "Customer experience"],
        "bio": "CS lead with 95%+ retention across 3 startups.",
        "availability": "Available"
    },
    {
        "id": "collab_85",
        "name": "Nadia Ivanova",
        "role": "QA Engineer",
        "skills": ["Test automation", "Selenium", "Python", "QA"],
        "interests": ["Software quality", "Testing", "Reliability"],
        "bio": "QA engineer passionate about shipping bug-free products.",
        "availability": "Available"
    },
    {
        "id": "collab_86",
        "name": "Taylor Brooks",
        "role": "Finance & Operations",
        "skills": ["HR", "Recruiting", "Culture", "People ops"],
        "interests": ["Company culture", "Diversity", "Leadership"],
        "bio": "People ops leader who built teams at hyper-growth startups.",
        "availability": "Available"
    },
    {
        "id": "collab_87",
        "name": "Javier Garcia",
        "role": "Software Engineer",
        "skills": ["CSS animations", "Framer Motion", "React"],
        "interests": ["UI engineering", "Design tools", "Web animations"],
        "bio": "Frontend specialist making products feel delightful.",
        "availability": "Available"
    },
    {
        "id": "collab_88",
        "name": "Alicia Washington",
        "role": "Designer",
        "skills": ["Accessibility", "WCAG", "Screen readers"],
        "interests": ["A11y", "Healthcare", "Education"],
        "bio": "Accessibility advocate ensuring products work for everyone.",
        "availability": "Available"
    },
    {
        "id": "collab_89",
        "name": "Ryan Park",
        "role": "Marketing & Growth",
        "skills": ["Growth hacking", "Viral loops", "A/B testing"],
        "interests": ["Consumer apps", "Growth", "Experimentation"],
        "bio": "Growth lead who achieved 40% MoM growth.",
        "availability": "Available"
    },
    {
        "id": "collab_90",
        "name": "Maya Johnson",
        "role": "Marketing & Growth",
        "skills": ["Community management", "Discord/Slack", "Events"],
        "interests": ["Web3", "Gaming", "Creator economy"],
        "bio": "Built and managed communities of 50K+ members.",
        "availability": "Available"
    },
    {
        "id": "collab_91",
        "name": "Tomás Ramirez",
        "role": "Designer",
        "skills": ["Product design", "User research", "Prototyping"],
        "interests": ["B2B SaaS", "Enterprise", "Productivity"],
        "bio": "Product designer solving complex workflow problems.",
        "availability": "Available"
    },
    {
        "id": "collab_92",
        "name": "Zainab Khan",
        "role": "Product Manager",
        "skills": ["Strategy", "Vision", "Fundraising", "Team building"],
        "interests": ["HealthTech", "AI", "Social impact"],
        "bio": "Serial entrepreneur. Exited a healthtech startup. Seeking co-founder.",
        "availability": "Available"
    },
    # === Auto-generated profiles ===
    {
        "id": "collab_93",
        "name": "Quinn Zhao",
        "role": "Data Scientist",
        "skills": ["PyTorch", "Computer Vision", "CNNs", "Transfer Learning"],
        "interests": ["Food Tech", "Data Tools"],
        "bio": "MLOps engineer making ML systems production-ready.",
        "availability": "Available"
    },
    {
        "id": "collab_94",
        "name": "Felix Green",
        "role": "Data Scientist",
        "skills": ["PyTorch", "Computer Vision", "CNNs", "Transfer Learning"],
        "interests": ["AI/ML", "Privacy"],
        "bio": "ML engineer deploying models that drive business value.",
        "availability": "Available"
    },
    {
        "id": "collab_95",
        "name": "Carlos Yang",
        "role": "Designer",
        "skills": ["Framer", "Motion Design", "Micro-interactions", "CSS"],
        "interests": ["Diversity", "Privacy", "Climate Tech"],
        "bio": "Design systems architect building scalable component libraries.",
        "availability": "Available"
    },
    {
        "id": "collab_96",
        "name": "Sofia Johnson",
        "role": "Data Scientist",
        "skills": ["R", "Statistics", "Hypothesis Testing", "Causal Inference"],
        "interests": ["Developer Tools", "Music"],
        "bio": "MLOps engineer making ML systems production-ready.",
        "availability": "Part-time"
    },
    {
        "id": "collab_97",
        "name": "Winston Nelson",
        "role": "Sales & Business Development",
        "skills": ["Sales Ops", "CRM", "Salesforce", "Pipeline Management"],
        "interests": ["Workflow Automation", "Nonprofit", "Travel"],
        "bio": "SDR turned AE with 8 years of quota crushing.",
        "availability": "Available"
    },
    {
        "id": "collab_98",
        "name": "Viktor Usman",
        "role": "Data Scientist",
        "skills": ["Python", "Pandas", "NumPy", "Scikit-learn", "Jupyter"],
        "interests": ["Drones", "Public Health", "Food Tech"],
        "bio": "MLOps engineer making ML systems production-ready.",
        "availability": "Advisory"
    },
    {
        "id": "collab_99",
        "name": "Lucia Santos",
        "role": "Designer",
        "skills": ["User Research", "Journey Mapping", "Personas", "A/B Testing"],
        "interests": ["Wellness", "Robotics", "Diversity"],
        "bio": "Brand designer crafting memorable identities.",
        "availability": "Available"
    },
    {
        "id": "collab_100",
        "name": "Gabriel Yamamoto",
        "role": "Software Engineer",
        "skills": ["Go", "gRPC", "Kubernetes", "Docker"],
        "interests": ["Democracy", "Legal Tech", "Food Tech"],
        "bio": "Full-stack developer with 6 years building scalable web applications.",
        "availability": "Part-time"
    },
    {
        "id": "collab_101",
        "name": "Nina Zhao",
        "role": "Sales & Business Development",
        "skills": ["Partnerships", "Channel Sales", "Alliances", "Co-selling"],
        "interests": ["Economic Justice", "Security"],
        "bio": "Revenue leader who's built teams from 0 to 100 reps.",
        "availability": "Available"
    },
    {
        "id": "collab_102",
        "name": "Rosa Johnson",
        "role": "Sales & Business Development",
        "skills": ["Enterprise Sales", "MEDDIC", "Solution Selling", "Demos"],
        "interests": ["Agriculture", "Mental Health", "Collaboration"],
        "bio": "Inbound sales specialist converting high-intent leads.",
        "availability": "Available"
    },
    {
        "id": "collab_103",
        "name": "Xander Ramos",
        "role": "Designer",
        "skills": ["Adobe XD", "Illustration", "Brand Identity", "Typography"],
        "interests": ["E-commerce", "Drones"],
        "bio": "Visual designer with an eye for detail and storytelling.",
        "availability": "Part-time"
    },
    {
        "id": "collab_104",
        "name": "Felix Ramos",
        "role": "Marketing & Growth",
        "skills": ["Content Marketing", "SEO", "Copywriting", "Blogging"],
        "interests": ["Developer Tools", "Music", "FinTech"],
        "bio": "Brand marketer crafting memorable stories that resonate.",
        "availability": "Part-time"
    },
    {
        "id": "collab_105",
        "name": "Xiao Berg",
        "role": "Designer",
        "skills": ["Sketch", "InVision", "Wireframing", "UI Animation"],
        "interests": ["Creator Economy", "Workflow Automation", "Quantum Computing"],
        "bio": "Design lead who's mentored 15 designers.",
        "availability": "Contract"
    },
    {
        "id": "collab_106",
        "name": "Wei Ibrahim",
        "role": "Sales & Business Development",
        "skills": ["Sales Enablement", "Training", "Playbooks", "Documentation"],
        "interests": ["Quantum Computing", "Workflow Automation", "Policy"],
        "bio": "Enterprise AE who's closed 3 six-figure deals.",
        "availability": "Available"
    },
    {
        "id": "collab_107",
        "name": "Yasmin Abbas",
        "role": "Sales & Business Development",
        "skills": ["Outbound", "Cold Email", "Prospecting", "Lead Generation"],
        "interests": ["E-commerce", "Supply Chain", "Open Source"],
        "bio": "Revenue leader who's built teams from 0 to 5 reps.",
        "availability": "Available"
    },
    {
        "id": "collab_108",
        "name": "Jorge Lopez",
        "role": "Product Manager",
        "skills": ["A/B Testing", "Analytics", "SQL", "Data-Driven Decisions"],
        "interests": ["Mental Health", "Analytics", "FinTech"],
        "bio": "AI/ML PM translating research into product value.",
        "availability": "Available"
    },
    {
        "id": "collab_109",
        "name": "Rosa Qureshi",
        "role": "Designer",
        "skills": ["Design Ops", "Documentation", "Design Tokens", "Collaboration"],
        "interests": ["Climate Tech", "B2B SaaS"],
        "bio": "Product designer passionate about creating intuitive user experiences.",
        "availability": "Advisory"
    },
    {
        "id": "collab_110",
        "name": "Winston Smith",
        "role": "Designer",
        "skills": ["User Research", "Journey Mapping", "Personas", "A/B Testing"],
        "interests": ["Education", "Gaming", "Privacy"],
        "bio": "Visual designer with an eye for detail and storytelling.",
        "availability": "Available"
    },
    {
        "id": "collab_111",
        "name": "Vera Anderson",
        "role": "Designer",
        "skills": ["3D Design", "Blender", "3D Modeling", "Rendering"],
        "interests": ["AI/ML", "Social Media", "Policy"],
        "bio": "UX researcher who loves uncovering user needs through data.",
        "availability": "Contract"
    },
    {
        "id": "collab_112",
        "name": "Isla Quinn",
        "role": "Designer",
        "skills": ["3D Design", "Blender", "3D Modeling", "Rendering"],
        "interests": ["EdTech", "Gaming", "Diversity"],
        "bio": "UX researcher who loves uncovering user needs through data.",
        "availability": "Available"
    },
])


def create_embedding(text):
    """Create embedding for text."""
    return embedding_model.encode(text).tolist()


def seed_database():
    """Seed ChromaDB with fake collaborators."""
    try:
        # Delete existing collection if it exists
        try:
            chroma_client.delete_collection(name="collaborators")
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
                "availability": "Available",  # All mock users start as available
                "team_id": "None"  # Not in any team initially
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