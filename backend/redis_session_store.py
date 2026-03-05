#!/usr/bin/env python3
"""
QUIRRELY REDIS SESSION STORE v1.0
Redis-backed session storage for persistent authentication.

Features:
- Persistent session storage across application restarts
- Automatic session expiration
- Connection pooling and retry logic
- Encryption for sensitive session data
- Performance monitoring
"""

import os
import json
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from cryptography.fernet import Fernet
import base64

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

logger = logging.getLogger("quirrely.redis_session")

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class RedisSessionConfig:
    """Redis session storage configuration."""
    
    # Connection settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CONNECTION_POOL_SIZE: int = 10
    CONNECTION_TIMEOUT: int = 5
    
    # Session settings
    SESSION_PREFIX: str = "quirrely:session:"
    DEFAULT_TIMEOUT: int = 3600  # 1 hour
    MAX_TIMEOUT: int = 86400     # 24 hours
    
    # Security settings
    ENCRYPT_SESSIONS: bool = True
    ENCRYPTION_KEY: Optional[str] = None
    
    # Performance settings
    ENABLE_COMPRESSION: bool = True
    MAX_SESSION_SIZE: int = 1024 * 1024  # 1MB
    
    def __post_init__(self):
        """Initialize configuration from environment."""
        self.REDIS_URL = os.environ.get("REDIS_URL", self.REDIS_URL)
        self.CONNECTION_POOL_SIZE = int(os.environ.get("REDIS_POOL_SIZE", str(self.CONNECTION_POOL_SIZE)))
        self.DEFAULT_TIMEOUT = int(os.environ.get("SESSION_TIMEOUT", str(self.DEFAULT_TIMEOUT)))
        self.ENCRYPT_SESSIONS = os.environ.get("ENCRYPT_SESSIONS", "true").lower() == "true"
        
        # Initialize encryption key
        if self.ENCRYPT_SESSIONS:
            env_key = os.environ.get("SESSION_ENCRYPTION_KEY")
            if env_key:
                self.ENCRYPTION_KEY = env_key
            else:
                # Generate a key (should be stored securely in production)
                self.ENCRYPTION_KEY = Fernet.generate_key().decode()
                logger.warning("Generated ephemeral encryption key. Set SESSION_ENCRYPTION_KEY for persistence.")

config = RedisSessionConfig()

# ═══════════════════════════════════════════════════════════════════════════
# SESSION ENCRYPTION
# ═══════════════════════════════════════════════════════════════════════════

