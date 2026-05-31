from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION,
              description="AI-powered intake automation and lead qualification for law firms.")

app.add_middleware(CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "service": settings.APP_NAME}

@app.get("/api/pricing")
async def get_pricing():
    from app.pricing import SUBSCRIPTION_PLANS, USAGE_FEES, INTEGRATION_FEES, COMPETITOR_PRICES, SAVINGS_MESSAGE
    return {
        "plans": SUBSCRIPTION_PLANS,
        "usage_fees": USAGE_FEES,
        "integration_fees": INTEGRATION_FEES,
        "competitor_comparison": COMPETITOR_PRICES,
        "savings_message": SAVINGS_MESSAGE,
    }
