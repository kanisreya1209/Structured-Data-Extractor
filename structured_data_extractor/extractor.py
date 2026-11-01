"""
ResumeIQ — extraction and validation engine.
Handles PDF, DOCX and TXT resumes with varied formatting.
"""
from __future__ import annotations

import io
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError, ConfigDict

# ── Sample resume ─────────────────────────────────────────────────────────────
SAMPLE_RESUME = """ARUN KUMAR
arun.kumar@example.com | +91 98765 43210 | Chennai, Tamil Nadu

PROFESSIONAL SUMMARY
Computer Science graduate with 2 years of experience building Python applications,
ML pipelines and data-driven solutions. Strong communicator and fast learner.

SKILLS
Python, Java, SQL, Machine Learning, Pandas, Scikit-learn, FastAPI, Git, Communication,
NumPy, TensorFlow, Docker, REST APIs, Data Analysis

EXPERIENCE
Machine Learning Intern | DataSpark Technologies | Jan 2024 - Jun 2024
Developed data preprocessing pipelines and trained classification models to improve prediction accuracy by 18%.

Web Developer Intern | BrightLabs | Jul 2023 - Sep 2023
Built responsive web pages and integrated REST APIs using JavaScript and HTML/CSS.

EDUCATION
B.Tech Computer Science | Example Institute of Technology | 2024
"""

# ── Expanded skill dictionary ─────────────────────────────────────────────────
KNOWN_SKILLS = [
    # Languages
    "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Bash",
    "Shell", "PowerShell", "Objective-C", "Dart", "Lua",
    # Web
    "HTML", "CSS", "React", "Angular", "Vue", "Vue.js", "Next.js", "Nuxt.js",
    "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring Boot", "Laravel",
    "Rails", "ASP.NET", "GraphQL", "REST APIs", "WebSockets", "Tailwind CSS",
    "Bootstrap", "jQuery", "Webpack", "Vite", "Svelte",
    # Data / ML
    "Machine Learning", "Deep Learning", "Natural Language Processing", "NLP",
    "Computer Vision", "Reinforcement Learning", "Data Science", "Data Analysis",
    "Data Engineering", "Data Visualization", "Pandas", "NumPy", "Scikit-learn",
    "TensorFlow", "PyTorch", "Keras", "Hugging Face", "OpenCV", "NLTK", "spaCy",
    "XGBoost", "LightGBM", "Spark", "PySpark", "Hadoop", "Kafka", "Airflow",
    "dbt", "LangChain", "LlamaIndex", "Streamlit", "Tableau", "Power BI",
    "Looker", "Matplotlib", "Seaborn", "Plotly",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform",
    "Ansible", "Jenkins", "GitHub Actions", "CI/CD", "Linux", "Nginx", "Helm",
    "Prometheus", "Grafana", "Elasticsearch",
    # Databases
    "SQL", "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Cassandra",
    "DynamoDB", "Oracle", "MS SQL", "BigQuery", "Snowflake", "Firebase",
    # Tools
    "Git", "GitHub", "GitLab", "Jira", "Confluence", "Figma", "Postman",
    "VS Code", "IntelliJ", "Eclipse", "MATLAB",
    # Soft skills
    "Communication", "Problem Solving", "Team Leadership", "Agile", "Scrum",
    "Project Management", "Critical Thinking", "Public Speaking",
]

# ── Known section heading aliases ─────────────────────────────────────────────
# Each group maps to a canonical name; matching is case-insensitive.
SECTION_ALIASES: Dict[str, List[str]] = {
    "summary": [
        "professional summary", "summary", "objective", "career objective",
        "profile", "professional profile", "about me", "about", "overview",
    ],
    "skills": [
        "skills", "technical skills", "key skills", "core competencies",
        "competencies", "technologies", "tech stack", "tools", "expertise",
        "areas of expertise",
    ],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "career history", "internships",
        "internship", "positions held",
    ],
    "education": [
        "education", "educational background", "academic background",
        "qualifications", "academic qualifications", "degrees",
    ],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "courses", "training", "awards"],
}

# Flat reverse-lookup: alias → canonical
_ALIAS_MAP: Dict[str, str] = {
    alias.lower(): canon
    for canon, aliases in SECTION_ALIASES.items()
    for alias in aliases
}

ALL_HEADINGS = list(_ALIAS_MAP.keys())


# ── Pydantic models ───────────────────────────────────────────────────────────
class Contact(BaseModel):
    full_name: Optional[str] = None
    email:     Optional[str] = None
    phone:     Optional[str] = None
    location:  Optional[str] = None


class Experience(BaseModel):
    job_title:   Optional[str] = None
    company:     Optional[str] = None
    start_date:  Optional[str] = None
    end_date:    Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    degree:          Optional[str] = None
    institution:     Optional[str] = None
    graduation_year: Optional[str] = None


