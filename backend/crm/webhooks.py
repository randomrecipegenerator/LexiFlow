"""
CRM Webhook Receivers for LexiFlow.

Handles inbound webhooks from Filevine, Clio Grow, and LeadDock
so LexiFlow can respond to events in real-time (bidirectional sync).

Supported events:
- Filevine: project.created, project.updated, contact.created
- Clio Grow: lead.created, lead.updated, lead.converted
- LeadDock: lead.created, lead.updated
"""
import json
import hashlib
import hmac
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field

from fastapi import Request, HTTPException
import httpx

logger = logging.getLogger(__name__)


@dataclass
class WebhookEvent:
    """Normalized webhook event from any CRM."""
    source: str  # "filevine", "clio", "leaddock"
    event_type: str  # e.g. "project.created", "lead.converted"
    external_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    raw_payload: Dict[str, Any] = field(default_factory=dict)


class WebhookVerifier:
    """Verify webhook signatures for supported CRMs."""

    @staticmethod
    def verify_filevine(payload: bytes, signature: str, secret: str) -> bool:
        """HMAC-SHA256 verification for Filevine webhooks."""
        if not secret or not signature:
            return False
        expected = hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    @staticmethod
    def verify_clio(payload: bytes, signature: str, secret: str) -> bool:
        """HMAC-SHA256 verification for Clio webhooks."""
        if not secret or not signature:
            return False
        expected = hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def verify_leaddock(api_key: str, expected_key: str) -> bool:
        """Simple API key verification for LeadDock webhooks."""
        return hmac.compare_digest(api_key, expected_key)


class WebhookHandler:
    """
    Routes webhook events from various CRMs to registered handlers.

    Usage:
        handler = WebhookHandler()
        handler.register("filevine", "project.created", my_handler)
        await handler.process(event)
    """

    def __init__(self):
        self._handlers: Dict[str, Dict[str, list]] = {}
        self._verifiers = WebhookVerifier()

    def register(
        self,
        source: str,
        event_type: str,
        handler_fn: Callable[[WebhookEvent], Awaitable[Dict[str, Any]]]
    ):
        """Register a handler function for a specific source + event type."""
        if source not in self._handlers:
            self._handlers[source] = {}
        if event_type not in self._handlers[source]:
            self._handlers[source][event_type] = []
        self._handlers[source][event_type].append(handler_fn)
        logger.info(f"Registered webhook handler: {source}/{event_type}")

    async def process(self, event: WebhookEvent) -> list:
        """
        Dispatch a webhook event to all registered handlers.
        Returns list of handler results.
        """
        results = []
        source_handlers = self._handlers.get(event.source, {})
        handlers = source_handlers.get(event.event_type, [])

        if not handlers:
            logger.info(f"No handlers for {event.source}/{event.event_type}")
            return []

        for handler_fn in handlers:
            try:
                result = await handler_fn(event)
                results.append(result)
            except Exception as e:
                logger.error(f"Webhook handler error: {str(e)}")
                results.append({"error": str(e)})

        return results


# =========================================================================
# FastAPI route handlers for webhook endpoints
# =========================================================================

async def handle_filevine_webhook(
    request: Request,
    webhook_secret: str,
    handler: WebhookHandler
) -> Dict[str, Any]:
    """
    FastAPI route handler for Filevine webhooks.

    Expects:
    - Header: x-fv-signature (HMAC-SHA256)
    - Body: Filevine event payload
    """
    body = await request.body()
    signature = request.headers.get("x-fv-signature", "")

    if not WebhookVerifier.verify_filevine(body, signature, webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = json.loads(body)
    event_type = payload.get("event", {}).get("type", "unknown")
    external_id = str(payload.get("event", {}).get("objectId", ""))

    event = WebhookEvent(
        source="filevine",
        event_type=event_type,
        external_id=external_id,
        data=payload.get("event", {}),
        raw_payload=payload
    )

    await handler.process(event)
    return {"status": "received"}


async def handle_clio_webhook(
    request: Request,
    webhook_secret: str,
    handler: WebhookHandler
) -> Dict[str, Any]:
    """
    FastAPI route handler for Clio Grow webhooks.

    Expects:
    - Header: x-clio-webhook-signature
    - Body: Clio event payload
    """
    body = await request.body()
    signature = request.headers.get("x-clio-webhook-signature", "")

    if not WebhookVerifier.verify_clio(body, signature, webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = json.loads(body)
    event = payload.get("event", {})
    event_type = event.get("type", "unknown")
    external_id = str(event.get("id", ""))

    event_obj = WebhookEvent(
        source="clio",
        event_type=event_type,
        external_id=external_id,
        data=event,
        raw_payload=payload
    )

    await handler.process(event_obj)
    return {"status": "received"}


async def handle_leaddock_webhook(
    request: Request,
    expected_api_key: str,
    handler: WebhookHandler
) -> Dict[str, Any]:
    """
    FastAPI route handler for LeadDock webhooks.

    Expects:
    - Header: x-api-key
    - Body: LeadDock event payload
    """
    api_key = request.headers.get("x-api-key", "")

    if not WebhookVerifier.verify_leaddock(api_key, expected_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

    payload = await request.json()
    event_type = payload.get("event", "lead.updated")
    external_id = str(payload.get("lead", {}).get("id", ""))

    event_obj = WebhookEvent(
        source="leaddock",
        event_type=event_type,
        external_id=external_id,
        data=payload.get("lead", payload),
        raw_payload=payload
    )

    await handler.process(event_obj)
    return {"status": "received"}


# =========================================================================
# Built-in handlers for common CRM events
# =========================================================================

async def on_filevine_project_created(event: WebhookEvent) -> Dict[str, Any]:
    """
    When a project is created in Filevine, update the matching LexiFlow lead.
    """
    logger.info(f"Filevine project created: {event.external_id}")
    # In production: query LexiFlow DB for matching lead and update status
    return {"action": "project_created", "external_id": event.external_id}


async def on_clio_lead_converted(event: WebhookEvent) -> Dict[str, Any]:
    """
    When a lead is converted to a matter in Clio, update LexiFlow.
    """
    logger.info(f"Clio lead converted: {event.external_id}")
    return {"action": "lead_converted", "external_id": event.external_id}


async def on_leaddock_lead_updated(event: WebhookEvent) -> Dict[str, Any]:
    """
    When a lead is updated in LeadDock, sync status back to LexiFlow.
    """
    logger.info(f"LeadDock lead updated: {event.external_id}")
    return {"action": "lead_updated", "external_id": event.external_id}