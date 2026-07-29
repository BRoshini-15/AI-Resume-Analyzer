"""
LLM Engine - Integration with Google Gemini API with intelligent offline fallback.
"""

import os
from typing import Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from src.prompts import (
    ATS_SYSTEM_PROMPT,
    STAR_BULLET_REWRITER_PROMPT,
    INTERVIEW_COACH_PROMPT,
    COVER_LETTER_PROMPT
)

def _load_env_key() -> str:
    """Reads GEMINI_API_KEY from .env file if present."""
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key
    
    # Try reading .env file from project root
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
        except Exception:
            pass
    return ""

class LLMEngine:
    """
    Handles LLM interactions via Google Gemini API with smart offline fallback.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or _load_env_key()
        self.client = None
        self.init_error: Optional[str] = None

        if not GENAI_AVAILABLE:
            if self.api_key:
                self.init_error = "google-genai package is not installed (pip install google-genai)"
        elif self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.client = None
                self.init_error = f"{type(e).__name__}: {e}"

    def is_connected(self) -> bool:
        return self.client is not None

    def generate_response(self, prompt: str, system_instruction: Optional[str] = None, temperature: float = 0.3, model_name: str = "gemini-3.6-flash") -> str:
        """
        Generates text completion using Gemini LLM if connected, else returns offline synthesis.
        """
        if self.client:
            models_to_try = [model_name, "gemini-3.6-flash", "gemini-3.1-flash"]
            # Deduplicate preserving order
            models_to_try = list(dict.fromkeys(models_to_try))

            last_error = None
            for m_name in models_to_try:
                try:
                    config = types.GenerateContentConfig(
                        temperature=temperature,
                    )
                    if system_instruction:
                        config.system_instruction = system_instruction

                    response = self.client.models.generate_content(
                        model=m_name,
                        contents=prompt,
                        config=config
                    )
                    return response.text
                except Exception as e:
                    last_error = e
                    continue

            self.init_error = f"{type(last_error).__name__}: {last_error}" if last_error else self.init_error
            return f"⚠️ LLM API Error: {str(last_error)}\n\n(Falling back to offline preview logic)"

        return self._generate_offline_fallback(prompt, system_instruction)

    def analyze_resume_with_ai(self, resume_text: str, job_text: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
        sys_instruction = system_prompt or ATS_SYSTEM_PROMPT
        user_prompt = f"Candidate Resume Text:\n{resume_text}\n\n"
        if job_text:
            user_prompt += f"Target Job Description:\n{job_text}\n\n"
        user_prompt += "Please provide your comprehensive executive feedback and ATS improvement report."
        
        return self.generate_response(user_prompt, system_instruction=sys_instruction)

    def rewrite_bullets(self, raw_bullets: str, context: str = "") -> str:
        prompt = STAR_BULLET_REWRITER_PROMPT.format(bullet_points=raw_bullets, context=context)
        return self.generate_response(prompt, temperature=0.5)

    def generate_interview_questions(self, resume_text: str, job_text: str) -> str:
        prompt = INTERVIEW_COACH_PROMPT.format(resume_text=resume_text[:2000], job_description=job_text[:2000])
        return self.generate_response(prompt, temperature=0.4)

    def generate_cover_letter(self, resume_text: str, job_text: str) -> str:
        prompt = COVER_LETTER_PROMPT.format(resume_text=resume_text[:2000], job_description=job_text[:2000])
        return self.generate_response(prompt, temperature=0.6)

    def _generate_offline_fallback(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generates realistic, structured response preview when offline / without API key.
        """
        return """### 🤖 Offline Feedback Preview (Gemini API Key missing or not set)

> **Note:** To enable real-time dynamic Gemini LLM generation, enter your Gemini API Key in the sidebar.

#### 💡 General Resume Feedback
- **Structure & Layout:** Your resume exhibits clear section boundaries. Ensure standard section headings like "Work Experience", "Education", and "Skills" are used.
- **Action Verbs & Impact:** Increase the density of quantitative metrics (percentages, team sizes, dollar amounts, scale).
- **Keyword Alignment:** Ensure technical skills mentioned in the target job posting appear naturally within your experience bullet points, not just in a standalone skills list.

#### 🎯 Quick Recommendation:
1. Rephrase passive sentences to start with strong verbs like *Engineered*, *Spearheaded*, *Optimized*.
2. Add explicit metrics (e.g. *"Improved query performance by 40% using indexing"*).
3. Tailor the professional summary to match the specific title of your target job posting.
"""
