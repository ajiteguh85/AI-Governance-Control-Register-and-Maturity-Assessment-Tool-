"""API views for AI engine features."""
import os
import tempfile
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from candidates.models import Candidate
from jobs.models import Job, Application
from .resume_parser import ResumeParser
from .scoring import CandidateScorer
from .llm_service import LLMService

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def parse_resume(request):
    """Parse an uploaded resume and extract information."""
    file = request.FILES.get('resume')
    if not file:
        return Response({'error': 'No resume file provided'}, status=status.HTTP_400_BAD_REQUEST)

    ext = os.path.splitext(file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        for chunk in file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        parser = ResumeParser()
        result = parser.parse(tmp_path)
        if result.get('raw_text'):
            llm = LLMService()
            result['ai_summary'] = llm.generate_candidate_summary(result['raw_text'])
        return Response(result)
    finally:
        os.unlink(tmp_path)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def score_candidate(request):
    """Score a candidate against a specific job."""
    candidate_id = request.data.get('candidate_id')
    job_id = request.data.get('job_id')
    if not candidate_id or not job_id:
        return Response(
            {'error': 'Both candidate_id and job_id are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        candidate = Candidate.objects.get(id=candidate_id)
        job = Job.objects.get(id=job_id)
    except (Candidate.DoesNotExist, Job.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    scorer = CandidateScorer()
    scores = scorer.score_candidate(candidate, job)

    llm = LLMService()
    scores['explanation'] = llm.generate_match_explanation(
        candidate.full_name, job.title, scores,
    )

    application = Application.objects.filter(job=job, candidate=candidate).first()
    if application:
        application.ai_match_score = scores['overall_score']
        application.ai_match_explanation = scores['explanation']
        application.save()

    return Response(scores)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rank_candidates_for_job(request, job_id):
    """Rank all candidates for a job."""
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

    candidates = Candidate.objects.filter(is_active=True)
    scorer = CandidateScorer()
    rankings = scorer.rank_candidates(candidates, job)

    results = []
    for item in rankings[:50]:
        c = item['candidate']
        results.append({
            'candidate_id': str(c.id),
            'name': c.full_name,
            'current_title': c.current_title,
            'scores': item['scores'],
        })
    return Response({'job': str(job.id), 'job_title': job.title, 'rankings': results})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_job_description(request):
    """Generate an AI-powered job description."""
    title = request.data.get('title', '')
    if not title:
        return Response({'error': 'Job title is required'}, status=status.HTTP_400_BAD_REQUEST)
    requirements = request.data.get('requirements', [])
    department = request.data.get('department', '')
    context = request.data.get('context', '')

    llm = LLMService()
    description = llm.generate_job_description(title, requirements, department, context)
    return Response({'description': description})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_interview_questions(request):
    """Generate interview questions for a role."""
    job_id = request.data.get('job_id')
    candidate_id = request.data.get('candidate_id')
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

    candidate_summary = ""
    if candidate_id:
        try:
            candidate_summary = Candidate.objects.get(id=candidate_id).ai_summary
        except Candidate.DoesNotExist:
            pass

    llm = LLMService()
    questions = llm.generate_interview_questions(
        job.title, job.required_skills, candidate_summary,
    )
    return Response({'questions': questions})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def screen_resume_against_job(request):
    """Screen a candidate's resume against job requirements."""
    candidate_id = request.data.get('candidate_id')
    job_id = request.data.get('job_id')
    try:
        candidate = Candidate.objects.get(id=candidate_id)
        job = Job.objects.get(id=job_id)
    except (Candidate.DoesNotExist, Job.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    if not candidate.resume_text:
        return Response(
            {'error': 'Candidate has no resume text. Upload and parse a resume first.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    llm = LLMService()
    result = llm.screen_resume(candidate.resume_text, job.requirements)
    return Response(result)
