import os
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import json

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB client (disable telemetry noise)
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(anonymized_telemetry=False)
)


def get_chat_response(message, chat_history):
    """
    Get a real-time chat response using Groq's llama-3.1-8b-instant model.
    Optimized to gather info in 3-4 messages max.
    """
    messages = [
        {
            "role": "system",
            "content": """You are Synergy, a concise slot-filling assistant. Collect info to build a profile and then stop.
TARGET SLOTS (in priority order):
1) Skills (technical abilities)
2) Interests/domains (e.g., HealthTech, AI)
3) Looking_for (role needed) — OPTIONAL if user is unsure
4) Name — OPTIONAL

BEHAVIOR RULES:
- FIRST: Check if the user's message contains BOTH skills AND interests/domain.
- If YES (even on first message), say EXACTLY: "Great, I have everything I need!"
- If NO, ask at most ONE short question (<= 12 words) about what's missing.
- Never ask for info already provided.
- If user is unsure about role or says "any/unsure/open": accept it and proceed.
- Do not add explanations, checklists, or summaries. Keep replies minimal.

EXAMPLES:
User: "Product designer with fintech experience. Want to build a B2B payments platform, need an engineer who knows backend systems."
You: Great, I have everything I need!

User: "I'm Alex, Python/React, into HealthTech/AI, not sure what role I need"
You: Great, I have everything I need!

User: "Founder with a productivity idea, need two more people"
You: What skills do you have?

User: "CS student, love AI agents, full-stack; open to any role"
You: What domains interest you most?
"""
        }
    ]
    
    # Add chat history
    messages.extend(chat_history)
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2,  # Lower for more consistent tracking
            max_tokens=30  # Strictly short responses
        )
        return response.choices[0].message.content
    except Exception as e:
        return "I'm having trouble responding right now. Could you try again?"


