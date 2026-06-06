import os
import uuid
import datetime

class DropboxSignClient:
    """
    Simulated Dropbox Sign (formerly HelloSign) API Client.
    In a real implementation, this would use the 'hellosign-python-sdk'.
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DROPBOX_SIGN_API_KEY", "simulated_key")
        self.client_id = os.getenv("DROPBOX_SIGN_CLIENT_ID", "simulated_client_id")

    def create_embedded_signature_request(self, lead_name, lead_email, document_type="Retainer"):
        """
        Simulates creating a signature request and returning a signature_id and signing_url.
        """
        request_id = f"ds_{uuid.uuid4().hex[:12]}"
        signature_id = f"sig_{uuid.uuid4().hex[:12]}"
        
        # In a real API, we would send the document and signer info to Dropbox Sign.
        # They would return a request object.
        
        return {
            "signature_request_id": request_id,
            "signature_id": signature_id,
            "signing_url": f"https://app.hellosign.com/editor/embeddedSign?signature_id={signature_id}",
            "status": "sent"
        }

    def get_signature_request_status(self, request_id):
        """
        Simulates checking the status of a request.
        """
        # In production, this would hit GET /signature_request/{id}
        return {
            "signature_request_id": request_id,
            "is_complete": False,
            "status": "awaiting_signature"
        }

# Global instance
esign_client = DropboxSignClient()
