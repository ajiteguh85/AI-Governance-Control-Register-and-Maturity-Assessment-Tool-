from rest_framework import serializers
from .models import Integration, SyncLog, WebhookEvent


class SyncLogSerializer(serializers.ModelSerializer):
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SyncLog
        fields = [
            'id', 'integration', 'direction', 'direction_display',
            'status', 'status_display', 'records_processed', 'records_created',
            'records_updated', 'records_failed', 'error_details',
            'started_at', 'completed_at',
        ]
        read_only_fields = ['id', 'started_at']


class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'integration', 'event_type', 'payload', 'headers',
            'processed', 'processing_result', 'received_at', 'processed_at',
        ]
        read_only_fields = ['id', 'received_at']


class IntegrationListSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'provider', 'provider_display', 'status', 'status_display',
            'is_active', 'last_sync_at', 'last_sync_status', 'created_at',
        ]


class IntegrationDetailSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    recent_syncs = serializers.SerializerMethodField()

    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'provider', 'provider_display', 'status', 'status_display',
            'config', 'webhook_url', 'sync_frequency', 'last_sync_at',
            'last_sync_status', 'last_sync_message', 'sync_stats',
            'field_mapping', 'is_active', 'created_by', 'created_at', 'updated_at',
            'recent_syncs',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def get_recent_syncs(self, obj):
        syncs = obj.sync_logs.all()[:5]
        return SyncLogSerializer(syncs, many=True).data
