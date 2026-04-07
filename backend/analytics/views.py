"""Analytics API views for recruitment dashboard."""
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from candidates.models import Candidate
from jobs.models import Job, Application, Interview


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get overview statistics for the dashboard."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    total_candidates = Candidate.objects.filter(is_active=True).count()
    new_candidates_30d = Candidate.objects.filter(created_at__gte=thirty_days_ago).count()
    open_jobs = Job.objects.filter(status='open').count()
    total_applications = Application.objects.count()
    active_applications = Application.objects.exclude(
        status__in=['rejected', 'withdrawn', 'accepted']
    ).count()
    interviews_scheduled = Interview.objects.filter(
        scheduled_at__gte=now, completed=False
    ).count()

    # Pipeline summary
    pipeline = (
        Candidate.objects.filter(is_active=True)
        .values('stage')
        .annotate(count=Count('id'))
        .order_by('stage')
    )

    # Average AI score
    avg_ai_score = Candidate.objects.filter(
        ai_score__isnull=False
    ).aggregate(avg=Avg('ai_score'))['avg']

    return Response({
        'total_candidates': total_candidates,
        'new_candidates_30d': new_candidates_30d,
        'open_jobs': open_jobs,
        'total_applications': total_applications,
        'active_applications': active_applications,
        'interviews_scheduled': interviews_scheduled,
        'pipeline': list(pipeline),
        'avg_ai_score': round(avg_ai_score, 1) if avg_ai_score else None,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hiring_funnel(request):
    """Get hiring funnel data."""
    job_id = request.query_params.get('job_id')
    queryset = Application.objects.all()
    if job_id:
        queryset = queryset.filter(job_id=job_id)

    funnel = (
        queryset.values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )

    stage_order = ['applied', 'reviewing', 'shortlisted', 'interviewing',
                   'offered', 'accepted', 'rejected', 'withdrawn']
    funnel_dict = {item['status']: item['count'] for item in funnel}
    ordered_funnel = [
        {'stage': s, 'count': funnel_dict.get(s, 0)} for s in stage_order
    ]

    return Response({'funnel': ordered_funnel})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def candidate_sources(request):
    """Get candidate source distribution."""
    sources = (
        Candidate.objects.filter(is_active=True)
        .values('source')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    return Response({'sources': list(sources)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hiring_trends(request):
    """Get monthly hiring trends."""
    six_months_ago = timezone.now() - timedelta(days=180)

    candidates_by_month = (
        Candidate.objects.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    applications_by_month = (
        Application.objects.filter(applied_at__gte=six_months_ago)
        .annotate(month=TruncMonth('applied_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    return Response({
        'candidates': [
            {'month': item['month'].isoformat(), 'count': item['count']}
            for item in candidates_by_month
        ],
        'applications': [
            {'month': item['month'].isoformat(), 'count': item['count']}
            for item in applications_by_month
        ],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_performance(request):
    """Get performance metrics per job."""
    jobs = (
        Job.objects.filter(status='open')
        .annotate(
            app_count=Count('applications'),
            avg_match=Avg('applications__ai_match_score'),
        )
        .values('id', 'title', 'department', 'app_count', 'avg_match', 'created_at')
        .order_by('-app_count')[:20]
    )

    results = []
    for job in jobs:
        days_open = (timezone.now() - job['created_at']).days
        results.append({
            'id': str(job['id']),
            'title': job['title'],
            'department': job['department'],
            'applications': job['app_count'],
            'avg_match_score': round(job['avg_match'], 1) if job['avg_match'] else None,
            'days_open': days_open,
        })

    return Response({'jobs': results})
