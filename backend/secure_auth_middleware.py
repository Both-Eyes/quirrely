#!/usr/bin/env python3
"""
QUIRRELY SECURE AUTH MIDDLEWARE v2.0
Enhanced authentication middleware with secure JWT handling.

SECURITY IMPROVEMENTS:
- Mandatory JWT secret validation (no defaults)
- Secure secret generation utilities
- Enhanced token validation
- Key rotation support
- Audit logging for auth events
"""

from __future__ import annotations

import os
import jwt
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
import json

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logger = logging.getLogger("quirrely.secure_auth")

# ═══════════════════════════════════════════════════════════════════════════
# SECURE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SecureAuthConfig:
    """Secure authentication configuration with mandatory secrets."""
    
    # Cookie names
    ACCESS_TOKEN_COOKIE: str = "quirrely_auth"
    REFRESH_TOKEN_COOKIE: str = "quirrely_refresh"
    
    # Cookie settings
    COOKIE_DOMAIN: Optional[str] = None
    COOKIE_PATH: str = "/"
    COOKIE_SECURE: bool = True
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"
    
    # Token lifetimes (shortened for security)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Reduced from 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # JWT settings
    JWT_SECRET: str = None
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_MIN_LENGTH: int = 64  # Minimum secret length
    
    # Key rotation
    PREVIOUS_JWT_SECRETS: List[str] = None  # For graceful key rotation
    SECRET_ROTATION_DAYS: int = 90
    
    # Security features
    REQUIRE_SECURE_RANDOM: bool = True
    VALIDATE_SECRET_STRENGTH: bool = True
    LOG_AUTH_EVENTS: bool = True
    
    def __post_init__(self):
        """Initialize and validate configuration."""
        # CRITICAL: JWT secret is mandatory in production
        self.JWT_SECRET = os.environ.get('JWT_SECRET')
        if not self.JWT_SECRET:
            raise ValueError(
                "JWT_SECRET environment variable is required. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(64))\""
            )
        
        # Validate secret strength
        if self.VALIDATE_SECRET_STRENGTH:
            self._validate_secret_strength(self.JWT_SECRET)
        
        # Load previous secrets for rotation
        prev_secrets = os.environ.get('JWT_PREVIOUS_SECRETS', '')
        self.PREVIOUS_JWT_SECRETS = [s.strip() for s in prev_secrets.split(',') if s.strip()]
        
        # Security settings based on environment
        env = os.environ.get('APP_ENV', 'development')
        self.COOKIE_SECURE = env == 'production'
        self.COOKIE_DOMAIN = os.environ.get('COOKIE_DOMAIN', None)
        
        if env == 'production':
            self.ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Even shorter in production
    
    def _validate_secret_strength(self, secret: str) -> None:
        """Validate JWT secret meets security requirements."""
        if len(secret) < self.JWT_SECRET_MIN_LENGTH:
            raise ValueError(f"JWT_SECRET must be at least {self.JWT_SECRET_MIN_LENGTH} characters")
        
        # Check for common weak patterns
        weak_patterns = ['password', '123456', 'secret', 'admin', 'test', 'dev']
        secret_lower = secret.lower()
        for pattern in weak_patterns:
            if pattern in secret_lower:
                raise ValueError(f"JWT_SECRET contains weak pattern: {pattern}")
        
        # Check entropy (basic)
        unique_chars = len(set(secret))
        if unique_chars < 16:
            logger.warning("JWT_SECRET may have low entropy (few unique characters)")
    
    def get_all_valid_secrets(self) -> List[str]:
        """Get current and previous secrets for token validation during rotation."""
        secrets = [self.JWT_SECRET]
        secrets.extend(self.PREVIOUS_JWT_SECRETS or [])
        return secrets

# Initialize configuration with validation
config = SecureAuthConfig()

# ═══════════════════════════════════════════════════════════════════════════
# SECURE JWT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def generate_secure_jwt_secret() -> str:
    """
    Generate a cryptographically secure JWT secret.
    
    Returns:
        High-entropy secret suitable for JWT signing
    """
    # Generate 64 bytes of secure random data
    secure_bytes = secrets.token_bytes(64)
    # Convert to hex for easy handling
    return secure_bytes.hex()

def create_access_token(
    user_id: str,
    email: str,
    tier: str,
    addons: list = None,
    extra_claims: Dict[str, Any] = None,
) -> str:
    """
    Create a secure JWT access token.
    
    Args:
        user_id: User's unique identifier
        email: User's email
        tier: User's subscription tier
        addons: User's active addons
        extra_claims: Additional JWT claims
        
    Returns:
        Encoded JWT token string
    """
    now = datetime.utcnow()
    expire = now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Enhanced payload with security fields
    payload = {
        "sub": user_id,
        "email": email,
        "tier": tier,
        "addons": addons or [],
        "type": "access",
        "iat": now,
        "exp": expire,
        "jti": secrets.token_hex(16),  # Unique token ID
        "iss": "quirrely-auth",       # Issuer
        "aud": "quirrely-api",        # Audience
        "nbf": now,                   # Not before
    }
    
    if extra_claims:
        # Validate extra claims don't override security fields
        forbidden_claims = {"sub", "iat", "exp", "jti", "iss", "aud", "nbf"}
        for claim in forbidden_claims:
            if claim in extra_claims:
                logger.warning(f"Ignoring attempt to override security claim: {claim}")
                extra_claims.pop(claim, None)
        payload.update(extra_claims)
    
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    
    # Log token creation for audit
    if config.LOG_AUTH_EVENTS:
        logger.info(f"Access token created for user {user_id}, expires {expire.isoformat()}")
    
    return token

