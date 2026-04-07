from django.contrib import admin

from .models import Application, Interview, Job


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    fields = ['candidate', 'status', 'ai_match_score', 'applied_at']
    readonly_fields = ['applied_at']
    show_change_link = True


class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 0
    fields = ['interview_type', 'scheduled_at', 'duration_minutes', 'completed']
    show_change_link = True


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'department',
        'location',
        'job_type',
        'experience_level',
        'status',
        'is_active',
        'hiring_manager',
        'application_count',
        'published_at',
        'created_at',
    ]
    list_filter = ['status', 'job_type', 'experience_level', 'remote_policy', 'is_active']
    search_fields = ['title', 'department', 'location', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'application_count']
    inlines = [ApplicationInline]
    date_hierarchy = 'created_at'
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('id', 'title', 'department', 'status', 'is_active'),
        }),
        ('Location & Type', {
            'fields': ('location', 'remote_policy', 'job_type', 'experience_level'),
        }),
        ('Description', {
            'fields': ('description', 'requirements', 'nice_to_have', 'required_skills'),
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'salary_currency'),
        }),
        ('AI & Integration', {
            'fields': ('ai_generated_description', 'external_id'),
            'classes': ('collapse',),
        }),
        ('People & Dates', {
            'fields': (
                'hiring_manager',
                'published_at',
                'closes_at',
                'created_at',
                'updated_at',
            ),
        }),
    )

    def application_count(self, obj):
        return obj.application_count
    application_count.short_description = 'Applications'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'status',
        'ai_match_score',
        'reviewed_by',
        'applied_at',
        'updated_at',
    ]
    list_filter = ['status']
    search_fields = ['job__title', 'candidate__first_name', 'candidate__last_name']
    readonly_fields = ['id', 'applied_at', 'updated_at']
    inlines = [InterviewInline]
    list_per_page = 25
    raw_id_fields = ['job', 'candidate', 'reviewed_by']


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'interview_type',
        'scheduled_at',
        'duration_minutes',
        'rating',
        'completed',
    ]
    list_filter = ['interview_type', 'completed']
    search_fields = ['application__job__title']
    readonly_fields = ['id', 'created_at']
    filter_horizontal = ['interviewers']
    list_per_page = 25
    raw_id_fields = ['application']
