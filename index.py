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
    from main import app as backend_app
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
async def health(request: Request):
    return {
        "status": "healthy",
        "environment": "vercel" if os.getenv("VERCEL") else "local",
        "path": request.url.path,
        "query_params": str(request.query_params),
        "ai_configured": os.getenv("AI_API_KEY") is not None
    }

# Standardize the path by removing /api prefix if present
# This makes the app resilient to whether the rewrite stripped the prefix or not
@app.middleware("http")
async def standardize_path(request: Request, call_next):
    path = request.url.path
    # If the path starts with /api/, we strip it because the mounted backend_app 
    # expects routes starting from root (e.g. /chat/start)
    if path.startswith("/api/"):
        scope = request.scope.copy()
        scope["path"] = path[4:] # Keep the leading slash: /api/chat/start -> /chat/start
        
        from starlette.requests import Request as StarletteRequest
        request = StarletteRequest(scope, receive=request.receive)
    elif path == "/api":
        scope = request.scope.copy()
        scope["path"] = "/"
        from starlette.requests import Request as StarletteRequest
        request = StarletteRequest(scope, receive=request.receive)
        
    response = await call_next(request)
    return response

# Mount the backend app at the root
# The middleware above ensures it sees paths without "/api"
app.mount("/", backend_app)
