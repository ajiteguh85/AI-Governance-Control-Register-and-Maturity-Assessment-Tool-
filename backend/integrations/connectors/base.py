from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Base class for all external system connectors."""

    def __init__(self, integration):
        self.integration = integration
        self.config = integration.config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def test_connection(self) -> dict:
        """
        Test the connection to the external system.

        Returns:
            dict with keys 'success' (bool) and 'message' (str).
        """
        pass

    @abstractmethod
    def sync_candidates(self, since=None) -> dict:
        """
        Sync candidates from the external system.

        Args:
            since: Optional datetime; only sync records modified after this time.

        Returns:
            dict with sync statistics (created, updated, failed, etc.).
        """
        pass

    @abstractmethod
    def sync_jobs(self, since=None) -> dict:
        """
        Sync jobs/positions from the external system.

        Args:
            since: Optional datetime; only sync records modified after this time.

        Returns:
            dict with sync statistics.
        """
        pass

    @abstractmethod
    def push_candidate(self, candidate) -> dict:
        """
        Push a candidate record to the external system.

        Args:
            candidate: A Candidate model instance.

        Returns:
            dict with 'success' (bool), 'external_id' (str), and 'message' (str).
        """
        pass

    @abstractmethod
    def push_application(self, application) -> dict:
        """
        Push an application/submission to the external system.

        Args:
            application: An application dict or model instance.

        Returns:
            dict with 'success' (bool), 'external_id' (str), and 'message' (str).
        """
        pass

    def map_fields(self, data: dict, direction: str = 'inbound') -> dict:
        """
        Map fields between internal and external schemas using the integration's
        configured field_mapping.

        Args:
            data: The source data dict to map.
            direction: 'inbound' (external -> internal) or 'outbound' (internal -> external).

        Returns:
            A new dict with mapped field names.
        """
        mapping = self.integration.field_mapping.get(direction, {})
        mapped = {}
        for ext_field, int_field in mapping.items():
            if direction == 'inbound':
                if ext_field in data:
                    mapped[int_field] = data[ext_field]
            else:
                if int_field in data:
                    mapped[ext_field] = data[int_field]
        return mapped

    def _get_api_key(self) -> str:
        """
        Retrieve the decrypted API key for this integration.

        In production this would use a proper encryption backend (e.g. Fernet,
        AWS KMS). For now we return the stored value directly.
        """
        return self.integration.api_key_encrypted

    def process_webhook(self, payload: dict) -> dict:
        """Process an incoming webhook event. Override in subclasses for specific handling."""
        self.logger.info("Processing webhook payload with %d keys", len(payload))
        return {'processed': True}

    def _get_base_url(self) -> str:
        """Return the base API URL from the integration config."""
        return self.config.get('base_url', '')

    def _get_headers(self) -> dict:
        """Build default HTTP headers for API requests."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
