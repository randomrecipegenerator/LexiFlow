
from fastapi import FastAPI
app = FastAPI()
@app.get("/api/health")
@app.get("/health")
def health():
    return {"status": "ok", "source": "health.py"}
