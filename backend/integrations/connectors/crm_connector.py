"""
HubSpot-style CRM connector.

Handles synchronisation of contacts (candidates) and deals (placements) with
HubSpot or compatible CRM platforms. Falls back to mock data when the remote
API is unreachable.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from .base import BaseConnector

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock / demo data
# ---------------------------------------------------------------------------

MOCK_CONTACTS = [
    {
        'id': '3001',
        'properties': {
            'firstname': 'Carol',
            'lastname': 'Williams',
            'email': 'carol.williams@example.com',
            'phone': '+1-555-0201',
            'jobtitle': 'Data Scientist',
            'company': 'DataWorks',
            'createdate': '2025-01-20T08:00:00Z',
            'lastmodifieddate': '2025-03-25T12:00:00Z',
        },
    },
    {
        'id': '3002',
        'properties': {
            'firstname': 'David',
            'lastname': 'Lee',
            'email': 'david.lee@example.com',
            'phone': '+1-555-0202',
            'jobtitle': 'UX Researcher',
            'company': 'DesignHub',
            'createdate': '2025-02-10T10:00:00Z',
            'lastmodifieddate': '2025-03-26T09:30:00Z',
        },
    },
]

MOCK_DEALS = [
    {
        'id': '4001',
        'properties': {
            'dealname': 'Backend Engineer Placement',
            'dealstage': 'contractsent',
            'amount': '95000',
            'createdate': '2025-03-01T00:00:00Z',
            'closedate': '2025-04-15T00:00:00Z',
        },
    },
]

# Default field mapping (HubSpot property -> internal field)
DEFAULT_INBOUND_MAPPING = {
    'firstname': 'first_name',
    'lastname': 'last_name',
    'email': 'email',
    'phone': 'phone',
    'jobtitle': 'current_title',
    'company': 'current_company',
}


class CRMConnector(BaseConnector):
    """
    Connector for HubSpot-compatible CRM systems.

    Configuration keys (stored in ``Integration.config``):
        base_url   - API root, default ``https://api.hubapi.com``
        per_page   - records per request (default 100, max 100 for HubSpot)
        use_mock   - force mock mode
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_headers(self) -> dict:
        api_key = self._get_api_key()
        headers = super()._get_headers()
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        return headers

    def _get_base_url(self) -> str:
        return self.config.get('base_url', 'https://api.hubapi.com')

    @property
    def _use_mock(self) -> bool:
        return self.config.get('use_mock', False) or not self._get_api_key()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make an HTTP request to the CRM API with standard error handling."""
        url = f"{self._get_base_url()}/{path.lstrip('/')}"
        timeout = self.config.get('timeout', 30)
        response = requests.request(
            method,
            url,
            headers=self._get_headers(),
            timeout=timeout,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def _paginate_contacts(self, params: Optional[dict] = None) -> list:
        """
        Fetch all contacts using HubSpot CRM v3 cursor-based pagination.
        """
        results = []
        limit = self.config.get('per_page', 100)
        params = params or {}
        params['limit'] = limit
        after = None

        while True:
            if after:
                params['after'] = after
            resp = self._request(
                'GET', '/crm/v3/objects/contacts', params=params
            )
            data = resp.json()
            results.extend(data.get('results', []))
            paging = data.get('paging', {}).get('next')
            if paging:
                after = paging.get('after')
            else:
                break

        return results

    # ------------------------------------------------------------------
    # BaseConnector interface
    # ------------------------------------------------------------------

    def test_connection(self) -> dict:
        if self._use_mock:
            return {
                'success': True,
                'message': 'Connected in mock mode (no API key configured).',
            }
        try:
            resp = self._request(
                'GET', '/crm/v3/objects/contacts', params={'limit': 1}
            )
            return {
                'success': True,
                'message': f'Connected successfully (HTTP {resp.status_code}).',
            }
        except (ConnectionError, Timeout) as exc:
            self.logger.warning("CRM connection test failed: %s", exc)
            return {'success': False, 'message': f'Connection failed: {exc}'}
        except HTTPError as exc:
            self.logger.warning("CRM connection test HTTP error: %s", exc)
            return {'success': False, 'message': f'HTTP error: {exc}'}

    def sync_candidates(self, since=None) -> dict:
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        try:
            if self._use_mock:
                raw_contacts = MOCK_CONTACTS
            else:
                params = {
                    'properties': 'firstname,lastname,email,phone,jobtitle,company',
                }
                if since:
                    # HubSpot filtering via search API for modified-after
                    raw_contacts = self._search_contacts_modified_since(since)
                else:
                    raw_contacts = self._paginate_contacts(params)
        except Exception as exc:
            self.logger.error("Failed to fetch contacts from CRM: %s", exc)
            raw_contacts = MOCK_CONTACTS
            stats['errors'].append(
                f'API fetch failed, using mock data: {exc}'
            )

        from candidates.models import Candidate

        for raw in raw_contacts:
            stats['processed'] += 1
            try:
                props = raw.get('properties', raw)
                mapped = self.map_fields(props, direction='inbound')
                if not mapped:
                    mapped = {
                        v: props[k]
                        for k, v in DEFAULT_INBOUND_MAPPING.items()
                        if k in props
                    }

                email = mapped.get('email') or props.get('email')
                if not email:
                    stats['failed'] += 1
                    stats['errors'].append(
                        f"Contact {raw.get('id', '?')} has no email, skipped."
                    )
                    continue

                candidate, created = Candidate.objects.update_or_create(
                    email=email,
                    defaults={
                        'first_name': mapped.get('first_name', ''),
                        'last_name': mapped.get('last_name', ''),
                        'phone': mapped.get('phone', ''),
                        'current_title': mapped.get('current_title', ''),
                        'current_company': mapped.get('current_company', ''),
                        'source': 'crm_import',
                        'external_id': str(raw.get('id', '')),
                    },
                )
                if created:
                    stats['created'] += 1
                else:
                    stats['updated'] += 1

            except Exception as exc:
                stats['failed'] += 1
                stats['errors'].append(
                    f"Error processing contact {raw.get('id', '?')}: {exc}"
                )
                self.logger.exception("Error syncing contact %s", raw.get('id'))

        return stats

    def _search_contacts_modified_since(self, since) -> list:
        """Use HubSpot Search API to find contacts modified after *since*."""
        payload = {
            'filterGroups': [
                {
                    'filters': [
                        {
                            'propertyName': 'lastmodifieddate',
                            'operator': 'GTE',
                            'value': str(int(since.timestamp() * 1000)),
                        }
                    ]
                }
            ],
            'properties': [
                'firstname', 'lastname', 'email', 'phone',
                'jobtitle', 'company',
            ],
            'limit': self.config.get('per_page', 100),
        }
        results = []
        after = 0

        while True:
            payload['after'] = after
            resp = self._request(
                'POST', '/crm/v3/objects/contacts/search', json=payload
            )
            data = resp.json()
            results.extend(data.get('results', []))
            paging = data.get('paging', {}).get('next')
            if paging:
                after = paging['after']
            else:
                break

        return results

    def sync_jobs(self, since=None) -> dict:
        """
        Sync deals from HubSpot as a proxy for job/placement records.
        """
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        try:
            if self._use_mock:
                raw_deals = MOCK_DEALS
            else:
                resp = self._request(
                    'GET',
                    '/crm/v3/objects/deals',
                    params={
                        'limit': self.config.get('per_page', 100),
                        'properties': 'dealname,dealstage,amount,closedate',
                    },
                )
                raw_deals = resp.json().get('results', [])
        except Exception as exc:
            self.logger.error("Failed to fetch deals from CRM: %s", exc)
            raw_deals = MOCK_DEALS
            stats['errors'].append(f'API fetch failed, using mock data: {exc}')

        for raw in raw_deals:
            stats['processed'] += 1
            try:
                props = raw.get('properties', raw)
                self.logger.info(
                    "Received deal %s: %s (stage=%s)",
                    raw.get('id'),
                    props.get('dealname'),
                    props.get('dealstage'),
                )
                stats['created'] += 1
            except Exception as exc:
                stats['failed'] += 1
                stats['errors'].append(
                    f"Error processing deal {raw.get('id', '?')}: {exc}"
                )

        return stats

    def push_candidate(self, candidate) -> dict:
        payload = {
            'properties': {
                'firstname': candidate.first_name,
                'lastname': candidate.last_name,
                'email': candidate.email,
                'phone': candidate.phone or '',
                'jobtitle': candidate.current_title,
                'company': candidate.current_company,
            }
        }

        if self._use_mock:
            return {
                'success': True,
                'external_id': '39999',
                'message': 'Contact pushed to CRM (mock mode).',
            }

        try:
            resp = self._request(
                'POST', '/crm/v3/objects/contacts', json=payload
            )
            data = resp.json()
            return {
                'success': True,
                'external_id': str(data.get('id', '')),
                'message': 'Contact created in CRM.',
            }
        except HTTPError as exc:
            # HubSpot returns 409 if the contact already exists
            if exc.response is not None and exc.response.status_code == 409:
                self.logger.info("Contact already exists in CRM: %s", candidate.email)
                return {
                    'success': False,
                    'external_id': '',
                    'message': 'Contact already exists in CRM.',
                }
            self.logger.exception("Failed to push contact to CRM")
            return {
                'success': False,
                'external_id': '',
                'message': f'Push failed: {exc}',
            }
        except Exception as exc:
            self.logger.exception("Failed to push contact to CRM")
            return {
                'success': False,
                'external_id': '',
                'message': f'Push failed: {exc}',
            }

    def push_application(self, application) -> dict:
        """
        In a CRM context an "application" maps to creating or updating a Deal
        associated with a Contact.
        """
        deal_name = (
            application.get('deal_name', 'New Placement')
            if isinstance(application, dict)
            else getattr(application, 'deal_name', 'New Placement')
        )
        candidate_id = (
            application.get('candidate_id')
            if isinstance(application, dict)
            else getattr(application, 'candidate_id', None)
        )

        if self._use_mock:
            return {
                'success': True,
                'external_id': '49999',
                'message': 'Deal pushed to CRM (mock mode).',
            }

        payload = {
            'properties': {
                'dealname': deal_name,
                'dealstage': 'appointmentscheduled',
                'pipeline': 'default',
            }
        }

        try:
            resp = self._request(
                'POST', '/crm/v3/objects/deals', json=payload
            )
            data = resp.json()
            deal_id = str(data.get('id', ''))

            # Associate the deal with the CRM contact if we have an external id
            if candidate_id and deal_id:
                try:
                    self._request(
                        'PUT',
                        f'/crm/v3/objects/deals/{deal_id}/associations/'
                        f'contacts/{candidate_id}/deal_to_contact',
                    )
                except Exception:
                    self.logger.warning(
                        "Could not associate deal %s with contact %s",
                        deal_id,
                        candidate_id,
                    )

            return {
                'success': True,
                'external_id': deal_id,
                'message': 'Deal created in CRM.',
            }
        except Exception as exc:
            self.logger.exception("Failed to push deal to CRM")
            return {
                'success': False,
                'external_id': '',
                'message': f'Push failed: {exc}',
            }
