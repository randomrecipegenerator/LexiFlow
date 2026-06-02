"""Vercel serverless function handler for LexiFlow Legal Suite API."""
from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    """Handle all API requests routed through Vercel."""

    def do_GET(self):
        """Route GET requests based on path."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path == '/api/health' or self.path == '/health':
            response = {
                "status": "healthy",
                "service": "LexiFlow Legal Suite API",
                "version": "1.0.0",
                "uptime": "operational"
            }
        elif self.path == '/api' or self.path == '/':
            response = {
                "status": "ok",
                "service": "LexiFlow Legal Suite API",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/api/health",
                    "leads": "/api/leads",
                    "chat": "/api/chat"
                }
            }
        else:
            response = {
                "status": "ok",
                "endpoint": self.path,
                "message": "LexiFlow Legal Suite API"
            }

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "status": "ok",
            "endpoint": self.path,
            "message": "LexiFlow Legal Suite API - POST received"
        }
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()