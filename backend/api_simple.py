#!/usr/bin/env python3
"""
LNCP Web App API (Lightweight Version)
Version: 0.1.0

Simple HTTP API server using only Python standard library.
No external dependencies required.

Endpoints:
  POST /api/game/init          - Initialize Phase-5 session
  POST /api/game/submit        - Submit sentence group
  GET  /api/game/state/{id}    - Get current game state
  POST /api/analyze            - Run full pipeline (post-gate)
  POST /api/quick-analyze      - Quick analysis (no game)
  GET  /api/results/{id}       - Get analysis results
  DELETE /api/session/{id}     - Clean up session
  GET  /api/health             - Health check

Usage:
  python api_simple.py [--port 8000] [--host 0.0.0.0]
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lncp_orchestrator import get_orchestrator, quick_analyze


class LNCPAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for LNCP API."""
    
    # Orchestrator instance (shared across requests)
    orchestrator = None
    
    @classmethod
    def get_orchestrator(cls):
        if cls.orchestrator is None:
            cls.orchestrator = get_orchestrator()
        return cls.orchestrator
    
    def _send_json(self, data: Any, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))
    
    def _send_error(self, message: str, status: int = 400):
        """Send error response."""
        self._send_json({"error": message, "status": status}, status)
    
    def _read_json_body(self) -> Optional[Dict[str, Any]]:
        """Read and parse JSON request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))
    
    def _extract_path_param(self, pattern: str) -> Optional[str]:
        """Extract parameter from path using regex pattern."""
        match = re.match(pattern, self.path)
        if match:
            return match.group(1)
        return None
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        # Health check
        if path == "/api/health":
            self._send_json({
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "0.1.0",
            })
            return
        
        # Game state
        session_id = self._extract_path_param(r"/api/game/state/([^/]+)")
        if session_id:
            self._handle_get_game_state(session_id)
            return
        
        # Get results
        session_id = self._extract_path_param(r"/api/results/([^/]+)")
        if session_id:
            self._handle_get_results(session_id)
            return
        
        self._send_error("Not found", 404)
    
    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        
        # Initialize game
        if path == "/api/game/init":
            self._handle_game_init()
            return
        
        # Submit group
        if path == "/api/game/submit":
            self._handle_submit_group()
            return
        
        # Run analysis
        if path == "/api/analyze":
            self._handle_analyze()
            return
        
        # Quick analyze
        if path == "/api/quick-analyze":
            self._handle_quick_analyze()
            return
        
        self._send_error("Not found", 404)
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        session_id = self._extract_path_param(r"/api/session/([^/]+)")
        if session_id:
            self._handle_delete_session(session_id)
            return
        
        self._send_error("Not found", 404)
    
    # --- Handler Methods ---
    
    def _handle_game_init(self):
        """Initialize a new game session."""
        try:
            body = self._read_json_body() or {}
            mode = body.get("mode", "STORY")
            
            if mode not in ("STORY", "LAB"):
                self._send_error(f"Invalid mode: {mode}. Must be STORY or LAB.")
                return
            
            orch = self.get_orchestrator()
            session_id, state = orch.create_session(mode=mode)
            
            self._send_json({
                "session_id": session_id,
                "mode": state["mode"],
                "current_prompt": state["current_prompt"],
                "gate": state["gate"],
            })
        except Exception as e:
            self._send_error(f"Failed to initialize game: {str(e)}", 500)
    
    def _handle_submit_group(self):
        """Submit a sentence group."""
        try:
            body = self._read_json_body()
            if not body:
                self._send_error("Request body required")
                return
            
            session_id = body.get("session_id")
            sentences = body.get("sentences", [])
            
            if not session_id:
                self._send_error("session_id required")
                return
            
            if len(sentences) < 2 or len(sentences) > 3:
                self._send_error("Must submit 2-3 sentences per group")
                return
            
            orch = self.get_orchestrator()
            session = orch.get_session(session_id)
            
            if not session:
                self._send_error(f"Session not found: {session_id}", 404)
                return
            
            state = orch.submit_group(session_id, sentences)
            
            self._send_json({
                "session_id": session_id,
                "state": state["state"],
                "gate": state["gate"],
                "current_prompt": state["current_prompt"],
                "last_submission": state["last_submission"],
                "coverage": state["coverage"],
                "safety": state["safety"],
            })
        except Exception as e:
            self._send_error(f"Failed to submit group: {str(e)}", 500)
    
    def _handle_get_game_state(self, session_id: str):
        """Get current game state."""
        try:
            orch = self.get_orchestrator()
            session = orch.get_session(session_id)
            
            if not session:
                self._send_error(f"Session not found: {session_id}", 404)
                return
            
            state = orch.get_game_state(session_id)
            self._send_json(state)
        except Exception as e:
            self._send_error(f"Failed to get state: {str(e)}", 500)
    
    def _handle_analyze(self):
        """Run full analysis pipeline."""
        try:
            # Get session_id from query string or body
            query = parse_qs(urlparse(self.path).query)
            session_id = query.get("session_id", [None])[0]
            
            if not session_id:
                body = self._read_json_body() or {}
                session_id = body.get("session_id")
            
            if not session_id:
                self._send_error("session_id required")
                return
            
            orch = self.get_orchestrator()
            session = orch.get_session(session_id)
            
            if not session:
                self._send_error(f"Session not found: {session_id}", 404)
                return
            
            if not session.state_machine.state.is_gate_complete:
                self._send_error("Phase-5 gate not complete. Submit more sentence groups.")
                return
            
            results = orch.run_analysis(session_id)
            
            self._send_json({
                "session_id": session_id,
                "sentences_analyzed": results["sentences_analyzed"],
                "phase1": results["phase1"],
                "phase2": results["phase2"],
                "phase3": results["phase3"],
                "phase4a": results["phase4a"],
                "phase4b": results["phase4b"],
            })
        except Exception as e:
            self._send_error(f"Analysis failed: {str(e)}", 500)
    
    def _handle_quick_analyze(self):
        """Quick analysis without game."""
        try:
            body = self._read_json_body()
            if not body:
                self._send_error("Request body required")
                return
            
            sentences = body.get("sentences", [])
            
            if len(sentences) < 2:
                self._send_error("At least 2 sentences required")
                return
            
            results = quick_analyze(sentences)
            
            self._send_json({
                "session_id": None,
                "sentences_analyzed": results["sentences_analyzed"],
                "phase1": results["phase1"],
                "phase2": results["phase2"],
                "phase3": results["phase3"],
                "phase4a": results["phase4a"],
                "phase4b": results["phase4b"],
            })
        except Exception as e:
            self._send_error(f"Analysis failed: {str(e)}", 500)
    
    def _handle_get_results(self, session_id: str):
        """Get cached analysis results."""
        try:
            orch = self.get_orchestrator()
            results = orch.get_analysis_results(session_id)
            
            if not results:
                self._send_error("Analysis not yet run for this session", 404)
                return
            
            self._send_json({
                "session_id": session_id,
                "sentences_analyzed": results["sentences_analyzed"],
                "phase1": results["phase1"],
                "phase2": results["phase2"],
                "phase3": results["phase3"],
                "phase4a": results["phase4a"],
                "phase4b": results["phase4b"],
            })
        except Exception as e:
            self._send_error(f"Failed to get results: {str(e)}", 500)
    
    def _handle_delete_session(self, session_id: str):
        """Delete a session."""
        try:
            orch = self.get_orchestrator()
            deleted = orch.cleanup_session(session_id)
            
            if not deleted:
                self._send_error(f"Session not found: {session_id}", 404)
                return
            
            self._send_json({"status": "deleted", "session_id": session_id})
        except Exception as e:
            self._send_error(f"Failed to delete session: {str(e)}", 500)
    
    def log_message(self, format: str, *args):
        """Custom logging."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    server = HTTPServer((host, port), LNCPAPIHandler)
    print(f"LNCP API Server running on http://{host}:{port}")
    print(f"  Health: http://{host}:{port}/api/health")
    print(f"  Docs: See api.py for FastAPI version with auto-docs")
    print()
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LNCP API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port)
