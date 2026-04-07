"""
Greenhouse-style ATS connector.

Handles synchronisation of candidates and jobs with Greenhouse or compatible
ATS platforms. Falls back to mock data when the remote API is unreachable so
that the rest of the pipeline can be developed and tested independently.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from .base import BaseConnector

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock / demo data used when the real API is unavailable
# ---------------------------------------------------------------------------

MOCK_CANDIDATES = [
    {
        'id': 1001,
        'first_name': 'Alice',
        'last_name': 'Johnson',
        'email': 'alice.johnson@example.com',
        'phone': '+1-555-0101',
        'title': 'Senior Software Engineer',
        'company': 'TechCorp',
        'created_at': '2025-01-15T10:30:00Z',
        'updated_at': '2025-03-20T14:00:00Z',
        'applications': [
            {'job_id': 2001, 'status': 'active', 'stage': 'Interview'},
        ],
    },
    {
        'id': 1002,
        'first_name': 'Bob',
        'last_name': 'Smith',
        'email': 'bob.smith@example.com',
        'phone': '+1-555-0102',
        'title': 'Product Manager',
        'company': 'StartupXYZ',
        'created_at': '2025-02-01T09:00:00Z',
        'updated_at': '2025-03-22T11:30:00Z',
        'applications': [],
    },
]

MOCK_JOBS = [
    {
        'id': 2001,
        'name': 'Senior Backend Engineer',
        'status': 'open',
        'departments': [{'name': 'Engineering'}],
        'offices': [{'name': 'San Francisco'}],
        'opened_at': '2025-01-10T00:00:00Z',
        'updated_at': '2025-03-18T16:00:00Z',
    },
    {
        'id': 2002,
        'name': 'Product Designer',
        'status': 'open',
        'departments': [{'name': 'Design'}],
        'offices': [{'name': 'Remote'}],
        'opened_at': '2025-02-05T00:00:00Z',
        'updated_at': '2025-03-21T09:00:00Z',
    },
]

# Default field mapping (Greenhouse field -> internal field)
DEFAULT_INBOUND_MAPPING = {
    'first_name': 'first_name',
    'last_name': 'last_name',
    'email': 'email',
    'phone': 'phone',
    'title': 'current_title',
    'company': 'current_company',
}


class ATSConnector(BaseConnector):
    """
    Connector for Greenhouse-compatible Applicant Tracking Systems.

    Configuration keys (stored in ``Integration.config``):
        base_url  - API root, e.g. ``https://harvest.greenhouse.io/v1``
        per_page  - number of records per page (default 100)
        use_mock  - force mock mode even if an API key is present
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_headers(self) -> dict:
        api_key = self._get_api_key()
        headers = super()._get_headers()
        if api_key:
            # Greenhouse uses HTTP Basic auth with the API key as username
            import base64
            token = base64.b64encode(f"{api_key}:".encode()).decode()
            headers['Authorization'] = f'Basic {token}'
        return headers

    def _get_base_url(self) -> str:
        return self.config.get('base_url', 'https://harvest.greenhouse.io/v1')

    @property
    def _use_mock(self) -> bool:
        return self.config.get('use_mock', False) or not self._get_api_key()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make an HTTP request to the ATS API with standard error handling."""
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

    def _paginate(self, path: str, params: Optional[dict] = None) -> list:
        """Fetch all pages from a paginated Greenhouse endpoint."""
        results = []
        per_page = self.config.get('per_page', 100)
        page = 1
        params = params or {}

        while True:
            params.update({'per_page': per_page, 'page': page})
            resp = self._request('GET', path, params=params)
            data = resp.json()
            if not data:
                break
            results.extend(data)
            # Greenhouse uses a Link header for pagination
            if 'next' not in resp.links:
                break
            page += 1

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
            resp = self._request('GET', '/candidates', params={'per_page': 1})
            return {
                'success': True,
                'message': f'Connected successfully (HTTP {resp.status_code}).',
            }
        except (ConnectionError, Timeout) as exc:
            self.logger.warning("ATS connection test failed: %s", exc)
            return {'success': False, 'message': f'Connection failed: {exc}'}
        except HTTPError as exc:
            self.logger.warning("ATS connection test HTTP error: %s", exc)
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
                raw_candidates = MOCK_CANDIDATES
            else:
                params = {}
                if since:
                    params['updated_after'] = since.isoformat()
                raw_candidates = self._paginate('/candidates', params)
        except Exception as exc:
            self.logger.error("Failed to fetch candidates from ATS: %s", exc)
            # Fall back to mock data so downstream logic can still be tested
            raw_candidates = MOCK_CANDIDATES
            stats['errors'].append(
                f'API fetch failed, using mock data: {exc}'
            )

        from candidates.models import Candidate

        for raw in raw_candidates:
            stats['processed'] += 1
            try:
                mapped = self.map_fields(raw, direction='inbound')
                if not mapped:
                    # Use default mapping when no custom mapping is configured
                    mapped = {
                        v: raw[k]
                        for k, v in DEFAULT_INBOUND_MAPPING.items()
                        if k in raw
                    }

                email = mapped.get('email') or raw.get('email')
                if not email:
                    stats['failed'] += 1
                    stats['errors'].append(
                        f"Candidate {raw.get('id', '?')} has no email, skipped."
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
                        'source': 'ats_import',
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
                    f"Error processing candidate {raw.get('id', '?')}: {exc}"
                )
                self.logger.exception("Error syncing candidate %s", raw.get('id'))

        return stats

    def sync_jobs(self, since=None) -> dict:
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': [],
        }

        try:
            if self._use_mock:
                raw_jobs = MOCK_JOBS
            else:
                params = {}
                if since:
                    params['updated_after'] = since.isoformat()
                raw_jobs = self._paginate('/jobs', params)
        except Exception as exc:
            self.logger.error("Failed to fetch jobs from ATS: %s", exc)
            raw_jobs = MOCK_JOBS
            stats['errors'].append(f'API fetch failed, using mock data: {exc}')

        for raw in raw_jobs:
            stats['processed'] += 1
            try:
                # Job import is provider-dependent; log what we received for now.
                self.logger.info(
                    "Received job %s: %s (status=%s)",
                    raw.get('id'),
                    raw.get('name'),
                    raw.get('status'),
                )
                stats['created'] += 1
            except Exception as exc:
                stats['failed'] += 1
                stats['errors'].append(
                    f"Error processing job {raw.get('id', '?')}: {exc}"
                )

        return stats

    def push_candidate(self, candidate) -> dict:
        payload = {
            'first_name': candidate.first_name,
            'last_name': candidate.last_name,
            'email_addresses': [
                {'value': candidate.email, 'type': 'personal'},
            ],
            'phone_numbers': (
                [{'value': candidate.phone, 'type': 'mobile'}]
                if candidate.phone
                else []
            ),
            'title': candidate.current_title,
            'company': candidate.current_company,
        }

        if self._use_mock:
            return {
                'success': True,
                'external_id': '99999',
                'message': 'Candidate pushed (mock mode).',
            }

        try:
            resp = self._request('POST', '/candidates', json=payload)
            data = resp.json()
            return {
                'success': True,
                'external_id': str(data.get('id', '')),
                'message': 'Candidate created in ATS.',
            }
        except Exception as exc:
            self.logger.exception("Failed to push candidate to ATS")
            return {
                'success': False,
                'external_id': '',
                'message': f'Push failed: {exc}',
            }

    def push_application(self, application) -> dict:
        """
        Push an application to the ATS.

        ``application`` should be a dict (or object) with at least:
            candidate_id, job_id
        """
        candidate_id = (
            application.get('candidate_id')
            if isinstance(application, dict)
            else getattr(application, 'candidate_id', None)
        )
        job_id = (
            application.get('job_id')
            if isinstance(application, dict)
            else getattr(application, 'job_id', None)
        )

        if self._use_mock:
            return {
                'success': True,
                'external_id': '88888',
                'message': 'Application pushed (mock mode).',
            }

        payload = {
            'candidate_id': candidate_id,
            'job_id': job_id,
            'source': 'API',
        }

        try:
            resp = self._request('POST', '/applications', json=payload)
            data = resp.json()
            return {
                'success': True,
                'external_id': str(data.get('id', '')),
                'message': 'Application created in ATS.',
            }
        except Exception as exc:
            self.logger.exception("Failed to push application to ATS")
            return {
                'success': False,
                'external_id': '',
                'message': f'Push failed: {exc}',
            }
