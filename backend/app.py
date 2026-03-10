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
import html as _html
import sys
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
import asyncio
from datetime import datetime
from typing import Set, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quirrely")

# Database connection pool
_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://quirrely:Quirr2026db@127.0.0.1:5432/quirrely_prod")
try:
    _db_pool = ThreadedConnectionPool(2, 10, _DATABASE_URL)
    logger.info("DB connection pool initialized (2-10 connections)")
except Exception as _pool_err:
    logger.error(f"DB pool init failed: {_pool_err}")
    _db_pool = None

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════════════════════════
# IMPORT ROUTERS
# ═══════════════════════════════════════════════════════════════════════════

from features_api import router as features_router
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
    version="3.2.0",
    description="Quirrely Writing Voice Analysis API - Complete Platform",
    docs_url=None,
    redoc_url=None
)


# Rate limiting
def get_real_ip(request):
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host or "unknown"

limiter = Limiter(key_func=get_real_ip, default_limits=["100/minute"])
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
        "https://quirrely.ca",
        "https://www.quirrely.ca",
        "https://www.quirrely.com",
        "https://api.quirrely.com",
        "https://admin.quirrely.com",
        # Chrome extension (disabled - add specific ID when needed)
        # Development
        # localhost origins removed from production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Extension-Version"],
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
    from share_api import router as share_router, get_public_profile
    app.include_router(share_router, tags=["Share"])
    app.include_router(features_router, tags=["Features"])
    from featured_api import router as featured_router
    app.include_router(featured_router, tags=["Featured"])
    from super_admin_api import router as super_admin_router
    app.include_router(super_admin_router)
    logger.info("✅ Super Admin API loaded")
    logger.info("✅ Newsletter API loaded")
    logger.info("✅ Payments API loaded")
except Exception as e:
    logger.warning(f"Payments API not loaded: {e}")


# ── Public voice profile page (server-rendered for OG tags) ──
from fastapi.responses import HTMLResponse
PROFILE_COLORS={"ASSERTIVE":"#E74C3C","MINIMAL":"#3498DB","POETIC":"#9B59B6","DENSE":"#2C3E50","CONVERSATIONAL":"#E67E22","FORMAL":"#1ABC9C","INTERROGATIVE":"#F39C12","HEDGED":"#7F8C8D","PARALLEL":"#2ECC71","LONGFORM":"#8E44AD"}

