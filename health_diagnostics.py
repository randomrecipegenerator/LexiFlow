"""
LexiFlow Enterprise Health Diagnostics Module.

Provides comprehensive system health checks for all Enterprise Suite modules:
1. Discovery-Vault™ — AI document processing pipeline
2. Settlement-Predictor Pro™ — Case valuation engine + damage caps DB
3. DepoLens™ / Veritas Deposition™ — Deposition analysis + contradiction engine
4. Compliance-Shield™ — HIPAA monitoring
5. CRM Integration — Filevine, Clio sync engines
6. AI Engine — OpenAI/Groq connectivity
7. Database — SQLAlchemy / Turso connectivity
8. Desktop Backend — Sync engine status
"""
import os
import json
import logging
import importlib
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HealthDiagnostics:
    """Runs health checks across all Enterprise modules and infrastructure."""

    def __init__(self):
        self.start_time = datetime.utcnow()
        self.results: Dict[str, Any] = {}

    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive diagnostics."""
        checks = {
            "system": self._check_system(),
            "database": await self._check_database(),
            "ai_engine": self._check_ai_engine(),
            "enterprise_modules": self._check_enterprise_modules(),
            "crm_integration": self._check_crm_integration(),
            "desktop_backend": self._check_desktop_backend(),
            "auth": self._check_auth(),
        }

        # Calculate overall status
        all_ok = all(
            c.get("status") == "ok" or c.get("status") == "configured"
            for c in checks.values()
        )

        return {
            "service": "LexiFlow Enterprise Suite",
            "version": "1.0.0",
            "environment": os.getenv("VERCEL", "local") if os.getenv("VERCEL") else "local",
            "uptime_seconds": (datetime.utcnow() - self.start_time).seconds,
            "overall_status": "healthy" if all_ok else "degraded",
            "modules": checks,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _check_system(self) -> Dict:
        """System-level health checks."""
        return {
            "status": "ok",
            "python_version": __import__('sys').version[:6],
            "platform": __import__('sys').platform,
        }

    async def _check_database(self) -> Dict:
        """Check database connectivity via SQLAlchemy."""
        try:
            from database import SessionLocal
            db = SessionLocal()
            result = db.execute(__import__('sqlalchemy').text("SELECT 1 as ok")).fetchone()
            db.close()
            if result and result[0] == 1:
                return {"status": "ok", "engine": "SQLAlchemy"}
            return {"status": "error", "detail": "Query returned unexpected result"}
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return {"status": "degraded", "detail": str(e), "note": "Demo mode — DB not required"}

    def _check_ai_engine(self) -> Dict:
        """Check AI engine configuration."""
        try:
            from ai_engine import client, model_name, api_key
            if client and api_key:
                return {"status": "ok", "model": model_name, "provider": "OpenAI/Groq"}
            elif api_key:
                return {"status": "configured", "model": model_name, "note": "API key set, client ready"}
            return {"status": "degraded", "detail": "No API key configured", "note": "Running in mock/demo mode"}
        except Exception as e:
            return {"status": "degraded", "detail": str(e)}

    def _check_enterprise_modules(self) -> Dict:
        """Check all Enterprise modules are importable."""
        modules = {
            "discovery_vault": {"import": "enterprise_api", "status": "unknown"},
            "settlement_predictor": {"import": "enterprise_api", "features": ["damage_caps"]},
            "depolens": {"import": "enterprise_api"},
            "compliance_shield": {"import": "enterprise_api"},
        }

        try:
            ent = importlib.import_module('enterprise_api')
            modules["discovery_vault"]["status"] = "ok"
            modules["settlement_predictor"]["status"] = "ok"
            modules["depolens"]["status"] = "ok"
            modules["compliance_shield"]["status"] = "ok"

            # Check damage caps data
            try:
                caps = importlib.import_module('damage_caps')
                cap_count = len(caps.STATE_DAMAGE_CAPS)
                modules["settlement_predictor"]["damage_caps_loaded"] = f"{cap_count} states"
            except ImportError:
                modules["settlement_predictor"]["damage_caps_loaded"] = "not_loaded"

        except ImportError as e:
            for m in modules.values():
                m["status"] = "error"
                m["detail"] = str(e)

        return {
            "status": "ok",
            "route_prefix": "/api/enterprise",
            "modules_available": list(modules.keys()),
            "details": modules,
        }

    def _check_crm_integration(self) -> Dict:
        """Check CRM integration engines."""
        crm_status = {}
        crm_available = []

        for crm_name in ['filevine', 'clio']:
            try:
                mod = importlib.import_module(f'crm.{crm_name}')
                crm_available.append(crm_name)
                crm_status[crm_name] = {"status": "ok", "module_loaded": True}
            except ImportError:
                crm_status[crm_name] = {"status": "not_installed"}

        try:
            from crm.score_sync_engine import score_sync_engine
            crm_status["score_sync"] = {"status": "ok"}
        except ImportError:
            crm_status["score_sync"] = {"status": "not_installed"}

        return {
            "status": "ok" if crm_available else "degraded",
            "crm_modules": crm_available,
            "api_prefix": "/api/crm",
            "details": crm_status,
        }

    def _check_desktop_backend(self) -> Dict:
        """Check Desktop backend API."""
        try:
            import desktop_api
            routes = [r.path for r in desktop_api.router.routes]
            return {
                "status": "ok",
                "routes_available": len(routes),
                "route_prefix": "/api/desktop",
                "sample_routes": routes[:5],
            }
        except ImportError as e:
            return {"status": "not_installed", "detail": str(e)}

    def _check_auth(self) -> Dict:
        """Check authentication system."""
        try:
            from auth import create_access_token, verify_password, auth_router
            routes = [r.path for r in auth_router.routes]
            return {
                "status": "ok",
                "jwt_enabled": True,
                "auth_routes": routes,
                "token_type": "HS256",
            }
        except ImportError as e:
            return {"status": "degraded", "detail": str(e)}


# Singleton
health_diagnostics = HealthDiagnostics()