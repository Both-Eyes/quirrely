#!/usr/bin/env python3
"""
LNCP META: EVENT COLLECTOR v5.1
Meta-side event reader that processes the file-based queue.

Usage:
    from lncp.meta.events import EventCollector
    
    collector = EventCollector()
    
    # Process new events
    events = collector.collect()
    for event in events:
        process(event)
    
    # Or with callback
    collector.collect_with_callback(lambda e: print(e.event_type))
"""

import os
import json
import glob
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Callable, Generator
from dataclasses import dataclass

from .schema import AppEvent, EventType, EventCategory


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_EVENTS_DIR = os.environ.get("LNCP_EVENTS_DIR", "/var/lib/lncp/events")
PROCESSED_DIR = "processed"
RETENTION_DAYS = 90


# ═══════════════════════════════════════════════════════════════════════════
# EVENT COLLECTOR
# ═══════════════════════════════════════════════════════════════════════════

class EventCollector:
    """
    Collects events from the file-based queue.
    
    Features:
    - Reads event files in order
    - Moves processed files to archive
    - Handles corrupt files gracefully
    - Supports filtering and streaming
    """
    
    def __init__(
        self,
        events_dir: str = DEFAULT_EVENTS_DIR,
        retention_days: int = RETENTION_DAYS,
    ):
        self.events_dir = events_dir
        self.processed_dir = os.path.join(events_dir, PROCESSED_DIR)
        self.retention_days = retention_days
        
        # Ensure directories exist
        Path(events_dir).mkdir(parents=True, exist_ok=True)
        Path(self.processed_dir).mkdir(parents=True, exist_ok=True)
        
        # Metrics
        self._files_processed = 0
        self._events_collected = 0
        self._errors = 0
    
    # ─────────────────────────────────────────────────────────────────────
    # COLLECTION
    # ─────────────────────────────────────────────────────────────────────
    
    def collect(self, limit: int = 10000) -> List[AppEvent]:
        """
        Collect all pending events.
        
        Returns list of events, moves processed files to archive.
        """
        events = []
        
        for filepath in self._get_pending_files():
            file_events = self._read_file(filepath)
            events.extend(file_events)
            self._mark_processed(filepath)
            
            if len(events) >= limit:
                break
        
        return events
    
    def collect_stream(self) -> Generator[AppEvent, None, None]:
        """
        Stream events one at a time.
        
        More memory efficient for large volumes.
        """
        for filepath in self._get_pending_files():
            for event in self._read_file_stream(filepath):
                yield event
            self._mark_processed(filepath)
    
    def collect_with_callback(
        self,
        callback: Callable[[AppEvent], None],
        filter_types: Optional[List[EventType]] = None,
    ) -> int:
        """
        Collect events and call callback for each.
        
        Returns count of events processed.
        """
        count = 0
        
        for event in self.collect_stream():
            if filter_types is None or event.event_type in filter_types:
                try:
                    callback(event)
                    count += 1
                except Exception as e:
                    self._errors += 1
        
        return count
    
    def peek(self, limit: int = 10) -> List[AppEvent]:
        """
        Peek at pending events without marking as processed.
        """
        events = []
        
        for filepath in self._get_pending_files():
            file_events = self._read_file(filepath)
            events.extend(file_events)
            
            if len(events) >= limit:
                break
        
        return events[:limit]
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERYING PROCESSED EVENTS
    # ─────────────────────────────────────────────────────────────────────
    
    def query_historical(
        self,
        start_date: datetime,
        end_date: datetime,
        event_types: Optional[List[EventType]] = None,
        user_id: Optional[str] = None,
    ) -> List[AppEvent]:
        """
        Query historical (processed) events.
        """
        events = []
        
        # Find files in date range
        for filepath in sorted(glob.glob(os.path.join(self.processed_dir, "*.jsonl"))):
            # Check file date from filename
            filename = os.path.basename(filepath)
            try:
                file_date_str = filename.split("_")[1]
                file_date = datetime.strptime(file_date_str, "%Y%m%d")
                
                if file_date.date() < start_date.date() or file_date.date() > end_date.date():
                    continue
            except:
                continue
            
            # Read and filter
            for event in self._read_file_stream(filepath):
                # Date filter
                if event.timestamp < start_date or event.timestamp > end_date:
                    continue
                
                # Type filter
                if event_types and event.event_type not in event_types:
                    continue
                
                # User filter
                if user_id and event.user_id != user_id:
                    continue
                
                events.append(event)
        
        return events
    
    # ─────────────────────────────────────────────────────────────────────
    # FILE HANDLING
    # ─────────────────────────────────────────────────────────────────────
    
    def _get_pending_files(self) -> List[str]:
        """Get list of pending event files, sorted by timestamp."""
        pattern = os.path.join(self.events_dir, "events_*.jsonl")
        files = glob.glob(pattern)
        return sorted(files)
    
    def _read_file(self, filepath: str) -> List[AppEvent]:
        """Read all events from a file."""
        events = []
        for event in self._read_file_stream(filepath):
            events.append(event)
        return events
    
    def _read_file_stream(self, filepath: str) -> Generator[AppEvent, None, None]:
        """Stream events from a file."""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        event = AppEvent.from_json(line)
                        self._events_collected += 1
                        yield event
                    except Exception as e:
                        self._errors += 1
                        continue
                        
        except Exception as e:
            self._errors += 1
    
    def _mark_processed(self, filepath: str):
        """Move file to processed directory."""
        try:
            filename = os.path.basename(filepath)
            dest = os.path.join(self.processed_dir, filename)
            shutil.move(filepath, dest)
            self._files_processed += 1
        except Exception as e:
            self._errors += 1
    
    # ─────────────────────────────────────────────────────────────────────
    # MAINTENANCE
    # ─────────────────────────────────────────────────────────────────────
    
    def cleanup_old_files(self) -> int:
        """Remove processed files older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        removed = 0
        
        for filepath in glob.glob(os.path.join(self.processed_dir, "*.jsonl")):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime < cutoff:
                    os.remove(filepath)
                    removed += 1
            except:
                pass
        
        return removed
    
    def get_queue_stats(self) -> Dict:
        """Get statistics about the event queue."""
        pending_files = self._get_pending_files()
        processed_files = glob.glob(os.path.join(self.processed_dir, "*.jsonl"))
        
        # Count pending events
        pending_events = 0
        for filepath in pending_files:
            try:
                with open(filepath, 'r') as f:
                    pending_events += sum(1 for _ in f)
            except:
                pass
        
        return {
            "pending_files": len(pending_files),
            "pending_events": pending_events,
            "processed_files": len(processed_files),
            "files_processed_total": self._files_processed,
            "events_collected_total": self._events_collected,
            "errors": self._errors,
        }


# ═══════════════════════════════════════════════════════════════════════════
# EVENT AGGREGATOR
# ═══════════════════════════════════════════════════════════════════════════

class EventAggregator:
    """
    Aggregates events into metrics.
    
    Used by observers to convert raw events into signals.
    """
    
    def __init__(self):
        self.events: List[AppEvent] = []
    
    def add(self, event: AppEvent):
        """Add event to aggregation."""
        self.events.append(event)
    
    def add_all(self, events: List[AppEvent]):
        """Add multiple events."""
        self.events.extend(events)
    
    def clear(self):
        """Clear all events."""
        self.events.clear()
    
    # ─────────────────────────────────────────────────────────────────────
    # AGGREGATIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def count_by_type(self) -> Dict[EventType, int]:
        """Count events by type."""
        counts = {}
        for event in self.events:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1
        return counts
    
    def count_by_category(self) -> Dict[EventCategory, int]:
        """Count events by category."""
        counts = {}
        for event in self.events:
            cat = event.event_type.category
            counts[cat] = counts.get(cat, 0) + 1
        return counts
    
    def count_by_user(self) -> Dict[str, int]:
        """Count events by user."""
        counts = {}
        for event in self.events:
            if event.user_id:
                counts[event.user_id] = counts.get(event.user_id, 0) + 1
        return counts
    
    def unique_users(self) -> int:
        """Count unique users."""
        return len(set(e.user_id for e in self.events if e.user_id))
    
    def unique_visitors(self) -> int:
        """Count unique visitors."""
        return len(set(e.visitor_id for e in self.events))
    
    def filter_by_type(self, event_types: List[EventType]) -> List[AppEvent]:
        """Filter events by type."""
        return [e for e in self.events if e.event_type in event_types]
    
    def filter_by_user(self, user_id: str) -> List[AppEvent]:
        """Filter events by user."""
        return [e for e in self.events if e.user_id == user_id]
    
    def filter_by_time(self, start: datetime, end: datetime) -> List[AppEvent]:
        """Filter events by time range."""
        return [e for e in self.events if start <= e.timestamp <= end]
    
    def get_user_journey(self, user_id: str) -> List[AppEvent]:
        """Get all events for a user, sorted by time."""
        events = [e for e in self.events if e.user_id == user_id]
        return sorted(events, key=lambda e: e.timestamp)
    
    def get_session_events(self, session_id: str) -> List[AppEvent]:
        """Get all events in a session."""
        events = [e for e in self.events if e.session_id == session_id]
        return sorted(events, key=lambda e: e.timestamp)


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_event_collector: Optional[EventCollector] = None

def get_event_collector() -> EventCollector:
    """Get the global event collector instance."""
    global _event_collector
    if _event_collector is None:
        _event_collector = EventCollector()
    return _event_collector


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "EventCollector",
    "EventAggregator",
    "get_event_collector",
]
