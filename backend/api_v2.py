#!/usr/bin/env python3
"""
QUIRRELY API v2.0
Enhanced with: Pattern Collection, Profile History, Feature Gating, Trial Management

This API delivers on the pitch deck promises:
- Words → Tokens → Profiles (LNCP core)
- Patterns stored → System learns (virtuous cycle)
- Anonymous → Authenticated handoff (session linking)
- Free → Trial → Pro (feature gating)

Endpoints:
  # Analysis
  POST /api/v2/analyze              - Run analysis (records patterns)
  GET  /api/v2/results/{id}         - Get cached results
  
  # User & Auth (ready for Supabase integration)
  POST /api/v2/auth/register        - Register user
  POST /api/v2/auth/link-session    - Link anonymous session to user
  GET  /api/v2/user/profile         - Get user profile
  GET  /api/v2/user/tier            - Get user tier info
  
  # History & Evolution
  GET  /api/v2/user/history         - Profile history
  GET  /api/v2/user/evolution       - Profile evolution over time
  
  # Trial
  POST /api/v2/trial/start          - Start 7-day trial
  GET  /api/v2/trial/status         - Check trial status
  
  # Features
  GET  /api/v2/features             - Get all features with access
  GET  /api/v2/features/check/{key} - Check specific feature access
  
  # Patterns (admin/system)
  GET  /api/v2/patterns/top         - Top patterns
  GET  /api/v2/patterns/learning    - Learning candidates
  GET  /api/v2/stats/daily          - Daily statistics
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pattern_collector import get_pattern_collector, PatternCollector
from feature_gate import get_feature_gate, FeatureGate, Tier


# ═══════════════════════════════════════════════════════════════════════════
# Mock LNCP Classifier (replace with actual import in production)
# ═══════════════════════════════════════════════════════════════════════════

class MockLNCPClassifier:
    """Mock classifier for development. Replace with actual LNCP v3.8."""
    
    PROFILES = ["ASSERTIVE", "MINIMAL", "POETIC", "DENSE", "CONVERSATIONAL",
                "FORMAL", "INTERROGATIVE", "HEDGED", "PARALLEL", "LONGFORM"]
    STANCES = ["OPEN", "CLOSED", "BALANCED", "CONTRADICTORY"]
    
    def classify(self, text: str) -> Dict[str, Any]:
        """Classify text and return profile + tokens."""
        import hashlib
        import random
        
        # Deterministic but varied based on text
        seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Generate mock tokens (first 50 words get token values 0-9)
        words = text.split()[:50]
        tokens = [random.randint(0, 9) for _ in words]
        
        # Select profile and stance
        profile = random.choice(self.PROFILES)
        stance = random.choice(self.STANCES)
        
        # Generate scores
        scores = {
            "profiles": {p: random.uniform(0, 1) for p in self.PROFILES},
            "stances": {s: random.uniform(0, 1) for s in self.STANCES},
        }
        scores["profiles"][profile] = random.uniform(0.7, 0.95)
        scores["stances"][stance] = random.uniform(0.6, 0.9)
        
        return {
            "profile": profile,
            "stance": stance,
            "tokens": tokens,
            "word_count": len(words),
            "sentence_count": text.count(".") + text.count("!") + text.count("?"),
            "scores": scores,
            "confidence": random.uniform(0.75, 0.95),
        }


# Global classifier instance
_classifier = MockLNCPClassifier()


def get_classifier() -> MockLNCPClassifier:
    return _classifier


# ═══════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════

class AnalyzeRequest(BaseModel):
    """Request to analyze text."""
    text: str = Field(..., min_length=20, description="Text to analyze (min 20 chars)")
    source: str = Field(default="web", description="Source: web, extension, api")


class AnalyzeResponse(BaseModel):
    """Analysis result."""
    profile: str
    stance: str
    word_count: int
    sentence_count: int
    confidence: float
    scores: Dict[str, Any]
    pattern_id: str
    history_id: str
    features_used: List[str]


class RegisterRequest(BaseModel):
    """User registration request."""
    email: str
    session_id: Optional[str] = None  # To link anonymous session


class LinkSessionRequest(BaseModel):
    """Link session to user request."""
    session_id: str


class TrialStartResponse(BaseModel):
    """Trial start response."""
    success: bool
    message: str
    trial_ends_at: Optional[str] = None
    days: int = 7


class FeatureCheckResponse(BaseModel):
    """Feature check response."""
    feature: str
    allowed: bool
    tier: str
    reason: str


class UserTierResponse(BaseModel):
    """User tier information."""
    user_id: str
    base_tier: str
    effective_tier: str
    trial_ends_at: Optional[str]
    trial_analyses: int
    daily_limit: Dict[str, Any]


class EvolutionResponse(BaseModel):
    """Profile evolution response."""
    entries: int
    dominant_profile: Optional[str]
    dominant_stance: Optional[str]
    trend: Optional[str]
    profiles: Dict[str, int]
    stances: Dict[str, int]
    timeline: List[Dict[str, str]]


# ═══════════════════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Quirrely API v2",
    description="LNCP-powered writing voice analysis with pattern learning",
    version="2.0.0",
    docs_url="/api/v2/docs",
    redoc_url="/api/v2/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quirrely.com","https://www.quirrely.com","https://quirrely.ca","https://www.quirrely.ca"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════
# Dependencies
# ═══════════════════════════════════════════════════════════════════════════

async def get_user_id(x_user_id: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user ID from header."""
    return x_user_id


