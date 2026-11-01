"""
ResumeIQ — ATS (Applicant Tracking System) Checker
Analyses extracted resume data and returns scored checks + actionable suggestions.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ── Types ─────────────────────────────────────────────────────────────────────
# Each check: { id, category, title, status, score, max_score, message, suggestions[] }

STATUS_PASS    = "pass"
STATUS_WARN    = "warn"
STATUS_FAIL    = "fail"

CAT_CONTACT    = "Contact & Identity"
CAT_CONTENT    = "Content Completeness"
CAT_SKILLS     = "Skills & Keywords"
CAT_FORMAT     = "Formatting & ATS Parsing"
CAT_EXPERIENCE = "Experience Quality"
CAT_EDUCATION  = "Education"


def _check(
    id: str, category: str, title: str,
    status: str, score: int, max_score: int,
    message: str, suggestions: Optional[List[str]] = None
) -> Dict[str, Any]:
    return {
        "id": id, "category": category, "title": title,
        "status": status, "score": score, "max_score": max_score,
        "message": message, "suggestions": suggestions or [],
    }


# ── Individual checks ─────────────────────────────────────────────────────────

def check_full_name(data: Dict) -> Dict:
    c = data.get("contact") or {}
    name = c.get("full_name") or ""
    if not name:
        return _check("name", CAT_CONTACT, "Full name present", STATUS_FAIL, 0, 5,
            "No candidate name was detected.",
            ["Place your full name prominently at the very top of the resume.",
             "Use a larger font size (18–24pt) so it stands out to both ATS and recruiters.",
             "Avoid using images of text — ATS cannot read them."])
    words = name.strip().split()
    if len(words) < 2:
        return _check("name", CAT_CONTACT, "Full name present", STATUS_WARN, 3, 5,
            f"Only a single name token '{name}' was found — ATS systems expect first and last name.",
            ["Add both your first and last name.",
             "Do not use nicknames or abbreviations on the resume header."])
    return _check("name", CAT_CONTACT, "Full name present", STATUS_PASS, 5, 5,
        f"Full name '{name}' detected successfully.")


def check_email(data: Dict) -> Dict:
    c = data.get("contact") or {}
    email = c.get("email") or ""
    if not email:
        return _check("email", CAT_CONTACT, "Email address", STATUS_FAIL, 0, 5,
            "No email address was found.",
            ["Always include a professional email address in your contact section.",
             "Format: firstname.lastname@domain.com is widely recognised by ATS."])
    if re.search(r"(hotmail|yahoo|aol)\.", email, re.I):
        return _check("email", CAT_CONTACT, "Email address", STATUS_WARN, 3, 5,
            f"Email '{email}' uses an older provider which can appear unprofessional.",
            ["Consider a Gmail or custom-domain address for a more professional impression.",
             "Ensure the email is current and actively monitored."])
    return _check("email", CAT_CONTACT, "Email address", STATUS_PASS, 5, 5,
        f"Email '{email}' found.")


def check_phone(data: Dict) -> Dict:
    c = data.get("contact") or {}
    phone = c.get("phone") or ""
    if not phone:
        return _check("phone", CAT_CONTACT, "Phone number", STATUS_FAIL, 0, 5,
            "No phone number was detected.",
            ["Add a direct phone number in your contact section.",
             "Include the country code (e.g. +1, +91) for international applications.",
             "Use a consistent format: +1 (555) 000-0000 or +91 98765 43210."])
    return _check("phone", CAT_CONTACT, "Phone number", STATUS_PASS, 5, 5,
        f"Phone '{phone}' found.")


def check_location(data: Dict) -> Dict:
    c = data.get("contact") or {}
    loc = c.get("location") or ""
    if not loc:
        return _check("location", CAT_CONTACT, "Location", STATUS_WARN, 2, 4,
            "No location was detected.",
            ["Add at least a City and Country/State so ATS can match location filters.",
             "You do not need a full street address — City, State is sufficient.",
             "Remote-only candidates can write 'Remote' or 'Open to relocation'."])
    return _check("location", CAT_CONTACT, "Location", STATUS_PASS, 4, 4,
        f"Location '{loc}' found.")


def check_summary(data: Dict) -> Dict:
    summary = (data.get("summary") or "").strip()
    if not summary:
        return _check("summary", CAT_CONTENT, "Professional summary", STATUS_FAIL, 0, 8,
            "No professional summary or objective was found.",
            ["Add a 2–4 sentence summary at the top of your resume.",
             "Mention your years of experience, primary domain and top skills.",
             "Tailor the summary for each job application using keywords from the job description.",
             "Example: 'Results-driven Software Engineer with 4 years of Python and cloud experience…'"])
    words = summary.split()
    if len(words) < 20:
        return _check("summary", CAT_CONTENT, "Professional summary", STATUS_WARN, 4, 8,
            f"Summary is very short ({len(words)} words). ATS and recruiters prefer 40–80 words.",
            ["Expand your summary to at least 40 words.",
             "Highlight specific achievements or impact, not just responsibilities.",
             "Include 2–3 relevant keywords that appear in the target job description."])
    if len(words) > 120:
        return _check("summary", CAT_CONTENT, "Professional summary", STATUS_WARN, 5, 8,
            f"Summary is very long ({len(words)} words). Keep it under 100 words for ATS.",
            ["Trim to 60–80 words focusing on your strongest points.",
             "Move detailed achievements into the experience section."])
    return _check("summary", CAT_CONTENT, "Professional summary", STATUS_PASS, 8, 8,
        f"Summary present ({len(words)} words).")


def check_skills_count(data: Dict) -> Dict:
    skills = data.get("skills") or []
    n = len(skills)
    if n == 0:
        return _check("skills_count", CAT_SKILLS, "Skills section present", STATUS_FAIL, 0, 10,
            "No skills were detected.",
            ["Add a dedicated 'Skills' or 'Technical Skills' section.",
             "List skills as comma-separated keywords — ATS parsers prefer this format.",
             "Include both hard skills (Python, SQL) and soft skills (Communication, Agile)."])
    if n < 5:
        return _check("skills_count", CAT_SKILLS, "Skills section present", STATUS_WARN, 5, 10,
            f"Only {n} skills detected — ATS systems typically expect 8–15 skills.",
            ["Expand your skills list to at least 8–10 keywords.",
             "Review the job description and add matching technology/tool names.",
             "Separate unrelated skills with commas for better ATS parsing."])
    if n >= 5 and n < 10:
        return _check("skills_count", CAT_SKILLS, "Skills section present", STATUS_WARN, 7, 10,
            f"{n} skills detected. Adding a few more can improve keyword matching.",
            ["Aim for 10–15 skills covering your main technical and soft competencies.",
             "Mirror keywords from job descriptions you are targeting."])
    return _check("skills_count", CAT_SKILLS, "Skills section present", STATUS_PASS, 10, 10,
        f"{n} skills detected — solid keyword coverage.")


def check_skill_diversity(data: Dict) -> Dict:
    from extractor import KNOWN_SKILLS
    skills = data.get("skills") or []
    # Check for at least one soft skill indicator
    soft = ["communication","leadership","agile","scrum","problem solving","project management","critical thinking"]
    has_soft = any(s.lower() in soft for s in skills)
    # Check for measurable/domain skills (more than just tools)
    domain_skills = [s for s in skills if len(s.split()) > 1]  # multi-word = domain skill
    checks = []
    if not has_soft:
        checks.append("Add at least one soft skill (e.g. Communication, Agile, Problem Solving) — recruiters filter on these.")
    if len(domain_skills) < 2:
        checks.append("Include domain/technology skills with full names (e.g. 'Machine Learning', 'REST APIs') not just abbreviations.")
    if len(skills) > 0 and len(set(s.lower() for s in skills)) < len(skills):
        checks.append("Remove duplicate skills — duplicates can confuse ATS parsers.")

    if checks:
        return _check("skill_diversity", CAT_SKILLS, "Skill diversity & balance", STATUS_WARN, 4, 6,
            "Skill list could be more balanced for ATS keyword matching.",
            checks)
    return _check("skill_diversity", CAT_SKILLS, "Skill diversity & balance", STATUS_PASS, 6, 6,
        "Good mix of technical and soft skills detected.")


def check_experience(data: Dict) -> Dict:
    exp = data.get("experience") or []
    if not exp:
        return _check("experience", CAT_EXPERIENCE, "Work experience present", STATUS_FAIL, 0, 12,
            "No work experience entries were detected.",
            ["Add an 'Experience' or 'Work Experience' section.",
             "Use the format: Job Title | Company | Start Date – End Date",
             "Include at least one bullet point describing responsibilities or achievements.",
             "For freshers, add internships, projects or freelance work."])

    issues = []
    missing_dates = [e for e in exp if not e.get("start_date")]
    missing_desc  = [e for e in exp if not e.get("description")]
    missing_company = [e for e in exp if not e.get("company")]
    no_metrics = []
    metric_keywords = r"\b(\d+%|\d+x|\d+ (users|clients|projects|months|years|hours|dollars|\$|million|thousand|queries|requests|teams?|members?))\b"
    for e in exp:
        desc = e.get("description") or ""
        if desc and not re.search(metric_keywords, desc, re.I):
            no_metrics.append(e.get("job_title") or "a role")

    score = 12
    if missing_dates:
        score -= 2
        issues.append(f"{len(missing_dates)} role(s) are missing dates — always include start and end dates.")
    if missing_company:
        score -= 2
        issues.append(f"{len(missing_company)} role(s) are missing the company name.")
    if missing_desc:
        score -= 3
        issues.append(f"{len(missing_desc)} role(s) have no description — add bullet points for each.")
    if no_metrics:
        score -= 2
        issues.append(f"Descriptions for {len(no_metrics)} role(s) lack measurable metrics (numbers, %, impact).")

    if issues:
        suggestions = [
            *issues,
            "Use action verbs: 'Developed', 'Led', 'Reduced', 'Improved', 'Delivered'.",
            "Quantify achievements: 'Reduced API latency by 30%' beats 'Improved performance'.",
            "ATS scores higher when dates are in a consistent format (e.g. Jan 2022 – Jun 2023).",
        ]
        status = STATUS_WARN if score >= 7 else STATUS_FAIL
        return _check("experience", CAT_EXPERIENCE, "Work experience quality", status, max(score, 0), 12,
            f"{len(exp)} experience entr{'y' if len(exp)==1 else 'ies'} found but improvements needed.",
            suggestions)

    return _check("experience", CAT_EXPERIENCE, "Work experience quality", STATUS_PASS, 12, 12,
        f"{len(exp)} experience entr{'y' if len(exp)==1 else 'ies'} found with good coverage.")


def check_education(data: Dict) -> Dict:
    edu = data.get("education") or []
    if not edu:
        return _check("education", CAT_EDUCATION, "Education present", STATUS_WARN, 3, 6,
            "No education entries were detected.",
            ["Add an 'Education' section with your degree, institution and graduation year.",
             "ATS systems often filter candidates by minimum education level.",
             "Format: B.Tech Computer Science | XYZ University | 2024"])
    missing_year = [e for e in edu if not e.get("graduation_year")]
    if missing_year:
        return _check("education", CAT_EDUCATION, "Education present", STATUS_WARN, 4, 6,
            f"{len(edu)} education entr{'y' if len(edu)==1 else 'ies'} found but missing graduation year(s).",
            ["Always include your graduation year — recruiters and ATS filters rely on it.",
             "If still studying, write 'Expected 2025' or 'Pursuing'."])
    return _check("education", CAT_EDUCATION, "Education present", STATUS_PASS, 6, 6,
        f"{len(edu)} education entr{'y' if len(edu)==1 else 'ies'} found.")


def check_ats_keywords(data: Dict) -> Dict:
    """Check for high-value ATS keywords that are commonly filtered on."""
    HIGH_VALUE = [
        "python","java","sql","javascript","machine learning","data analysis",
        "project management","agile","aws","docker","kubernetes","react","node",
        "git","ci/cd","rest api","cloud","deep learning","nlp","postgresql","mongodb",
    ]
    skills = [s.lower() for s in (data.get("skills") or [])]
    summary_text = (data.get("summary") or "").lower()
    exp_text = " ".join(
        (e.get("description") or "") for e in (data.get("experience") or [])
    ).lower()
    full_text = " ".join(skills) + " " + summary_text + " " + exp_text

    matched = [kw for kw in HIGH_VALUE if kw in full_text]
    coverage = len(matched) / len(HIGH_VALUE)

    if coverage < 0.15:
        return _check("keywords", CAT_SKILLS, "ATS keyword coverage", STATUS_FAIL, 0, 8,
            f"Very low keyword coverage — only {len(matched)} of {len(HIGH_VALUE)} high-value ATS keywords found.",
            ["Mirror exact keywords from the job description you are targeting.",
             "ATS systems score resumes by keyword frequency — use precise technology names.",
             "Add: " + ", ".join(kw.title() for kw in HIGH_VALUE[:6] if kw not in full_text)[:120]])
    if coverage < 0.35:
        return _check("keywords", CAT_SKILLS, "ATS keyword coverage", STATUS_WARN, 4, 8,
            f"{len(matched)} of {len(HIGH_VALUE)} high-value keywords detected — consider adding more.",
            ["Review job postings you are targeting and add their exact keywords.",
             "Common missing keywords: " + ", ".join(kw.title() for kw in HIGH_VALUE if kw not in full_text)[:120]])
    return _check("keywords", CAT_SKILLS, "ATS keyword coverage", STATUS_PASS, 8, 8,
        f"Good keyword coverage — {len(matched)} of {len(HIGH_VALUE)} high-value ATS keywords present.")


def check_section_headings(data: Dict) -> Dict:
    """Infer whether the resume used standard section headings ATS can parse."""
    has_exp  = bool(data.get("experience"))
    has_edu  = bool(data.get("education"))
    has_sk   = bool(data.get("skills"))
    has_sum  = bool(data.get("summary"))
    missing  = []
    if not has_exp: missing.append("Experience")
    if not has_edu: missing.append("Education")
    if not has_sk:  missing.append("Skills")

    if missing:
        return _check("headings", CAT_FORMAT, "Standard section headings", STATUS_FAIL, 0, 6,
            f"ATS could not parse sections: {', '.join(missing)}.",
            [f"Use exact headings: {', '.join(missing)} — avoid creative labels like 'My Journey' or 'What I Do'.",
             "Each section heading should be on its own line in plain text.",
             "Avoid tables and text boxes — ATS parsers often skip them."])
    if not has_sum:
        return _check("headings", CAT_FORMAT, "Standard section headings", STATUS_WARN, 4, 6,
            "Experience, Education and Skills sections found but no Summary/Objective section.",
            ["Add a 'Summary' or 'Professional Summary' section — it improves ATS ranking.",
             "Place it immediately after your contact details."])
    return _check("headings", CAT_FORMAT, "Standard section headings", STATUS_PASS, 6, 6,
        "All key ATS sections (Summary, Skills, Experience, Education) detected.")


def check_resume_length(data: Dict) -> Dict:
    exp_count = len(data.get("experience") or [])
    edu_count = len(data.get("education") or [])
    skill_count = len(data.get("skills") or [])
    total_items = exp_count + edu_count + skill_count

    if total_items < 5:
        return _check("length", CAT_FORMAT, "Resume density / length", STATUS_FAIL, 0, 4,
            "Resume appears very sparse — ATS systems may rank it low.",
            ["Aim for a one-page resume with dense, relevant content.",
             "Add more bullet points under each experience entry.",
             "List all relevant projects, certifications and achievements."])
    if total_items > 50:
        return _check("length", CAT_FORMAT, "Resume density / length", STATUS_WARN, 2, 4,
            "Resume may be too long — ATS systems and recruiters prefer 1–2 pages.",
            ["Trim experience bullet points to the 3–5 most impactful per role.",
             "Remove roles older than 10–15 years unless highly relevant.",
             "Consolidate similar skills into single entries."])
    return _check("length", CAT_FORMAT, "Resume density / length", STATUS_PASS, 4, 4,
        "Resume length and density looks appropriate.")


# ── Main ATS check function ───────────────────────────────────────────────────

def run_ats_check(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run all ATS checks and return a structured report.
    """
    checks = [
        check_full_name(data),
        check_email(data),
        check_phone(data),
        check_location(data),
        check_summary(data),
        check_skills_count(data),
        check_skill_diversity(data),
        check_ats_keywords(data),
        check_experience(data),
        check_education(data),
        check_section_headings(data),
        check_resume_length(data),
    ]

    total_score = sum(c["score"] for c in checks)
    total_max   = sum(c["max_score"] for c in checks)
    pct         = round((total_score / total_max) * 100) if total_max else 0

    passes  = sum(1 for c in checks if c["status"] == STATUS_PASS)
    warns   = sum(1 for c in checks if c["status"] == STATUS_WARN)
    fails   = sum(1 for c in checks if c["status"] == STATUS_FAIL)

    if pct >= 80:
        overall = "ATS-Ready"
        overall_color = "green"
    elif pct >= 55:
        overall = "Needs Improvement"
        overall_color = "amber"
    else:
        overall = "Not ATS Optimised"
        overall_color = "red"

    # Group by category
    categories: Dict[str, List] = {}
    for c in checks:
        categories.setdefault(c["category"], []).append(c)

    return {
        "score": total_score,
        "max_score": total_max,
        "percent": pct,
        "overall": overall,
        "overall_color": overall_color,
        "passes": passes,
        "warns": warns,
        "fails": fails,
        "categories": [
            {"name": cat, "checks": chks}
            for cat, chks in categories.items()
        ],
    }
