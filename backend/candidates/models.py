from django.db import models
from django.conf import settings
import uuid


class Candidate(models.Model):
    STAGE_CHOICES = [
        ('new', 'New'),
        ('screening', 'Screening'),
        ('interview', 'Interview'),
        ('assessment', 'Assessment'),
        ('offer', 'Offer'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]

    SOURCE_CHOICES = [
        ('direct', 'Direct Application'),
        ('referral', 'Referral'),
        ('linkedin', 'LinkedIn'),
        ('job_board', 'Job Board'),
        ('agency', 'Agency'),
        ('ats_import', 'ATS Import'),
        ('crm_import', 'CRM Import'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    current_title = models.CharField(max_length=200, blank=True)
    current_company = models.CharField(max_length=200, blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    skills = models.JSONField(default=list, blank=True)
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_text = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='direct')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
    ai_score = models.FloatField(null=True, blank=True)
    ai_summary = models.TextField(blank=True)
    ai_skills_extracted = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    external_id = models.CharField(
        max_length=200, blank=True, help_text='ID from external ATS/CRM'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='candidates_created',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class CandidateNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name='candidate_notes'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    content = models.TextField()
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.candidate} by {self.author}"


class CandidateActivity(models.Model):
    ACTIVITY_TYPES = [
        ('stage_change', 'Stage Change'),
        ('note_added', 'Note Added'),
        ('email_sent', 'Email Sent'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('ai_assessment', 'AI Assessment'),
        ('document_uploaded', 'Document Uploaded'),
        ('integration_sync', 'Integration Sync'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name='activities'
    )
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Candidate activities'

    def __str__(self):
        return f"{self.activity_type} - {self.candidate}"