class SessionEncryption:
    """Handle session data encryption/decryption."""
    
    def __init__(self, encryption_key: str):
        self.fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt session data."""
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt session data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt session data."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt session data: {e}")
            raise

# ═══════════════════════════════════════════════════════════════════════════
# REDIS SESSION STORE
# ═══════════════════════════════════════════════════════════════════════════

class RedisSessionStore:
    """Redis-backed session storage with security features."""
    
    def __init__(self):
        self.config = config
        self.pool = None
        self.redis_client = None
        self.encryption = None
        self._stats = {
            "operations": 0,
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
        
        # Initialize encryption if enabled
        if self.config.ENCRYPT_SESSIONS:
            self.encryption = SessionEncryption(self.config.ENCRYPTION_KEY)
    
    async def initialize(self):
        """Initialize Redis connection pool."""
        try:
            # Create connection pool
            self.pool = ConnectionPool.from_url(
                self.config.REDIS_URL,
                max_connections=self.config.CONNECTION_POOL_SIZE,
                socket_timeout=self.config.CONNECTION_TIMEOUT,
                socket_connect_timeout=self.config.CONNECTION_TIMEOUT,
                health_check_interval=30,
            )
            
            self.redis_client = redis.Redis(
                connection_pool=self.pool,
                decode_responses=False  # We handle encoding ourselves
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info(f"Redis session store initialized: {self.config.REDIS_URL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis session store: {e}")
            raise
    
    async def set_session(
        self, 
        session_id: str, 
        session_data: Dict[str, Any], 
        timeout: Optional[int] = None
    ) -> bool:
        """
        Store session data with optional timeout.
        
        Args:
            session_id: Unique session identifier
            session_data: Session data to store
            timeout: Session timeout in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        self._stats["operations"] += 1
        
        try:
            if not self.redis_client:
                await self.initialize()
            
            # Validate session size
            data_str = json.dumps(session_data, separators=(',', ':'))
            if len(data_str) > self.config.MAX_SESSION_SIZE:
                logger.warning(f"Session data too large: {len(data_str)} bytes")
                return False
            
            # Encrypt if enabled
            if self.config.ENCRYPT_SESSIONS:
                data_str = self.encryption.encrypt_data(data_str)
            
            # Set timeout
            timeout = timeout or self.config.DEFAULT_TIMEOUT
            timeout = min(timeout, self.config.MAX_TIMEOUT)
            
            # Store in Redis
            key = f"{self.config.SESSION_PREFIX}{session_id}"
            await self.redis_client.setex(key, timeout, data_str)
            
            logger.debug(f"Session stored: {session_id} (expires in {timeout}s)")
            return True
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Failed to store session {session_id}: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None if not found
        """
        self._stats["operations"] += 1
        
        try:
            if not self.redis_client:
                await self.initialize()
            
            key = f"{self.config.SESSION_PREFIX}{session_id}"
            data = await self.redis_client.get(key)
            
            if data is None:
                self._stats["misses"] += 1
                logger.debug(f"Session not found: {session_id}")
                return None
            
            self._stats["hits"] += 1
            
            # Decode data
            data_str = data.decode('utf-8')
            
            # Decrypt if enabled
            if self.config.ENCRYPT_SESSIONS:
                data_str = self.encryption.decrypt_data(data_str)
            
            session_data = json.loads(data_str)
            logger.debug(f"Session retrieved: {session_id}")
            return session_data
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Failed to retrieve session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was deleted, False otherwise
        """
        self._stats["operations"] += 1
        
        try:
            if not self.redis_client:
                await self.initialize()
            
            key = f"{self.config.SESSION_PREFIX}{session_id}"
            result = await self.redis_client.delete(key)
            
            if result > 0:
                logger.debug(f"Session deleted: {session_id}")
                return True
            else:
                logger.debug(f"Session not found for deletion: {session_id}")
                return False
                
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    async def extend_session(self, session_id: str, additional_time: int) -> bool:
        """
        Extend session timeout.
        
        Args:
            session_id: Session identifier
            additional_time: Additional seconds to add to timeout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.redis_client:
                await self.initialize()
            
            key = f"{self.config.SESSION_PREFIX}{session_id}"
            current_ttl = await self.redis_client.ttl(key)
            
            if current_ttl > 0:
                new_ttl = min(current_ttl + additional_time, self.config.MAX_TIMEOUT)
                result = await self.redis_client.expire(key, new_ttl)
                
                if result:
                    logger.debug(f"Session extended: {session_id} (+{additional_time}s)")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to extend session {session_id}: {e}")
            return False
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session metadata without retrieving data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session info dictionary or None
        """
        try:
            if not self.redis_client:
                await self.initialize()
            
            key = f"{self.config.SESSION_PREFIX}{session_id}"
            ttl = await self.redis_client.ttl(key)
            
            if ttl > 0:
                return {
                    "session_id": session_id,
                    "ttl": ttl,
                    "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session info {session_id}: {e}")
            return None
    
    async def list_user_sessions(self, user_id: str) -> List[str]:
        """
        List all active sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session IDs
        """
        try:
            if not self.redis_client:
                await self.initialize()
            
            # Use a pattern to find sessions for this user
            # This requires sessions to include user_id in their data
            pattern = f"{self.config.SESSION_PREFIX}*"
            session_keys = await self.redis_client.keys(pattern)
            
            user_sessions = []
            
            for key in session_keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        # Check if this session belongs to the user
                        data_str = data.decode('utf-8')
                        if self.config.ENCRYPT_SESSIONS:
                            data_str = self.encryption.decrypt_data(data_str)
                        
                        session_data = json.loads(data_str)
                        if session_data.get("user_id") == user_id:
                            session_id = key.decode('utf-8').replace(self.config.SESSION_PREFIX, "")
                            user_sessions.append(session_id)
                            
                except Exception:
                    # Skip invalid sessions
                    continue
            
            return user_sessions
            
        except Exception as e:
            logger.error(f"Failed to list sessions for user {user_id}: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (Redis handles this automatically, but we can get stats).
        
        Returns:
            Number of active sessions
        """
        try:
            if not self.redis_client:
                await self.initialize()
            
            pattern = f"{self.config.SESSION_PREFIX}*"
            session_keys = await self.redis_client.keys(pattern)
            return len(session_keys)
            
        except Exception as e:
            logger.error(f"Failed to get session count: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get session store statistics."""
        active_sessions = await self.cleanup_expired_sessions()
        
        hit_rate = 0
        if self._stats["hits"] + self._stats["misses"] > 0:
            hit_rate = self._stats["hits"] / (self._stats["hits"] + self._stats["misses"])
        
        return {
            "active_sessions": active_sessions,
            "total_operations": self._stats["operations"],
            "cache_hits": self._stats["hits"],
            "cache_misses": self._stats["misses"],
            "errors": self._stats["errors"],
            "hit_rate": f"{hit_rate:.2%}",
            "encryption_enabled": self.config.ENCRYPT_SESSIONS,
            "redis_url": self.config.REDIS_URL.split('@')[-1] if '@' in self.config.REDIS_URL else self.config.REDIS_URL  # Hide credentials
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Redis connection."""
        try:
            if not self.redis_client:
                await self.initialize()
            
            start_time = datetime.utcnow()
            await self.redis_client.ping()
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Close Redis connections."""
        try:
            if self.redis_client:
                await self.redis_client.close()
            if self.pool:
                await self.pool.disconnect()
            logger.info("Redis session store closed")
        except Exception as e:
            logger.error(f"Error closing Redis session store: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

# Global session store instance
session_store = RedisSessionStore()

# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'RedisSessionConfig',
    'RedisSessionStore', 
    'SessionEncryption',
    'session_store'
]