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
import asyncio
from datetime import datetime
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging

# Import security middleware
from admin_security_middleware import AdminSecurityMiddleware
from websocket_auth_middleware import (
    authenticate_websocket, 
    AuthenticatedConnection,
    secure_manager,
    handle_secure_websocket_connection
)

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
    docs_url="/docs",
    redoc_url="/redoc"
)

# ═══════════════════════════════════════════════════════════════════════════
# CORS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Add security middleware for admin endpoints
app.add_middleware(AdminSecurityMiddleware)

# Hardened CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Production only (remove dev origins for production)
        "https://quirrely.com",
        "https://www.quirrely.com", 
        "https://api.quirrely.com",
        "https://admin.quirrely.com",
        # Specific chrome extension ID (update with actual ID)
        "chrome-extension://abcdefghijklmnopqrstuvwxyz123456",
        # Development (only if APP_ENV != production)
        *([
            "http://localhost:3000",
            "http://localhost:8000", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ] if os.environ.get('APP_ENV') != 'production' else [])
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
        "X-Request-ID",
        "Origin",
        "Accept"
    ],
    expose_headers=["X-Request-ID", "X-Extension-Version", "X-Rate-Limit-Remaining"],
    max_age=3600
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
async def websocket_metrics(
    websocket: WebSocket,
    auth: AuthenticatedConnection = Depends(authenticate_websocket)
):
    """
    Secure WebSocket endpoint for real-time admin metrics.
    
    Requires:
    - Valid JWT token (passed as ?token=... query parameter)
    - Admin-level access (authority tier or admin addon)
    
    Sends metrics updates every 5 seconds to authenticated admin users.
    """
    logger.info(f"Authenticated admin WebSocket connection: {auth.user_id}")
    
    async def metrics_message_handler(websocket: WebSocket, auth_conn: AuthenticatedConnection, data: str):
        """Handle incoming messages for metrics WebSocket."""
        try:
            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
                return
            
            # Parse JSON requests
            if data.startswith("{"):
                import json
                try:
                    request = json.loads(data)
                    request_type = request.get("type", "unknown")
                    
                    if request_type == "get_metrics":
                        metrics = manager._get_current_metrics()
                        await websocket.send_json({
                            "type": "metrics_response",
                            "data": metrics,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    
                    elif request_type == "get_connection_stats":
                        stats = secure_manager.get_connection_stats()
                        await websocket.send_json({
                            "type": "connection_stats",
                            "data": stats,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Unknown request type: {request_type}"
                        })
                        
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON request"
                    })
            
            # Legacy request format
            elif data.startswith("request:"):
                request_type = data.split(":")[1] if ":" in data else "metrics"
                if request_type == "metrics":
                    metrics = manager._get_current_metrics()
                    await websocket.send_json({
                        "type": "metrics_response",
                        "data": metrics
                    })
            
        except Exception as e:
            logger.error(f"Error handling metrics message from {auth_conn.user_id}: {e}")
            await websocket.send_json({
                "type": "error",
                "message": "Internal error processing request"
            })
    
    # Handle the secure connection
    await handle_secure_websocket_connection(websocket, auth, metrics_message_handler)


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