def extract_user_profile(chat_transcript):
    """
    Extract structured profile from chat transcript using Groq's llama-3.3-70b-versatile model with JSON mode.
    Optimized to handle long, informal Slack-style intros or multi-turn chats.
    """
    prompt = f"""Extract a JSON profile from the conversation or intro text.
Required keys (always present):
- name: string
- skills: array of strings
- interests: array of strings
- looking_for: string (the role they want, e.g., "Designer", "Software Engineer", "PM", or "Collaborator")

Optional keys (include when you can infer):
- roles_offered: array of strings
- roles_needed: array of strings
- project_idea: string (one-liner if founder mentions an idea/space)
- commitment: string (e.g., "weekend", "hackathon", "10-15 hrs/wk")
- timezone: string or region
- teammates_count: integer (number on their existing team, if mentioned)
- links: object with any of: linkedin, github, website
- education: string or short array (school/degree)
- achievements: array of short strings (wins/awards)
- experience: array of short strings (projects worked on, internships, notable work)

Rules:
- The input may be a single long intro (Slack-style) or a dialogue. Parse either.
- Normalize skills to short tokens (e.g., "Python", "React", "RAG", "LLM", "UI/UX").
- If no explicit "looking_for" is stated, infer ("Collaborator" or likely role) from context.
- Return ONLY valid JSON.

Conversation or Intro:
{chat_transcript}

Return ONLY valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Updated to current model
            messages=[
                {"role": "system", "content": "You are a JSON extraction expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        raw_content = response.choices[0].message.content
        profile = json.loads(raw_content)
        
        # Ensure all required fields exist
        if not profile.get("name"):
            profile["name"] = "User"
        if not profile.get("skills"):
            profile["skills"] = ["General"]
        if not profile.get("interests"):
            profile["interests"] = ["Collaboration"]
        if not profile.get("looking_for"):
            profile["looking_for"] = "Collaborator"
            
        return profile
    except json.JSONDecodeError as e:
        return {
            "name": "User",
            "skills": ["General"],
            "interests": ["Collaboration"],
            "looking_for": "Software Engineer"
        }
    except Exception as e:
        return {
            "name": "User",
            "skills": ["General"],
            "interests": ["Collaboration"],
            "looking_for": "Software Engineer"
        }


def create_embedding(text):
    """
    Create embedding using sentence-transformers.
    """
    return embedding_model.encode(text).tolist()


def find_collaborators(user_profile):
    """
    Find matching collaborators from ChromaDB based on user profile.
    """
    try:
        # Get or create collection
        collection = chroma_client.get_collection(name="collaborators")
        
        # Helper: canonicalize role labels to match our DB roles
        def _canon_role(raw: str) -> str:
            if not raw:
                return ''
            s = str(raw).strip().lower()
            direct = {
                'software engineer': 'Software Engineer',
                'engineer': 'Software Engineer',
                'developer': 'Software Engineer',
                'swe': 'Software Engineer',
                'coder': 'Software Engineer',
                'frontend': 'Software Engineer',
                'backend': 'Software Engineer',
                'fullstack': 'Software Engineer',
                'full-stack': 'Software Engineer',
                'ux': 'Designer',
                'ui': 'Designer',
                'ui/ux': 'Designer',
                'designer': 'Designer',
                'product manager': 'Product Manager',
                'pm': 'Product Manager',
                'product': 'Product Manager',
                'data scientist': 'Data Scientist',
                'ml engineer': 'Data Scientist',
                'ai engineer': 'Data Scientist',
                'finance expert': 'Finance & Operations',
                'marketing': 'Marketing & Growth',
                'growth': 'Marketing & Growth',
                'sales': 'Sales & Business Development',
                'business development': 'Sales & Business Development',
                'biz dev': 'Sales & Business Development',
                'finance': 'Finance & Operations',
                'operations': 'Finance & Operations',
                'ops': 'Finance & Operations',
            }
            if s in direct:
                return direct[s]
            if any(k in s for k in ['engineer', 'developer', 'dev', 'coder']):
                return 'Software Engineer'
            if any(k in s for k in ['design', 'figma', 'ux', 'ui']):
                return 'Designer'
            if 'product' in s or s == 'pm':
                return 'Product Manager'
            if any(k in s for k in ['data', 'ml', 'machine learning', 'ai']):
                return 'Data Scientist'
            if any(k in s for k in ['marketing', 'growth']):
                return 'Marketing & Growth'
            if any(k in s for k in ['sales', 'business', 'partnership']):
                return 'Sales & Business Development'
            if any(k in s for k in ['finance', 'operation', 'ops']):
                return 'Finance & Operations'
            return raw.strip()

        # Create query embedding from desired roles (roles_needed or looking_for) and interests
        roles_needed = user_profile.get('roles_needed', []) or []
        roles_needed_canon = [ _canon_role(r) for r in roles_needed if r ]
        looking_for_raw = user_profile.get('looking_for', 'collaborator')
        looking_for_canon = _canon_role(looking_for_raw)
        # Only use known roles for filtering/targeting; treat others as generic
        known_roles = {
            'Software Engineer','Designer','Product Manager','Data Scientist',
            'Marketing & Growth','Sales & Business Development','DevOps Engineer',
            'Security Engineer','Finance & Operations','Hardware Engineer',
            'Biomedical Engineer','QA Engineer','Data Engineer'
        }
        roles_needed_canon = [r for r in roles_needed_canon if r in known_roles]
        lf_for_filter = looking_for_canon if looking_for_canon in known_roles else ''
        roles_part = ' '.join(roles_needed_canon) if roles_needed_canon else lf_for_filter
        # Include interests and skills to improve semantic recall
        query_text = f"{roles_part} {' '.join(user_profile.get('interests', []))} {' '.join(user_profile.get('skills', []))}"
        query_embedding = create_embedding(query_text)
        
        # Build where clause: prefer broad availability; narrow by role only if explicitly requested
        where_clause = {"availability": {"$in": ["Available", "Full-time", "Part-time", "Contract", "Advisory", "Open"]}}
        looking_for = lf_for_filter.strip() if isinstance(lf_for_filter, str) else ''
        role_filters = []

        # Add OR filters from roles_needed array
        if isinstance(roles_needed_canon, list):
            for r in roles_needed_canon:
                r = str(r).strip()
                if r:
                    role_filters.append({"role": {"$eq": r}})

        # Add filter from looking_for if it's not generic
        generic_terms = {"collaborator", "any", "anyone", "any role", "teammate", "partner"}
        if looking_for and looking_for.lower() not in generic_terms:
            if looking_for in known_roles:
                role_filters.append({"role": {"$eq": looking_for}})

        if role_filters:
            where_clause = {
                "$and": [
                    {"availability": {"$in": ["Available", "Full-time", "Part-time", "Contract", "Advisory", "Open"]}},
                    {"$or": role_filters}
                ]
            }
        else:
            # Heuristic: if no explicit target roles, infer complimentary roles from user's skills
            skills_lower = ' '.join([s.lower() for s in user_profile.get('skills', [])])
            inferred_role = None
            if any(w in skills_lower for w in ['python', 'javascript', 'react', 'node', 'c++', 'java', 'backend', 'frontend', 'fullstack', 'devops']):
                inferred_role = 'Software Engineer'
            elif any(w in skills_lower for w in ['design', 'figma', 'ui', 'ux', 'sketch', 'adobe']):
                inferred_role = 'Designer'
            elif any(w in skills_lower for w in ['product', 'roadmap', 'pm', 'strategy', 'analytics']):
                inferred_role = 'Product Manager'
            elif any(w in skills_lower for w in ['data', 'ml', 'machine learning', 'analytics', 'sql', 'pytorch', 'tensorflow']):
                inferred_role = 'Data Scientist'

            default_targets = []
            if inferred_role == 'Software Engineer':
                default_targets = ['Designer', 'Product Manager']
            elif inferred_role == 'Designer':
                default_targets = ['Software Engineer', 'Product Manager']
            elif inferred_role == 'Product Manager':
                default_targets = ['Software Engineer', 'Designer']
            elif inferred_role == 'Data Scientist':
                default_targets = ['Software Engineer', 'Product Manager']

            # For generic cases, don't hard-filter on role; rely on semantic search + re-ranking
            where_clause = {"availability": {"$in": ["Available", "Full-time", "Part-time", "Contract", "Advisory", "Open"]}}
        
        # Prepare token functions (needed for domain logic)
        def _tokens(s):
            if not s:
                return []
            if isinstance(s, list):
                toks = []
                for x in s:
                    x = str(x).lower()
                    for ch in [',', '/', '|', '&']:
                        x = x.replace(ch, ' ')
                    toks.extend([t for t in x.split() if t])
                return toks
            s = str(s).lower()
            for ch in [',', '/', '|', '&']:
                s = s.replace(ch, ' ')
            return [t for t in s.split() if t]

        # Normalize topic tokens to reduce synonym mismatch
        def _norm_topics(tokens):
            aliases = {
                'healthtech': 'healthcare', 'health': 'healthcare', 'medtech': 'healthcare', 'medical': 'healthcare',
                'healthpolicy': 'healthcare', 'policy': 'healthcare',
                'fintech': 'finance', 'fin': 'finance', 'financial': 'finance', 'finsec': 'security', 'financialsecurity': 'security', 'finsecurity': 'security',
                'ai': 'ai', 'ml': 'ai', 'machine': 'ai', 'machinelearning': 'ai', 'llm': 'ai', 'agents': 'ai',
                'edtech': 'education', 'ed': 'education',
                'climatetech': 'climate', 'climate': 'climate',
                'robotics': 'robotics', 'drone': 'robotics', 'drones': 'robotics',
                'security': 'security', 'infosec': 'security', 'cyber': 'security'
            }
            out = []
            for t in tokens:
                t2 = aliases.get(t, t)
                out.append(t2)
            return set(out)

        user_interest_toks = _norm_topics(set(_tokens(user_profile.get('interests', []))))
        user_skills_toks = set(_tokens(user_profile.get('skills', [])))
        
        # Query ChromaDB with filters
        try:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=50,  # Larger pool for robust re-ranking
                where=where_clause,
                include=["metadatas"]
            )
            
            # If no matches with role filter, try without role but keep availability filter
            if not results['metadatas'] or len(results['metadatas'][0]) == 0:
                if looking_for:
                    print(f"No exact role matches for '{looking_for}', trying semantic search...")
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=50,
                        where={"availability": {"$in": ["Available", "Full-time", "Part-time", "Contract", "Advisory", "Open"]}},
                        include=["metadatas"]
                    )
            # Final fallback: fully unfiltered semantic search
            if not results['metadatas'] or len(results['metadatas'][0]) == 0:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=50,
                    include=["metadatas"]
                )
        except Exception as query_error:
            print(f"Query with filter failed: {query_error}, trying without filter...")
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=20,
                include=["metadatas"]
            )
        
        # Gather candidate pool for fallback and re-ranking
        cand_pool = []
        try:
            if results and results.get('metadatas') and len(results['metadatas']) > 0:
                cand_pool = results['metadatas'][0] or []
        except Exception:
            cand_pool = []

        # Deterministic re-ranker for better demo results (functions already defined above)

        # Infer user's own role for complementarity
        skills_lower = ' '.join([s.lower() for s in user_profile.get('skills', [])])
        if any(w in skills_lower for w in ['python', 'javascript', 'react', 'node', 'c++', 'java', 'backend', 'frontend', 'fullstack', 'devops']):
            user_role = 'Software Engineer'
        elif any(w in skills_lower for w in ['design', 'figma', 'ui', 'ux', 'sketch', 'adobe']):
            user_role = 'Designer'
        elif any(w in skills_lower for w in ['product', 'roadmap', 'pm', 'strategy', 'analytics']):
            user_role = 'Product Manager'
        elif any(w in skills_lower for w in ['data', 'ml', 'machine learning', 'analytics', 'sql', 'pytorch', 'tensorflow']):
            user_role = 'Data Scientist'
        else:
            user_role = 'Other'

        # Determine target and complementary roles for scoring
        generic_terms = {"collaborator", "any", "anyone", "any role", "teammate", "partner"}
        target_roles = []
        if roles_needed_canon:
            target_roles = roles_needed_canon
        elif looking_for and looking_for.lower() not in generic_terms:
            target_roles = [looking_for]

        complement_roles = []
        if user_role == 'Software Engineer':
            complement_roles = ['Designer', 'Product Manager', 'Data Scientist']
        elif user_role == 'Designer':
            complement_roles = ['Software Engineer', 'Product Manager']
        elif user_role == 'Product Manager':
            complement_roles = ['Software Engineer', 'Designer']
        elif user_role == 'Data Scientist':
            complement_roles = ['Software Engineer', 'Product Manager', 'Designer']

        scored = []
        core_roles = {"Software Engineer", "Designer", "Product Manager", "Data Scientist", "DevOps Engineer", "Security Engineer"}

        # Domain-driven role bonuses
        domain_bonus = {}
        if 'finance' in user_interest_toks:
            domain_bonus['Finance & Operations'] = domain_bonus.get('Finance & Operations', 0) + 1.2
            domain_bonus['Sales & Business Development'] = domain_bonus.get('Sales & Business Development', 0) + 0.6
        if 'healthcare' in user_interest_toks:
            domain_bonus['Designer'] = domain_bonus.get('Designer', 0) + 0.3
            domain_bonus['Data Scientist'] = domain_bonus.get('Data Scientist', 0) + 0.3
            domain_bonus['Software Engineer'] = domain_bonus.get('Software Engineer', 0) + 0.2
        if 'ai' in user_interest_toks:
            domain_bonus['Data Scientist'] = domain_bonus.get('Data Scientist', 0) + 0.6
            domain_bonus['Software Engineer'] = domain_bonus.get('Software Engineer', 0) + 0.5
            domain_bonus['Product Manager'] = domain_bonus.get('Product Manager', 0) + 0.2
        if 'education' in user_interest_toks:
            domain_bonus['Product Manager'] = domain_bonus.get('Product Manager', 0) + 0.4
            domain_bonus['Designer'] = domain_bonus.get('Designer', 0) + 0.2
        if 'security' in user_interest_toks:
            domain_bonus['Security Engineer'] = domain_bonus.get('Security Engineer', 0) + 0.8
            domain_bonus['Software Engineer'] = domain_bonus.get('Software Engineer', 0) + 0.3
        if 'robotics' in user_interest_toks:
            domain_bonus['Software Engineer'] = domain_bonus.get('Software Engineer', 0) + 0.6
            domain_bonus['Data Scientist'] = domain_bonus.get('Data Scientist', 0) + 0.4
        if results and results.get('metadatas') and len(results['metadatas']) > 0:
            user_name_lower = (user_profile.get('name') or '').strip().lower()
            for md in results['metadatas'][0]:
                # Skip self-matches by name
                try:
                    cand_name = (md.get('name') or '').strip().lower()
                    if user_name_lower and cand_name and cand_name == user_name_lower:
                        continue
                except Exception:
                    pass
                c_role = _canon_role(md.get('role', ''))
                c_interest_toks = _norm_topics(set(_tokens(md.get('interests', ''))))
                c_skills_toks = set(_tokens(md.get('skills', '')))
                c_bio = (md.get('bio') or '').lower()

                score = 0.0
                
                # ROLE MATCHING: Strongly prioritize complementary skills for team building
                if c_role in target_roles:
                    score += 10.0  # Explicitly requested role
                elif c_role in complement_roles:
                    score += 6.0   # Complementary role (KEY for team building)
                elif c_role == user_role:
                    score += 0.5   # Same role (less useful for a founder building a team)
                else:
                    score += 2.0   # Other roles (business, ops, etc.)

                # DOMAIN OVERLAP: Match on shared interests/domain (critical for co-founders)
                overlap = len(user_interest_toks & c_interest_toks)
                if user_interest_toks:
                    score += 3.0 * (overlap / max(1, len(user_interest_toks)))
                if overlap == 0:
                    score -= 1.0  # Penalize if no shared interests

                # Domain-driven role bonus
                score += domain_bonus.get(c_role, 0)

                # Bio mention boost
                for kw in user_interest_toks:
                    if kw in c_bio:
                        score += 0.3

                # SKILLS DIVERSITY: Penalize skill overlap (we want different skills!)
                if user_skills_toks and c_skills_toks:
                    skill_overlap = len(user_skills_toks & c_skills_toks)
                    total_skills = len(user_skills_toks | c_skills_toks)
                    overlap_ratio = skill_overlap / max(1, total_skills)
                    score -= 2.0 * overlap_ratio  # Penalize skill similarity

                # Strong penalty for same role when building a team
                if not target_roles and c_role == user_role:
                    score -= 2.0  # You don't need another person with your exact role

                scored.append((score, md, c_role))

        # Sort and apply a category-aware selection for better demo diversity
        scored.sort(key=lambda x: x[0], reverse=True)

        target_list = [md for s, md, r in scored if r in target_roles]
        complement_list = [md for s, md, r in scored if r in complement_roles]
        peer_list = [md for s, md, r in scored if r == user_role]
        other_list = [md for s, md, r in scored if md not in target_list and md not in complement_list and md not in peer_list]

        matches = []
        def _take(src, k):
            for item in src:
                if item in matches:
                    continue
                matches.append(item)
                if len(matches) >= 5:  # Stop at 5 total matches
                    return

        # PRIORITIZE COMPLEMENTARY ROLES for team building
        if target_roles:
            _take(target_list, 2)        # Explicitly requested roles first
            _take(complement_list, 2)    # Then complementary roles
            _take(other_list, 3)         # Business/ops roles
            _take(peer_list, 5)          # Same role last (least useful)
        else:
            # Generic "looking for collaborator" - assume team building
            _take(complement_list, 3)    # Complementary roles FIRST
            _take(other_list, 1)         # Business/ops/marketing
            _take(peer_list, 1)          # Maybe 1 same role if they have unique skills

        # Fallback: if re-ranker yields nothing but we have candidates, return top few raw
        if not matches and cand_pool:
            return cand_pool[:5]

        # Final fallback: fetch any available collaborators
        if not matches:
            try:
                raw = collection.get(where={"availability": {"$eq": "Available"}}, include=["metadatas"], limit=10)
                if raw and raw.get('metadatas'):
                    return raw['metadatas'][:5]
            except Exception:
                pass

        # Ultimate fallback: compute simple heuristic over all collaborators
        if not matches:
            try:
                all_collabs = get_all_collaborators()
                user_name_lower = (user_profile.get('name') or '').strip().lower()
                interests_join = ' '.join(user_profile.get('interests', [])).lower()
                skills_join = ' '.join(user_profile.get('skills', [])).lower()
                def score_cand(c):
                    try:
                        name = (c.get('name') or '').strip().lower()
                        if user_name_lower and name == user_name_lower:
                            return -1
                        cint = (c.get('interests') or '').lower()
                        cskills = (c.get('skills') or '').lower()
                        d = 0
                        for tok in interests_join.split():
                            if tok and tok in cint:
                                d += 2
                        for tok in skills_join.split():
                            if tok and tok in cskills:
                                d += 1
                        return d
                    except Exception:
                        return 0
                ranked = sorted(all_collabs, key=score_cand, reverse=True)
                return ranked[:5]
            except Exception:
                pass

        return matches
    except Exception as e:
        print(f"Error finding collaborators: {e}")
        # Emergency fallback: return SOMETHING
        try:
            collection = chroma_client.get_collection(name="collaborators")
            emergency = collection.get(limit=5, include=["metadatas"])
            if emergency and emergency.get('metadatas'):
                return emergency['metadatas'][:5]
        except:
            pass
        return []


# ============================================================================
# Database Query Helper Functions
# ============================================================================

def build_team_suggestions(user_profile, matches):
    """
    Build small team suggestions (2–3 people) from the candidate matches.
    Returns a list of suggestions, each with members (subset of matches).
    """
    try:
        # Determine user's own role from skills
        skills_lower = ' '.join([s.lower() for s in user_profile.get('skills', [])])
        if any(w in skills_lower for w in ['python', 'javascript', 'react', 'node', 'c++', 'java', 'backend', 'frontend', 'fullstack', 'devops']):
            user_role = 'Software Engineer'
        elif any(w in skills_lower for w in ['design', 'figma', 'ui', 'ux', 'sketch', 'adobe']):
            user_role = 'Designer'
        elif any(w in skills_lower for w in ['product', 'roadmap', 'pm', 'strategy', 'analytics']):
            user_role = 'Product Manager'
        elif any(w in skills_lower for w in ['data', 'ml', 'machine learning', 'analytics', 'sql', 'pytorch', 'tensorflow']):
            user_role = 'Data Scientist'
        else:
            user_role = 'Other'

        # Canonicalize roles helper
        def _canon_role(raw: str) -> str:
            if not raw:
                return ''
            s = str(raw).strip().lower()
            direct = {
                'software engineer': 'Software Engineer',
                'engineer': 'Software Engineer',
                'developer': 'Software Engineer',
                'swe': 'Software Engineer',
                'coder': 'Software Engineer',
                'frontend': 'Software Engineer',
                'backend': 'Software Engineer',
                'fullstack': 'Software Engineer',
                'full-stack': 'Software Engineer',
                'ux': 'Designer',
                'ui': 'Designer',
                'ui/ux': 'Designer',
                'designer': 'Designer',
                'product manager': 'Product Manager',
                'pm': 'Product Manager',
                'product': 'Product Manager',
                'data scientist': 'Data Scientist',
                'ml engineer': 'Data Scientist',
                'ai engineer': 'Data Scientist',
            }
            if s in direct:
                return direct[s]
            if any(k in s for k in ['engineer', 'developer', 'dev', 'coder']):
                return 'Software Engineer'
            if any(k in s for k in ['design', 'figma', 'ux', 'ui']):
                return 'Designer'
            if 'product' in s or s == 'pm':
                return 'Product Manager'
            if any(k in s for k in ['data', 'ml', 'machine learning', 'ai']):
                return 'Data Scientist'
            return (raw or '').strip()

        # Bucket candidates by role (preserve match order from re-ranker)
        buckets = {}
        for md in matches:
            r = _canon_role(md.get('role', '')) or 'Other'
            buckets.setdefault(r, []).append(md)

        # Select complement roles based on user's own role
        if user_role == 'Software Engineer':
            plan_roles = ['Designer', 'Product Manager']
        elif user_role == 'Designer':
            plan_roles = ['Software Engineer', 'Product Manager']
        elif user_role == 'Product Manager':
            plan_roles = ['Software Engineer', 'Designer']
        elif user_role == 'Data Scientist':
            plan_roles = ['Software Engineer', 'Product Manager']
        else:
            # Generic: prioritize core builder roles
            plan_roles = ['Software Engineer', 'Designer']

        suggestion = []
        for role in plan_roles:
            if buckets.get(role):
                suggestion.append(buckets[role][0])
        # If we still have only one, try add any remaining strong role
        if len(suggestion) < 2:
            for role in ['Data Scientist', 'Product Manager', 'Software Engineer', 'Designer']:
                if buckets.get(role):
                    cand = buckets[role][0]
                    if cand not in suggestion:
                        suggestion.append(cand)
                    if len(suggestion) == 2:
                        break

        # Build multiple team suggestions with different combinations
        teams = []
        
        # Suggestion 1: Core balanced team (Designer + Product/Engineer)
        if suggestion and len(suggestion) >= 2:
            teams.append({
                "members": suggestion[:2],
                "reasoning": f"A balanced team combining {suggestion[0].get('role', 'Unknown')} and {suggestion[1].get('role', 'Unknown')} skills. Perfect for early-stage product development with complementary expertise."
            })
        
        # Suggestion 2: Technical powerhouse (2 different technical roles)
        tech_suggestion = []
        for role in ['Software Engineer', 'Data Scientist']:
            if buckets.get(role) and len(buckets[role]) > 0:
                # Get different person than first suggestion
                for candidate in buckets[role]:
                    if candidate not in suggestion[:2]:
                        tech_suggestion.append(candidate)
                        break
        if len(tech_suggestion) >= 2:
            teams.append({
                "members": tech_suggestion[:2],
                "reasoning": f"Strong technical foundation with {tech_suggestion[0].get('role', 'Unknown')} and {tech_suggestion[1].get('role', 'Unknown')}. Ideal for building complex tech infrastructure and AI/ML features."
            })
        
        # Suggestion 3: Growth-focused team (PM + another complementary role)
        if buckets.get('Product Manager') and len(suggestion) > 0:
            pm = buckets['Product Manager'][0]
            # Find someone different from first two suggestions
            other = None
            for role in ['Designer', 'Software Engineer', 'Data Scientist']:
                if buckets.get(role):
                    for candidate in buckets[role]:
                        if candidate not in suggestion[:2] and candidate != pm:
                            other = candidate
                            break
                    if other:
                        break
            
            if other:
                teams.append({
                    "members": [pm, other],
                    "reasoning": f"Product-led team with {pm.get('role', 'PM')} driving strategy and {other.get('role', 'Unknown')} executing. Great for user-centric product development and rapid iteration."
                })
        
        # If we only have 1-2 teams, add a diverse alternative
        if len(teams) < 3 and len(suggestion) >= 2:
            # Try to create a diverse team from remaining matches
            diverse_team = []
            used_roles = set()
            for match in matches[:5]:  # Look at top 5 matches
                role = _canon_role(match.get('role', ''))
                if role not in used_roles and match not in suggestion[:2]:
                    diverse_team.append(match)
                    used_roles.add(role)
                if len(diverse_team) == 2:
                    break
            
            if len(diverse_team) == 2:
                teams.append({
                    "members": diverse_team,
                    "reasoning": f"Diverse skill combination with {diverse_team[0].get('role', 'Unknown')} and {diverse_team[1].get('role', 'Unknown')}. Brings different perspectives and broader capabilities to your project."
                })
        
        return teams[:3]  # Return max 3 suggestions
    except Exception as e:
        print(f"Error building team suggestions: {e}")
        return []

def get_all_collaborators():
    """
    Get all collaborators from the database.
    Useful for debugging and testing.
    """
    try:
        collection = chroma_client.get_collection(name="collaborators")
        results = collection.get()
        
        collaborators = []
        if results and results['metadatas']:
            for metadata in results['metadatas']:
                collaborators.append(metadata)
        
        return collaborators
    except Exception as e:
        print(f"Error getting all collaborators: {e}")
        return []


def get_collaborators_by_role(role):
    """
    Get all collaborators with a specific role.
    
    Args:
        role: String like "Software Engineer", "Designer", etc.
    """
    try:
        collection = chroma_client.get_collection(name="collaborators")
        results = collection.get(
            where={"role": {"$eq": role}}
        )
        
        collaborators = []
        if results and results['metadatas']:
            for metadata in results['metadatas']:
                collaborators.append(metadata)
        
        return collaborators
    except Exception as e:
        print(f"Error getting collaborators by role: {e}")
        return []


def get_collaborator_by_id(collab_id):
    """
    Get a single collaborator by ID.
    
    Args:
        collab_id: String ID like "collab_1"
    """
    try:
        collection = chroma_client.get_collection(name="collaborators")
        results = collection.get(
            ids=[collab_id]
        )
        
        if results and results['metadatas'] and len(results['metadatas']) > 0:
            return results['metadatas'][0]
        return None
    except Exception as e:
        print(f"Error getting collaborator by ID: {e}")
        return None


def search_by_skills(skills_list):
    """
    Find collaborators with specific skills using semantic search.
    
    Args:
        skills_list: List of skill strings like ["Python", "React"]
    """
    try:
        collection = chroma_client.get_collection(name="collaborators")
        
        # Create query from skills
        query_text = ' '.join(skills_list)
        query_embedding = create_embedding(query_text)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        matches = []
        if results and results['metadatas'] and len(results['metadatas'][0]) > 0:
            for metadata in results['metadatas'][0]:
                matches.append(metadata)
        
        return matches
    except Exception as e:
        print(f"Error searching by skills: {e}")
        return []


def get_database_stats():
    """
    Get statistics about the database.
    """
    try:
        collection = chroma_client.get_collection(name="collaborators")
        all_collabs = get_all_collaborators()
        
        # Count by role
        role_counts = {}
        for collab in all_collabs:
            role = collab.get('role', 'Unknown')
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "total": collection.count(),
            "by_role": role_counts
        }
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {"total": 0, "by_role": {}}


def save_user_profile(profile, availability_status="Available"):
    """
    Save a new user profile to ChromaDB so they can be matched with others.
    
    This adds the user to the database as a searchable collaborator.
    Others looking for their role will now see them in matches!
    
    Args:
        profile: Dict with keys: name, skills, interests, looking_for
        availability_status: "Available" or "In Team" (default: "Available")
    
    Returns:
        user_id: String ID of the saved user (e.g. "user_123")
    """
    try:
        collection = chroma_client.get_collection(name="collaborators")
        
        # Generate unique user ID
        import time
        user_id = f"user_{int(time.time())}_{profile.get('name', 'unknown').lower().replace(' ', '_')}"
        
        # Determine the user's role based on their skills
        # This is what they ARE, not what they're looking for
        skills_lower = ' '.join([s.lower() for s in profile.get('skills', [])])
        
        if any(word in skills_lower for word in ['python', 'javascript', 'react', 'node', 'c++', 'java', 'code', 'dev', 'backend', 'frontend']):
            user_role = "Software Engineer"
        elif any(word in skills_lower for word in ['design', 'figma', 'ui', 'ux', 'sketch', 'adobe']):
            user_role = "Designer"
        elif any(word in skills_lower for word in ['product', 'roadmap', 'pm', 'strategy', 'analytics']):
            user_role = "Product Manager"
        elif any(word in skills_lower for word in ['data', 'ml', 'machine learning', 'analytics', 'sql']):
            user_role = "Data Scientist"
        elif any(word in skills_lower for word in ['marketing', 'growth', 'seo', 'content']):
            user_role = "Marketing & Growth"
        elif any(word in skills_lower for word in ['sales', 'business', 'partnerships']):
            user_role = "Sales & Business Development"
        elif any(word in skills_lower for word in ['finance', 'accounting', 'fundraising']):
            user_role = "Finance & Operations"
        else:
            user_role = "Other"
        
        # Create searchable text
        searchable_text = f"{user_role} {' '.join(profile.get('skills', []))} {' '.join(profile.get('interests', []))}"
        
        # Create embedding
        embedding = create_embedding(searchable_text)
        
        # Create bio from interests and looking_for
        interests_str = ', '.join(profile.get('interests', []))
        looking_for = profile.get('looking_for', 'collaborators')
        bio = f"Interested in {interests_str}. Looking for {looking_for} to collaborate with."
        
        # Prepare metadata
        metadata = {
            "id": user_id,
            "name": profile.get('name', 'Unknown'),
            "role": user_role,
            "skills": ', '.join(profile.get('skills', [])),
            "interests": ', '.join(profile.get('interests', [])),
            "bio": bio,
            "availability": availability_status,  # Can be "Available" or "In Team"
            "looking_for": profile.get('looking_for', 'Collaborator'),
            "team_id": "None"  # Will be set when they join a team
        }
        
        # Add to ChromaDB
        collection.add(
            ids=[user_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[searchable_text]
        )
        
        print(f"✅ Saved user profile: {profile.get('name')} as {user_role} (ID: {user_id})")
        return user_id
        
    except Exception as e:
        print(f"Error saving user profile: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_team(user_ids, team_name="Unnamed Team"):
    """
    Form a team from multiple users. Marks them as "In Team" and assigns team_id.
    They will no longer appear in search results.
    
    Args:
        user_ids: List of user IDs to form a team
        team_name: Optional team name
    
    Returns:
        team_id: String ID of the created team
    """
    try:
        collection = chroma_client.get_collection(name="collaborators")
        import time
        team_id = f"team_{int(time.time())}"
        
        # Update each user's metadata
        for user_id in user_ids:
            # Get existing user
            result = collection.get(ids=[user_id], include=["metadatas", "embeddings", "documents"])
            if not result or not result['ids']:
                print(f"⚠️  User {user_id} not found")
                continue
            
            # Update metadata
            metadata = result['metadatas'][0]
            metadata['availability'] = "In Team"
            metadata['team_id'] = team_id
            
            # Update in ChromaDB
            collection.update(
                ids=[user_id],
                metadatas=[metadata]
            )
            
            print(f"✅ Added {metadata.get('name', user_id)} to {team_name}")
        
        print(f"🎉 Team created: {team_name} (ID: {team_id})")
        return team_id
        
    except Exception as e:
        print(f"Error creating team: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_available_users():
    """
    Get all users who are still available (not in a team yet).
    """
    try:
        all_users = get_all_collaborators()
        available = [u for u in all_users if u.get('availability') == 'Available']
        return available
    except Exception as e:
        print(f"Error getting available users: {e}")
        return []


def get_teams():
    """
    Get all formed teams grouped by team_id.
    """
    try:
        all_users = get_all_collaborators()
        teams = {}
        
        for user in all_users:
            team_id = user.get('team_id', 'None')
            if team_id != 'None':
                if team_id not in teams:
                    teams[team_id] = []
                teams[team_id].append(user)
        
        return teams
    except Exception as e:
        print(f"Error getting teams: {e}")
        return {}


def dissolve_team(team_id):
    """
    Dissolve a team - make all members available again.
    """
    try:
        collection = chroma_client.get_collection(name="collaborators")
        all_users = get_all_collaborators()
        
        # Find team members
        team_members = [u for u in all_users if u.get('team_id') == team_id]
        
        if not team_members:
            print(f"⚠️  Team {team_id} not found")
            return False
        
        # Make each member available again
        for member in team_members:
            user_id = member.get('id')
            result = collection.get(ids=[user_id], include=["metadatas"])
            
            if result and result['ids']:
                metadata = result['metadatas'][0]
                metadata['availability'] = "Available"
                metadata['team_id'] = "None"
                
                collection.update(
                    ids=[user_id],
                    metadatas=[metadata]
                )
                
                print(f"✅ {metadata.get('name', user_id)} is now available again")
        
        print(f"🎉 Team {team_id} dissolved")
        return True
        
    except Exception as e:
        print(f"Error dissolving team: {e}")
        import traceback
        traceback.print_exc()
        return False
