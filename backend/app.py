#!/usr/bin/env python3
"""
QUIRRELY MAIN API SERVER v3.1.3
Complete integration of all API endpoints with WebSocket support.

This is the production entry point that combines:
- API v2 (Core analysis, auth, billing)
- Admin API v2 (Meta orchestrator bridge)
- Extension API (Chrome extension sync)
- WebSocket (Real-time admin metrics)

Run with: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
import asyncio
from datetime import datetime
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quirrely")

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════════════════════════
# IMPORT ROUTERS
# ═══════════════════════════════════════════════════════════════════════════

# Import API v2 app (we'll mount it)
try:
    from api_v2 import app as api_v2_app
    API_V2_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v2 not available: {e}")
    API_V2_AVAILABLE = False

# Import Admin API v2 router
try:
    from admin_api_v2 import router as admin_router
    ADMIN_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Admin API v2 not available: {e}")
    ADMIN_API_AVAILABLE = False

# Import Extension API router
try:
    from extension_api import router as extension_router
    EXTENSION_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Extension API not available: {e}")
    EXTENSION_API_AVAILABLE = False

# Import STRETCH API router (v3.1.3)
try:
    from stretch_api import router as stretch_router
    STRETCH_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"STRETCH API not available: {e}")
    STRETCH_API_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
# CREATE MAIN APP
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Quirrely API",
    version="3.1.3",
    description="Quirrely Writing Voice Analysis API - Complete Platform",
    docs_url=None,
    redoc_url=None
)


# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ═══════════════════════════════════════════════════════════════════════════
# CORS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Comprehensive CORS for all clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Production
        "https://quirrely.com",
        "https://www.quirrely.com",
        "https://api.quirrely.com",
        "https://admin.quirrely.com",
        # Chrome extension
        "chrome-extension://*",
        # Development
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        # Allow null origin for file:// access (dev)
        "null"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Extension-Version"],
    max_age=3600  # Cache preflight for 1 hour
)


# ═══════════════════════════════════════════════════════════════════════════
# WEBSOCKET CONNECTION MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class ConnectionManager:
    """Manage WebSocket connections for real-time admin metrics."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._broadcast_task = None
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
        
        # Start broadcast loop if not running
        if self._broadcast_task is None or self._broadcast_task.done():
            self._broadcast_task = asyncio.create_task(self._broadcast_metrics())
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def _broadcast_metrics(self):
        """Periodically broadcast metrics to all connected admin clients."""
        while self.active_connections:
            try:
                metrics = self._get_current_metrics()
                await self.broadcast({
                    "type": "metrics_update",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": metrics
                })
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                await asyncio.sleep(5)
    
    def _get_current_metrics(self) -> dict:
        """Get current system metrics (mock data for now)."""
        import random
        return {
            "health": {
                "overall": random.randint(95, 99),
                "meta": random.randint(96, 99),
                "halo": random.randint(97, 100),
                "stretch": random.randint(94, 98),
                "billing": random.randint(92, 97)
            },
            "stretch": {
                "started": random.randint(2100, 2300),
                "completed": random.randint(1600, 1800),
                "streak_avg": round(random.uniform(3.5, 5.5), 1)
            },
            "revenue": {
                "mrr": random.randint(4800, 5500),
                "arr": random.randint(57000, 66000),
                "active_subs": random.randint(580, 650)
            },
            "observers": {
                "active": 8,
                "events_1h": random.randint(1200, 1800)
            }
        }


manager = ConnectionManager()


# ═══════════════════════════════════════════════════════════════════════════
# WEBSOCKET ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """
    WebSocket endpoint for real-time admin metrics.
    
    Sends metrics updates every 5 seconds to all connected admin dashboards.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, handle incoming messages
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
            
            # Handle specific requests
            elif data.startswith("request:"):
                request_type = data.split(":")[1] if ":" in data else "metrics"
                if request_type == "metrics":
                    metrics = manager._get_current_metrics()
                    await websocket.send_json({
                        "type": "metrics_response",
                        "data": metrics
                    })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ═══════════════════════════════════════════════════════════════════════════
