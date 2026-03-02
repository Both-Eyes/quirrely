#!/usr/bin/env python3
"""
LNCP Session Persistence Layer
Version: 0.1.0

Provides file-based persistence for LNCP sessions with export/import capability.
Sessions are saved automatically and can be retrieved for historical comparison.

Storage structure:
  sessions/
    {session_id}.json    # Full session data
    index.json           # Session index with metadata
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib


# Default storage directory (relative to this file)
DEFAULT_STORAGE_DIR = Path(__file__).parent / "sessions"


class SessionStore:
    """
    Manages session persistence to filesystem.
    
    Each session is stored as a JSON file with full analysis results.
    An index file tracks all sessions with metadata for quick lookup.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the session store.
        
        Args:
            storage_dir: Directory to store session files. Defaults to ./sessions/
        """
        self.storage_dir = storage_dir or DEFAULT_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.storage_dir / "index.json"
        self._ensure_index()
    
    def _ensure_index(self):
        """Create index file if it doesn't exist."""
        if not self.index_path.exists():
            self._write_index({"version": "0.1.0", "sessions": {}})
    
    def _read_index(self) -> Dict[str, Any]:
        """Read the session index."""
        with open(self.index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _write_index(self, index: Dict[str, Any]):
        """Write the session index."""
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, default=str)
    
    def save_session(
        self,
        session_id: str,
        session_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save a session to storage.
        
        Args:
            session_id: Unique session identifier
            session_data: Full session data including all phase outputs
            metadata: Optional metadata (mode, timestamp, etc.)
            
        Returns:
            Path to saved session file
        """
        # Build session record
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Extract key metrics for index
        phase1 = session_data.get("phase1", {}).get("outputs", {})
        phase6 = session_data.get("phase6", {})
        hi_profile = session_data.get("high_intent_profile", {})
        
        index_entry = {
            "session_id": session_id,
            "created_at": timestamp,
            "mode": metadata.get("mode", "STORY") if metadata else "STORY",
            "sentence_count": phase1.get("sentence_count", {}).get("count", 0),
            "epistemic_stance": phase6.get("high_intent_reflection", {}).get("epistemic_stance", "UNKNOWN"),
            "variety_ratio": phase1.get("structural_variety", {}).get("variety_ratio", 0),
            "title": phase6.get("summary", {}).get("title", "Untitled Analysis"),
        }
        
        # Build full session record
        session_record = {
            "session_id": session_id,
            "created_at": timestamp,
            "metadata": metadata or {},
            "data": session_data,
        }
        
        # Write session file
        session_path = self.storage_dir / f"{session_id}.json"
        with open(session_path, "w", encoding="utf-8") as f:
            json.dump(session_record, f, indent=2, default=str)
        
        # Update index
        index = self._read_index()
        index["sessions"][session_id] = index_entry
        self._write_index(index)
        
        return str(session_path)
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a session from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session record or None if not found
        """
        session_path = self.storage_dir / f"{session_id}.json"
        if not session_path.exists():
            return None
        
        with open(session_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def list_sessions(
        self,
        limit: int = 20,
        offset: int = 0,
        mode: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List sessions with optional filtering.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            mode: Filter by mode (STORY or SCHOOL)
            
        Returns:
            List of session index entries, sorted by created_at descending
        """
        index = self._read_index()
        sessions = list(index.get("sessions", {}).values())
        
        # Filter by mode if specified
        if mode:
            sessions = [s for s in sessions if s.get("mode") == mode]
        
        # Sort by created_at descending
        sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
        
        # Apply pagination
        return sessions[offset:offset + limit]
    
    def get_session_count(self, mode: Optional[str] = None) -> int:
        """Get total number of sessions."""
        index = self._read_index()
        sessions = list(index.get("sessions", {}).values())
        if mode:
            sessions = [s for s in sessions if s.get("mode") == mode]
        return len(sessions)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        session_path = self.storage_dir / f"{session_id}.json"
        
        if session_path.exists():
            session_path.unlink()
            
            # Update index
            index = self._read_index()
            if session_id in index.get("sessions", {}):
                del index["sessions"][session_id]
                self._write_index(index)
            
            return True
        
        return False
    
    def export_session(self, session_id: str) -> Optional[str]:
        """
        Export a session as a JSON string for download.
        
        Args:
            session_id: Session identifier
            
        Returns:
            JSON string or None if not found
        """
        session = self.load_session(session_id)
        if session:
            return json.dumps(session, indent=2, default=str)
        return None
    
    def import_session(self, json_data: str) -> Optional[str]:
        """
        Import a session from JSON string.
        
        Args:
            json_data: JSON string of session record
            
        Returns:
            Session ID if successful, None if failed
        """
        try:
            session_record = json.loads(json_data)
            session_id = session_record.get("session_id")
            
            if not session_id:
                # Generate new ID if missing
                session_id = hashlib.sha256(json_data.encode()).hexdigest()[:12]
                session_record["session_id"] = session_id
            
            # Mark as imported
            session_record["metadata"] = session_record.get("metadata", {})
            session_record["metadata"]["imported"] = True
            session_record["metadata"]["imported_at"] = datetime.utcnow().isoformat() + "Z"
            
            # Save to storage
            session_data = session_record.get("data", {})
            self.save_session(session_id, session_data, session_record.get("metadata"))
            
            return session_id
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Import failed: {e}")
            return None
    
    def get_historical_comparison(
        self,
        current_session_id: str,
        metric_key: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get comparison data for a metric across historical sessions.
        
        Args:
            current_session_id: Current session to compare
            metric_key: Metric to compare (e.g., "variety_ratio", "sentence_count")
            
        Returns:
            Comparison data with current value, previous value, and trend
        """
        sessions = self.list_sessions(limit=10)
        
        # Filter out current session
        past_sessions = [s for s in sessions if s.get("session_id") != current_session_id]
        
        if not past_sessions:
            return None
        
        # Get current value
        current = self.load_session(current_session_id)
        if not current:
            return None
        
        current_data = current.get("data", {})
        current_value = self._extract_metric(current_data, metric_key)
        
        # Get previous session value
        prev_session = self.load_session(past_sessions[0].get("session_id"))
        if not prev_session:
            return None
        
        prev_data = prev_session.get("data", {})
        prev_value = self._extract_metric(prev_data, metric_key)
        
        # Calculate trend
        if current_value is not None and prev_value is not None:
            if current_value > prev_value:
                trend = "UP"
            elif current_value < prev_value:
                trend = "DOWN"
            else:
                trend = "STABLE"
        else:
            trend = "UNKNOWN"
        
        return {
            "current": current_value,
            "previous": prev_value,
            "trend": trend,
            "previous_session_id": past_sessions[0].get("session_id"),
            "previous_date": past_sessions[0].get("created_at"),
        }
    
    def _extract_metric(self, session_data: Dict[str, Any], metric_key: str) -> Optional[float]:
        """Extract a metric value from session data."""
        phase1 = session_data.get("phase1", {}).get("outputs", {})
        
        metric_paths = {
            "variety_ratio": ("structural_variety", "variety_ratio"),
            "sentence_count": ("sentence_count", "count"),
            "mean_tokens": ("token_volume", "mean_tokens_per_sentence"),
            "total_events": ("structural_density", "total_events"),
            "zero_count": ("zero_event_presence", "count"),
            "scope_count": ("scope_event_presence", "count"),
        }
        
        if metric_key in metric_paths:
            key1, key2 = metric_paths[metric_key]
            return phase1.get(key1, {}).get(key2)
        
        return None


# =============================================================================
# Singleton Instance
# =============================================================================

_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get or create the global session store instance."""
    global _store
    if _store is None:
        _store = SessionStore()
    return _store


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("Session Persistence Demo")
    print("=" * 50)
    
    store = get_session_store()
    
    # Create a mock session
    mock_session = {
        "phase1": {
            "outputs": {
                "sentence_count": {"count": 6},
                "structural_variety": {"variety_ratio": 0.83},
                "token_volume": {"mean_tokens_per_sentence": 9.5},
            }
        },
        "phase6": {
            "summary": {"title": "A First Glimpse: Structure in Balance"},
            "high_intent_reflection": {"epistemic_stance": "BALANCED"},
        },
        "high_intent_profile": {"epistemic_openness": 0.6},
    }
    
    # Save session
    session_id = "demo-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = store.save_session(session_id, mock_session, {"mode": "STORY"})
    print(f"Saved session: {session_id}")
    print(f"Path: {path}")
    
    # List sessions
    sessions = store.list_sessions()
    print(f"\nTotal sessions: {len(sessions)}")
    for s in sessions[:3]:
        print(f"  - {s['session_id']}: {s['title']} ({s['created_at'][:10]})")
    
    # Export
    exported = store.export_session(session_id)
    print(f"\nExported JSON length: {len(exported)} chars")
    
    print("\n✅ Session persistence working")
