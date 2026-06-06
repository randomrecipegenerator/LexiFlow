"""
Clio Grow (Lexicata) Enterprise CRM Client

Handles OAuth2 authentication, lead creation, contact management,
and webhook processing for the Clio Grow legal CRM platform.
"""
import os
import json
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ClioConfig:
    """Configuration for Clio Grow API access."""
    client_id: str = ""
    client_secret: str = ""
    access_token: str = ""
    refresh_token: str = ""
    redirect_uri: str = ""
    api_base_url: str = "https://grow.clio.com/api/v1"
    auth_base_url: str = "https://app.clio.com"
    api_version: str = "v1"


class ClioOAuthClient:
    """
    Manages OAuth2 PKCE flow for Clio Grow.

    Clio uses a standard OAuth2 flow:
    1. Get authorization URL for user to grant access
    2. Exchange authorization code for access + refresh tokens
    3. Use access token for API calls
    4. Refresh token when expired
    """

    def __init__(self, config: ClioConfig):
        self.config = config
        self._http: Optional[httpx.AsyncClient] = None
        self._token_expires_at: float = 0

    def get_authorization_url(self, state: str = "") -> str:
        """
        Generate the Clio OAuth authorization URL.

        Args:
            state: Optional CSRF state parameter
        Returns:
            URL for the user to authorize access
        """
        params = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
        }
        if state:
            params["state"] = state
        return f"{self.config.auth_base_url}/oauth/authorize?{urlencode(params)}"

    async def exchange_code(self, code: str) -> bool:
        """
        Exchange an authorization code for access and refresh tokens.

        Args:
            code: The authorization code from the OAuth callback
        Returns:
            True if token exchange succeeded
        """
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=30.0)

        try:
            response = await self._http.post(
                f"{self.config.auth_base_url}/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "code": code,
                    "redirect_uri": self.config.redirect_uri,
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.config.access_token = data.get("access_token", "")
                self.config.refresh_token = data.get("refresh_token", "")
                # Tokens typically last 2 hours
                self._token_expires_at = time.time() + (data.get("expires_in", 7200) - 300)
                return True
            logger.error(f"Clio token exchange failed: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Clio token exchange exception: {str(e)}")
            return False

    async def refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        if not self.config.refresh_token:
            return False

        if self._http is None:
            self._http = httpx.AsyncClient(timeout=30.0)

        try:
            response = await self._http.post(
                f"{self.config.auth_base_url}/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "refresh_token": self.config.refresh_token,
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.config.access_token = data.get("access_token", self.config.access_token)
                self.config.refresh_token = data.get("refresh_token", self.config.refresh_token)
                self._token_expires_at = time.time() + (data.get("expires_in", 7200) - 300)
                return True
            logger.error(f"Clio token refresh failed: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Clio token refresh exception: {str(e)}")
            return False

    async def close(self):
        if self._http:
            await self._http.aclose()


class ClioGrowClient:
    """
    Enterprise-grade Clio Grow CRM client for LexiFlow.

    Supports:
    - Lead (inbox_lead) creation and management
    - Contact search (deduplication)
    - Activity logging
    - Custom field mapping
    - OAuth2 authentication flow
    """

    def __init__(self, config: ClioConfig):
        self.config = config
        self.oauth = ClioOAuthClient(config)
        self._http: Optional[httpx.AsyncClient] = None

    async def _ensure_auth(self):
        """Ensure valid access token, refreshing if needed."""
        if time.time() >= self._token_expires_at and self.config.refresh_token:
            await self.oauth.refresh_access_token()

        if not self.config.access_token:
            raise ValueError("Clio: No access token available. Authenticate first.")

    @property
    def _token_expires_at(self):
        return self.oauth._token_expires_at

    @_token_expires_at.setter
    def _token_expires_at(self, value):
        self.oauth._token_expires_at = value

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def _request(
        self, method: str, path: str, **kwargs
    ) -> Dict[str, Any]:
        """Make an authenticated request to Clio Grow API with auto-refresh."""
        await self._ensure_auth()
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=30.0)

        url = f"{self.config.api_base_url}/{path.lstrip('/')}"
        headers = self._get_headers()

        for attempt in range(3):
            try:
                response = await self._http.request(method, url, headers=headers, **kwargs)
                if response.status_code == 401 and attempt < 2:
                    # Token expired, try refresh
                    if await self.oauth.refresh_access_token():
                        headers = self._get_headers()
                        continue
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if attempt < 2:
                    continue
                logger.error(f"Clio API error ({method} {path}): {str(e)}")
                return {"error": "api_error", "detail": str(e)}
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(1 * (2 ** attempt))
                    continue
                logger.error(f"Clio request failed ({method} {path}): {str(e)}")
                return {"error": "request_failed", "detail": str(e)}

    # --- Lead (Inbox) Operations ---

    async def create_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new lead in Clio Grow (inbox_lead).

        Standard fields: from_first, from_last, from_email,
        from_phone, from_message, referring_url
        """
        payload = {"inbox_lead": lead_data}
        return await self._request("POST", "inbox_leads", json=payload)

    async def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """Get lead details by ID."""
        return await self._request("GET", f"inbox_leads/{lead_id}")

    async def update_lead(self, lead_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing lead."""
        payload = {"inbox_lead": data}
        return await self._request("PATCH", f"inbox_leads/{lead_id}", json=payload)

    async def convert_to_matter(self, lead_id: str, matter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a lead to a matter (case) in Clio Grow.
        This is the intake-to-case conversion flow.
        """
        return await self._request("POST", f"inbox_leads/{lead_id}/convert", json=matter_data)

    # --- Contact Operations ---

    async def search_contacts(self, email: str = None, phone: str = None) -> List[Dict[str, Any]]:
        """Search for existing contacts by email or phone."""
        params = {}
        if email:
            params["q"] = email
        if phone:
            params["q"] = phone
        result = await self._request("GET", "contacts", params=params)
        return result.get("data", [])

    # --- Activity Logging ---

    async def log_activity(self, lead_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log an activity on a lead (e.g., "AI Qualified", "SMS Sent").
        """
        return await self._request(
            "POST", f"inbox_leads/{lead_id}/activities",
            json=activity_data
        )

    # --- Lead Mapping ---

    @staticmethod
    def map_lead_to_inbox(lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a LexiFlow lead to a Clio Grow inbox_lead payload.

        Expected lead_data keys: firstName, lastName, email, phone,
        description, caseType, aiSummary, qualificationScore, source
        """
        name_parts = (lead_data.get("firstName", "") + " " + lead_data.get("lastName", "")).strip()
        if not name_parts:
            name_parts = "Anonymous Lead"
        names = name_parts.split(" ", 1)
        first = names[0]
        last = names[1] if len(names) > 1 else "Lead"

        summary = lead_data.get("aiSummary") or lead_data.get("description", "")

        return {
            "from_first": first,
            "from_last": last,
            "from_email": lead_data.get("email", ""),
            "from_phone": lead_data.get("phone", ""),
            "from_message": summary[:500] if summary else "Synced from LexiFlow AI",
            "referring_url": f"https://lexiflow.co?source={lead_data.get('source', 'api')}",
            "custom_fields": {
                "ai_qualification_score": str(lead_data.get("qualificationScore", 0)),
                "case_type": lead_data.get("caseType", ""),
                "lexiflow_lead_id": str(lead_data.get("id", ""))
            }
        }

    async def close(self):
        await self.oauth.close()
        if self._http:
            await self._http.aclose()


import asyncio  # Import here to avoid circular issues at module level