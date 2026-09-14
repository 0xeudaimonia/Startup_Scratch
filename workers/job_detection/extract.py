from __future__ import annotations

import re

from models.enums import EngineeringCategory

ENGINEERING_KEYWORDS = {
    EngineeringCategory.FRONTEND: ["frontend", "front-end", "front end", "react", "vue", "angular"],
    EngineeringCategory.BACKEND: ["backend", "back-end", "back end", "api engineer", "server"],
    EngineeringCategory.FULLSTACK: ["fullstack", "full-stack", "full stack"],
    EngineeringCategory.MOBILE: ["ios", "android", "mobile engineer", "react native", "flutter"],
    EngineeringCategory.DEVOPS: ["devops", "infrastructure engineer", "ci/cd"],
    EngineeringCategory.SRE: ["sre", "site reliability"],
    EngineeringCategory.PLATFORM: ["platform engineer", "platform engineering"],
    EngineeringCategory.DATA: ["data engineer", "analytics engineer"],
    EngineeringCategory.MACHINE_LEARNING: ["machine learning", "ml engineer"],
    EngineeringCategory.AI: ["ai engineer", "llm", "machine learning engineer"],
    EngineeringCategory.SECURITY: ["security engineer", "appsec"],
    EngineeringCategory.QA: ["qa engineer", "sdet", "quality engineer"],
    EngineeringCategory.ENGINEERING_MANAGEMENT: [
        "engineering manager",
        "head of engineering",
        "cto",
        "vp engineering",
        "director of engineering",
    ],
}

TECH_PATTERNS = {
    "frontend_technologies": ["React", "Next.js", "Vue", "Svelte", "Angular"],
    "backend_technologies": ["Node.js", "FastAPI", "Django", "Rails", "Laravel", "Spring Boot", "Express"],
    "programming_languages": ["Python", "TypeScript", "JavaScript", "Go", "Rust", "Java", "Ruby", "PHP", "Kotlin", "Swift"],
    "frameworks": ["Next.js", "Django", "FastAPI", "Rails", "Spring Boot", "LangChain", "LangGraph"],
    "databases": ["PostgreSQL", "MongoDB", "Redis", "MySQL", "Elasticsearch"],
    "cloud_providers": ["AWS", "GCP", "Azure"],
    "ai_technologies": ["OpenAI", "Anthropic", "LangChain", "LangGraph", "PyTorch", "TensorFlow"],
    "devops_technologies": ["Docker", "Kubernetes", "Terraform", "GitHub Actions"],
}


def classify_engineering_role(title: str, description: str | None = None) -> EngineeringCategory | None:
    text = f"{title} {description or ''}".lower()
    if not any(
        token in text
        for token in ["engineer", "developer", "sre", "devops", "cto", "software", "ml ", "data"]
    ):
        return None
    for category, keywords in ENGINEERING_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    if "software" in text or "engineer" in text or "developer" in text:
        return EngineeringCategory.FULLSTACK
    return None


def detect_technologies(*texts: str | None) -> dict[str, list[str]]:
    blob = "\n".join(text or "" for text in texts)
    found: dict[str, list[str]] = {}
    for bucket, names in TECH_PATTERNS.items():
        hits = []
        for name in names:
            pattern = re.compile(rf"(?<![A-Za-z]){re.escape(name)}(?![A-Za-z])", re.I)
            if pattern.search(blob):
                hits.append(name)
        if hits:
            found[bucket] = hits
    return found