def _build_voice_html(title,name,profile,stance,desc,color,bars,og_img,slug,tw,ta,scores_js="{}",cols_js="{}",dom_color="#FF5C34",vtitle=""):
    title=_html.escape(str(title))
    name=_html.escape(str(name))
    profile=_html.escape(str(profile))
    stance=_html.escape(str(stance))
    desc=_html.escape(str(desc))
    slug=_html.escape(str(slug))
    # bars already built by us, og_img is internal URL
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Quirrely</title>
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}. {stance} stance. Discover your writing voice.">
<meta property="og:image" content="{og_img}">
<meta property="og:url" content="https://quirrely.ca/user/{slug}">
<meta property="og:type" content="profile">
<meta property="fb:app_id" content="4334298873522506">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Nunito+Sans:wght@400;600&display=swap');
body{{font-family:Nunito Sans,-apple-system,sans-serif;background:#FFFBF5;color:#351E28;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:48px 20px}}
.card{{background:#fff;border-radius:20px;box-shadow:0 8px 32px rgba(0,0,0,.06);max-width:480px;width:100%;padding:48px 40px;text-align:center}}
.badge{{display:inline-block;padding:10px 28px;border-radius:24px;color:#fff;font-family:Outfit,sans-serif;font-size:1.2em;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;background:{color}}}
.nm{{font-family:Outfit,sans-serif;font-size:1.3em;font-weight:600;color:#351E28;margin:20px 0 6px}}
.st{{font-size:.9em;color:#999;margin-bottom:16px;text-transform:lowercase}}
.ds{{font-size:.95em;color:#666;line-height:1.6;margin-bottom:28px}}
.sc{{text-align:left;margin:0 auto 24px;max-width:360px}}
.stats{{display:flex;justify-content:center;gap:32px;margin:16px 0;color:#999;font-size:.85em}}
.stats div span{{font-weight:700;color:#351E28;font-size:1.1em;display:block}}
.cta{{display:inline-block;margin-top:20px;padding:14px 36px;background:linear-gradient(135deg,#FF5C34,#E04820);color:#fff;border-radius:24px;text-decoration:none;font-weight:600;font-size:1em;box-shadow:0 4px 14px rgba(255,107,107,.3);transition:all .2s}}
.cta:hover{{transform:translateY(-2px);box-shadow:0 6px 20px rgba(255,107,107,.4)}}
.logo{{margin-bottom:28px;display:flex;align-items:center;justify-content:center;gap:8px}}
</style></head><body>
<div class="card">
<div style="font-family:Outfit,sans-serif;font-size:1.1em;font-weight:600;color:#351E28;margin-bottom:16px">My Voice Shape</div><div class="logo" style="margin-bottom:0"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 120" width="40" height="60" style="vertical-align:middle"><path d="M58 112 Q85 98,94 62 Q100 26,74 8 Q50-8,42 22 Q38 44,54 60 Q70 78,62 100 Q58 110,58 112" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.4"/><ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.4"/><path d="M20 68 Q12 72,14 80 Q16 86,24 88 L32 86" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.8"/><path d="M60 68 Q68 72,66 80 Q64 86,56 88 L48 86" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.8"/><ellipse cx="28" cy="86" rx="7" ry="5" fill="#FFFEF9"/><ellipse cx="52" cy="86" rx="7" ry="5" fill="#FFFEF9"/><ellipse cx="40" cy="78" rx="9" ry="4" fill="#E85A5A"/><rect x="38.5" y="74" width="3" height="4" rx="1.5" fill="#D4504A"/><path d="M31 78 Q30 94,40 99 Q50 94,49 78 Z" fill="#FF5C34"/><ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.4"/><ellipse cx="24" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/><ellipse cx="56" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/><ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/><ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/><circle cx="33" cy="46.5" r="2" fill="#FFF"/><circle cx="49" cy="46.5" r="2" fill="#FFF"/><ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/></svg> <span style="font-family:Outfit,system-ui,sans-serif;font-size:1.4em;font-weight:700;color:#351E28">Quir<span style="color:#FF5C34">re</span><span style="font-style:italic;font-weight:500">ly</span></span></div>
<div class="nm">{name}</div>
<div class="vt" style="font-family:Outfit,sans-serif;font-size:1em;font-style:italic;color:#6B5B62;margin:4px 0 14px">{vtitle}</div>
<div class="badge">{profile}</div>
<div class="st">{stance} stance</div>
<div class="sc">{bars}</div><script>(function(){{var SC={scores_js},CL={cols_js},dm="{dom_color}";var keys=Object.keys(SC),n=keys.length,R=95,ns="http://www.w3.org/2000/svg";var svg=document.createElementNS(ns,"svg");svg.setAttribute("viewBox","-120 -120 240 240");svg.setAttribute("width","220");svg.setAttribute("height","220");svg.style.overflow="visible";var pt=function(i,r){{var a=(i/n)*2*Math.PI-Math.PI/2;return[r*Math.cos(a),r*Math.sin(a)];}};var spts=keys.map(function(k,i){{return pt(i,R*(SC[k]/100));}});var sp=spts.map(function(p){{return p.join(",");}}).join(" ");[0.25,0.5,0.75,1].forEach(function(f){{var po=document.createElementNS(ns,"polygon");po.setAttribute("points",keys.map(function(_,i){{return pt(i,R*f).join(",");}}).join(" "));po.setAttribute("fill","none");po.setAttribute("stroke",f===1?"#CDD4C5":"#CDD4C5");po.setAttribute("stroke-width",f===1?"1.5":"1");svg.appendChild(po);}});keys.forEach(function(_,i){{var p=pt(i,R),ln=document.createElementNS(ns,"line");["x1","y1","x2","y2"].forEach(function(a,j){{ln.setAttribute(a,[0,0,p[0],p[1]][j]);}});ln.setAttribute("stroke","#CDD4C5");ln.setAttribute("stroke-width","1");svg.appendChild(ln);}});var defs=document.createElementNS(ns,"defs");var cp=document.createElementNS(ns,"clipPath");cp.setAttribute("id","vc");cp.setAttribute("clipPathUnits","userSpaceOnUse");var cpp=document.createElementNS(ns,"polygon");cpp.setAttribute("points",sp);cp.appendChild(cpp);defs.appendChild(cp);svg.appendChild(defs);var rp=[["path","M58 112 Q85 98,94 62 Q100 26,74 8 Q50-8,42 22 Q38 44,54 60 Q70 78,62 100 Q58 110,58 112","#FFFEF9","#CDD4C5","1.4"],["ellipse","","#FFFEF9","#CDD4C5","1.4",40,98,22,26],["path","M20 68 Q12 72,14 80 Q16 86,24 88 L32 86","#FFFEF9","#CDD4C5","1.8"],["path","M60 68 Q68 72,66 80 Q64 86,56 88 L48 86","#FFFEF9","#CDD4C5","1.8"],["ellipse","","#FFFEF9","","",28,86,7,5],["ellipse","","#FFFEF9","","",52,86,7,5],["ellipse","","#E85A5A","","",40,78,9,4],["path","M31 78 Q30 94,40 99 Q50 94,49 78 Z","#FF5C34","",""],["ellipse","","#FFFEF9","#CDD4C5","1.4",40,50,22,20],["ellipse","","#D4CCC4","","",24,30,8,14],["ellipse","","#D4CCC4","","",56,30,8,14],["ellipse","","#1a1a1a","","",32,48,5.5,6],["ellipse","","#1a1a1a","","",48,48,5.5,6],["circle","","#FFF","","",33,46.5,2],["circle","","#FFF","","",49,46.5,2],["ellipse","","#4A4A4A","","",40,60,4.5,3.5]];function mkR(op){{var g=document.createElementNS(ns,"g");g.setAttribute("transform","scale(1.85) translate(-40,-60)");g.setAttribute("opacity",op);rp.forEach(function(r){{var el=document.createElementNS(ns,r[0]);if(r[1])el.setAttribute("d",r[1]);if(r[0]==="ellipse"){{el.setAttribute("cx",r[5]);el.setAttribute("cy",r[6]);el.setAttribute("rx",r[7]);el.setAttribute("ry",r[8]);}}if(r[0]==="circle"){{el.setAttribute("cx",r[5]);el.setAttribute("cy",r[6]);el.setAttribute("r",r[7]);}}el.setAttribute("fill",r[2]);if(r[3])el.setAttribute("stroke",r[3]);if(r[4])el.setAttribute("stroke-width",r[4]);g.appendChild(el);}});return g;}}svg.appendChild(mkR(0.06));var cg=document.createElementNS(ns,"g");cg.setAttribute("clip-path","url(#vc)");cg.appendChild(mkR(0.55));cg.style.opacity="0";svg.appendChild(cg);setTimeout(function(){{cg.style.transition="opacity 0.7s ease";cg.style.opacity="1";}},150);var fp=document.createElementNS(ns,"polygon");fp.setAttribute("points",sp);fp.setAttribute("fill",dm);fp.setAttribute("fill-opacity","0.12");fp.setAttribute("stroke",dm);fp.setAttribute("stroke-width","2");fp.setAttribute("stroke-linejoin","round");fp.style.transformOrigin="center";fp.style.animation="rEx 0.85s cubic-bezier(0.34,1.56,0.64,1) forwards";fp.style.animationDelay="0.15s";fp.style.opacity="0";svg.appendChild(fp);keys.forEach(function(k,i){{var p=pt(i,R*(SC[k]/100));var ci=document.createElementNS(ns,"circle");ci.setAttribute("cx",p[0]);ci.setAttribute("cy",p[1]);ci.setAttribute("r","3");ci.setAttribute("fill",CL[k]||"#ccc");ci.setAttribute("fill-opacity","0.8");ci.style.animation="rEx 0.4s ease-out "+(0.2+i*0.05)+"s forwards";ci.style.opacity="0";svg.appendChild(ci);}});keys.forEach(function(k,i){{var p=pt(i,R+18);var t=document.createElementNS(ns,"text");t.setAttribute("x",p[0]);t.setAttribute("y",p[1]);t.setAttribute("text-anchor","middle");t.setAttribute("dominant-baseline","middle");t.setAttribute("font-size","8");t.setAttribute("font-family","Nunito Sans,sans-serif");t.setAttribute("fill","#6B5B62");t.textContent=k;svg.appendChild(t);}});var st=document.createElement("style");st.textContent="@keyframes rEx{{from{{transform:scale(0);opacity:0}}to{{transform:scale(1);opacity:1}}}}";document.head.appendChild(st);document.getElementById("vsr").appendChild(svg);var leg=document.getElementById("vsl");var srt=Object.entries(SC).sort(function(a,b){{return b[1]-a[1];}}).slice(0,5);srt.forEach(function(e,i){{var d=document.createElement("div");d.style.cssText="display:flex;align-items:center;gap:4px;font-size:0.68rem;color:#6B5B62;text-transform:capitalize";var dot=document.createElement("div");dot.style.cssText="width:7px;height:7px;border-radius:50%;background:"+(CL[e[0]]||"#ccc")+";opacity:"+(i===0?"1":"0.55");var sp2=document.createElement("span");if(i===0)sp2.style.cssText="font-weight:700;color:#351E28";sp2.textContent=e[0]+" · "+e[1];d.appendChild(dot);d.appendChild(sp2);leg.appendChild(d);}});}})();</script>
<div class="stats"><div>{tw:,} words</div><div>{ta} analyses</div></div>
<div style="margin-top:24px;padding-top:20px;border-top:1px solid #AEB8A0;background:#351E28;display:flex;align-items:center;justify-content:center;gap:8px"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 120" width="22" height="33"><path d="M58 112 Q85 98,94 62 Q100 26,74 8 Q50-8,42 22 Q38 44,54 60 Q70 78,62 100 Q58 110,58 112" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.4"/><ellipse cx="40" cy="98" rx="22" ry="26" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.4"/><path d="M20 68 Q12 72,14 80 Q16 86,24 88 L32 86" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.8"/><path d="M60 68 Q68 72,66 80 Q64 86,56 88 L48 86" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.8"/><ellipse cx="28" cy="86" rx="7" ry="5" fill="#FFFEF9"/><ellipse cx="52" cy="86" rx="7" ry="5" fill="#FFFEF9"/><ellipse cx="40" cy="78" rx="9" ry="4" fill="#E85A5A"/><rect x="38.5" y="74" width="3" height="4" rx="1.5" fill="#D4504A"/><path d="M31 78 Q30 94,40 99 Q50 94,49 78 Z" fill="#FF5C34"/><ellipse cx="40" cy="50" rx="22" ry="20" fill="#FFFEF9" stroke="#CDD4C5" stroke-width="1.4"/><ellipse cx="24" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/><ellipse cx="56" cy="30" rx="8" ry="14" fill="#D4CCC4" opacity="0.6"/><ellipse cx="32" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/><ellipse cx="48" cy="48" rx="5.5" ry="6" fill="#1a1a1a"/><circle cx="33" cy="46.5" r="2" fill="#FFF"/><circle cx="49" cy="46.5" r="2" fill="#FFF"/><ellipse cx="40" cy="60" rx="4.5" ry="3.5" fill="#4A4A4A"/></svg><span style="font-family:Outfit,system-ui,sans-serif;font-size:1.1em;font-weight:700;color:#351E28">Quir<span style="color:#FF5C34">re</span><span style="font-style:italic;font-weight:500">ly</span></span></div>
<a class="cta" href="https://quirrely.ca/?ref={slug}">Find your writing voice. &rarr;</a>
</div>
<script>try{{var u=JSON.parse(localStorage.getItem('quirrely_user'));if(u){{var s=JSON.parse(localStorage.getItem('quirrely_session'));if(s&&s.token){{var slug='{slug}';var shareSlug=(u.share_slug||'').toLowerCase();var displayName=(u.display_name||'').toLowerCase();if(slug.toLowerCase()===shareSlug||slug.toLowerCase()===displayName){{fetch('/frontend/dashboard.html').then(function(r){{return r.text()}}).then(function(h){{document.open();document.write(h);document.close();history.replaceState(null,'','/user/'+slug)}}).catch(function(){{window.location.replace('/dashboard')}})}}}}}}}}catch(e){{}}</script>
</body></html>"""

PROFILE_DESC={"ASSERTIVE":"Bold, direct, and confident","MINIMAL":"Clean, precise, and economical","POETIC":"Lyrical, imagery-rich, and evocative","DENSE":"Complex, layered, and information-rich","CONVERSATIONAL":"Warm, natural, and approachable","FORMAL":"Structured, polished, and authoritative","INTERROGATIVE":"Curious, questioning, and exploratory","HEDGED":"Nuanced, cautious, and qualifying","PARALLEL":"Rhythmic, balanced, and patterned","LONGFORM":"Expansive, detailed, and immersive"}
PROFILE_TITLES={
"ASSERTIVE":{"open":"The Direct Voice","closed":"The Confident Verdict","balanced":"The Measured Advocate","contradictory":"The Restless Challenger"},
"MINIMAL":{"open":"The Quiet Observer","closed":"The Spare Absolutist","balanced":"The Careful Understater","contradictory":"The Silent Contrarian"},
"POETIC":{"open":"The Fragment Weaver","closed":"The Sealed Lyricist","balanced":"The Melodic Thinker","contradictory":"The Broken Sonneteer"},
"DENSE":{"open":"The Layered Thinker","closed":"The Closed System","balanced":"The Considered Architect","contradictory":"The Tangled Theorist"},
"CONVERSATIONAL":{"open":"The Voice in the Room","closed":"The Opinionated Friend","balanced":"The Even-Keeled Storyteller","contradictory":"The Ambivalent Confessor"},
"INTERROGATIVE":{"open":"The Questioner","closed":"The Skeptic","balanced":"The Careful Inquirer","contradictory":"The Doubting Voice"},
"HEDGED":{"open":"The Careful Scholar","closed":"The Reluctant Authority","balanced":"The Measured Equivocator","contradictory":"The Uncertain Sage"},
"FORMAL":{"open":"The Considered Essayist","closed":"The Authoritative Voice","balanced":"The Disciplined Thinker","contradictory":"The Formal Dissenter"},
"LONGFORM":{"open":"The Sentence Builder","closed":"The Exhaustive Chronicler","balanced":"The Patient Explicator","contradictory":"The Labyrinthine Mind"},
"BALANCED":{"open":"The Fair Witness","closed":"The Principled Moderator","balanced":"The Centred Voice","contradictory":"The Torn Observer"},
"PARALLEL":{"open":"The Pattern Maker","closed":"The Rigid Stylist","balanced":"The Rhythmic Thinker","contradictory":"The Fractured Composer"},
}

@app.get("/user/{slug}", response_class=HTMLResponse)
async def public_voice_page(slug: str):
    p=get_public_profile(slug)
    if not p:
        return HTMLResponse("<html><body><h1>Not found</h1><a href='/'>Try Quirrely</a></body></html>",status_code=404)
    profile=p.get("profile") or "UNKNOWN"
    stance=p.get("stance") or ""
    name=p.get("display_name") or slug
    profile=profile.upper()
    color=PROFILE_COLORS.get(profile,"#666")
    desc=PROFILE_DESC.get(profile,"A unique writing voice")
    scores=p.get("scores") or {}
    tw=p.get("total_words") or 0
    ta=p.get("total_analyses") or 0
    import json as _j
    RCOLS={"assertive":"#FF5C34","minimal":"#7CAE9E","poetic":"#B08090","dense":"#8B6E9B","conversational":"#D4A853","formal":"#6B8EAE","longform":"#D4A853","interrogative":"#7CAE9E","hedged":"#B08090","balanced":"#7CAE82"}
    RKEYS=["assertive","minimal","poetic","dense","conversational","formal","longform","interrogative","hedged","balanced"]
    sc_norm={k.lower():v for k,v in scores.items()}
    sorted_scores=sorted(sc_norm.items(),key=lambda x:x[1] if x[1] else 0,reverse=True)
    dominant=sorted_scores[0][0] if sorted_scores else profile.lower()
    dom_color=RCOLS.get(dominant,color)
    scores_js=_j.dumps({k:sc_norm.get(k,0) for k in RKEYS})
    cols_js=_j.dumps(RCOLS)
    bars='<div id="vsr" style="display:flex;justify-content:center;margin:8px 0 4px"></div><div id="vsl" style="display:flex;flex-wrap:wrap;gap:5px 12px;justify-content:center;margin-top:8px"></div>'
    # Use personalized OG image if exists, else generic
    import os
    if os.path.exists(f"/home/quirrely/quirrely.ca/og/users/{slug}.png"):
        og_img=f"https://quirrely.ca/og/users/{slug}.png"
    else:
        og_img=f"https://quirrely.ca/og/{profile.lower()}.png"
    vtitle=PROFILE_TITLES.get(profile,{}).get((stance or "open").lower(), PROFILE_TITLES.get(profile,{}).get("open",""))
    title=f"{name} — {vtitle}" if vtitle else f"{name} writes with a {profile} voice"
    html=_build_voice_html(title,name,profile,stance,desc,color,bars,og_img,slug,tw,ta,scores_js,cols_js,dom_color,vtitle=vtitle)
    return HTMLResponse(html)

from starlette.responses import RedirectResponse
@app.get("/voice/{slug}")
async def voice_redirect(slug: str):
    return RedirectResponse(url=f"/user/{slug}", status_code=301)


# ── Analyze endpoint (with auth + word tracking) ──────────────────────
if API_V2_AVAILABLE:
    from api_v2 import get_classifier, get_pattern_collector, AnalyzeRequest, AnalyzeResponse
    from feature_gate import get_feature_gate
    from auth_api import get_current_user

    @app.post("/api/v2/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
    async def analyze_text_proxy(request: AnalyzeRequest, authorization: Optional[str] = Header(None)):
        # Resolve user from Bearer token
        user = get_current_user(authorization) if authorization else None
        user_id = str(user["id"]) if user else None

        gate = get_feature_gate()
        # Check daily limit if authenticated
        if user_id:
            est_words = len(request.text.split())
            lc = gate.check_daily_limit(user_id, None, est_words)
            if not lc["allowed"]:
                raise HTTPException(status_code=429, detail=f"Word limit reached ({lc['used']}/{lc['limit']} words).")

        classifier = get_classifier()
        result = classifier.classify(request.text)

        # Record patterns + word usage + writing_profiles
        collector = get_pattern_collector()
        pid, hid = collector.record_analysis(
            tokens=result["tokens"], profile=result["profile"], stance=result["stance"],
            word_count=result["word_count"], sentence_count=result["sentence_count"],
            user_id=user_id, session_id=None, source=request.source,
            input_preview=request.text[:100], scores=result["scores"],
            confidence_score=result["confidence"],
        )
        if user_id:
            gate.record_analysis(user_id, None, result["word_count"])
            # Write to writing_profiles for share/history
            _cn = None
            try:
                _cn = _db_pool.getconn() if _db_pool else psycopg2.connect(_DATABASE_URL)
                _cr = _cn.cursor()
                ps = result["scores"].get("profiles",{})
                sts = result["scores"].get("stances",{})
                _cr.execute("""INSERT INTO writing_profiles
                    (user_id, profile, stance, score_assertive, score_minimal,
                     score_poetic, score_dense, score_conversational, score_formal,
                     score_balanced, score_longform, score_interrogative, score_hedged,
                     score_open, score_closed, score_stance_balanced, score_contradictory,
                     input_text, input_word_count)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (user_id, result["profile"], result["stance"],
                     round(ps.get("ASSERTIVE",0)*100), round(ps.get("MINIMAL",0)*100),
                     round(ps.get("POETIC",0)*100), round(ps.get("DENSE",0)*100),
                     round(ps.get("CONVERSATIONAL",0)*100), round(ps.get("FORMAL",0)*100),
                     0, round(ps.get("LONGFORM",0)*100),
                     round(ps.get("INTERROGATIVE",0)*100), round(ps.get("HEDGED",0)*100),
                     round(sts.get("OPEN",0)*100), round(sts.get("CLOSED",0)*100),
                     round(sts.get("BALANCED",0)*100), round(sts.get("CONTRADICTORY",0)*100),
                     request.text[:500], result["word_count"]))
                _cn.commit()
            except Exception as _wpe:
                logger.warning(f"writing_profiles insert failed: {_wpe}")
                if _cn: _cn.rollback()
            finally:
                if _cn and _db_pool: _db_pool.putconn(_cn)
                elif _cn: _cn.close()

        return AnalyzeResponse(
            profile=result["profile"], stance=result["stance"],
            word_count=result["word_count"], sentence_count=result["sentence_count"],
            confidence=result["confidence"], scores=result["scores"],
            pattern_id=pid or "", history_id=hid or "",
            features_used=["basic_analysis"],
        )
    logger.info("\u2705 API v2 analyze endpoint loaded (with word tracking)")

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
    conn = None
    try:
        import hashlib, json
        ip = request.headers.get("x-forwarded-for", request.client.host or "unknown").split(",")[0].strip()
        user_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
        sql = """INSERT INTO analytics_events (event_name, event_category, user_hash, properties, session_id, page_url, referrer)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        conn = _db_pool.getconn() if _db_pool else psycopg2.connect(_DATABASE_URL)
        cur = conn.cursor()
        cur.execute(sql, (req.event, "frontend", user_hash, json.dumps(req.properties), req.sessionId, request.headers.get("referer",""), request.headers.get("referer","")))
        conn.commit()
        cur.close()
        return {"ok": True}
    except Exception as e:
        logger.error(f"track error: {e}")
        if conn: conn.rollback()
        return {"ok": False}
    finally:
        if conn and _db_pool: _db_pool.putconn(conn)
        elif conn: conn.close()
