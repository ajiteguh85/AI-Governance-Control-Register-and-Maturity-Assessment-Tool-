import logging

from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Application, Interview, Job
from .serializers import (
    ApplicationDetailSerializer,
    ApplicationSerializer,
    InterviewSerializer,
    JobDetailSerializer,
    JobListSerializer,
)

logger = logging.getLogger(__name__)


class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job postings.

    Supports full CRUD, filtering by status/type/department/experience_level,
    search across title and description, and ordering.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact', 'in'],
        'job_type': ['exact', 'in'],
        'department': ['exact', 'icontains'],
        'experience_level': ['exact', 'in'],
        'remote_policy': ['exact'],
        'is_active': ['exact'],
        'hiring_manager': ['exact'],
    }
    search_fields = ['title', 'description', 'department', 'location', 'required_skills']
    ordering_fields = ['created_at', 'updated_at', 'title', 'published_at', 'salary_min']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Job.objects
            .select_related('hiring_manager')
            .annotate(application_count=Count('applications'))
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobDetailSerializer

    def perform_create(self, serializer):
        serializer.save(hiring_manager=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a draft job, setting status to 'open' and recording published_at."""
        job = self.get_object()
        if job.status != 'draft':
            return Response(
                {'detail': 'Only draft jobs can be published.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        job.status = 'open'
        job.published_at = timezone.now()
        job.save(update_fields=['status', 'published_at', 'updated_at'])
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close an open or paused job."""
        job = self.get_object()
        if job.status not in ('open', 'paused'):
            return Response(
                {'detail': 'Only open or paused jobs can be closed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        job.status = 'closed'
        job.closes_at = timezone.now()
        job.save(update_fields=['status', 'closes_at', 'updated_at'])
        serializer = self.get_serializer(job)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def match_candidates(self, request, pk=None):
        """
        Trigger AI-based candidate matching for this job.

        Delegates to the ai_engine app. Returns match results or queues the
        task asynchronously depending on the AI engine implementation.
        """
        job = self.get_object()
        if job.status not in ('open', 'paused'):
            return Response(
                {'detail': 'Candidate matching is only available for open or paused jobs.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from ai_engine.matching import match_candidates_for_job
            results = match_candidates_for_job(job.id)
            return Response(
                {'detail': 'Candidate matching completed.', 'matches': results},
                status=status.HTTP_200_OK,
            )
        except ImportError:
            logger.warning(
                'ai_engine.matching module not available; '
                'candidate matching skipped for job %s.',
                job.id,
            )
            return Response(
                {'detail': 'AI matching engine is not configured.'},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
        except Exception:
            logger.exception('Error during candidate matching for job %s', job.id)
            return Response(
                {'detail': 'An error occurred during candidate matching.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """List all applications for a specific job."""
        job = self.get_object()
        applications = Application.objects.filter(job=job).select_related('candidate')
        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = ApplicationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job applications.

    Supports CRUD and status transition actions.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact', 'in'],
        'job': ['exact'],
        'candidate': ['exact'],
        'ai_match_score': ['gte', 'lte'],
    }
    search_fields = ['job__title', 'cover_letter']
    ordering_fields = ['applied_at', 'updated_at', 'ai_match_score']
    ordering = ['-applied_at']

    def get_queryset(self):
        return Application.objects.select_related('job', 'candidate', 'reviewed_by')

    def get_serializer_class(self):
        if self.action in ('retrieve', 'update', 'partial_update'):
            return ApplicationDetailSerializer
        return ApplicationSerializer

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """
        Transition an application to a new status.

        Expects: {"status": "<new_status>", "rejection_reason": "..." (optional)}
        """
        application = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {'detail': 'The "status" field is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApplicationDetailSerializer(
            application,
            data={'status': new_status},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        if new_status == 'rejected':
            application.rejection_reason = request.data.get('rejection_reason', '')

        application.status = new_status
        application.reviewed_by = request.user
        application.save(update_fields=['status', 'rejection_reason', 'reviewed_by', 'updated_at'])

        return Response(ApplicationDetailSerializer(application).data)

    @action(detail=True, methods=['get'])
    def interviews(self, request, pk=None):
        """List all interviews for a specific application."""
        application = self.get_object()
        interviews = Interview.objects.filter(application=application).prefetch_related(
            'interviewers'
        )
        serializer = InterviewSerializer(interviews, many=True)
        return Response(serializer.data)


class InterviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing interviews."""

    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'application': ['exact'],
        'interview_type': ['exact', 'in'],
        'completed': ['exact'],
        'scheduled_at': ['gte', 'lte'],
    }
    ordering_fields = ['scheduled_at', 'created_at']
    ordering = ['scheduled_at']

    def get_queryset(self):
        return Interview.objects.select_related(
            'application', 'application__job', 'application__candidate'
        ).prefetch_related('interviewers')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark an interview as completed and optionally record feedback/rating.

        Expects: {"feedback": "...", "rating": 1-5} (both optional)
        """
        interview = self.get_object()
        if interview.completed:
            return Response(
                {'detail': 'This interview is already marked as completed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        interview.completed = True
        update_fields = ['completed']

        feedback = request.data.get('feedback')
        if feedback:
            interview.feedback = feedback
            update_fields.append('feedback')

        rating = request.data.get('rating')
        if rating is not None:
            try:
                rating = int(rating)
                if not 1 <= rating <= 5:
                    raise ValueError
            except (TypeError, ValueError):
                return Response(
                    {'detail': 'Rating must be an integer between 1 and 5.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            interview.rating = rating
            update_fields.append('rating')

        interview.save(update_fields=update_fields)
        return Response(InterviewSerializer(interview).data)
