#!/usr/bin/env python3
"""
QUIRRELY WEBSOCKET AUTHENTICATION MIDDLEWARE v1.0
Secure WebSocket authentication for real-time admin features.

Features:
- JWT token validation for WebSocket connections
- Admin-only access controls
- Connection rate limiting
- Security event logging
- Graceful connection management
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Set
from dataclasses import dataclass

from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Query, Header
from starlette.websockets import WebSocketState

# Import our secure auth middleware
from secure_auth_middleware import decode_token, validate_token_claims

# Configure logging
logger = logging.getLogger("quirrely.websocket_auth")

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class WebSocketAuthConfig:
    """WebSocket authentication configuration."""
    
    # Authentication requirements
    REQUIRE_AUTH: bool = True
    REQUIRE_ADMIN_ACCESS: bool = True
    
    # Connection limits
    MAX_CONNECTIONS_PER_IP: int = 3
    MAX_TOTAL_CONNECTIONS: int = 50
    
    # Rate limiting
    MAX_MESSAGES_PER_MINUTE: int = 60
    CONNECTION_TIMEOUT_SECONDS: int = 300  # 5 minutes idle timeout
    
    # Security
    ALLOWED_ORIGINS: list = None
    LOG_ALL_CONNECTIONS: bool = True
    VALIDATE_USER_PERMISSIONS: bool = True
    
    def __post_init__(self):
        # Load from environment
        self.REQUIRE_AUTH = os.environ.get("WS_REQUIRE_AUTH", "true").lower() == "true"
        self.REQUIRE_ADMIN_ACCESS = os.environ.get("WS_REQUIRE_ADMIN", "true").lower() == "true"
        self.MAX_CONNECTIONS_PER_IP = int(os.environ.get("WS_MAX_CONN_PER_IP", "3"))
        self.MAX_TOTAL_CONNECTIONS = int(os.environ.get("WS_MAX_TOTAL_CONN", "50"))
        
        # Allowed origins for WebSocket connections
        origins_env = os.environ.get("WS_ALLOWED_ORIGINS", "")
        if origins_env:
            self.ALLOWED_ORIGINS = [o.strip() for o in origins_env.split(",")]
        else:
            self.ALLOWED_ORIGINS = [
                "https://quirrely.com",
                "https://www.quirrely.com",
                "https://admin.quirrely.com"
            ]

config = WebSocketAuthConfig()

# ═══════════════════════════════════════════════════════════════════════════
# CONNECTION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AuthenticatedConnection:
    """Represents an authenticated WebSocket connection."""
    websocket: WebSocket
    user_id: str
    client_ip: str
    is_admin: bool
    connected_at: datetime
    last_activity: datetime
    message_count: int = 0

class SecureConnectionManager:
    """Manage authenticated WebSocket connections with security controls."""
    
    def __init__(self):
        self.connections: Dict[WebSocket, AuthenticatedConnection] = {}
        self.connections_by_ip: Dict[str, Set[WebSocket]] = {}
        self.connections_by_user: Dict[str, Set[WebSocket]] = {}
        self._cleanup_task = None
    
    async def authenticate_and_connect(
        self, 
        websocket: WebSocket, 
        token: Optional[str] = None,
        origin: Optional[str] = None
    ) -> AuthenticatedConnection:
        """
        Authenticate and register a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            token: JWT authentication token
            origin: Connection origin for validation
            
        Returns:
            AuthenticatedConnection object
            
        Raises:
            HTTPException: If authentication fails
        """
        client_ip = self._get_client_ip(websocket)
        
        # Validate origin if provided
        if origin and config.ALLOWED_ORIGINS:
            if not any(origin.startswith(allowed) for allowed in config.ALLOWED_ORIGINS):
                logger.warning(f"WebSocket connection rejected from unauthorized origin: {origin}")
                raise HTTPException(status_code=403, detail="Unauthorized origin")
        
        # Check connection limits per IP
        if client_ip in self.connections_by_ip:
            if len(self.connections_by_ip[client_ip]) >= config.MAX_CONNECTIONS_PER_IP:
                logger.warning(f"Max connections per IP exceeded for {client_ip}")
                raise HTTPException(status_code=429, detail="Too many connections from this IP")
        
        # Check total connection limit
        if len(self.connections) >= config.MAX_TOTAL_CONNECTIONS:
            logger.warning("Max total WebSocket connections exceeded")
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        
        # Authenticate token
        if config.REQUIRE_AUTH:
            if not token:
                raise HTTPException(status_code=401, detail="Authentication token required")
            
            payload = decode_token(token)
            if not payload or not validate_token_claims(payload, "access"):
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            user_id = payload["sub"]
            user_tier = payload.get("tier", "free")
            user_addons = payload.get("addons", [])
            
            # Check admin access if required
            is_admin = user_tier in ["authority", "admin"] or "admin" in user_addons
            if config.REQUIRE_ADMIN_ACCESS and not is_admin:
                logger.warning(f"Non-admin user {user_id} attempted WebSocket connection")
                raise HTTPException(status_code=403, detail="Admin access required")
        else:
            user_id = "anonymous"
            is_admin = False
        
        # Accept the connection
        await websocket.accept()
        
        # Create authenticated connection
        now = datetime.utcnow()
        auth_conn = AuthenticatedConnection(
            websocket=websocket,
            user_id=user_id,
            client_ip=client_ip,
            is_admin=is_admin,
            connected_at=now,
            last_activity=now
        )
        
        # Register connection
        self.connections[websocket] = auth_conn
        
        if client_ip not in self.connections_by_ip:
            self.connections_by_ip[client_ip] = set()
        self.connections_by_ip[client_ip].add(websocket)
        
        if user_id not in self.connections_by_user:
            self.connections_by_user[user_id] = set()
        self.connections_by_user[user_id].add(websocket)
        
        # Log successful connection
        if config.LOG_ALL_CONNECTIONS:
            logger.info(f"Authenticated WebSocket connection: user={user_id}, ip={client_ip}, admin={is_admin}")
        
        return auth_conn
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Properly disconnect and cleanup a WebSocket connection.
        
        Args:
            websocket: WebSocket to disconnect
        """
        if websocket not in self.connections:
            return
        
        auth_conn = self.connections[websocket]
        
        # Remove from all tracking structures
        del self.connections[websocket]
        
        if auth_conn.client_ip in self.connections_by_ip:
            self.connections_by_ip[auth_conn.client_ip].discard(websocket)
            if not self.connections_by_ip[auth_conn.client_ip]:
                del self.connections_by_ip[auth_conn.client_ip]
        
        if auth_conn.user_id in self.connections_by_user:
            self.connections_by_user[auth_conn.user_id].discard(websocket)
            if not self.connections_by_user[auth_conn.user_id]:
                del self.connections_by_user[auth_conn.user_id]
        
        # Log disconnection
        duration = datetime.utcnow() - auth_conn.connected_at
        logger.info(f"WebSocket disconnected: user={auth_conn.user_id}, duration={duration}, messages={auth_conn.message_count}")
    
    def update_activity(self, websocket: WebSocket) -> bool:
        """
        Update last activity for a connection and check rate limits.
        
        Args:
            websocket: WebSocket connection
            
        Returns:
            True if message is allowed, False if rate limited
        """
        if websocket not in self.connections:
            return False
        
        auth_conn = self.connections[websocket]
        now = datetime.utcnow()
        
        # Check rate limiting
        time_window = now - timedelta(minutes=1)
        if auth_conn.last_activity > time_window:
            auth_conn.message_count += 1
            if auth_conn.message_count > config.MAX_MESSAGES_PER_MINUTE:
                logger.warning(f"Rate limit exceeded for user {auth_conn.user_id}")
                return False
        else:
            # Reset count for new time window
            auth_conn.message_count = 1
        
        auth_conn.last_activity = now
        return True
    
    async def broadcast_to_admins(self, message: Dict[str, Any]) -> int:
        """
        Broadcast message to all authenticated admin connections.
        
        Args:
            message: Message to broadcast
            
        Returns:
            Number of successful sends
        """
        admin_connections = [
            conn for conn in self.connections.values()
            if conn.is_admin and conn.websocket.client_state == WebSocketState.CONNECTED
        ]
        
        successful_sends = 0
        failed_connections = []
        
        for auth_conn in admin_connections:
            try:
                await auth_conn.websocket.send_json(message)
                successful_sends += 1
            except Exception as e:
                logger.warning(f"Failed to send to admin {auth_conn.user_id}: {e}")
                failed_connections.append(auth_conn.websocket)
        
        # Clean up failed connections
        for websocket in failed_connections:
            await self.disconnect(websocket)
        
        return successful_sends
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to all connections for a specific user.
        
        Args:
            user_id: Target user ID
            message: Message to send
            
        Returns:
            True if message was sent to at least one connection
        """
        if user_id not in self.connections_by_user:
            return False
        
        user_connections = self.connections_by_user[user_id].copy()
        sent_count = 0
        
        for websocket in user_connections:
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception:
                await self.disconnect(websocket)
        
        return sent_count > 0
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics."""
        return {
            "total_connections": len(self.connections),
            "unique_users": len(self.connections_by_user),
            "unique_ips": len(self.connections_by_ip),
            "admin_connections": sum(1 for conn in self.connections.values() if conn.is_admin),
            "oldest_connection": min(
                (conn.connected_at for conn in self.connections.values()),
                default=None
            )
        }
    
    def _get_client_ip(self, websocket: WebSocket) -> str:
        """Extract client IP from WebSocket headers."""
        # Check forwarded headers
        forwarded_for = websocket.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = websocket.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return websocket.client.host if websocket.client else "unknown"