def create_refresh_token(user_id: str) -> str:
    """
    Create a secure JWT refresh token.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Encoded JWT refresh token string
    """
    now = datetime.utcnow()
    expire = now + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": expire,
        "jti": secrets.token_hex(16),
        "iss": "quirrely-auth",
        "aud": "quirrely-api",
        "nbf": now,
    }
    
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    
    if config.LOG_AUTH_EVENTS:
        logger.info(f"Refresh token created for user {user_id}, expires {expire.isoformat()}")
    
    return token

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token with support for key rotation.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    # Try current secret first
    valid_secrets = config.get_all_valid_secrets()
    
    for secret in valid_secrets:
        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=[config.JWT_ALGORITHM],
                issuer="quirrely-auth",
                audience="quirrely-api",
                options={
                    "require": ["sub", "iat", "exp", "jti", "iss", "aud"],
                    "verify_nbf": True
                }
            )
            
            # Additional validation
            if not payload.get("sub"):
                logger.warning("Token missing subject")
                return None
            
            if payload.get("type") not in ["access", "refresh"]:
                logger.warning("Invalid token type")
                return None
            
            # Log successful decode if using previous secret (rotation)
            if secret != config.JWT_SECRET:
                logger.info(f"Token validated with previous secret (key rotation)")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.debug("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.debug(f"Invalid token with secret {secret[:8]}...: {e}")
            continue
    
    logger.warning("Token validation failed with all available secrets")
    return None

def validate_token_claims(payload: Dict[str, Any], required_type: str = None) -> bool:
    """
    Validate token claims for security.
    
    Args:
        payload: Decoded token payload
        required_type: Required token type ("access" or "refresh")
        
    Returns:
        True if claims are valid
    """
    if not payload:
        return False
    
    # Check required type
    if required_type and payload.get("type") != required_type:
        return False
    
    # Validate timestamps
    now = datetime.utcnow()
    
    # Check expiration
    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp) <= now:
        return False
    
    # Check not before
    nbf = payload.get("nbf")
    if nbf and datetime.fromtimestamp(nbf) > now:
        return False
    
    return True

# ═══════════════════════════════════════════════════════════════════════════
# SECURE COOKIE UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def set_auth_cookies(
    response: Response,
    user_id: str,
    email: str,
    tier: str,
    addons: list = None,
) -> Tuple[str, str]:
    """
    Set secure authentication cookies on response.
    
    Args:
        response: FastAPI Response object
        user_id: User's unique identifier
        email: User's email
        tier: User's subscription tier
        addons: User's active addons
        
    Returns:
        Tuple of (access_token, refresh_token)
    """
    access_token = create_access_token(user_id, email, tier, addons)
    refresh_token = create_refresh_token(user_id)
    
    # Set access token cookie
    response.set_cookie(
        key=config.ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        samesite=config.COOKIE_SAMESITE,
    )
    
    # Set refresh token cookie
    response.set_cookie(
        key=config.REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        samesite=config.COOKIE_SAMESITE,
    )
    
    if config.LOG_AUTH_EVENTS:
        logger.info(f"Secure auth cookies set for user {user_id}")
    
    return access_token, refresh_token

def clear_auth_cookies(response: Response) -> None:
    """
    Securely clear authentication cookies from response.
    
    Args:
        response: FastAPI Response object
    """
    # Clear with same settings as when set
    response.delete_cookie(
        key=config.ACCESS_TOKEN_COOKIE,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        samesite=config.COOKIE_SAMESITE,
    )
    response.delete_cookie(
        key=config.REFRESH_TOKEN_COOKIE,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        samesite=config.COOKIE_SAMESITE,
    )
    
    if config.LOG_AUTH_EVENTS:
        logger.info("Secure auth cookies cleared")

# ═══════════════════════════════════════════════════════════════════════════
# SECRET GENERATION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def generate_deployment_secrets() -> Dict[str, str]:
    """
    Generate all required secrets for deployment.
    
    Returns:
        Dictionary of secret names and values
    """
    return {
        "JWT_SECRET": generate_secure_jwt_secret(),
        "SESSION_SECRET": secrets.token_hex(32),
        "COOKIE_SECRET": secrets.token_hex(32),
        "CSRF_SECRET": secrets.token_hex(32),
        "ENCRYPTION_KEY": secrets.token_hex(32),
    }

def validate_environment_secrets() -> Dict[str, Any]:
    """
    Validate all required secrets are present and secure.
    
    Returns:
        Validation report
    """
    report = {
        "valid": True,
        "issues": [],
        "warnings": []
    }
    
    required_secrets = ["JWT_SECRET", "SESSION_SECRET"]
    
    for secret_name in required_secrets:
        value = os.environ.get(secret_name)
        if not value:
            report["valid"] = False
            report["issues"].append(f"Missing required secret: {secret_name}")
        elif len(value) < 32:
            report["valid"] = False
            report["issues"].append(f"Secret too short: {secret_name}")
        elif value in ["secret", "password", "admin", "test"]:
            report["valid"] = False
            report["issues"].append(f"Weak secret detected: {secret_name}")
    
    return report

# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'SecureAuthConfig',
    'config',
    'generate_secure_jwt_secret',
    'create_access_token',
    'create_refresh_token',
    'decode_token',
    'validate_token_claims',
    'set_auth_cookies',
    'clear_auth_cookies',
    'generate_deployment_secrets',
    'validate_environment_secrets'
]