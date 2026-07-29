"""
Configuration and Taxonomy Rules for AI Resume Analyzer
"""

# Weights for multi-factor ATS Score (must sum to 1.0)
ATS_WEIGHTS = {
    "keyword_match": 0.35,      # TF-IDF similarity & keyphrase overlap
    "skills_alignment": 0.25,   # Essential & domain skills match
    "formatting": 0.20,         # Section presence, contact info, length check
    "impact_metrics": 0.20      # Action verbs, metrics/quantification, readability
}

# Standard resume section headers expected by ATS
EXPECTED_SECTIONS = [
    "experience",
    "work experience",
    "employment",
    "education",
    "skills",
    "technical skills",
    "projects",
    "summary",
    "professional summary",
    "certifications"
]

# Action verbs that ATS and hiring managers look for
STRONG_ACTION_VERBS = {
    "achieved", "orchestrated", "architected", "developed", "spearheaded", "engineered",
    "implemented", "accelerated", "optimized", "streamlined", "created", "launched",
    "pioneered", "scaled", "automated", "transformed", "designed", "generated",
    "increased", "decreased", "reduced", "maximized", "minimized", "lead", "led",
    "managed", "collaborated", "built", "established", "delivering", "expanded",
    "formulated", "identified", "improved", "integrated", "produced", "resolved"
}

# Comprehensive skill taxonomy divided into domain categories
SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
        "rust", "ruby", "php", "sql", "html", "css", "r", "swift", "kotlin", "bash", "shell"
    ],
    "Frameworks & Libraries": [
        "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask",
        "fastapi", "spring boot", "pandas", "numpy", "scikit-learn", "tensorflow",
        "pytorch", "keras", "spacy", "nltk", "opencv", "streamlit", "tailwind", "bootstrap"
    ],
    "Cloud & Infrastructure": [
        "aws", "gcp", "azure", "google cloud", "docker", "kubernetes", "terraform",
        "ansible", "ci/cd", "github actions", "gitlab ci", "jenkins", "serverless",
        "cloudformation", "linux", "nginx", "load balancer"
    ],
    "Data & Databases": [
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
        "snowflake", "bigquery", "redshift", "apache spark", "hadoop", "kafka",
        "dbt", "airflow", "data modeling", "etl", "data warehousing"
    ],
    "AI / ML & NLP": [
        "llm", "large language models", "prompt engineering", "nlp", "natural language processing",
        "generative ai", "langchain", "rag", "retrieval augmented generation", "vector databases",
        "pinecone", "chromadb", "transformers", "fine-tuning", "bert", "gpt", "ats"
    ],
    "Product & Agile": [
        "agile", "scrum", "kanban", "jira", "confluence", "product roadmap", "user stories",
        "a/b testing", "product analytics", "stakeholder management", "okrs", "kpis"
    ],
    "Soft Skills": [
        "leadership", "communication", "problem solving", "critical thinking",
        "collaboration", "adaptability", "time management", "mentorship", "presentation",
        "cross-functional", "ownership", "strategic thinking"
    ]
}

# Flattened set of all skills for fast lookup
ALL_SKILLS_SET = {skill.lower() for cat in SKILL_TAXONOMY.values() for skill in cat}
