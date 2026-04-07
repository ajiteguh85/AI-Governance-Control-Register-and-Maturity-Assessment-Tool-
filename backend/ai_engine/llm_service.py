"""LLM-powered AI services for recruitment workflows."""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for AI-powered text generation and analysis using OpenAI API."""

    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-4')
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        return self._client

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        if not self.client:
            return self._fallback_response(user_prompt)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return self._fallback_response(user_prompt)

    def _fallback_response(self, prompt: str) -> str:
        return (
            "AI analysis is currently unavailable. Please configure your "
            "OpenAI API key in the environment settings."
        )

    def generate_candidate_summary(self, resume_text: str) -> str:
        system = (
            "You are a recruitment AI assistant. Analyze the resume and provide a concise "
            "professional summary (3-4 sentences) highlighting key qualifications, experience, "
            "and notable achievements. Be objective and factual."
        )
        return self._call_llm(system, f"Resume:\n{resume_text[:3000]}", temperature=0.3)

    def generate_job_description(self, title: str, requirements: list,
                                  department: str = "", extra_context: str = "") -> str:
        system = (
            "You are a recruitment AI assistant. Generate a professional, engaging job description "
            "that is inclusive and compelling. Include sections: About the Role, Responsibilities, "
            "Requirements, and What We Offer. Use clear, concise language."
        )
        user = f"Title: {title}\nDepartment: {department}\nKey Requirements: {', '.join(requirements)}\n"
        if extra_context:
            user += f"Additional Context: {extra_context}"
        return self._call_llm(system, user, temperature=0.7)

    def generate_interview_questions(self, job_title: str, required_skills: list,
                                      candidate_summary: str = "") -> list:
        system = (
            "You are a recruitment AI assistant. Generate 8-10 interview questions tailored to the "
            "role. Include a mix of technical, behavioral, and situational questions. Return as a "
            "JSON array of strings. Only return the JSON array, no other text."
        )
        user = f"Role: {job_title}\nRequired Skills: {', '.join(required_skills)}\n"
        if candidate_summary:
            user += f"Candidate Background: {candidate_summary}"
        result = self._call_llm(system, user, temperature=0.6)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            skill1 = required_skills[0] if required_skills else 'this field'
            skill2 = required_skills[1] if len(required_skills) > 1 else 'architecture'
            return [
                f"Tell me about your experience with {skill1}.",
                "Describe a challenging project you've led and how you handled it.",
                "How do you approach learning new technologies?",
                "Tell me about a time you had to work under pressure.",
                "Where do you see yourself in 3-5 years?",
                f"How would you handle a technical disagreement about {skill2}?",
                "What's your approach to code reviews and mentoring?",
                "Describe your ideal team culture.",
            ]

    def generate_match_explanation(self, candidate_name: str, job_title: str,
                                    score_data: dict) -> str:
        system = (
            "You are a recruitment AI assistant. Write a brief (2-3 sentences) explanation of "
            "how well this candidate matches the job. Be specific about strengths and gaps."
        )
        user = (
            f"Candidate: {candidate_name}\nJob: {job_title}\n"
            f"Overall Score: {score_data.get('overall_score', 'N/A')}%\n"
            f"Skill Match: {score_data.get('skill_match', 'N/A')}%\n"
            f"Matched Skills: {', '.join(score_data.get('matched_skills', []))}\n"
            f"Missing Skills: {', '.join(score_data.get('missing_skills', []))}\n"
            f"Experience Score: {score_data.get('experience_score', 'N/A')}%"
        )
        return self._call_llm(system, user, temperature=0.4)

    def screen_resume(self, resume_text: str, job_requirements: list) -> dict:
        system = (
            "You are a recruitment AI assistant performing resume screening. Analyze the resume "
            "against the job requirements. Return a JSON object with: 'pass' (boolean), "
            "'confidence' (0-100), 'strengths' (list of strings), 'concerns' (list of strings), "
            "'recommendation' (string). Only return valid JSON."
        )
        user = (
            f"Resume:\n{resume_text[:3000]}\n\n"
            f"Job Requirements:\n" + "\n".join(f"- {r}" for r in job_requirements)
        )
        result = self._call_llm(system, user, temperature=0.3)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                'pass': True,
                'confidence': 50,
                'strengths': ['Unable to perform detailed AI analysis'],
                'concerns': ['Manual review recommended'],
                'recommendation': 'Please review this candidate manually.',
            }
