"""
NLP Processing Engine for Text Analysis, Similarity, Readability, and Extraction.
"""

import re
import math
from typing import Dict, List, Set, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.config import SKILL_TAXONOMY, ALL_SKILLS_SET, STRONG_ACTION_VERBS, EXPECTED_SECTIONS

def calculate_tfidf_similarity(text1: str, text2: str) -> float:
    """
    Computes TF-IDF Cosine Similarity between two text documents (0.0 to 1.0).
    """
    if not text1.strip() or not text2.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim)
    except Exception:
        return 0.0

def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extracts email, phone number, and professional URLs (LinkedIn, GitHub).
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9_-]+'
    github_pattern = r'github\.com/[a-zA-Z0-9_-]+'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
    github = re.findall(github_pattern, text, re.IGNORECASE)

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
        "has_contact": bool(emails or phones)
    }

def extract_matched_skills(text: str) -> Dict[str, List[str]]:
    """
    Scans text against the skill taxonomy and categorizes detected skills.
    """
    text_lower = text.lower()
    # Normalize punctuation for token search.
    # NOTE: \b anchors on a word/non-word transition, which fails for tokens
    # ending in symbol characters (e.g. "c++", "c#") when followed by
    # whitespace or punctuation (also non-word) - the trailing symbol can get
    # silently dropped from the match. Split on separators instead so
    # symbol-suffixed skills are captured intact.
    raw_tokens = re.split(r'[\s,;:()\[\]{}"\'!?]+', text_lower)
    cleaned_tokens = set()
    for t in raw_tokens:
        t = t.rstrip('.')  # drop trailing sentence periods, keep leading dots (e.g. ".net")
        if t:
            cleaned_tokens.add(t)

    categorized_skills = {}
    all_matched = []

    for category, skill_list in SKILL_TAXONOMY.items():
        matched_in_cat = []
        for skill in skill_list:
            skill_lower = skill.lower()
            # For multi-word skills like "machine learning" or "spring boot"
            if " " in skill_lower or "-" in skill_lower:
                if skill_lower in text_lower:
                    matched_in_cat.append(skill)
            else:
                if skill_lower in cleaned_tokens:
                    matched_in_cat.append(skill)
        
        categorized_skills[category] = matched_in_cat
        all_matched.extend(matched_in_cat)

    return {
        "categorized": categorized_skills,
        "all_matched": sorted(list(set(all_matched)))
    }

def analyze_job_match(resume_text: str, job_text: str) -> Dict[str, Any]:
    """
    Compares resume text against job description for keyword match & missing skills.
    """
    resume_skills = set(extract_matched_skills(resume_text)["all_matched"])
    job_skills = set(extract_matched_skills(job_text)["all_matched"])

    matched_skills = sorted(list(resume_skills.intersection(job_skills)))
    missing_skills = sorted(list(job_skills.difference(resume_skills)))

    tfidf_sim = calculate_tfidf_similarity(resume_text, job_text)

    skill_overlap_ratio = len(matched_skills) / len(job_skills) if job_skills else 0.5

    return {
        "tfidf_similarity": round(tfidf_sim * 100, 1),
        "skill_overlap_ratio": round(skill_overlap_ratio * 100, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_job_skills": len(job_skills)
    }

def calculate_readability_metrics(text: str) -> Dict[str, Any]:
    """
    Calculates readability statistics and Flesch Reading Ease score.
    """
    words = re.findall(r'\b\w+\b', text)
    # Resume text is often bullet fragments with no terminal punctuation, so
    # split on line breaks too - otherwise sentence_count can collapse toward
    # 1, words_per_sentence spikes, and the Flesch score is unfairly punished.
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]
    word_count = len(words)
    sentence_count = max(len(sentences), 1)

    if word_count == 0:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "flesch_reading_ease": 0.0,
            "readability_label": "N/A"
        }

    # Estimate syllables
    syllable_count = 0
    for word in words:
        w = word.lower()
        count = len(re.findall(r'[aeiouy]{1,2}', w))
        if w.endswith('e'):
            count -= 1
        syllable_count += max(count, 1)

    # Flesch Reading Ease formula
    words_per_sentence = word_count / sentence_count
    syllables_per_word = syllable_count / word_count
    flesch_score = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
    flesch_score = max(0.0, min(100.0, flesch_score))

    if flesch_score >= 70:
        label = "Easy / Very Clear"
    elif flesch_score >= 50:
        label = "Standard Professional"
    elif flesch_score >= 30:
        label = "Complex / Dense"
    else:
        label = "Very Difficult to Read"

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "flesch_reading_ease": round(flesch_score, 1),
        "readability_label": label
    }

def analyze_impact_metrics(text: str) -> Dict[str, Any]:
    """
    Analyzes action verb usage and quantifiable metrics (numbers, $, %).
    """
    words = [w.lower() for w in re.findall(r'\b[a-z]+\b', text)]
    text_lower = text.lower()

    # Detect action verbs
    detected_verbs = sorted(list(set(words).intersection(STRONG_ACTION_VERBS)))

    # Detect metric statements
    metric_pattern = r'(\d+%\s*|\$\d+[\d,]*[kKmMbB]?|\d+x\b|\d+\s*(percent|million|billion|thousand|users|clients|projects|team members|revenue))'
    metrics_found = re.findall(metric_pattern, text_lower, re.IGNORECASE)

    # Count bullet points
    bullets = [line.strip() for line in text.split('\n') if line.strip().startswith(('•', '-', '*', '1.', '2.', '3.'))]

    return {
        "action_verb_count": len(detected_verbs),
        "action_verbs": detected_verbs[:10],
        "metric_statement_count": len(metrics_found),
        "bullet_point_count": len(bullets)
    }

def check_section_headers(text: str) -> Dict[str, Any]:
    """
    Checks for the presence of standard ATS section headers.
    """
    text_lower = text.lower()
    detected = []
    missing = []

    for section in EXPECTED_SECTIONS:
        pattern = r'\b' + re.escape(section) + r'\b'
        if re.search(pattern, text_lower):
            detected.append(section.title())
        else:
            missing.append(section.title())

    return {
        "detected_sections": detected,
        "missing_sections": missing,
        "section_coverage_ratio": len(detected) / len(EXPECTED_SECTIONS)
    }