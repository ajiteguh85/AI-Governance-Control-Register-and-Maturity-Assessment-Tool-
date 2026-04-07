"""Resume parsing service using NLP and pattern matching."""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

TECH_SKILLS = [
    'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'ruby', 'php',
    'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'node.js', 'express',
    'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
    'git', 'ci/cd', 'jenkins', 'github actions',
    'machine learning', 'deep learning', 'nlp', 'computer vision',
    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
    'html', 'css', 'sass', 'tailwind', 'bootstrap',
    'rest api', 'graphql', 'microservices', 'agile', 'scrum',
    'data analysis', 'data engineering', 'etl', 'spark', 'hadoop',
]

SOFT_SKILLS = [
    'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
    'adaptability', 'time management', 'creativity', 'emotional intelligence',
    'conflict resolution', 'decision making', 'mentoring', 'coaching',
    'strategic thinking', 'negotiation', 'presentation', 'collaboration',
]


class ResumeParser:
    """Parse resumes and extract structured information."""

    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""

    def extract_text_from_docx(self, file_path: str) -> str:
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs]).strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return ""

    def extract_text(self, file_path: str) -> str:
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.docx', '.doc')):
            return self.extract_text_from_docx(file_path)
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        return ""

    def extract_email(self, text: str) -> Optional[str]:
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}'
        match = re.search(pattern, text)
        return match.group(0).strip() if match else None

    def extract_skills(self, text: str) -> dict:
        text_lower = text.lower()
        technical = [s for s in TECH_SKILLS if s.lower() in text_lower]
        soft = [s for s in SOFT_SKILLS if s.lower() in text_lower]
        return {
            'technical': list(set(technical)),
            'soft': list(set(soft)),
            'all': list(set(technical + soft)),
        }

    def extract_years_experience(self, text: str) -> int:
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s+)?experience',
            r'experience\s*:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:in|of)\s+(?:software|development|engineering)',
        ]
        max_years = 0
        for pattern in patterns:
            for match in re.findall(pattern, text, re.IGNORECASE):
                years = int(match)
                if years < 50:
                    max_years = max(max_years, years)
        return max_years

    def extract_linkedin(self, text: str) -> Optional[str]:
        pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def parse(self, file_path: str) -> dict:
        text = self.extract_text(file_path)
        if not text:
            return {'error': 'Could not extract text from file', 'raw_text': ''}
        skills = self.extract_skills(text)
        return {
            'raw_text': text,
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'skills': skills,
            'years_experience': self.extract_years_experience(text),
            'linkedin_url': self.extract_linkedin(text),
        }
