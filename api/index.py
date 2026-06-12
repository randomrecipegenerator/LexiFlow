import sys
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Initialize the main app from main.py in root
try:
    from main import app as backend_app
except Exception as e:
    # If backend fails to import, provide a fallback app
    backend_app = FastAPI()
    @backend_app.all("/{path:path}")
    async def fallback(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": "Backend initialization failed", "details": str(e)}
        )

# In Vercel, this file is the entry point.
# We use the backend_app directly.
# The middleware in main.py will handle stripping /api if needed.
app = backend_app
