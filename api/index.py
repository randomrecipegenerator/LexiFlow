"""
Vercel serverless entry point for LexiFlow API.

Routes all /api/* requests to the FastAPI application.
Uses Vercel's Python ASGI support.
"""
import os
import sys

# Add backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Import and expose the FastAPI app
from backend.main import app as handler