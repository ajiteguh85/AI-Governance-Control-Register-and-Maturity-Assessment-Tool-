from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Candidate, CandidateActivity, CandidateNote
from .serializers import (
    CandidateCreateSerializer,
    CandidateDetailSerializer,
    CandidateListSerializer,
    CandidateNoteSerializer,
)


class CandidateViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for candidates with filtering, searching, and custom actions.
    """

    queryset = Candidate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stage', 'source', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'current_title', 'current_company']
    ordering_fields = ['created_at', 'updated_at', 'first_name', 'last_name', 'ai_score']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return CandidateCreateSerializer
        if self.action == 'list':
            return CandidateListSerializer
        return CandidateDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        # Filter by skills (comma-separated query param)
        skills = self.request.query_params.get('skills')
        if skills:
            skill_list = [s.strip().lower() for s in skills.split(',') if s.strip()]
            for skill in skill_list:
                qs = qs.filter(skills__icontains=skill)

        return qs

    @action(detail=True, methods=['post'])
    def advance_stage(self, request, pk=None):
        """Advance a candidate to the next pipeline stage."""
        candidate = self.get_object()
        stage_order = [choice[0] for choice in Candidate.STAGE_CHOICES if choice[0] != 'rejected']

        new_stage = request.data.get('stage')
        if new_stage:
            valid_stages = [c[0] for c in Candidate.STAGE_CHOICES]
            if new_stage not in valid_stages:
                return Response(
                    {'error': f"Invalid stage. Choose from: {valid_stages}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Auto-advance to next stage
            try:
                current_index = stage_order.index(candidate.stage)
            except ValueError:
                return Response(
                    {'error': 'Cannot advance from current stage.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if current_index >= len(stage_order) - 1:
                return Response(
                    {'error': 'Candidate is already at the final stage.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            new_stage = stage_order[current_index + 1]

        old_stage = candidate.stage
        candidate.stage = new_stage
        candidate.save(update_fields=['stage', 'updated_at'])

        CandidateActivity.objects.create(
            candidate=candidate,
            activity_type='stage_change',
            description=f"Stage changed from {old_stage} to {new_stage}",
            metadata={'old_stage': old_stage, 'new_stage': new_stage},
            performed_by=request.user if request.user.is_authenticated else None,
        )

        serializer = CandidateDetailSerializer(candidate, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """
        Perform bulk actions on multiple candidates.

        Supported actions: change_stage, deactivate, activate, delete.
        Expects: { "ids": [...], "action": "...", "params": {...} }
        """
        candidate_ids = request.data.get('ids', [])
        bulk_action = request.data.get('action')
        params = request.data.get('params', {})

        if not candidate_ids:
            return Response(
                {'error': 'No candidate IDs provided.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        candidates = Candidate.objects.filter(id__in=candidate_ids)
        count = candidates.count()

        if not count:
            return Response(
                {'error': 'No matching candidates found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if bulk_action == 'change_stage':
            new_stage = params.get('stage')
            valid_stages = [c[0] for c in Candidate.STAGE_CHOICES]
            if new_stage not in valid_stages:
                return Response(
                    {'error': f"Invalid stage. Choose from: {valid_stages}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            candidates.update(stage=new_stage)
            message = f"Updated stage to '{new_stage}' for {count} candidate(s)."

        elif bulk_action == 'deactivate':
            candidates.update(is_active=False)
            message = f"Deactivated {count} candidate(s)."

        elif bulk_action == 'activate':
            candidates.update(is_active=True)
            message = f"Activated {count} candidate(s)."

        elif bulk_action == 'delete':
            candidates.delete()
            message = f"Deleted {count} candidate(s)."

        else:
            return Response(
                {'error': "Invalid action. Choose from: change_stage, deactivate, activate, delete."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'message': message, 'affected': count})

    @action(detail=True, methods=['post'], parser_classes=[parsers.MultiPartParser])
    def upload_resume(self, request, pk=None):
        """Upload a resume file for a candidate."""
        candidate = self.get_object()
        resume_file = request.FILES.get('resume_file')

        if not resume_file:
            return Response(
                {'error': 'No file provided.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        candidate.resume_file = resume_file
        candidate.save(update_fields=['resume_file', 'updated_at'])

        CandidateActivity.objects.create(
            candidate=candidate,
            activity_type='document_uploaded',
            description=f"Resume uploaded: {resume_file.name}",
            metadata={'filename': resume_file.name, 'size': resume_file.size},
            performed_by=request.user if request.user.is_authenticated else None,
        )

        serializer = CandidateDetailSerializer(candidate, context={'request': request})
        return Response(serializer.data)


class CandidateNoteViewSet(viewsets.ModelViewSet):
    """
    CRUD for candidate notes. Scoped to a specific candidate via query param
    or accessible globally.
    """

    serializer_class = CandidateNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        qs = CandidateNote.objects.select_related('author')
        candidate_id = self.request.query_params.get('candidate')
        if candidate_id:
            qs = qs.filter(candidate_id=candidate_id)
        return qs

    def perform_create(self, serializer):
        note = serializer.save()
        CandidateActivity.objects.create(
            candidate=note.candidate,
            activity_type='note_added',
            description='Note added to candidate profile.',
            metadata={'note_id': str(note.id), 'is_ai_generated': note.is_ai_generated},
            performed_by=self.request.user if self.request.user.is_authenticated else None,
        )
