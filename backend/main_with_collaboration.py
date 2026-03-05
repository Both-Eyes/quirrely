#!/usr/bin/env python3
"""
QUIRRELY API v2.0 WITH COLLABORATION
Complete FastAPI application including collaboration features.

This is the complete main application that includes all existing features
plus the new collaboration system.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import existing modules
from pattern_collector import get_pattern_collector, PatternCollector
from feature_gate import get_feature_gate, FeatureGate, Tier

# Import collaboration system
from collaboration_api import router as collaboration_router
from collaboration_service import initialize_collaboration_service

# ═══════════════════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Quirrely API v2.0",
    description="Enhanced with Pattern Collection, Feature Gating, Trials, and Collaboration",
    version="2.0.0",
    docs_url="/api/v2/docs",
    redoc_url="/api/v2/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
# STARTUP/SHUTDOWN
# ═══════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    
    # Initialize database connection for collaboration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        await initialize_collaboration_service(database_url)
        print("✅ Collaboration service initialized")
    else:
        print("⚠️  DATABASE_URL not set - collaboration will use mock data")
    
    print("🚀 Quirrely API v2.0 started with collaboration features")

@app.on_event("shutdown")
async def shutdown():
    """Clean up on shutdown."""
    print("🛑 Quirrely API v2.0 shutting down")

# ═══════════════════════════════════════════════════════════════════════════
# INCLUDE EXISTING API ROUTES
# ═══════════════════════════════════════════════════════════════════════════

# Mock LNCP Classifier (replace with actual import in production)
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
        }

# Initialize classifier
classifier = MockLNCPClassifier()

# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES (matching existing api_v2.py)
# ═══════════════════════════════════════════════════════════════════════════

async def get_user_id(x_user_id: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user ID from header."""
    return x_user_id

async def get_session_id(x_session_id: Optional[str] = Header(None)) -> Optional[str]:
    """Extract session ID from header."""
    return x_session_id

# ═══════════════════════════════════════════════════════════════════════════
# MODELS (from existing api_v2.py)
# ═══════════════════════════════════════════════════════════════════════════

class AnalyzeRequest(BaseModel):
    text: str = Field(..., max_length=50000)
    profile_mode: str = Field(default="auto")
    save_result: bool = Field(default=False)

class AnalysisResult(BaseModel):
    profile: str
    stance: str
    tokens: List[int]
    scores: Dict[str, Any]
    word_count: int
    sentence_count: int
    analysis_id: Optional[str] = None
    cached: bool = False

# ═══════════════════════════════════════════════════════════════════════════
# HEALTH & INFO
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/v2/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "version": "2.0.0",
        "features": ["collaboration", "partnerships", "word_tracking"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v2/info")
async def get_info():
    """API information and capabilities."""
    return {
        "name": "Quirrely API v2.0 with Collaboration",
        "version": "2.0.0",
        "features": {
            "pattern_collection": "Automatic learning from user analyses",
            "feature_gating": "Tier-based access control",
            "trial_management": "7-day trial system", 
            "collaboration": "Writing partnerships for Pro users",
            "word_tracking": "Shared and solo word allocation",
            "featured_partnerships": "Community showcase system"
        },
        "tiers": ["free", "trial", "pro", "curator", "featured_writer", "featured_curator", "authority_writer", "authority_curator"],
        "partnership_types": ["heart", "growth", "professional", "creative", "life"]
    }

# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS (from existing api_v2.py)
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/api/v2/analyze", response_model=AnalysisResult)
async def analyze_text(
    request: AnalyzeRequest,
    user_id: Optional[str] = Depends(get_user_id),
    session_id: Optional[str] = Depends(get_session_id),
):
    """Run analysis and collect patterns."""
    
    # Check word limits for collaboration users
    words_needed = len(request.text.split())
    
    if user_id:
        # Check if user has collaboration and sufficient word allowance
        from collaboration_service import get_user_collaboration, update_word_allocation
        try:
            partnership = await get_user_collaboration(user_id)
            if partnership and partnership['status'] == 'active':
                # User has active partnership - check word pools
                shared_available = partnership['shared_creative_space'] - partnership['shared_space_used']
                solo_available = (partnership['initiator_solo_space_remaining'] 
                                if partnership['initiator_user_id'] == user_id 
                                else partnership['partner_solo_space_remaining'])
                
                # For now, prefer shared pool
                if shared_available >= words_needed:
                    pool_type = 'shared'
                elif solo_available >= words_needed:
                    pool_type = 'solo'
                else:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "insufficient_words",
                            "shared_available": shared_available,
                            "solo_available": solo_available,
                            "words_needed": words_needed
                        }
                    )
                
                # Record word usage
                await update_word_allocation(partnership['id'], user_id, words_needed, pool_type)
        except Exception as e:
            print(f"Partnership word check failed: {e}")
            # Continue with analysis even if partnership check fails
    
    # Run analysis
    result = classifier.classify(request.text)
    
    # Store patterns
    collector = get_pattern_collector()
    analysis_id = collector.collect_patterns(
        profile=result["profile"],
        stance=result["stance"], 
        tokens=result["tokens"],
        user_id=user_id,
        session_id=session_id or "anonymous",
        save_result=request.save_result
    )
    
    return AnalysisResult(
        analysis_id=analysis_id,
        **result
    )

# ═══════════════════════════════════════════════════════════════════════════
# COLLABORATION ROUTES
# ═══════════════════════════════════════════════════════════════════════════

# Include collaboration router
app.include_router(collaboration_router)

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_with_collaboration:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )