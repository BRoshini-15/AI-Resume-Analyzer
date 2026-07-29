"""
ATS Scoring Engine calculating overall and sub-dimensional scores with actionable advice.
"""

from typing import Dict, Any, Optional
from src.config import ATS_WEIGHTS
from src.nlp_engine import (
    analyze_job_match,
    extract_contact_info,
    extract_matched_skills,
    calculate_readability_metrics,
    analyze_impact_metrics,
    check_section_headers
)

def calculate_ats_score(resume_text: str, job_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Computes complete ATS Evaluation including scores, metrics, and recommendations.
    """
    # 1. Contact & Section Headers check
    contact_info = extract_contact_info(resume_text)
    sections_info = check_section_headers(resume_text)

    # 2. Readability & Length check
    readability = calculate_readability_metrics(resume_text)

    # 3. Impact & Action metrics
    impact = analyze_impact_metrics(resume_text)

    # 4. Skills extraction
    skills = extract_matched_skills(resume_text)
    all_resume_skills = skills["all_matched"]

    # --- Dimension 1: Formatting & Structure Score (0-100) ---
    format_score = 0.0
    if contact_info["email"]: format_score += 15.0
    if contact_info["phone"]: format_score += 15.0
    format_score += (sections_info["section_coverage_ratio"] * 40.0)
    wc = readability["word_count"]
    if 300 <= wc <= 1000:
        format_score += 30.0
    elif 200 <= wc < 300 or 1000 < wc <= 1500:
        format_score += 20.0
    else:
        format_score += 10.0
    format_score = min(100.0, format_score)

    # --- Dimension 2: Impact & Action Verbs Score (0-100) ---
    impact_score = 0.0
    if impact["action_verb_count"] >= 8: impact_score += 40.0
    elif impact["action_verb_count"] >= 4: impact_score += 25.0
    else: impact_score += 10.0
    if impact["metric_statement_count"] >= 5: impact_score += 40.0
    elif impact["metric_statement_count"] >= 2: impact_score += 25.0
    else: impact_score += 10.0
    if 50.0 <= readability["flesch_reading_ease"] <= 80.0: impact_score += 20.0
    else: impact_score += 10.0
    impact_score = min(100.0, impact_score)

    # --- Dimension 3: Skills Alignment Score (0-100) ---
    skills_score = 0.0
    if job_text and job_text.strip():
        job_match = analyze_job_match(resume_text, job_text)
        skills_score = job_match["skill_overlap_ratio"]
        keyword_match_score = (job_match["tfidf_similarity"] * 0.4) + (job_match["skill_overlap_ratio"] * 0.6)
    else:
        job_match = None
        if len(all_resume_skills) >= 12: skills_score = 90.0
        elif len(all_resume_skills) >= 7: skills_score = 75.0
        elif len(all_resume_skills) >= 4: skills_score = 60.0
        else: skills_score = 40.0
        keyword_match_score = skills_score

    # Calculate Weighted Overall ATS Score
    w = ATS_WEIGHTS
    overall_score = (
        (keyword_match_score * w["keyword_match"]) +
        (skills_score * w["skills_alignment"]) +
        (format_score * w["formatting"]) +
        (impact_score * w["impact_metrics"])
    )
    overall_score = round(min(100.0, max(0.0, overall_score)), 1)

    # Generate Actionable Insights & Warnings
    warnings = []
    successes = []
    recommendations = []

    if not contact_info["email"]:
        warnings.append("Missing contact email address.")
        recommendations.append("Ensure your email address is clearly visible at the top of the resume.")
    else:
        successes.append(f"Contact email detected ({contact_info['email']}).")

    if not contact_info["phone"]:
        warnings.append("Missing phone number.")
        recommendations.append("Add a direct phone number to facilitate recruiter outreach.")

    if sections_info["missing_sections"]:
        missing_str = ", ".join(sections_info["missing_sections"][:3])
        warnings.append(f"Missing recommended ATS section headers: {missing_str}")
        recommendations.append(f"Add standard section headers like '{missing_str}' to improve ATS parsing accuracy.")

    if impact["action_verb_count"] < 5:
        warnings.append("Low action verb count detected.")
        recommendations.append("Begin bullet points with dynamic action verbs like 'Architected', 'Spearheaded', 'Optimized'.")
    else:
        successes.append(f"Strong action verb count ({impact['action_verb_count']} unique verbs).")

    if impact["metric_statement_count"] < 3:
        warnings.append("Few quantifiable metrics or results found.")
        recommendations.append("Include hard metrics (e.g. 'Increased conversion by 24%', 'Reduced latency by 150ms').")

    if job_match and job_match["missing_skills"]:
        top_missing = ", ".join(job_match["missing_skills"][:5])
        recommendations.append(f"Target role keywords missing from resume: {top_missing}")

    return {
        "overall_score": overall_score,
        "sub_scores": {
            "Keyword & Role Match": round(keyword_match_score, 1),
            "Skills Alignment": round(skills_score, 1),
            "Formatting & Health": round(format_score, 1),
            "Impact & Metrics": round(impact_score, 1)
        },
        "contact_info": contact_info,
        "sections_info": sections_info,
        "readability": readability,
        "impact_metrics": impact,
        "skills_summary": skills,
        "job_match": job_match,
        "warnings": warnings,
        "successes": successes,
        "recommendations": recommendations
    }
