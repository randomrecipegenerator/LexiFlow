"""
LexiFlow Postmark Client — Automated Outreach Engine

Handles transactional and bulk email dispatch through Postmark API.
Supports templates, batch sending, webhook tracking, and personalized
outreach sequences for sales automation.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


@dataclass
class PostmarkConfig:
    """Postmark API configuration."""
    server_token: str = ""
    from_email: str = "lexiflow-legal-suite-88a6f8e9@ctomail.io"
    from_name: str = "LexiFlow Technologies Inc"
    api_base_url: str = "https://api.postmarkapp.com"
    message_stream: str = "outbound"
    track_opens: bool = True
    track_links: bool = True


class PostmarkClient:
    """
    Enterprise Postmark email client for LexiFlow.

    Supports:
    - Single and batch email sending
    - Template-based emails
    - Personalized dispatch from outreach sheets
    - Attachment support (retainers, forms)
    - Webhook event processing (opens, clicks, bounces)
    - Email status tracking
    """

    def __init__(self, config: Optional[PostmarkConfig] = None):
        self.config = config or PostmarkConfig()
        self._http: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(
                base_url=self.config.api_base_url,
                timeout=30.0
            )
        return self._http

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Postmark-Server-Token": self.config.server_token
        }

    def is_configured(self) -> bool:
        """Check if Postmark is properly configured."""
        return bool(self.config.server_token) and \
               "placeholder" not in self.config.server_token.lower()

    # =====================================================================
    # Single Email Sending
    # =====================================================================

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: Optional[str] = None,
        text_body: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, str]] = None,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a single email via Postmark.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML version of the email
            text_body: Plain text version
            cc: CC recipient
            bcc: BCC recipient
            attachments: List of attachment dicts with Name, Content, ContentType
            metadata: Custom metadata key-value pairs (strings)
            tag: Email tag for categorization
        Returns:
            Postmark API response
        """
        if not self.is_configured():
            logger.info(f"SIMULATED EMAIL to {to_email}: {subject}")
            return {
                "status": "success",
                "simulated": True,
                "to": to_email,
                "subject": subject,
                "message": "Postmark not configured — simulated send"
            }

        payload = {
            "From": f"{self.config.from_name} <{self.config.from_email}>",
            "To": to_email,
            "Subject": subject,
            "MessageStream": self.config.message_stream,
            "TrackOpens": self.config.track_opens,
        }

        if html_body:
            payload["HtmlBody"] = html_body
        if text_body:
            payload["TextBody"] = text_body
        if cc:
            payload["Cc"] = cc
        if bcc:
            payload["Bcc"] = bcc
        if attachments:
            payload["Attachments"] = attachments
        if metadata:
            payload["Metadata"] = metadata
        if tag:
            payload["Tag"] = tag

        client = self._get_client()
        try:
            response = await client.post(
                "/email",
                json=payload,
                headers=self._get_headers()
            )
            result = response.json()
            if response.status_code == 200:
                logger.info(f"Email sent to {to_email}: MessageID={result.get('MessageID', 'N/A')}")
            else:
                logger.error(f"Postmark send error: {response.status_code} - {result}")
            return result
        except Exception as e:
            logger.error(f"Postmark connection error: {str(e)}")
            return {"ErrorCode": -1, "Message": str(e)}

    # =====================================================================
    # Template-Based Sending
    # =====================================================================

    async def send_template(
        self,
        to_email: str,
        template_id: int,
        template_model: Dict[str, Any],
        subject: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an email using a Postmark template.

        Args:
            to_email: Recipient
            template_id: Postmark template ID
            template_model: Dict of template variables
            subject: Override subject (optional)
            cc, bcc: Additional recipients
            metadata: Custom metadata
            tag: Email tag
        """
        if not self.is_configured():
            logger.info(f"SIMULATED TEMPLATE to {to_email}: template_id={template_id}")
            return {"status": "success", "simulated": True}

        payload = {
            "From": f"{self.config.from_name} <{self.config.from_email}>",
            "To": to_email,
            "TemplateId": template_id,
            "TemplateModel": template_model,
            "MessageStream": self.config.message_stream,
            "TrackOpens": self.config.track_opens,
        }
        if subject:
            payload["Subject"] = subject
        if cc:
            payload["Cc"] = cc
        if bcc:
            payload["Bcc"] = bcc
        if metadata:
            payload["Metadata"] = metadata
        if tag:
            payload["Tag"] = tag

        client = self._get_client()
        try:
            response = await client.post(
                "/email/withTemplate",
                json=payload,
                headers=self._get_headers()
            )
            return response.json()
        except Exception as e:
            logger.error(f"Postmark template error: {str(e)}")
            return {"ErrorCode": -1, "Message": str(e)}

    # =====================================================================
    # Batch Sending
    # =====================================================================

    async def send_batch(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Send up to 500 emails in a single API call (Postmark batch).

        Each message in the list should have the same structure as
        a single email payload: To, Subject, HtmlBody/TextBody, etc.
        """
        if not self.is_configured():
            logger.info(f"SIMULATED BATCH: {len(messages)} emails")
            return [{"status": "success", "simulated": True} for _ in messages]

        # Ensure each message has From set
        from_addr = f"{self.config.from_name} <{self.config.from_email}>"
        for msg in messages:
            msg.setdefault("From", from_addr)
            msg.setdefault("MessageStream", self.config.message_stream)
            msg.setdefault("TrackOpens", self.config.track_opens)

        client = self._get_client()
        try:
            response = await client.post(
                "/email/batch",
                json=messages,
                headers=self._get_headers()
            )
            results = response.json()
            success_count = sum(1 for r in results if r.get("ErrorCode") == 0)
            logger.info(f"Batch sent: {success_count}/{len(messages)} succeeded")
            return results
        except Exception as e:
            logger.error(f"Postmark batch error: {str(e)}")
            return [{"ErrorCode": -1, "Message": str(e)} for _ in messages]

    # =====================================================================
    # Dispatch from Outreach Sheets
    # =====================================================================

    async def send_dispatch(
        self,
        dispatch_rows: List[Dict[str, Any]],
        from_firm_name: str = "LexiFlow Technologies Inc",
    ) -> List[Dict[str, Any]]:
        """
        Send personalized outreach emails from a dispatch sheet.

        Each dispatch row should contain:
        - to_email: Recipient
        - first_name: For personalization
        - practice_area: e.g. "Personal Injury"
        - message_body: Personalized email body (HTML)
        - subject: Email subject
        - Optional: cc, bcc, attachments, metadata

        Auto-inserts firm branding and signature.
        """
        messages = []
        for row in dispatch_rows:
            first_name = row.get("first_name", "there")
            practice_area = row.get("practice_area", "legal")
            body = row.get("message_body", "")
            subject = row.get("subject", f"LexiFlow for {practice_area} Firms")

            # Build HTML body with branding
            html_body = f"""
            <html>
            <body style="font-family: 'Inter', Arial, sans-serif; color: #1a3a5c; max-width: 600px; margin: 0 auto;">
                <div style="padding: 20px 0;">
                    {body}
                </div>
                <div style="border-top: 2px solid #c9a84c; padding: 15px 0; font-size: 12px; color: #666;">
                    <p style="margin: 0;">
                        <strong>{from_firm_name}</strong><br>
                        AI-Powered Legal Intake & Lead Qualification<br>
                        <a href="https://lexiflow.co" style="color: #c9a84c;">lexiflow.co</a>
                    </p>
                </div>
            </body>
            </html>
            """

            msg = {
                "To": row["to_email"],
                "Subject": subject,
                "HtmlBody": html_body,
                "Tag": "outreach-dispatch",
                "Metadata": {
                    "first_name": first_name,
                    "practice_area": practice_area,
                    "dispatch_batch": datetime.utcnow().strftime("%Y%m%d%H%M"),
                }
            }

            if row.get("cc"):
                msg["Cc"] = row["cc"]
            if row.get("attachments"):
                msg["Attachments"] = row["attachments"]

            messages.append(msg)

        return await self.send_batch(messages)

    # =====================================================================
    # Email Status & Tracking
    # =====================================================================

    async def get_email_status(self, message_id: str) -> Dict[str, Any]:
        """Get delivery status for a sent email."""
        if not self.is_configured():
            return {"status": "unknown", "simulated": True}

        client = self._get_client()
        try:
            response = await client.get(
                f"/messages/outbound/{message_id}/details",
                headers=self._get_headers()
            )
            return response.json()
        except Exception as e:
            logger.error(f"Postmark status error: {str(e)}")
            return {"ErrorCode": -1, "Message": str(e)}

    async def get_bounce_status(self, message_id: str) -> Dict[str, Any]:
        """Check if an email bounced and get bounce details."""
        if not self.is_configured():
            return {"bounced": False, "simulated": True}

        client = self._get_client()
        try:
            response = await client.get(
                f"/messages/outbound/{message_id}/bounces",
                headers=self._get_headers()
            )
            return response.json()
        except Exception as e:
            logger.error(f"Postmark bounce error: {str(e)}")
            return {"ErrorCode": -1, "Message": str(e)}

    # =====================================================================
    # Stats
    # =====================================================================

    async def get_stats(
        self, from_date: str = "", to_date: str = "", tag: str = ""
    ) -> Dict[str, Any]:
        """Get Postmark sending statistics for the configured server."""
        if not self.is_configured():
            return {"status": "unavailable", "simulated": True}

        params = {}
        if from_date:
            params["fromdate"] = from_date
        if to_date:
            params["todate"] = to_date
        if tag:
            params["tag"] = tag

        client = self._get_client()
        try:
            response = await client.get(
                "/stats/outbound",
                params=params,
                headers=self._get_headers()
            )
            return response.json()
        except Exception as e:
            logger.error(f"Postmark stats error: {str(e)}")
            return {"ErrorCode": -1, "Message": str(e)}

    async def close(self):
        if self._http:
            await self._http.aclose()


# =====================================================================
# Convienience: Module-level singleton
# =====================================================================

def create_from_config(config_dict: Dict[str, Any]) -> PostmarkClient:
    """Create a PostmarkClient from a config dict (e.g. from Firm.api_config_json)."""
    cfg = PostmarkConfig(
        server_token=config_dict.get("postmark_api_key", ""),
        from_email=config_dict.get("postmark_from_email", "lexiflow-legal-suite-88a6f8e9@ctomail.io"),
        from_name=config_dict.get("postmark_from_name", "LexiFlow Technologies Inc"),
    )
    return PostmarkClient(cfg)


postmark_client = PostmarkClient()


# =====================================================================
# FastAPI Router — Postmark Dispatch Endpoints
# =====================================================================

from fastapi import APIRouter, Depends, HTTPException, Header, Body, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Firm, Lead, AuditLog

router = APIRouter(prefix="/api/email", tags=["Email Dispatch"])


def _get_firm(x_firm_slug: str = Header(...), db: Session = Depends(get_db)):
    """Get firm from header."""
    firm = db.query(Firm).filter(Firm.slug == x_firm_slug).first()
    if not firm:
        raise HTTPException(404, "Firm not found")
    return firm


@router.post("/send")
async def send_single_email(
    to_email: str = Body(...),
    subject: str = Body(...),
    body: str = Body(""),
    template_id: int = Body(None),
    template_model: Dict[str, Any] = Body(None),
    firm: Firm = Depends(_get_firm),
    db: Session = Depends(get_db)
):
    """Send a single email via Postmark for this firm."""
    config = {}
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
        except: pass

    client = create_from_config(config)

    if template_id and template_model:
        result = await client.send_template(to_email, template_id, template_model, subject=subject)
    else:
        result = await client.send_email(to_email, subject, html_body=body)

    # Log
    log = AuditLog(
        firm_id=firm.id,
        action="email_sent",
        details=json.dumps({"to": to_email, "subject": subject, "result": result.get("MessageID", "simulated")})
    )
    db.add(log)
    db.commit()

    return result


@router.post("/dispatch")
async def send_dispatch_batch(
    dispatch_rows: List[Dict[str, Any]] = Body(...),
    firm: Firm = Depends(_get_firm),
    db: Session = Depends(get_db)
):
    """Send a batch of personalized outreach emails from a dispatch sheet."""
    config = {}
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
        except: pass

    client = create_from_config(config)
    results = await client.send_dispatch(dispatch_rows, from_firm_name=firm.name or "LexiFlow")

    # Log
    log = AuditLog(
        firm_id=firm.id,
        action="dispatch_batch",
        details=json.dumps({"count": len(dispatch_rows), "success_count": sum(1 for r in results if r.get("ErrorCode") == 0)})
    )
    db.add(log)
    db.commit()

    return {"total": len(results), "results": results}


@router.get("/stats")
async def get_email_stats(
    from_date: str = Query(""),
    to_date: str = Query(""),
    firm: Firm = Depends(_get_firm),
):
    """Get Postmark email statistics."""
    config = {}
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
        except: pass

    client = create_from_config(config)
    return await client.get_stats(from_date=from_date, to_date=to_date)


@router.get("/status/{message_id}")
async def get_message_status(
    message_id: str,
    firm: Firm = Depends(_get_firm),
):
    """Get delivery status for a sent email."""
    config = {}
    if firm.api_config_json:
        try:
            config = json.loads(firm.api_config_json)
        except: pass

    client = create_from_config(config)
    return await client.get_email_status(message_id)