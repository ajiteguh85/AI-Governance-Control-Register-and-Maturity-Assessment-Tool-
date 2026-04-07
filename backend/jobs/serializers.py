from rest_framework import serializers

from .models import Application, Interview, Job


class JobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for job listings."""

    application_count = serializers.IntegerField(read_only=True)
    hiring_manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'department',
            'location',
            'remote_policy',
            'job_type',
            'experience_level',
            'salary_min',
            'salary_max',
            'salary_currency',
            'status',
            'hiring_manager',
            'hiring_manager_name',
            'application_count',
            'is_active',
            'published_at',
            'closes_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_hiring_manager_name(self, obj):
        if obj.hiring_manager:
            return obj.hiring_manager.get_full_name() or obj.hiring_manager.username
        return None


class JobDetailSerializer(serializers.ModelSerializer):
    """Full serializer for job detail views."""

    application_count = serializers.IntegerField(read_only=True)
    hiring_manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'department',
            'location',
            'remote_policy',
            'job_type',
            'experience_level',
            'description',
            'requirements',
            'nice_to_have',
            'required_skills',
            'salary_min',
            'salary_max',
            'salary_currency',
            'status',
            'hiring_manager',
            'hiring_manager_name',
            'external_id',
            'ai_generated_description',
            'application_count',
            'is_active',
            'published_at',
            'closes_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_hiring_manager_name(self, obj):
        if obj.hiring_manager:
            return obj.hiring_manager.get_full_name() or obj.hiring_manager.username
        return None

    def validate(self, data):
        salary_min = data.get('salary_min', getattr(self.instance, 'salary_min', None))
        salary_max = data.get('salary_max', getattr(self.instance, 'salary_max', None))
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError(
                {'salary_max': 'Maximum salary must be greater than or equal to minimum salary.'}
            )
        return data


class InterviewSerializer(serializers.ModelSerializer):
    interviewer_names = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            'id',
            'application',
            'interview_type',
            'scheduled_at',
            'duration_minutes',
            'location',
            'meeting_link',
            'interviewers',
            'interviewer_names',
            'feedback',
            'rating',
            'ai_suggested_questions',
            'completed',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_interviewer_names(self, obj):
        return [
            user.get_full_name() or user.username
            for user in obj.interviewers.all()
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for application list views."""

    candidate_name = serializers.SerializerMethodField()
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'job_title',
            'candidate',
            'candidate_name',
            'status',
            'ai_match_score',
            'applied_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at']

    def get_candidate_name(self, obj):
        return str(obj.candidate)


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Full serializer for application detail views."""

    candidate_name = serializers.SerializerMethodField()
    job_title = serializers.CharField(source='job.title', read_only=True)
    interviews = InterviewSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'job_title',
            'candidate',
            'candidate_name',
            'status',
            'cover_letter',
            'ai_match_score',
            'ai_match_explanation',
            'rejection_reason',
            'interview_notes',
            'reviewed_by',
            'interviews',
            'applied_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at']

    def get_candidate_name(self, obj):
        return str(obj.candidate)

    def validate_status(self, value):
        """Validate status transitions."""
        if not self.instance:
            return value

        valid_transitions = {
            'applied': ['reviewing', 'rejected', 'withdrawn'],
            'reviewing': ['shortlisted', 'rejected', 'withdrawn'],
            'shortlisted': ['interviewing', 'rejected', 'withdrawn'],
            'interviewing': ['offered', 'rejected', 'withdrawn'],
            'offered': ['accepted', 'rejected', 'withdrawn'],
            'accepted': [],
            'rejected': [],
            'withdrawn': [],
        }

        current = self.instance.status
        allowed = valid_transitions.get(current, [])
        if value != current and value not in allowed:
            raise serializers.ValidationError(
                f'Cannot transition from "{current}" to "{value}". '
                f'Allowed transitions: {", ".join(allowed) or "none"}.'
            )
        return value
