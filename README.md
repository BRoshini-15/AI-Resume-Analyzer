<<<<<<< HEAD
# AI Resume Analyzer ⚡

An intelligent, full-featured Python application built with **LLM (Google Gemini)**, **Prompt Engineering**, **NLP**, and **ATS Scoring Algorithms**.

![AI Resume Analyzer](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?style=flat-square&logo=streamlit)
![Google Gemini](https://img.shields.io/badge/Gemini-LLM-brightgreen?style=flat-square)

---

## 🌟 Key Features

1. **📊 Multi-Factor ATS Scoring Engine**:
   - Calculates overall ATS Score (0-100) based on weighted metrics:
     - **Keyword & Job Match (35%)**: TF-IDF cosine similarity & N-gram key phrase overlap.
     - **Skills Alignment (25%)**: Category-wise skill taxonomy search (Languages, Frameworks, Cloud, ML, Agile, Soft Skills).
     - **Formatting & Structure (20%)**: Section header detection, contact info extraction (Email, Phone, LinkedIn, GitHub), document length.
     - **Impact & Metrics (20%)**: Action verb density, quantifiable numbers/percentages/dollars, Flesch Reading Ease score.

2. **🤖 LLM Integration (Google Gemini)**:
   - Live AI executive feedback and deep resume critique using `gemini-2.5-flash`.
   - **Offline Fallback Mode**: If no API key is set, local deterministic NLP logic handles analysis seamlessly without errors.

3. **🧠 Prompt Engineering & Prompt Studio**:
   - Structured JSON-enforcing system prompts.
   - STAR Method (Situation, Task, Action, Result) bullet point rewriter.
   - **Interactive Prompt Studio**: Inspect, customize, and test prompt templates & temperatures directly in the app.

4. **🎯 Job Match & Skill Gap Analysis**:
   - Side-by-side comparison of candidate resume vs. target job description.
   - Highlights **Matched Skills** vs **Missing Essential Skills**.

5. **📄 PDF / DOCX Support & Export**:
   - Supports uploading PDF, DOCX, and TXT resumes.
   - Exports comprehensive JSON or TXT evaluation reports.

---

## 📁 Directory Structure

```
ai-resume-analyzer/
├── app.py                      # Main Streamlit dashboard UI
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guide and features
└── src/
    ├── __init__.py
    ├── config.py               # Skill taxonomies, scoring weights, action verbs
    ├── parsers.py              # PDF, DOCX, TXT text extraction & cleaning
    ├── nlp_engine.py           # TF-IDF similarity, Flesch score, skill taxonomy
    ├── ats_scorer.py           # Multi-factor ATS scoring algorithm
    ├── llm_engine.py           # Gemini API client & offline fallback engine
    ├── prompts.py              # System prompt templates
    └── sample_data.py          # Pre-loaded sample resumes & job descriptions
```

---

## 🚀 Quick Start Guide

### 1. Set Up Virtual Environment & Dependencies

```bash
# Navigate to project directory
cd C:\Users\baika\.gemini\antigravity-ide\scratch\ai-resume-analyzer

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Launch the Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.
=======
# AI-Resume-Analyzer
>>>>>>> bb8001837bae74f0609f88304d72b7f5dc9f2155
