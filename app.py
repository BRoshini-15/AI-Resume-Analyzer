"""
AI Resume Analyzer - Main Streamlit Dashboard Application
"""

import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.parsers import parse_uploaded_file, clean_text
from src.nlp_engine import (
    extract_contact_info,
    extract_matched_skills,
    calculate_readability_metrics,
    analyze_impact_metrics,
    check_section_headers,
    analyze_job_match
)
from src.ats_scorer import calculate_ats_score
from src.prompts import ATS_SYSTEM_PROMPT, STAR_BULLET_REWRITER_PROMPT
from src.llm_engine import LLMEngine
from src.sample_data import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS

# Page Configuration
st.set_page_config(
    page_title="AI Resume Analyzer & ATS Coach",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Dark Glassmorphic Aesthetic
st.markdown("""
<style>
    /* Dark Theme Styles */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }

    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    /* Score Badges */
    .score-badge {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin: 10px 0;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .badge-excellent { color: #10b981; font-weight: bold; }
    .badge-good { color: #f59e0b; font-weight: bold; }
    .badge-poor { color: #ef4444; font-weight: bold; }

    /* Custom Metric Pills */
    .metric-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }
    .pill-matched { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }
    .pill-missing { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }
    .pill-skill { background-color: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid #6366f1; }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre;
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(99, 102, 241, 0.2) !important;
        border-bottom: 2px solid #6366f1 !important;
    }

    /* Text Input & Text Area Black Font Styling */
    .stTextArea textarea, .stTextInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.title("⚡ AI Resume Analyzer & ATS Coach")
st.caption("Powered by LLM, Prompt Engineering, NLP, and ATS Scoring Algorithms")

# Sidebar Controls
st.sidebar.header("🔑 Model & Data Setup")

api_key = st.sidebar.text_input(
    "Google API Key (Optional)",
    type="password",
    help="Enter Gemini API key to activate live generative AI features. If empty, app uses built-in offline NLP engine."
)

llm = LLMEngine(api_key=api_key)
if llm.is_connected():
    st.sidebar.success("🟢 Gemini API Connected")
else:
    st.sidebar.info("💡 Offline Mode (Local NLP active)")

st.sidebar.markdown("---")
st.sidebar.subheader("📄 Resume Input")


uploaded_file = st.sidebar.file_uploader(
    "Upload Resume (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Job Description Input")


custom_jd_input = st.sidebar.text_area(
    "Target Job Description",
    height=150,
    placeholder="Paste target job description here for side-by-side ATS match analysis..."
)

# Determine text inputs
resume_text = ""
if uploaded_file is not None:
    extracted, err = parse_uploaded_file(uploaded_file)
    if err:
        st.error(err)
    else:
        resume_text = extracted

job_text = ""
if custom_jd_input.strip():
    job_text = custom_jd_input
if not resume_text:
    st.info("👈 Please **Upload a PDF/DOCX resume** in the sidebar to begin analysis.")
    st.stop()

# Run ATS Analysis Engine
ats_data = calculate_ats_score(resume_text, job_text)

# Main Navigation Tabs
tab_overview, tab_job_match, tab_bullet_ai, tab_prompt_studio, tab_export = st.tabs([
    "📊 ATS Scorecard",
    "🎯 Job Match & Skills",
    "✏️ STAR Bullet Rewriter & AI",
    "🧪 Prompt Studio",
    "📄 Report & Export"
])

# ----------------------------------------------------
# TAB 1: ATS SCORECARD & OVERVIEW
# ----------------------------------------------------
with tab_overview:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Overall ATS Score")
        score = ats_data["overall_score"]
        st.markdown(f"<div class='score-badge'>{score}/100</div>", unsafe_allow_html=True)

        if score >= 80:
            st.markdown("<div style='text-align:center;' class='badge-excellent'>🟢 Excellent (High ATS Pass Rate)</div>", unsafe_allow_html=True)
        elif score >= 60:
            st.markdown("<div style='text-align:center;' class='badge-good'>🟡 Moderate Match (Room for Optimization)</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center;' class='badge-poor'>🔴 Needs Improvement (Risk of Filtering)</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Sub-dimensional Score Breakdown")
        
        sub_scores = ats_data["sub_scores"]
        df_sub = pd.DataFrame(list(sub_scores.items()), columns=["Category", "Score"])
        
        fig = px.bar(
            df_sub,
            x="Score",
            y="Category",
            orientation='h',
            range_x=[0, 100],
            color="Score",
            color_continuous_scale="Viridis",
            text="Score"
        )
        fig.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#ffffff")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### Quick Stats")
        rd = ats_data["readability"]
        imp = ats_data["impact_metrics"]
        st.metric("Word Count", rd["word_count"])
        st.metric("Flesch Readability", f"{rd['flesch_reading_ease']} ({rd['readability_label']})")
        st.metric("Action Verbs Used", imp["action_verb_count"])
        st.metric("Quantified Metrics", imp["metric_statement_count"])
        st.markdown("</div>", unsafe_allow_html=True)

    # Verification Checks & Insights
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 📋 Section & Contact Checks")
        ci = ats_data["contact_info"]
        sec = ats_data["sections_info"]
        
        st.write(f"• **Email Detected:** {'✅ ' + ci['email'] if ci['email'] else '❌ Missing'}")
        st.write(f"• **Phone Detected:** {'✅ ' + ci['phone'] if ci['phone'] else '❌ Missing'}")
        st.write(f"• **LinkedIn / GitHub:** {'✅ Found' if (ci['linkedin'] or ci['github']) else '⚠️ Optional'}")
        st.write(f"• **Detected Sections:** {', '.join(sec['detected_sections'])}")
        if sec['missing_sections']:
            st.write(f"• **Missing Sections:** <span style='color:#ef4444;'>{', '.join(sec['missing_sections'])}</span>", unsafe_allow_html=True)

    with col_b:
        st.markdown("#### 💡 Actionable Insights")
        for succ in ats_data["successes"]:
            st.success(succ)
        for warn in ats_data["warnings"]:
            st.warning(warn)

    if ats_data["recommendations"]:
        st.markdown("---")
        st.markdown("### 📌 Top Recommended Fixes")
        for rec in ats_data["recommendations"]:
            st.write(f"👉 {rec}")

# ----------------------------------------------------
# TAB 2: JOB MATCH & SKILL GAPS
# ----------------------------------------------------
with tab_job_match:
    if not job_text.strip():
        st.info("💡 Paste a **Job Description** in the sidebar to unlock side-by-side skill gap comparison and similarity scoring.")
    else:
        jm = ats_data["job_match"]
        c1, c2, c3 = st.columns(3)
        c1.metric("TF-IDF Keyword Similarity", f"{jm['tfidf_similarity']}%")
        c2.metric("Skill Overlap Ratio", f"{jm['skill_overlap_ratio']}%")
        c3.metric("Total Job Skills Identified", jm["total_job_skills"])

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("### ✅ Matched Skills in Resume")
            if jm["matched_skills"]:
                pills_html = "".join([f"<span class='metric-pill pill-matched'>{s}</span>" for s in jm["matched_skills"]])
                st.markdown(pills_html, unsafe_allow_html=True)
            else:
                st.write("No direct skills overlap detected.")

        with col_m2:
            st.markdown("### ❌ Missing Job Skills")
            if jm["missing_skills"]:
                pills_html = "".join([f"<span class='metric-pill pill-missing'>{s}</span>" for s in jm["missing_skills"]])
                st.markdown(pills_html, unsafe_allow_html=True)
            else:
                st.success("Great job! All key job skills are present in your resume.")

    st.markdown("---")
    st.markdown("### 🔍 Detected Skill Taxonomy in Resume")
    cats = ats_data["skills_summary"]["categorized"]
    for cat_name, skill_list in cats.items():
        if skill_list:
            st.markdown(f"**{cat_name}:**")
            pills_html = "".join([f"<span class='metric-pill pill-skill'>{s}</span>" for s in skill_list])
            st.markdown(pills_html, unsafe_allow_html=True)

# ----------------------------------------------------
# TAB 3: STAR BULLET REWRITER & AI COACH
# ----------------------------------------------------
with tab_bullet_ai:
    st.markdown("### ✏️ STAR Bullet Rewriter")
    st.caption("Paste weak bullet points to transform them into high-impact STAR method achievements with quantitative metrics.")

    sample_bullet = "Responsible for building backend services and writing unit tests."
    user_bullet = st.text_area("Enter Resume Bullet Point:", value=sample_bullet, height=80)

    if st.button("🚀 Enhance Bullet Point with AI"):
        with st.spinner("Rewriting bullet point using Prompt Engineering rules..."):
            enhanced_output = llm.rewrite_bullets(user_bullet, context=job_text[:500] if job_text else "")
            st.markdown("#### Enhanced Bullet Variations:")
            st.markdown(enhanced_output)

    st.markdown("---")
    col_ai1, col_ai2 = st.columns(2)

    with col_ai1:
        st.markdown("### 🎯 AI Interview Question Generator")
        if st.button("Generate Interview Prep Questions"):
            if not job_text:
                st.warning("Please provide a Job Description in the sidebar to generate tailored questions.")
            else:
                with st.spinner("Generating role-specific interview questions..."):
                    questions = llm.generate_interview_questions(resume_text, job_text)
                    st.markdown(questions)

    with col_ai2:
        st.markdown("### ✉️ Tailored Cover Letter Builder")
        if st.button("Generate Cover Letter"):
            if not job_text:
                st.warning("Please provide a Job Description in the sidebar to craft a cover letter.")
            else:
                with st.spinner("Drafting tailored cover letter..."):
                    cover_letter = llm.generate_cover_letter(resume_text, job_text)
                    st.markdown(cover_letter)

# ----------------------------------------------------
# TAB 4: PROMPT STUDIO
# ----------------------------------------------------
with tab_prompt_studio:
    st.markdown("### 🧪 Prompt Engineering Studio")
    st.caption("Inspect, customize, and test system prompts used by the AI Resume Analyzer.")

    selected_prompt_type = st.selectbox(
        "Select System Prompt Template to Inspect/Edit:",
        ["Executive ATS Evaluation", "STAR Bullet Rewriter"]
    )

    if selected_prompt_type == "Executive ATS Evaluation":
        default_prompt = ATS_SYSTEM_PROMPT
    else:
        default_prompt = STAR_BULLET_REWRITER_PROMPT

    custom_system_prompt = st.text_area("System Prompt:", value=default_prompt, height=200)

    temp = st.slider("Model Temperature", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

    if st.button("▶️ Execute Prompt against Current Resume"):
        with st.spinner("Executing custom prompt via LLM Engine..."):
            res = llm.analyze_resume_with_ai(resume_text, job_text, system_prompt=custom_system_prompt)
            st.markdown("#### Execution Output:")
            st.markdown(res)

# ----------------------------------------------------
# TAB 5: REPORT & EXPORT
# ----------------------------------------------------
with tab_export:
    st.markdown("### 📄 Full Analysis Report & Export")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.download_button(
            label="💾 Download Evaluation Report (JSON)",
            data=json.dumps(ats_data, indent=2),
            file_name="ats_resume_evaluation_report.json",
            mime="application/json"
        )
    with col_e2:
        report_text = f"""==================================================
AI RESUME ANALYZER & ATS EVALUATION REPORT
==================================================
Overall ATS Score: {ats_data['overall_score']}/100

Sub-Scores:
- Keyword & Role Match: {ats_data['sub_scores']['Keyword & Role Match']}/100
- Skills Alignment: {ats_data['sub_scores']['Skills Alignment']}/100
- Formatting & Health: {ats_data['sub_scores']['Formatting & Health']}/100
- Impact & Metrics: {ats_data['sub_scores']['Impact & Metrics']}/100

Readability & Stats:
- Word Count: {ats_data['readability']['word_count']}
- Flesch Reading Ease: {ats_data['readability']['flesch_reading_ease']}
- Action Verbs Count: {ats_data['impact_metrics']['action_verb_count']}

Recommendations:
""" + "\n".join([f"- {r}" for r in ats_data["recommendations"]])

        st.download_button(
            label="📄 Download Summary Report (TXT)",
            data=report_text,
            file_name="ats_resume_summary.txt",
            mime="text/plain"
        )

    st.markdown("---")
    st.markdown("### 🔍 Raw Extracted Resume Text")
    st.text_area("Extracted Text Preview:", value=resume_text, height=300)