# MOUNT ROUTERS
# ═══════════════════════════════════════════════════════════════════════════

# Include Admin API router
if ADMIN_API_AVAILABLE:
    app.include_router(admin_router, prefix="/api/admin/v2", tags=["Admin"])
    logger.info("✅ Admin API v2 loaded")

# Include Extension API router
if EXTENSION_API_AVAILABLE:
    app.include_router(extension_router, tags=["Extension"])
    logger.info("✅ Extension API loaded")

# Include STRETCH API router (v3.1.3)
if STRETCH_API_AVAILABLE:
    app.include_router(stretch_router, prefix="/api", tags=["STRETCH"])
    logger.info("✅ STRETCH API loaded")

# Include Auth API router
try:
    from auth_api import router as auth_router
    app.include_router(auth_router, tags=["Auth"])
    logger.info("✅ Auth API loaded")
except Exception as e:
    logger.warning(f"Auth API not loaded: {e}")

# Include Payments router
try:
    from payments_api import router as payments_router
    app.include_router(payments_router, tags=["Payments"])
    from payments_api import billing_compat_router
    app.include_router(billing_compat_router, tags=["Billing Compat"])

    from dashboard_api import router as dashboard_router
    from analytics_api import router as analytics_router
    app.include_router(dashboard_router, tags=["Dashboard"])
    app.include_router(analytics_router, tags=["Analytics"])
    from newsletter_api import router as newsletter_router
    app.include_router(newsletter_router, tags=["Newsletter"])
    from featured_api import router as featured_router
    app.include_router(featured_router, tags=["Featured"])
    from super_admin_api import router as super_admin_router
    app.include_router(super_admin_router)
    logger.info("✅ Super Admin API loaded")
    logger.info("✅ Newsletter API loaded")
    logger.info("✅ Payments API loaded")
except Exception as e:
    logger.warning(f"Payments API not loaded: {e}")

