from django.db import models
from django.conf import settings
import uuid


class Integration(models.Model):
    PROVIDER_CHOICES = [
        ('greenhouse', 'Greenhouse ATS'),
        ('lever', 'Lever ATS'),
        ('workday', 'Workday'),
        ('bamboohr', 'BambooHR'),
        ('salesforce', 'Salesforce CRM'),
        ('hubspot', 'HubSpot CRM'),
        ('bullhorn', 'Bullhorn'),
        ('custom_webhook', 'Custom Webhook'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('pending', 'Pending Setup'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    config = models.JSONField(default=dict, help_text='Provider-specific configuration')
    api_key_encrypted = models.TextField(blank=True, help_text='Encrypted API key')
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=200, blank=True)
    sync_frequency = models.PositiveIntegerField(
        default=60, help_text='Sync frequency in minutes'
    )
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, blank=True)
    last_sync_message = models.TextField(blank=True)
    sync_stats = models.JSONField(default=dict, blank=True)
    field_mapping = models.JSONField(
        default=dict, help_text='Field mapping between systems'
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"


class SyncLog(models.Model):
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
        ('bidirectional', 'Bidirectional'),
    ]

    STATUS_CHOICES = [
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(
        Integration, on_delete=models.CASCADE, related_name='sync_logs'
    )
    direction = models.CharField(max_length=15, choices=DIRECTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    records_processed = models.PositiveIntegerField(default=0)
    records_created = models.PositiveIntegerField(default=0)
    records_updated = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    error_details = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return (
            f"Sync {self.get_direction_display()} - {self.integration.name} "
            f"({self.get_status_display()})"
        )


class WebhookEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(
        Integration, on_delete=models.CASCADE, related_name='webhook_events'
    )
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    headers = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
    processing_result = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-received_at']

    def __str__(self):
        status = "processed" if self.processed else "pending"
        return f"{self.event_type} ({status}) - {self.integration.name}"
