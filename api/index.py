"""
Vercel serverless entry point for LexiFlow API.
Routes all /api/* requests to the FastAPI application.
Uses Vercel's Python ASGI support.
"""
import os
import sys

# Add root directory to Python path for imports
# This allows 'import backend.main' to work regardless of where the function is executed from
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import and expose the FastAPI app
try:
    from backend.main import app
    # Vercel's Python runtime searches for a variable named 'app' or 'handler'
    handler = app
except ImportError as e:
    # Basic fallback or error logging for deployment debugging
    print(f"Import error in api/index.py: {e}")
    raise e
