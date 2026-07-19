import sys, os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

app = FastAPI()

@app.get("/api/health")
async def health():
    return {"status": "healthy", "message": "LexiFlow API is running"}

@app.get("/api/admin/auth/login")
async def admin_login():
    return JSONResponse({"error": "Backend not fully loaded"}, status_code=500)

@app.get("/api/auth/register")
async def auth_register():
    return JSONResponse({"error": "Backend not fully loaded"}, status_code=500)

@app.get("/api/admin/firms/me")
async def firms_me():
    return JSONResponse({"error": "Backend not fully loaded"}, status_code=500)