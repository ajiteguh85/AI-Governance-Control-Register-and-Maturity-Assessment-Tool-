from django.contrib import admin

from .models import Candidate, CandidateActivity, CandidateNote


class CandidateNoteInline(admin.TabularInline):
    model = CandidateNote
    extra = 0
    readonly_fields = ['id', 'author', 'created_at']


class CandidateActivityInline(admin.TabularInline):
    model = CandidateActivity
    extra = 0
    readonly_fields = ['id', 'activity_type', 'description', 'performed_by', 'created_at']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'email',
        'current_title',
        'stage',
        'source',
        'ai_score',
        'is_active',
        'created_at',
    ]
    list_filter = ['stage', 'source', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'current_title', 'current_company']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [CandidateNoteInline, CandidateActivityInline]
    fieldsets = (
        (None, {
            'fields': ('id', 'first_name', 'last_name', 'email', 'phone'),
        }),
        ('Professional', {
            'fields': (
                'current_title', 'current_company', 'location',
                'years_experience', 'skills',
            ),
        }),
        ('Documents & Links', {
            'fields': ('resume_file', 'resume_text', 'linkedin_url', 'portfolio_url'),
        }),
        ('Pipeline', {
            'fields': ('source', 'stage', 'tags', 'notes', 'external_id', 'is_active'),
        }),
        ('AI', {
            'fields': ('ai_score', 'ai_summary', 'ai_skills_extracted'),
        }),
        ('Meta', {
            'fields': ('created_by', 'created_at', 'updated_at'),
        }),
    )


@admin.register(CandidateNote)
class CandidateNoteAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'author', 'is_ai_generated', 'created_at']
    list_filter = ['is_ai_generated', 'created_at']
    search_fields = ['content', 'candidate__first_name', 'candidate__last_name']
    readonly_fields = ['id', 'created_at']


@admin.register(CandidateActivity)
class CandidateActivityAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'activity_type', 'performed_by', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['description', 'candidate__first_name', 'candidate__last_name']
    readonly_fields = ['id', 'created_at']
