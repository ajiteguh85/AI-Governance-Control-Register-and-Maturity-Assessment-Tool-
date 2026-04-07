from django.contrib import admin
from .models import Integration, SyncLog, WebhookEvent


class SyncLogInline(admin.TabularInline):
    model = SyncLog
    extra = 0
    readonly_fields = ['started_at', 'completed_at']
    max_num = 10


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'status', 'is_active', 'last_sync_at', 'created_at']
    list_filter = ['provider', 'status', 'is_active']
    search_fields = ['name']
    inlines = [SyncLogInline]


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['integration', 'direction', 'status', 'records_processed', 'started_at']
    list_filter = ['status', 'direction']


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ['integration', 'event_type', 'processed', 'received_at']
    list_filter = ['processed', 'event_type']
