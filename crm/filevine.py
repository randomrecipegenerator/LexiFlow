"""
Filevine Enterprise CRM Client

Handles OAuth2 authentication, project creation, contact management,
document uploads, and webhook verification for the Filevine legal CRM.
"""
import os
import json
import time
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


@dataclass
class FilevineConfig:
    """Configuration for Filevine API access."""
    api_key: str = ""
    api_secret: str = ""
    session_id: str = ""
    org_id: str = ""
    webhook_secret: str = ""
    api_base_url: str = "https://api.filevine.io"
    auth_url: str = "https://auth.filevine.io"
    api_version: str = "v3"


class FilevineOAuthClient:
    """
    Manages OAuth2 token exchange for Filevine API.

    Filevine uses a session-based auth flow:
    1. Exchange api_key + api_secret for a session_id
    2. Use session_id for subsequent API calls
    """

    def __init__(self, config: FilevineConfig):
        self.config = config
        self._session: Optional[httpx.AsyncClient] = None
        self._token_expires_at: float = 0

    async def _get_client(self) -> httpx.AsyncClient:
        if self._session is None:
            self._session = httpx.AsyncClient(
                base_url=self.config.api_base_url,
                timeout=30.0
            )
        return self._session

    async def authenticate(self) -> bool:
        """
        Exchange API credentials for a session token.
        Returns True if authentication succeeded.
        """
        if time.time() < self._token_expires_at and self.config.session_id:
            return True  # Still valid

        client = await self._get_client()
        try:
            response = await client.post(
                f"{self.config.auth_url}/oauth/token",
                json={
                    "apiKey": self.config.api_key,
                    "apiSecret": self.config.api_secret
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.config.session_id = data.get("sessionId", "")
                # Sessions typically last 24 hours
                self._token_expires_at = time.time() + 82800
                return True
            else:
                logger.error(f"Filevine auth failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Filevine auth exception: {str(e)}")
            return False

    async def close(self):
        if self._session:
            await self._session.aclose()
            self._session = None


class FilevineClient:
    """
    Enterprise-grade Filevine CRM client for LexiFlow.

    Supports:
    - Project (case) creation and management
    - Contact creation and search
    - Document uploads
    - Custom field mapping
    - Webhook signature verification
    """

    def __init__(self, config: FilevineConfig):
        self.config = config
        self.oauth = FilevineOAuthClient(config)
        self._http: Optional[httpx.AsyncClient] = None

    async def _ensure_auth(self):
        """Ensure we have valid authentication before making API calls."""
        if not self.config.session_id:
            await self.oauth.authenticate()

    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-fv-apikey": self.config.api_key,
            "x-fv-sessionid": self.config.session_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _request(
        self, method: str, path: str, **kwargs
    ) -> Dict[str, Any]:
        """Make an authenticated request to the Filevine API with retry."""
        await self._ensure_auth()
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=30.0)

        url = f"{self.config.api_base_url}/{self.config.api_version}/{path.lstrip('/')}"
        headers = self._get_headers()

        for attempt in range(3):
            try:
                response = await self._http.request(
                    method, url, headers=headers, **kwargs
                )
                if response.status_code == 401 and attempt < 2:
                    # Token expired, re-authenticate
                    self.config.session_id = ""
                    await self._ensure_auth()
                    headers = self._get_headers()
                    continue
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return {"error": "not_found", "detail": str(e)}
                if attempt < 2:
                    await self._ensure_auth()
                    continue
                logger.error(f"Filevine API error ({method} {path}): {str(e)}")
                return {"error": "api_error", "detail": str(e)}
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(1 * (2 ** attempt))
                    continue
                logger.error(f"Filevine request failed ({method} {path}): {str(e)}")
                return {"error": "request_failed", "detail": str(e)}

    # --- Project (Case) Operations ---

    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project (case) in Filevine.

        Standard fields: projectName, typeId, personId, customFields
        """
        return await self._request("POST", "projects", json=project_data)

    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details by ID."""
        return await self._request("GET", f"projects/{project_id}")

    async def update_project(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing project."""
        return await self._request("PATCH", f"projects/{project_id}", json=data)

    async def search_projects(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search projects by custom query."""
        result = await self._request("POST", "projects/search", json=query)
        return result.get("items", [])

    # --- Contact Operations ---

    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a contact (person) in Filevine.

        Fields: firstName, lastName, email, phone, address, etc.
        """
        return await self._request("POST", "contacts", json=contact_data)

    async def search_contacts(self, email: str = None, phone: str = None) -> List[Dict[str, Any]]:
        """Search for contacts by email or phone for deduplication."""
        params = {}
        if email:
            params["email"] = email
        if phone:
            params["phone"] = phone
        result = await self._request("GET", "contacts", params=params)
        if isinstance(result, list):
            return result
        return result.get("items", [])

    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get contact details by ID."""
        return await self._request("GET", f"contacts/{contact_id}")

    # --- Document Operations ---

    async def upload_document(
        self, project_id: str, file_name: str, file_content: bytes,
        section_name: str = "General"
    ) -> Dict[str, Any]:
        """
        Upload a document to a Filevine project.
        Returns the document metadata.
        """
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=60.0)

        await self._ensure_auth()
        url = f"{self.config.api_base_url}/{self.config.api_version}/projects/{project_id}/documents"
        headers = self._get_headers()

        files = {
            "file": (file_name, file_content, "application/octet-stream"),
            "sectionName": (None, section_name)
        }

        for attempt in range(3):
            try:
                response = await self._http.post(url, headers=headers, files=files)
                if response.status_code == 401 and attempt < 2:
                    self.config.session_id = ""
                    await self._ensure_auth()
                    headers = self._get_headers()
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(1 * (2 ** attempt))
                    continue
                return {"error": "upload_failed", "detail": str(e)}

    # --- Custom Fields ---

    async def get_custom_fields(self, project_type_id: str) -> List[Dict[str, Any]]:
        """Get custom field definitions for a project type."""
        result = await self._request("GET", f"projecttypes/{project_type_id}/fields")
        if isinstance(result, list):
            return result
        return result.get("items", [])

    async def set_custom_field(
        self, project_id: str, field_id: str, value: Any
    ) -> Dict[str, Any]:
        """Set a custom field value on a project."""
        return await self._request(
            "PUT", f"projects/{project_id}/customfields/{field_id}",
            json={"value": value}
        )

    # --- Webhook Verification ---

    @staticmethod
    def verify_webhook_signature(
        payload: bytes, signature: str, secret: str
    ) -> bool:
        """
        Verify that a webhook payload came from Filevine.
        Uses HMAC-SHA256 with the webhook secret.

        Args:
            payload: Raw request body bytes
            signature: The x-fv-signature header value
            secret: The configured webhook secret
        Returns:
            True if signature is valid
        """
        if not secret or not signature:
            return False
        expected = hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def close(self):
        await self.oauth.close()
        if self._http:
            await self._http.aclose()

    # --- Lead Mapping ---

    @staticmethod
    def map_lead_to_project(
        lead_data: Dict[str, Any],
        project_type_id: str,
        section_name: str = "Intake"
    ) -> Dict[str, Any]:
        """
        Map a LexiFlow lead to a Filevine project payload.

        Expected lead_data keys: firstName, lastName, email, phone,
        description, caseType, caseValue, source, aiSummary
        """
        first = lead_data.get("firstName", "").strip()
        last = lead_data.get("lastName", "").strip() or "Lead"

        return {
            "projectName": f"{first} {last} - {lead_data.get('caseType', 'Intake')}",
            "typeId": project_type_id,
            "sectionName": section_name,
            "customFields": {
                "contactEmail": lead_data.get("email", ""),
                "contactPhone": lead_data.get("phone", ""),
                "caseDescription": lead_data.get("description", ""),
                "leadSource": lead_data.get("source", "LexiFlow AI"),
                "aiScore": str(lead_data.get("qualificationScore", 0)),
                "caseValue": str(lead_data.get("caseValue", 0)),
                "aiSummary": lead_data.get("aiSummary", "")
            },
            "persons": [{
                "firstName": first,
                "lastName": last,
                "email": lead_data.get("email", ""),
                "phone": lead_data.get("phone", ""),
                "type": "Client"
            }]
        }


import asyncio  # Import here to avoid circular issues at module level