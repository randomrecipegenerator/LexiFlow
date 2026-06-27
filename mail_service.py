import os
import json
import logging
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class MailService:
    """
    Unified Email Service for LexiFlow.
    Supports Postmark, SMTP, and placeholder simulation.
    """
    def __init__(self):
        self.postmark_server_token = os.getenv("POSTMARK_SERVER_TOKEN")
        self.postmark_from_email = os.getenv("POSTMARK_FROM_EMAIL", "info@lexiflow.co")
        
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_from = os.getenv("EMAIL_FROM", self.postmark_from_email)

    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        html_body: str = None,
        firm=None
    ) -> Dict[str, Any]:
        """
        Send an email using the best available provider.
        """
        # 1. Try Postmark if configured for firm or globally
        api_key = None
        from_email = self.postmark_from_email
        
        if firm and firm.api_config_json:
            try:
                config = json.loads(firm.api_config_json)
                api_key = config.get("postmark_api_key")
                if config.get("email_from"):
                    from_email = config.get("email_from")
            except:
                pass
        
        if not api_key:
            api_key = self.postmark_server_token

        if api_key and "placeholder" not in api_key.lower():
            return await self._send_postmark(api_key, from_email, to_email, subject, body, html_body)

        # 2. Try SMTP if configured
        if self.smtp_host and self.smtp_user and self.smtp_password:
            return await self._send_smtp(to_email, subject, body, html_body)

        # 3. Fallback to simulation
        logger.info(f"SIMULATED EMAIL to {to_email}: {subject}")
        return {
            "status": "success", 
            "simulated": True,
            "to": to_email,
            "subject": subject
        }

    async def _send_postmark(self, api_key: str, from_email: str, to_email: str, subject: str, body: str, html_body: str = None) -> Dict[str, Any]:
        payload = {
            "From": from_email,
            "To": to_email,
            "Subject": subject,
            "TextBody": body,
            "MessageStream": "outbound"
        }
        if html_body:
            payload["HtmlBody"] = html_body

        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(
                    "https://api.postmarkapp.com/email",
                    json=payload,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-Postmark-Server-Token": api_key
                    }
                )
                result = res.json()
                logger.info(f"Postmark Response: {result}")
                return result
            except Exception as e:
                logger.error(f"Postmark send failed: {str(e)}")
                return {"status": "error", "message": str(e)}

    async def _send_smtp(self, to_email: str, subject: str, body: str, html_body: str = None) -> Dict[str, Any]:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_from
            msg["To"] = to_email

            part1 = MIMEText(body, "plain")
            msg.attach(part1)

            if html_body:
                part2 = MIMEText(html_body, "html")
                msg.attach(part2)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.email_from, to_email, msg.as_string())
            
            logger.info(f"SMTP Email sent to {to_email}")
            return {"status": "success", "provider": "smtp"}
        except Exception as e:
            logger.error(f"SMTP send failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def send_template_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        variables: Dict[str, Any],
        firm=None
    ) -> Dict[str, Any]:
        """
        Load an HTML template, replace variables, and send.
        """
        template_path = os.path.join(os.path.dirname(__file__), "templates", "email", f"{template_name}.html")
        if not os.path.exists(template_path):
            logger.error(f"Email template not found: {template_path}")
            return await self.send_email(to_email, subject, f"Error: Template {template_name} missing.", firm=firm)

        with open(template_path, 'r') as f:
            html_content = f.read()

        # Simple replacement
        for key, value in variables.items():
            html_content = html_content.replace(f"{{{{{key}}}}}", str(value))

        # Plain text fallback
        import re
        text_content = re.sub('<[^<]+?>', '', html_content)

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            body=text_content,
            html_body=html_content,
            firm=firm
        )

mail_service = MailService()
