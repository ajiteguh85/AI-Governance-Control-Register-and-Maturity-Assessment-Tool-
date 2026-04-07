from rest_framework import serializers

from .models import Candidate, CandidateActivity, CandidateNote


class CandidateNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = CandidateNote
        fields = [
            'id',
            'candidate',
            'author',
            'author_name',
            'content',
            'is_ai_generated',
            'created_at',
        ]
        read_only_fields = ['id', 'author', 'created_at']

    def get_author_name(self, obj):
        if obj.author:
            full = f"{obj.author.first_name} {obj.author.last_name}".strip()
            return full or obj.author.username
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['author'] = request.user
        return super().create(validated_data)


class CandidateActivitySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CandidateActivity
        fields = [
            'id',
            'candidate',
            'activity_type',
            'description',
            'metadata',
            'performed_by',
            'performed_by_name',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            full = f"{obj.performed_by.first_name} {obj.performed_by.last_name}".strip()
            return full or obj.performed_by.username
        return None


class CandidateListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Candidate
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'current_title',
            'current_company',
            'location',
            'source',
            'stage',
            'ai_score',
            'tags',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CandidateDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    candidate_notes = CandidateNoteSerializer(many=True, read_only=True)
    activities = CandidateActivitySerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'location',
            'current_title',
            'current_company',
            'years_experience',
            'skills',
            'resume_file',
            'resume_text',
            'linkedin_url',
            'portfolio_url',
            'source',
            'stage',
            'ai_score',
            'ai_summary',
            'ai_skills_extracted',
            'tags',
            'notes',
            'external_id',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_name',
            'candidate_notes',
            'activities',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def get_created_by_name(self, obj):
        if obj.created_by:
            full = f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
            return full or obj.created_by.username
        return None


class CandidateCreateSerializer(serializers.ModelSerializer):
    resume_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Candidate
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'location',
            'current_title',
            'current_company',
            'years_experience',
            'skills',
            'resume_file',
            'resume_text',
            'linkedin_url',
            'portfolio_url',
            'source',
            'stage',
            'tags',
            'notes',
            'external_id',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
