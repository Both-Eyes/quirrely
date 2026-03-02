#!/usr/bin/env python3
"""
LNCP Web App API
Version: 0.1.0

FastAPI backend for the LNCP web application.

Endpoints:
  POST /api/game/init          - Initialize Phase-5 session
  POST /api/game/submit        - Submit sentence group
  GET  /api/game/state/{id}    - Get current game state
  POST /api/analyze            - Run full pipeline (post-gate)
  POST /api/quick-analyze      - Quick analysis (no game)
  GET  /api/results/{id}       - Get analysis results
  DELETE /api/session/{id}     - Clean up session
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lncp_orchestrator import get_orchestrator, quick_analyze, LNCPOrchestrator


# ----------------------------
# Pydantic Models
# ----------------------------

class GameInitRequest(BaseModel):
    """Request to initialize a new game session."""
    mode: str = Field(default="STORY", description="Game mode: STORY or LAB")


class GameInitResponse(BaseModel):
    """Response from game initialization."""
    session_id: str
    mode: str
    current_prompt: Dict[str, Any]
    gate: Dict[str, Any]


class SubmitGroupRequest(BaseModel):
    """Request to submit a sentence group."""
    session_id: str
    sentences: List[str] = Field(..., min_length=2, max_length=3)


class SubmitGroupResponse(BaseModel):
    """Response from group submission."""
    session_id: str
    state: str
    gate: Dict[str, Any]
    current_prompt: Dict[str, Any]
    last_submission: Optional[Dict[str, Any]]
    coverage: Dict[str, Any]
    safety: Dict[str, Any]


class QuickAnalyzeRequest(BaseModel):
    """Request for quick analysis without game."""
    sentences: List[str] = Field(..., min_length=2)


class AnalysisResponse(BaseModel):
    """Full analysis results."""
    session_id: Optional[str]
    sentences_analyzed: List[str]
    phase1: Dict[str, Any]
    phase2: Dict[str, Any]
    phase3: Dict[str, Any]
    phase4a: Dict[str, Any]
    phase4b: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    error_code: Optional[str] = None


# ----------------------------
# FastAPI App
# ----------------------------

app = FastAPI(
    title="LNCP Web App API",
    description="API for the LNCP structural writing analysis application",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://quirrely.com","https://www.quirrely.com","https://quirrely.ca","https://www.quirrely.ca"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Health Check
# ----------------------------

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


# ----------------------------
# Game Mode Endpoints
# ----------------------------

@app.post("/api/game/init", response_model=GameInitResponse)
async def init_game(request: GameInitRequest):
    """
    Initialize a new Phase-5 game session.
    
    Creates a new session with the specified mode (STORY or LAB)
    and returns the initial game state with the first prompt.
    """
    if request.mode not in ("STORY", "LAB"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode: {request.mode}. Must be STORY or LAB.",
        )
    
    try:
        orch = get_orchestrator()
        session_id, state = orch.create_session(mode=request.mode)
        
        return GameInitResponse(
            session_id=session_id,
            mode=state["mode"],
            current_prompt=state["current_prompt"],
            gate=state["gate"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.post("/api/game/submit", response_model=SubmitGroupResponse)
async def submit_group(request: SubmitGroupRequest):
    """
    Submit a sentence group to the game.
    
    Validates the group and updates the game state.
    Returns the updated state including validation result.
    """
    if len(request.sentences) < 2 or len(request.sentences) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must submit 2-3 sentences per group.",
        )
    
    try:
        orch = get_orchestrator()
        session = orch.get_session(request.session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {request.session_id}",
            )
        
        state = orch.submit_group(request.session_id, request.sentences)
        
        return SubmitGroupResponse(
            session_id=request.session_id,
            state=state["state"],
            gate=state["gate"],
            current_prompt=state["current_prompt"],
            last_submission=state["last_submission"],
            coverage=state["coverage"],
            safety=state["safety"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Internal server error",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get("/api/game/state/{session_id}")
async def get_game_state(session_id: str):
    """
    Get the current game state for a session.
    """
    try:
        orch = get_orchestrator()
        session = orch.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )
        
        return orch.get_game_state(session_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internal server error",
        )


# ----------------------------
# Analysis Endpoints
# ----------------------------

@app.post("/api/analyze", response_model=AnalysisResponse)
async def run_analysis(session_id: str):
    """
    Run the full analysis pipeline for a completed game session.
    
    Requires the Phase-5 gate to be complete (3/3 valid groups).
    Returns all phase outputs (1-4b).
    """
    try:
        orch = get_orchestrator()
        session = orch.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )
        
        if not session.state_machine.state.is_gate_complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phase-5 gate not complete. Submit more sentence groups.",
            )
        
        results = orch.run_analysis(session_id)
        
        return AnalysisResponse(
            session_id=session_id,
            sentences_analyzed=results["sentences_analyzed"],
            phase1=results["phase1"],
            phase2=results["phase2"],
            phase3=results["phase3"],
            phase4a=results["phase4a"],
            phase4b=results["phase4b"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Internal server error",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.post("/api/quick-analyze", response_model=AnalysisResponse)
async def quick_analyze_endpoint(request: QuickAnalyzeRequest):
    """
    Quick analysis without game mode.
    
    Directly analyzes the provided sentences through the full pipeline.
    Requires at least 2 sentences.
    """
    if len(request.sentences) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 sentences required for analysis.",
        )
    
    try:
        results = quick_analyze(request.sentences)
        
        return AnalysisResponse(
            session_id=None,
            sentences_analyzed=results["sentences_analyzed"],
            phase1=results["phase1"],
            phase2=results["phase2"],
            phase3=results["phase3"],
            phase4a=results["phase4a"],
            phase4b=results["phase4b"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Internal server error",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.get("/api/results/{session_id}", response_model=AnalysisResponse)
async def get_results(session_id: str):
    """
    Get cached analysis results for a session.
    
    Returns the results if analysis has been run, otherwise 404.
    """
    try:
        orch = get_orchestrator()
        results = orch.get_analysis_results(session_id)
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not yet run for this session.",
            )
        
        return AnalysisResponse(
            session_id=session_id,
            sentences_analyzed=results["sentences_analyzed"],
            phase1=results["phase1"],
            phase2=results["phase2"],
            phase3=results["phase3"],
            phase4a=results["phase4a"],
            phase4b=results["phase4b"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internal server error",
        )


# ----------------------------
# Session Management
# ----------------------------

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and free resources.
    """
    try:
        orch = get_orchestrator()
        deleted = orch.cleanup_session(session_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )
        
        return {"status": "deleted", "session_id": session_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# ----------------------------
# Main
# ----------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