async def get_session_id(x_session_id: Optional[str] = Header(None)) -> Optional[str]:
    """Extract session ID from header."""
    return x_session_id


# ═══════════════════════════════════════════════════════════════════════════
# Health Check
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "features": {
            "pattern_collection": True,
            "profile_history": True,
            "feature_gating": True,
            "trial_management": True,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# Analysis Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/api/v2/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    user_id: Optional[str] = Depends(get_user_id),
    session_id: Optional[str] = Depends(get_session_id),
):
    """
    Analyze text and return profile.
    
    Records patterns and history for the virtuous cycle.
    Respects feature gating and daily limits.
    """
    gate = get_feature_gate()
    collector = get_pattern_collector()
    classifier = get_classifier()
    
    # Check daily limit
    _est_words = len(request.text.split())
    limit_check = gate.check_daily_limit(user_id, session_id, _est_words)
    if not limit_check["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Word limit reached ({limit_check['used']}/{limit_check['limit']} words). Upgrade to Pro for more.",
        )
    
    # Check basic analysis feature (should always pass)
    access = gate.can_access("basic_analysis", user_id, session_id)
    if not access.allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=access.reason,
        )
    
    # Run classification
    try:
        result = classifier.classify(request.text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Classification failed",
        )
    
    # Record pattern and history (THE VIRTUOUS CYCLE)
    pattern_id, history_id = collector.record_analysis(
        tokens=result["tokens"],
        profile=result["profile"],
        stance=result["stance"],
        word_count=result["word_count"],
        sentence_count=result["sentence_count"],
        user_id=user_id,
        session_id=session_id,
        source=request.source,
        input_preview=request.text[:100],
        scores=result["scores"],
        confidence_score=result["confidence"],
    )
    
    # Record usage for daily limit
    gate.record_analysis(user_id, session_id, result["word_count"])
    
    # Track features used
    features_used = ["basic_analysis"]
    if gate.can_access("writer_matches", user_id, session_id).allowed:
        features_used.append("writer_matches")
    if user_id and gate.can_access("save_results", user_id).allowed:
        features_used.append("save_results")
    
    return AnalyzeResponse(
        profile=result["profile"],
        stance=result["stance"],
        word_count=result["word_count"],
        sentence_count=result["sentence_count"],
        confidence=result["confidence"],
        scores=result["scores"],
        pattern_id=pattern_id,
        history_id=history_id,
        features_used=features_used,
    )


# ═══════════════════════════════════════════════════════════════════════════
# User & Auth Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/api/v2/auth/register")
async def register_user(request: RegisterRequest):
    """
    Register a new user.
    
    In production, this integrates with Supabase Auth.
    For now, creates a local user record.
    """
    import hashlib
    
    gate = get_feature_gate()
    collector = get_pattern_collector()
    
    # Generate user ID (in production, comes from Supabase)
    user_id = hashlib.sha256(request.email.encode()).hexdigest()[:24]
    
    # Set as free tier initially
    gate.set_user_tier(user_id, Tier.FREE)
    
    # Link session if provided
    profiles_migrated = 0
    if request.session_id:
        profiles_migrated = collector.link_session_to_user(request.session_id, user_id)
    
    return {
        "success": True,
        "user_id": user_id,
        "email": request.email,
        "tier": "free",
        "profiles_migrated": profiles_migrated,
        "message": f"Account created. {profiles_migrated} previous analyses linked." if profiles_migrated else "Account created.",
    }


@app.post("/api/v2/auth/link-session")
async def link_session(
    request: LinkSessionRequest,
    user_id: str = Depends(get_user_id),
):
    """Link an anonymous session to the authenticated user."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    collector = get_pattern_collector()
    migrated = collector.link_session_to_user(request.session_id, user_id)
    
    return {
        "success": True,
        "session_id": request.session_id,
        "user_id": user_id,
        "profiles_migrated": migrated,
    }


@app.get("/api/v2/user/tier", response_model=UserTierResponse)
async def get_user_tier_info(user_id: str = Depends(get_user_id)):
    """Get user's tier information including trial status."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    gate = get_feature_gate()
    tier_info = gate.get_user_tier(user_id)
    daily_limit = gate.check_daily_limit(user_id)
    
    return UserTierResponse(
        user_id=user_id,
        base_tier=tier_info.base_tier.value,
        effective_tier=tier_info.effective_tier.value,
        trial_ends_at=tier_info.trial_ends_at.isoformat() if tier_info.trial_ends_at else None,
        trial_analyses=tier_info.trial_analyses,
        daily_limit=daily_limit,
    )


# ═══════════════════════════════════════════════════════════════════════════
# History & Evolution Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/user/history")
async def get_user_history(
    user_id: str = Depends(get_user_id),
    limit: int = 20,
):
    """Get user's profile history."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    gate = get_feature_gate()
    access = gate.can_access("profile_history", user_id)
    if not access.allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=access.reason,
        )
    
    collector = get_pattern_collector()
    history = collector.get_user_history(user_id, limit)
    
    return {
        "user_id": user_id,
        "count": len(history),
        "history": [
            {
                "id": h.id,
                "profile": h.profile,
                "stance": h.stance,
                "word_count": h.word_count,
                "analyzed_at": h.analyzed_at,
                "source": h.source,
            }
            for h in history
        ],
    }


@app.get("/api/v2/user/evolution", response_model=EvolutionResponse)
async def get_profile_evolution(
    user_id: str = Depends(get_user_id),
    days: int = 30,
):
    """Get profile evolution over time."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    gate = get_feature_gate()
    access = gate.can_access("evolution_tracking", user_id)
    if not access.allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=access.reason,
        )
    
    collector = get_pattern_collector()
    evolution = collector.get_profile_evolution(user_id, days)
    
    return EvolutionResponse(**evolution)


# ═══════════════════════════════════════════════════════════════════════════
# Trial Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/api/v2/trial/start", response_model=TrialStartResponse)
async def start_trial(user_id: str = Depends(get_user_id)):
    """Start a 7-day free trial."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    gate = get_feature_gate()
    success = gate.start_trial(user_id)
    
    if not success:
        return TrialStartResponse(
            success=False,
            message="Trial already used. Upgrade to Pro for full access.",
        )
    
    status_info = gate.get_trial_status(user_id)
    
    return TrialStartResponse(
        success=True,
        message="Your 7-day trial has started! Enjoy full access to all features.",
        trial_ends_at=status_info["ends_at"] if status_info else None,
        days=7,
    )


@app.get("/api/v2/trial/status")
async def get_trial_status(user_id: str = Depends(get_user_id)):
    """Get trial status."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    gate = get_feature_gate()
    status_info = gate.get_trial_status(user_id)
    
    if not status_info:
        return {
            "has_trial": False,
            "eligible": True,
            "message": "You're eligible for a 7-day free trial!",
        }
    
    return {
        "has_trial": True,
        **status_info,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Feature Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/features")
async def get_all_features(user_id: Optional[str] = Depends(get_user_id)):
    """Get all features with access status."""
    gate = get_feature_gate()
    features = gate.get_all_features(user_id)
    
    tier = "anonymous"
    if user_id:
        tier = gate.get_user_tier(user_id).effective_tier.value
    
    return {
        "tier": tier,
        "features": features,
    }


@app.get("/api/v2/features/check/{feature_key}", response_model=FeatureCheckResponse)
async def check_feature(
    feature_key: str,
    user_id: Optional[str] = Depends(get_user_id),
    session_id: Optional[str] = Depends(get_session_id),
):
    """Check access to a specific feature."""
    gate = get_feature_gate()
    result = gate.can_access(feature_key, user_id, session_id)
    
    return FeatureCheckResponse(
        feature=result.feature,
        allowed=result.allowed,
        tier=result.tier.value,
        reason=result.reason,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Pattern & Stats Endpoints (Admin/System)
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/patterns/top")
async def get_top_patterns(limit: int = 20):
    """Get most observed patterns."""
    collector = get_pattern_collector()
    patterns = collector.get_top_patterns(limit)
    
    return {
        "count": len(patterns),
        "patterns": [
            {
                "signature": p.token_signature,
                "observations": p.total_observations,
                "dominant_profile": p.dominant_profile,
                "dominant_stance": p.dominant_stance,
                "confidence": p.profile_confidence,
                "first_seen": p.first_seen_at,
                "last_seen": p.last_seen_at,
            }
            for p in patterns
        ],
    }


@app.get("/api/v2/patterns/learning")
async def get_learning_candidates(min_observations: int = 50):
    """Get patterns that might inform LNCP improvements."""
    collector = get_pattern_collector()
    candidates = collector.get_learning_candidates(min_observations)
    
    return {
        "count": len(candidates),
        "candidates": candidates,
    }


@app.get("/api/v2/stats/daily")
async def get_daily_stats(days: int = 7):
    """Get daily statistics."""
    collector = get_pattern_collector()
    stats = collector.get_daily_stats(days)
    
    # Calculate totals
    total_analyses = sum(s["total_analyses"] for s in stats)
    
    return {
        "days": days,
        "total_analyses": total_analyses,
        "daily": stats,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("Starting Quirrely API v2...")
    print("Docs: http://localhost:8000/api/v2/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ── QUICK-ANALYZE ALIAS (v3.1.3 compat) ────────────────────────────────────
# Alias for /api/v2/analyze — used by extension and external integrations
@app.post("/api/quick-analyze", response_model=AnalyzeResponse)
async def quick_analyze(request: AnalyzeRequest, authorization: str = Header(None)):
    """
    Alias for /api/v2/analyze.
    Retained for Chrome extension v1 compatibility and external integrations.
    Delegates to the full analyze_text handler.
    """
    return await analyze_text(request, authorization)
