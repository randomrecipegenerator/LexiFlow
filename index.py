import sys
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Initialize the main app from backend
try:
    from backend.main import app as backend_app
except Exception as e:
    # If backend fails to import (e.g. database error), provide a fallback app
    backend_app = FastAPI()
    @backend_app.all("/{path:path}")
    async def fallback(path: str):
        return JSONResponse(
            status_code=500,
            content={"error": "Backend initialization failed", "details": str(e)}
        )

app = FastAPI()

@app.get("/api/health")
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": "vercel" if os.getenv("VERCEL") else "local",
        "database": os.getenv("DATABASE_URL", "sqlite")[:10] + "...",
        "ai_configured": os.getenv("AI_API_KEY") is not None
    }

# Explicitly mount the backend app at both /api and /
# This ensures that /api/chat/start and /chat/start both work
app.mount("/api", backend_app)
app.mount("/", backend_app)
