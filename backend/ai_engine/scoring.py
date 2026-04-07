"""AI-powered candidate scoring and ranking."""
import logging

logger = logging.getLogger(__name__)


class CandidateScorer:
    """Score candidates based on job requirements."""

    def calculate_skill_match(self, candidate_skills: list, required_skills: list) -> float:
        if not required_skills:
            return 0.0
        candidate_lower = {s.lower() for s in candidate_skills}
        required_lower = {s.lower() for s in required_skills}
        matches = candidate_lower & required_lower
        return len(matches) / len(required_lower) * 100

    def calculate_experience_score(self, candidate_years: int, required_level: str) -> float:
        level_ranges = {
            'entry': (0, 2),
            'mid': (2, 5),
            'senior': (5, 10),
            'lead': (8, 15),
            'executive': (12, 30),
        }
        min_years, ideal_years = level_ranges.get(required_level, (0, 5))
        if candidate_years < min_years:
            return max(0, (candidate_years / min_years) * 50) if min_years > 0 else 50
        elif candidate_years <= ideal_years:
            return 100
        else:
            return max(60, 100 - (candidate_years - ideal_years) * 3)

    def calculate_location_score(self, candidate_location: str, job_location: str, remote_policy: str) -> float:
        if remote_policy == 'remote':
            return 100
        if not candidate_location or not job_location:
            return 50
        if candidate_location.lower() == job_location.lower():
            return 100
        candidate_parts = {p.strip() for p in candidate_location.lower().split(',')}
        job_parts = {p.strip() for p in job_location.lower().split(',')}
        if candidate_parts & job_parts:
            return 80
        return 30 if remote_policy == 'hybrid' else 20

    def score_candidate(self, candidate, job) -> dict:
        skill_score = self.calculate_skill_match(
            candidate.skills + candidate.ai_skills_extracted,
            job.required_skills,
        )
        experience_score = self.calculate_experience_score(
            candidate.years_experience, job.experience_level,
        )
        location_score = self.calculate_location_score(
            candidate.location, job.location, job.remote_policy,
        )
        weights = {'skills': 0.50, 'experience': 0.30, 'location': 0.20}
        overall = (
            skill_score * weights['skills']
            + experience_score * weights['experience']
            + location_score * weights['location']
        )
        candidate_all = set(s.lower() for s in candidate.skills + candidate.ai_skills_extracted)
        required_all = set(s.lower() for s in job.required_skills)
        return {
            'overall_score': round(overall, 1),
            'skill_match': round(skill_score, 1),
            'experience_score': round(experience_score, 1),
            'location_score': round(location_score, 1),
            'matched_skills': list(candidate_all & required_all),
            'missing_skills': list(required_all - candidate_all),
        }

    def rank_candidates(self, candidates, job) -> list:
        scored = []
        for candidate in candidates:
            score_data = self.score_candidate(candidate, job)
            scored.append({'candidate': candidate, 'scores': score_data})
        scored.sort(key=lambda x: x['scores']['overall_score'], reverse=True)
        return scored
