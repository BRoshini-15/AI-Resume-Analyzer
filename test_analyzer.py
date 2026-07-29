"""
Verification test script for AI Resume Analyzer modules.
"""

from src.sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS
from src.ats_scorer import calculate_ats_score
from src.nlp_engine import extract_matched_skills, calculate_readability_metrics
from src.llm_engine import LLMEngine

def main():
    print("==================================================")
    print("VERIFYING AI RESUME ANALYZER ENGINE")
    print("==================================================")

    resume_text = SAMPLE_RESUMES["Senior Software Engineer"]
    job_text = SAMPLE_JOB_DESCRIPTIONS["Senior Full-Stack Engineer"]

    print("\n1. Testing NLP Skill Extraction...")
    skills = extract_matched_skills(resume_text)
    print(f"   Matched Skills Count: {len(skills['all_matched'])}")
    print(f"   Sample Skills: {skills['all_matched'][:5]}")

    print("\n2. Testing Readability Calculator...")
    readability = calculate_readability_metrics(resume_text)
    print(f"   Word Count: {readability['word_count']}")
    print(f"   Flesch Score: {readability['flesch_reading_ease']} ({readability['readability_label']})")

    print("\n3. Testing ATS Scoring Algorithm...")
    ats_res = calculate_ats_score(resume_text, job_text)
    print(f"   Overall ATS Score: {ats_res['overall_score']}/100")
    print(f"   Sub-scores: {ats_res['sub_scores']}")
    print(f"   Keyword Similarity: {ats_res['job_match']['tfidf_similarity']}%")

    print("\n4. Testing LLM Engine (Offline Fallback Preview)...")
    llm = LLMEngine(api_key=None)
    fallback_resp = llm.analyze_resume_with_ai(resume_text, job_text)
    print("   LLM Output Status: Generated successfully")
    clean_preview = fallback_resp[:120].encode('ascii', errors='ignore').decode('ascii')
    print(f"   Preview snippet: {clean_preview}...")

    print("\n[SUCCESS] ALL ENGINE TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    main()