class Validation(BaseModel):
    is_valid:       bool
    missing_fields: List[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    contact:    Contact
    summary:    Optional[str]      = None
    skills:     List[str]          = Field(default_factory=list)
    experience: List[Experience]   = Field(default_factory=list)
    education:  List[Education]    = Field(default_factory=list)
    validation: Validation


# ── File reading ──────────────────────────────────────────────────────────────
def read_text(data: bytes, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "txt"
    if ext == "txt":
        return data.decode("utf-8", errors="ignore")
    if ext == "pdf":
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if text:
                    pages.append(text)
            return "\n".join(pages)
    if ext == "docx":
        from docx import Document
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file type. Please upload PDF, DOCX or TXT.")


# ── Section splitter ──────────────────────────────────────────────────────────
def _is_heading(line: str) -> bool:
    """Return True if a line looks like a section heading."""
    stripped = line.strip().rstrip(":").strip().lower()
    return stripped in _ALIAS_MAP


def split_sections(text: str) -> Dict[str, str]:
    """
    Split resume text into sections keyed by canonical name.
    Returns a dict like {"summary": "...", "skills": "...", ...}.
    Also stores "header" for the top block before the first heading.
    """
    lines = text.splitlines()
    sections: Dict[str, List[str]] = {"header": []}
    current = "header"

    for line in lines:
        stripped = line.strip().rstrip(":").strip().lower()
        if stripped in _ALIAS_MAP:
            current = _ALIAS_MAP[stripped]
            if current not in sections:
                sections[current] = []
        else:
            sections.setdefault(current, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


# ── Contact extraction ────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
_PHONE_RE = re.compile(
    r"(?<!\w)(\+?[\d][\d\s\-().]{6,}\d)(?!\w)"
)
_YEAR_RE  = re.compile(r"\b(19|20)\d{2}\b")


def extract_contact(header_text: str) -> Dict[str, Optional[str]]:
    lines = [l.strip() for l in header_text.splitlines() if l.strip()]

    # Email
    email_match = _EMAIL_RE.search(header_text)
    email = email_match.group(0) if email_match else None

    # Phone — try each line, take first plausible hit
    phone = None
    for line in lines:
        m = _PHONE_RE.search(line)
        if m:
            candidate = m.group(0).strip()
            # Must contain enough digits
            if len(re.sub(r"\D", "", candidate)) >= 7:
                phone = candidate
                break

    # Name — first non-email, non-phone, non-URL line with ≤6 words
    name = None
    for line in lines[:6]:
        if _EMAIL_RE.search(line):
            continue
        if _PHONE_RE.search(line):
            continue
        if re.search(r"https?://|linkedin|github|www\.", line, re.I):
            continue
        if re.search(r"\d{4}", line):  # skip year-heavy lines
            continue
        words = line.split()
        if 1 <= len(words) <= 6:
            name = line
            break

    # Location — look for city/state/country patterns in the header lines
    location = None
    loc_re = re.compile(
        r"\b([A-Z][a-zA-Z\s]+(?:,\s*[A-Z][a-zA-Z\s]+)*)"
        r"(?=\s*\||\s*$|\s*\n)",
    )
    # Prefer a line that contains the email (contact line pattern)
    contact_line = ""
    if email:
        for line in lines:
            if email in line:
                contact_line = line
                break
    if contact_line:
        parts = [p.strip() for p in contact_line.split("|")]
        for part in reversed(parts):
            if not _EMAIL_RE.search(part) and not _PHONE_RE.search(part):
                if re.search(r"[A-Za-z]", part):
                    location = part
                    break
    if not location:
        # scan all header lines for a location-ish phrase
        for line in lines:
            if _EMAIL_RE.search(line) or _PHONE_RE.search(line):
                continue
            if re.search(r"[A-Za-z]{3,}(?:,\s*[A-Za-z]{2,})", line):
                location = line.strip()
                break

    return {"full_name": name, "email": email, "phone": phone, "location": location}


# ── Skills extraction ─────────────────────────────────────────────────────────
def extract_skills(skills_text: str, fallback_text: str = "") -> List[str]:
    source = skills_text if skills_text.strip() else fallback_text
    found: List[str] = []
    for skill in KNOWN_SKILLS:
        pattern = rf"(?<![A-Za-z+#]){re.escape(skill)}(?![A-Za-z+#])"
        if re.search(pattern, source, re.I):
            found.append(skill)
    # Deduplicate while preserving order
    seen: set = set()
    result = []
    for s in found:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            result.append(s)
    return result


# ── Experience extraction ─────────────────────────────────────────────────────
_DATE_RE = re.compile(
    r"((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
    r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?"
    r"|Dec(?:ember)?)[,.]?\s*\d{4}|\d{4})"
    r"\s*[-–—to/]+\s*"
    r"((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
    r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?"
    r"|Dec(?:ember)?)[,.]?\s*\d{4}|\d{4}|Present|Current|Till date|Ongoing)",
    re.I,
)


def extract_experience(exp_text: str) -> List[Dict[str, Any]]:
    if not exp_text.strip():
        return []

    entries: List[Dict[str, Any]] = []
    lines = [l.strip() for l in exp_text.splitlines() if l.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]
        dm   = _DATE_RE.search(line)

        # ── Pattern A: "Title | Company | Dates" or "Title | Company" ─────
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            title   = parts[0] or None
            company = parts[1] if len(parts) > 1 else None
            if not dm:
                date_str = " ".join(parts[2:]) if len(parts) > 2 else ""
                dm = _DATE_RE.search(date_str)
            desc_lines = []
            j = i + 1
            while j < len(lines) and "|" not in lines[j] and not _is_heading(lines[j]):
                desc_lines.append(lines[j])
                j += 1
            entries.append({
                "job_title":   title,
                "company":     company,
                "start_date":  dm.group(1) if dm else None,
                "end_date":    dm.group(2) if dm else None,
                "description": " ".join(desc_lines) or None,
            })
            i = j
            continue

        # ── Pattern B: line with a date range (Title @ Company, Dates) ────
        if dm:
            # Try to split title and company around common separators
            before = line[:dm.start()].strip().rstrip(",-–")
            sep_m  = re.split(r"\s+(?:at|@|-|,)\s+", before, maxsplit=1)
            title   = sep_m[0].strip() or before or None
            company = sep_m[1].strip() if len(sep_m) > 1 else None
            desc_lines = []
            j = i + 1
            while j < len(lines) and "|" not in lines[j] and not _is_heading(lines[j]) and not _DATE_RE.search(lines[j]):
                desc_lines.append(lines[j])
                j += 1
            if title or company:
                entries.append({
                    "job_title":   title,
                    "company":     company,
                    "start_date":  dm.group(1),
                    "end_date":    dm.group(2),
                    "description": " ".join(desc_lines) or None,
                })
            i = j
            continue

        # ── Pattern C: standalone "Title\nCompany\nDates\nDesc" block ─────
        # Title is this line; peek ahead for a date line
        potential_title = line
        if i + 1 < len(lines):
            next_dm = _DATE_RE.search(lines[i + 1])
            if next_dm:
                entries.append({
                    "job_title":   potential_title,
                    "company":     None,
                    "start_date":  next_dm.group(1),
                    "end_date":    next_dm.group(2),
                    "description": lines[i + 2] if i + 2 < len(lines) else None,
                })
                i += 3
                continue

        i += 1

    return entries


# ── Education extraction ──────────────────────────────────────────────────────
def extract_education(edu_text: str) -> List[Dict[str, Any]]:
    if not edu_text.strip():
        return []

    entries = []
    lines = [l.strip() for l in edu_text.splitlines() if l.strip()]

    for line in lines:
        year = _YEAR_RE.search(line)
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            entries.append({
                "degree":          parts[0] or None,
                "institution":     parts[1] if len(parts) > 1 else None,
                "graduation_year": year.group(0) if year else None,
            })
        elif "," in line:
            parts = [p.strip() for p in line.split(",", 1)]
            entries.append({
                "degree":          parts[0] or None,
                "institution":     parts[1] if len(parts) > 1 else None,
                "graduation_year": year.group(0) if year else None,
            })
        else:
            # Could be degree on one line, institution on next
            entries.append({
                "degree":          line,
                "institution":     None,
                "graduation_year": year.group(0) if year else None,
            })

    # Merge consecutive entries that look like degree/institution pairs
    merged: List[Dict[str, Any]] = []
    i = 0
    while i < len(entries):
        e = entries[i]
        if (e["institution"] is None and e["graduation_year"] is None
                and i + 1 < len(entries)
                and entries[i + 1]["degree"] is not None
                and entries[i + 1]["graduation_year"] is not None):
            merged.append({
                "degree":          e["degree"],
                "institution":     entries[i + 1]["degree"],
                "graduation_year": entries[i + 1]["graduation_year"],
            })
            i += 2
        else:
            merged.append(e)
            i += 1

    return merged


# ── Main public API ───────────────────────────────────────────────────────────
def extract_resume(data: bytes, filename: str) -> Dict[str, Any]:
    text = read_text(data, filename)
    if not text.strip():
        raise ValueError("No readable text found. Try a text-based PDF, DOCX or TXT file.")

    sections = split_sections(text)

    contact    = extract_contact(sections.get("header", ""))
    summary    = sections.get("summary", None) or None
    skills     = extract_skills(sections.get("skills", ""), text)
    experience = extract_experience(sections.get("experience", ""))
    education  = extract_education(sections.get("education", ""))

    return {
        "contact":    contact,
        "summary":    summary,
        "skills":     skills,
        "experience": experience,
        "education":  education,
    }


def validate_resume(data: Dict[str, Any]) -> Dict[str, Any]:
    required_keys = [
        "contact.full_name", "contact.email", "contact.phone",
        "skills", "experience", "education",
    ]
    missing: List[str] = []
    c = data.get("contact") or {}
    for key in required_keys:
        if key.startswith("contact."):
            field = key.split(".", 1)[1]
            if not c.get(field):
                missing.append(key)
        else:
            val = data.get(key)
            if not val:
                missing.append(key)

    payload = {
        **data,
        "validation": {"is_valid": len(missing) == 0, "missing_fields": missing},
    }
    try:
        validated = ResumeData.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Schema validation failed: {exc}") from exc

    return validated.model_dump()
