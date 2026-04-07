import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Integration, SyncLog, WebhookEvent
from .serializers import (
    IntegrationListSerializer, IntegrationDetailSerializer,
    SyncLogSerializer, WebhookEventSerializer,
)
from .connectors.base import BaseConnector
from .connectors.ats_connector import ATSConnector
from .connectors.crm_connector import CRMConnector

logger = logging.getLogger(__name__)

CONNECTOR_MAP = {
    'greenhouse': ATSConnector,
    'lever': ATSConnector,
    'workday': ATSConnector,
    'bamboohr': ATSConnector,
    'salesforce': CRMConnector,
    'hubspot': CRMConnector,
    'bullhorn': CRMConnector,
}


def get_connector(integration: Integration) -> BaseConnector:
    connector_class = CONNECTOR_MAP.get(integration.provider)
    if not connector_class:
        raise ValueError(f"No connector available for provider: {integration.provider}")
    return connector_class(integration)


class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return IntegrationListSerializer
        return IntegrationDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        integration = self.get_object()
        try:
            connector = get_connector(integration)
            result = connector.test_connection()
            if result.get('success'):
                integration.status = 'active'
            else:
                integration.status = 'error'
                integration.last_sync_message = result.get('message', '')
            integration.save()
            return Response(result)
        except ValueError as e:
            return Response({'success': False, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def trigger_sync(self, request, pk=None):
        integration = self.get_object()
        direction = request.data.get('direction', 'inbound')

        sync_log = SyncLog.objects.create(
            integration=integration, direction=direction,
        )

        try:
            connector = get_connector(integration)
            if direction == 'inbound':
                result = connector.sync_candidates(since=integration.last_sync_at)
            else:
                result = connector.sync_jobs(since=integration.last_sync_at)

            sync_log.status = 'completed'
            sync_log.records_processed = result.get('processed', 0)
            sync_log.records_created = result.get('created', 0)
            sync_log.records_updated = result.get('updated', 0)
            sync_log.records_failed = result.get('failed', 0)
            sync_log.completed_at = timezone.now()
            sync_log.save()

            integration.last_sync_at = timezone.now()
            integration.last_sync_status = 'completed'
            integration.sync_stats = result
            integration.save()

            return Response(SyncLogSerializer(sync_log).data)
        except Exception as e:
            sync_log.status = 'failed'
            sync_log.error_details = [str(e)]
            sync_log.completed_at = timezone.now()
            sync_log.save()

            integration.last_sync_status = 'failed'
            integration.last_sync_message = str(e)
            integration.save()

            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=['get'])
    def sync_logs(self, request, pk=None):
        integration = self.get_object()
        logs = integration.sync_logs.all()[:20]
        return Response(SyncLogSerializer(logs, many=True).data)


@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_receive(request, integration_id):
    """Receive and store webhook events from external systems."""
    try:
        integration = Integration.objects.get(id=integration_id, is_active=True)
    except Integration.DoesNotExist:
        return Response({'error': 'Integration not found'}, status=status.HTTP_404_NOT_FOUND)

    event = WebhookEvent.objects.create(
        integration=integration,
        event_type=request.data.get('event', request.data.get('type', 'unknown')),
        payload=request.data,
        headers=dict(request.headers),
    )

    # Process webhook asynchronously in production
    try:
        connector = get_connector(integration)
        connector.process_webhook(event.payload)
        event.processed = True
        event.processing_result = 'Success'
        event.processed_at = timezone.now()
        event.save()
    except Exception as e:
        event.processing_result = str(e)
        event.save()
        logger.error(f"Webhook processing failed: {e}")

    return Response({'status': 'received', 'event_id': str(event.id)})