# ── Analyze endpoint (delegates to LNCP classifier) ──────────────────────
if API_V2_AVAILABLE:
    from api_v2 import get_classifier, AnalyzeRequest, AnalyzeResponse
    @app.post("/api/v2/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
    async def analyze_text_proxy(request: AnalyzeRequest):
        classifier = get_classifier()
        result = classifier.classify(request.text)
        return AnalyzeResponse(
            profile=result["profile"],
            stance=result["stance"],
            word_count=result["word_count"],
            sentence_count=result["sentence_count"],
            confidence=result["confidence"],
            scores=result["scores"],
            pattern_id="",
            history_id="",
            features_used=["basic_analysis"],
        )
    logger.info("✅ API v2 analyze endpoint loaded")

# ═══════════════════════════════════════════════════════════════════════════
# GEO-BLOCK MIDDLEWARE (France + Russia bot protection)
# ═══════════════════════════════════════════════════════════════════════════
_BLOCKED_COUNTRIES = {"FR", "RU"}
logger.info(f"\U0001f6e1\ufe0f Geo-blocking enabled for: {_BLOCKED_COUNTRIES}")

@app.middleware("http")
async def geo_block_middleware(request: Request, call_next):
    country = (request.headers.get("cf-ipcountry") or "").upper()
    if country in _BLOCKED_COUNTRIES:
        logger.warning(f"Blocked request from {country}: {request.url.path}")
        return JSONResponse(
            status_code=403,
            content={"error": "access_denied", "message": "Service not available in your region."}
        )
    return await call_next(request)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# ═══════════════════════════════════════════════════════════════════════════
# ROOT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """API root - service info."""
    return {
        "service": "Quirrely API",
        "version": "3.1.3",
        "codename": "The Stretched Squirrel",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api_v2": "/api/v2/*",
            "admin_api": "/api/admin/v2/*" if ADMIN_API_AVAILABLE else "not_loaded",
            "extension": "/api/extension/*" if EXTENSION_API_AVAILABLE else "not_loaded",
            "websocket": "/ws/metrics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "version": "3.1.3",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api_v2": "loaded" if API_V2_AVAILABLE else "not_available",
            "admin_api_v2": "loaded" if ADMIN_API_AVAILABLE else "not_available",
            "extension_api": "loaded" if EXTENSION_API_AVAILABLE else "not_available",
            "websocket": "enabled"
        }
    }


@app.get("/api/v2/health")
async def api_v2_health():
    """API v2 specific health check."""
    return {
        "status": "healthy",
        "api": "v2",
        "version": "3.1.3",
        "classifier": "LNCP v3.8 Quinquaginta",
        "features": ["analyze", "history", "trial", "billing"],
        "timestamp": datetime.utcnow().isoformat()
    }


# ═══════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": "The requested endpoint does not exist",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An internal error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ═══════════════════════════════════════════════════════════════════════════
# STARTUP/SHUTDOWN
# ═══════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    logger.info("=" * 60)
    logger.info("QUIRRELY API v3.1.3 'The Stretched Squirrel'")
    logger.info("=" * 60)
    logger.info(f"API v2: {'✅' if API_V2_AVAILABLE else '❌'}")
    logger.info(f"Admin API v2: {'✅' if ADMIN_API_AVAILABLE else '❌'}")
    logger.info(f"Extension API: {'✅' if EXTENSION_API_AVAILABLE else '❌'}")
    logger.info("WebSocket: ✅")
    logger.info("=" * 60)
    logger.info("Server ready!")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down Quirrely API...")
    # Close all WebSocket connections
    for connection in manager.active_connections.copy():
        try:
            await connection.close()
        except Exception:
            pass
    logger.info("Shutdown complete.")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("QUIRRELY API v3.1.3")
    print("=" * 60)
    print("\nEndpoints:")
    print("  - API Docs:    http://localhost:8000/docs")
    print("  - Health:      http://localhost:8000/health")
    print("  - Extension:   http://localhost:8000/api/extension/sync")
    print("  - Admin:       http://localhost:8000/api/admin/v2/health")
    print("  - WebSocket:   ws://localhost:8000/ws/metrics")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# ── Chrome Extension quick-analyze ──────────────────────────────────────────
from pydantic import BaseModel as _BM
from typing import Optional as _Opt

class _QuickReq(_BM):
    text: str
    session_id: _Opt[str] = None

@app.post("/api/quick-analyze", tags=["Extension"])
async def extension_quick_analyze(req: _QuickReq):
    try:
        import sys, os
        sys.path.insert(0, '/opt/quirrely/quirrely_v313_integrated/lncp')
        from engine.scoring import analyze
        result = analyze(req.text)
        return result
    except Exception as e:
        logger.error(f"quick-analyze error: {e}")
        return {"error": "analysis_failed", "message": "Analysis failed"}

# ── Analytics tracking endpoint ─────────────────────────────────────────
from pydantic import BaseModel as _TrackBM
from typing import Optional as _TrackOpt, Dict as _TrackDict, Any as _TrackAny

class _TrackReq(_TrackBM):
    event: str
    properties: _TrackDict[str, _TrackAny] = {}
    sessionId: _TrackOpt[str] = None
    ts: _TrackOpt[int] = None

@app.post("/api/v2/track", tags=["Analytics"])
async def track_event(req: _TrackReq, request: Request):
    try:
        import hashlib
        ip = request.headers.get("x-forwarded-for", request.client.host or "unknown").split(",")[0].strip()
        user_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
        sql = """INSERT INTO analytics_events (event_name, event_category, user_hash, properties, session_id, page_url, referrer)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        import psycopg2, json, os
        conn = psycopg2.connect(os.getenv("DATABASE_URL", "postgresql://quirrely:Quirr2026db@127.0.0.1:5432/quirrely_prod"))
        cur = conn.cursor()
        cur.execute(sql, (req.event, "frontend", user_hash, json.dumps(req.properties), req.sessionId, request.headers.get("referer",""), request.headers.get("referer","")))
        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True}
    except Exception as e:
        logger.error(f"track error: {e}")
        return {"ok": False}