# Global secure connection manager
secure_manager = SecureConnectionManager()

# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

async def authenticate_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT authentication token"),
    origin: Optional[str] = Header(None, alias="origin")
) -> AuthenticatedConnection:
    """
    WebSocket authentication dependency.
    
    Usage:
        @app.websocket("/ws/secure")
        async def secure_websocket(
            websocket: WebSocket,
            auth: AuthenticatedConnection = Depends(authenticate_websocket)
        ):
            # Connection is now authenticated and authorized
    """
    return await secure_manager.authenticate_and_connect(websocket, token, origin)

# ═══════════════════════════════════════════════════════════════════════════
# SECURE WEBSOCKET UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

async def handle_secure_websocket_connection(
    websocket: WebSocket,
    auth_conn: AuthenticatedConnection,
    message_handler: callable = None
):
    """
    Handle a secure WebSocket connection with proper error handling.
    
    Args:
        websocket: Authenticated WebSocket connection
        auth_conn: Authentication information
        message_handler: Optional custom message handler
    """
    try:
        while True:
            # Receive message
            try:
                data = await websocket.receive_text()
            except WebSocketDisconnect:
                break
            
            # Check rate limiting
            if not secure_manager.update_activity(websocket):
                await websocket.send_json({
                    "type": "error",
                    "message": "Rate limit exceeded",
                    "code": 429
                })
                continue
            
            # Handle message
            if message_handler:
                try:
                    await message_handler(websocket, auth_conn, data)
                except Exception as e:
                    logger.error(f"Message handler error for user {auth_conn.user_id}: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Internal error processing message",
                        "code": 500
                    })
            else:
                # Default ping/pong handler
                if data == "ping":
                    await websocket.send_text("pong")
                else:
                    await websocket.send_json({
                        "type": "info",
                        "message": "Message received",
                        "timestamp": datetime.utcnow().isoformat()
                    })
    
    except Exception as e:
        logger.error(f"WebSocket connection error for user {auth_conn.user_id}: {e}")
    
    finally:
        await secure_manager.disconnect(websocket)

def require_admin_websocket():
    """Decorator to require admin access for WebSocket endpoints."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find auth_conn in arguments
            auth_conn = None
            for arg in args:
                if isinstance(arg, AuthenticatedConnection):
                    auth_conn = arg
                    break
            
            if not auth_conn or not auth_conn.is_admin:
                raise HTTPException(status_code=403, detail="Admin access required for this WebSocket endpoint")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'WebSocketAuthConfig',
    'config',
    'AuthenticatedConnection',
    'SecureConnectionManager',
    'secure_manager',
    'authenticate_websocket',
    'handle_secure_websocket_connection',
    'require_admin_websocket'
]