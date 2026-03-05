#!/usr/bin/env python3
"""
LNCP Tracking API v1.0
Receives tracking events from the frontend and feeds them into the optimization loop.

Endpoints:
- POST /api/track - Receive batch of tracking events
- GET /api/track/status - Get tracking status

This bridges the frontend tracker to the LNCP Meta blog components.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import sys

# Add LNCP to path
sys.path.insert(0, '/mnt/user-data/outputs/lncp-web-app')

from lncp.meta.blog import (
    get_blog_tracker,
    get_cta_tracker,
    get_experiment_manager,
    TrafficSource,
    DeviceType,
    CTAPlacement,
)


# ═══════════════════════════════════════════════════════════════════════════
# EVENT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class TrackingEventType(str, Enum):
    PAGE_VIEW = "page_view"
    SCROLL_DEPTH = "scroll_depth"
    ENGAGEMENT = "engagement"
    CTA_IMPRESSION = "cta_impression"
    CTA_CLICK = "cta_click"
    CONVERSION = "conversion"
    EXPERIMENT_ASSIGNMENT = "experiment_assignment"


# ═══════════════════════════════════════════════════════════════════════════
# EVENT PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════

class TrackingEventProcessor:
    """
    Processes tracking events from the frontend and updates LNCP components.
    """
    
    def __init__(self):
        self.blog_tracker = get_blog_tracker()
        self.cta_tracker = get_cta_tracker()
        self.experiment_manager = get_experiment_manager()
        
        # Stats
        self.events_processed = 0
        self.events_by_type: Dict[str, int] = {}
        self.errors: List[Dict] = []
    
    def process_batch(self, events: List[Dict], meta: Dict = None) -> Dict:
        """Process a batch of tracking events."""
        results = {
            "processed": 0,
            "errors": 0,
            "by_type": {},
        }
        
        for event in events:
            try:
                event_type = event.get("type")
                
                if event_type == TrackingEventType.PAGE_VIEW.value:
                    self._process_page_view(event)
                elif event_type == TrackingEventType.SCROLL_DEPTH.value:
                    self._process_scroll_depth(event)
                elif event_type == TrackingEventType.ENGAGEMENT.value:
                    self._process_engagement(event)
                elif event_type == TrackingEventType.CTA_IMPRESSION.value:
                    self._process_cta_impression(event)
                elif event_type == TrackingEventType.CTA_CLICK.value:
                    self._process_cta_click(event)
                elif event_type == TrackingEventType.CONVERSION.value:
                    self._process_conversion(event)
                elif event_type == TrackingEventType.EXPERIMENT_ASSIGNMENT.value:
                    self._process_experiment_assignment(event)
                else:
                    # Unknown event type, skip
                    continue
                
                results["processed"] += 1
                results["by_type"][event_type] = results["by_type"].get(event_type, 0) + 1
                
                self.events_processed += 1
                self.events_by_type[event_type] = self.events_by_type.get(event_type, 0) + 1
                
            except Exception as e:
                results["errors"] += 1
                self.errors.append({
                    "event": event,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                })
        
        return results
    
    def _map_traffic_source(self, source: str) -> TrafficSource:
        """Map frontend source string to TrafficSource enum."""
        mapping = {
            "organic": TrafficSource.ORGANIC,
            "direct": TrafficSource.DIRECT,
            "referral": TrafficSource.REFERRAL,
            "social": TrafficSource.SOCIAL,
            "email": TrafficSource.EMAIL,
            "paid": TrafficSource.PAID,
            "internal": TrafficSource.INTERNAL,
        }
        return mapping.get(source.lower(), TrafficSource.DIRECT)
    
    def _map_device_type(self, device: str) -> DeviceType:
        """Map frontend device string to DeviceType enum."""
        mapping = {
            "desktop": DeviceType.DESKTOP,
            "mobile": DeviceType.MOBILE,
            "tablet": DeviceType.TABLET,
        }
        return mapping.get(device.lower(), DeviceType.DESKTOP)
    
    def _map_cta_placement(self, placement: str) -> CTAPlacement:
        """Map frontend placement string to CTAPlacement enum."""
        mapping = {
            "after_intro": CTAPlacement.AFTER_INTRO,
            "floating": CTAPlacement.FLOATING,
            "end": CTAPlacement.END_OF_CONTENT,
            "multiple": CTAPlacement.MULTIPLE,
        }
        return mapping.get(placement.lower(), CTAPlacement.AFTER_INTRO)
    
    # ─────────────────────────────────────────────────────────────────────
    # EVENT HANDLERS
    # ─────────────────────────────────────────────────────────────────────
    
    def _process_page_view(self, event: Dict):
        """Process a page view event."""
        view = self.blog_tracker.track_page_view(
            page_url=event.get("url", event.get("pageUrl", "/")),
            session_id=event.get("sessionId", "unknown"),
            visitor_id=event.get("visitorId", "unknown"),
            source=self._map_traffic_source(event.get("source", "direct")),
            referrer=event.get("referrer"),
            device=self._map_device_type(event.get("device", "desktop")),
            country=event.get("country"),
            profile_style=event.get("profileStyle"),
            profile_certitude=event.get("profileCertitude"),
        )
        
        # Store view ID mapping for later events
        # In production, this would use Redis or similar
        self._view_mapping = getattr(self, '_view_mapping', {})
        self._view_mapping[event.get("viewId")] = view.view_id
    
    def _process_scroll_depth(self, event: Dict):
        """Process a scroll depth event."""
        # Get mapped view ID
        view_id = self._get_mapped_view_id(event.get("viewId"))
        if not view_id:
            return
        
        # Update engagement
        self.blog_tracker.track_engagement(
            view_id=view_id,
            time_on_page_seconds=event.get("timeOnPage", 0),
            scroll_depth_percent=event.get("depth", 0),
        )
    
    def _process_engagement(self, event: Dict):
        """Process an engagement heartbeat event."""
        view_id = self._get_mapped_view_id(event.get("viewId"))
        if not view_id:
            return
        
        self.blog_tracker.track_engagement(
            view_id=view_id,
            time_on_page_seconds=event.get("timeOnPage", 0),
            scroll_depth_percent=event.get("scrollDepth", 0),
        )
    
    def _process_cta_impression(self, event: Dict):
        """Process a CTA impression event."""
        view_id = self._get_mapped_view_id(event.get("viewId"))
        if not view_id:
            return
        
        self.cta_tracker.track_impression(
            page_url=event.get("pageUrl", "/"),
            view_id=view_id,
            session_id=event.get("sessionId", "unknown"),
            visitor_id=event.get("visitorId", "unknown"),
            variant_id=event.get("variantId", "default"),
            placement=self._map_cta_placement(event.get("placement", "after_intro")),
            position_index=event.get("position", 0),
            scroll_depth=event.get("scrollDepth", 0),
            time_on_page=event.get("timeOnPage", 0),
        )
        
        # Also track in experiment manager if applicable
        experiment_id = event.get("experimentId")
        if experiment_id:
            self.experiment_manager.track_impression(
                experiment_id=experiment_id,
                variant_id=event.get("variantId", "default"),
            )
    
    def _process_cta_click(self, event: Dict):
        """Process a CTA click event."""
        view_id = self._get_mapped_view_id(event.get("viewId"))
        if not view_id:
            return
        
        self.cta_tracker.track_click(
            page_url=event.get("pageUrl", "/"),
            view_id=view_id,
            session_id=event.get("sessionId", "unknown"),
            visitor_id=event.get("visitorId", "unknown"),
            variant_id=event.get("variantId", "default"),
            placement=self._map_cta_placement(event.get("placement", "after_intro")),
            position_index=event.get("position", 0),
            scroll_depth=event.get("scrollDepth", 0),
            time_on_page=event.get("timeOnPage", 0),
        )
        
        # Also track in experiment manager if applicable
        experiment_id = event.get("experimentId")
        if experiment_id:
            self.experiment_manager.track_click(
                experiment_id=experiment_id,
                variant_id=event.get("variantId", "default"),
            )
    
    def _process_conversion(self, event: Dict):
        """Process a conversion event."""
        view_id = self._get_mapped_view_id(event.get("viewId"))
        if not view_id:
            return
        
        # Track signup in blog tracker
        self.blog_tracker.track_signup(view_id)
        
        # Track conversion in CTA tracker if we have variant info
        variant_id = event.get("variantId")
        if variant_id:
            self.cta_tracker.track_conversion(
                page_url=event.get("pageUrl", "/"),
                view_id=view_id,
                session_id=event.get("sessionId", "unknown"),
                visitor_id=event.get("visitorId", "unknown"),
                variant_id=variant_id,
                placement=self._map_cta_placement(event.get("placement", "after_intro")),
            )
        
        # Track in experiment manager if applicable
        experiment_id = event.get("experimentId")
        if experiment_id and variant_id:
            self.experiment_manager.track_conversion(
                experiment_id=experiment_id,
                variant_id=variant_id,
            )
    
    def _process_experiment_assignment(self, event: Dict):
        """Process an experiment assignment event (for logging)."""
        # This is mainly for analytics/debugging
        # The actual assignment happens on the frontend
        pass
    
    def _get_mapped_view_id(self, frontend_view_id: str) -> Optional[str]:
        """Get the backend view ID from the frontend view ID."""
        if not frontend_view_id:
            return None
        
        mapping = getattr(self, '_view_mapping', {})
        return mapping.get(frontend_view_id)
    
    # ─────────────────────────────────────────────────────────────────────
    # STATUS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_status(self) -> Dict:
        """Get processor status."""
        return {
            "events_processed": self.events_processed,
            "events_by_type": self.events_by_type,
            "recent_errors": self.errors[-10:],
            "blog_tracker": self.blog_tracker.get_summary(),
            "cta_tracker": self.cta_tracker.get_summary(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# API HANDLER (for Flask/FastAPI integration)
# ═══════════════════════════════════════════════════════════════════════════

# Global processor instance
_processor: Optional[TrackingEventProcessor] = None

def get_processor() -> TrackingEventProcessor:
    global _processor
    if _processor is None:
        _processor = TrackingEventProcessor()
    return _processor


def handle_track_request(request_body: Dict) -> Dict:
    """
    Handle a tracking API request.
    
    Expected request body:
    {
        "events": [...],
        "meta": {
            "trackerVersion": "1.0",
            "userAgent": "..."
        }
    }
    """
    processor = get_processor()
    
    events = request_body.get("events", [])
    meta = request_body.get("meta", {})
    
    result = processor.process_batch(events, meta)
    
    return {
        "success": True,
        "result": result,
    }


def handle_status_request() -> Dict:
    """Handle a tracking status request."""
    processor = get_processor()
    return processor.get_status()


# ═══════════════════════════════════════════════════════════════════════════
# FLASK EXAMPLE (if using Flask)
# ═══════════════════════════════════════════════════════════════════════════

"""
from flask import Flask, request, jsonify
from tracking_api import handle_track_request, handle_status_request

app = Flask(__name__)

@app.route('/api/track', methods=['POST'])
def track():
    result = handle_track_request(request.json)
    return jsonify(result)

@app.route('/api/track/status', methods=['GET'])
def track_status():
    status = handle_status_request()
    return jsonify(status)
"""


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "TrackingEventType",
    "TrackingEventProcessor",
    "get_processor",
    "handle_track_request",
    "handle_status_request",
]
