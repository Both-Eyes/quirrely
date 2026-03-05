#!/usr/bin/env python3
"""
STRETCH Observer — Meta Orchestrator Integration
Version: 1.0.0
Date: 2026-02-17

Observes STRETCH exercise lifecycle events and emits signals
to the Meta Orchestrator for parameter optimization.

Event Types Tracked:
- eligibility_changed
- cta_shown / cta_clicked / cta_dismissed
- exercise_started / exercise_completed / exercise_abandoned
- cycle_completed / input_submitted
- word_accumulated
- paste_attempted
- milestone_achieved
- trial_expiry_warning

Signals Generated:
- engagement_opportunity
- high_intent
- commitment
- trial_engagement
- achievement
- conversion_ready  (strength 0.95 on trial completion)
- churn_risk
- progress
- content_created
- friction
"""

from datetime import datetime
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("quirrely.meta.stretch_observer")


class StretchObserver:
    """
    Observes STRETCH exercise events and generates learning signals
    for the Meta Orchestrator.
    """

    SIGNAL_WEIGHTS = {
        "exercise_completed": {"signal": "conversion_ready", "strength": 0.95},
        "exercise_started": {"signal": "high_intent", "strength": 0.75},
        "cycle_completed": {"signal": "commitment", "strength": 0.60},
        "cta_clicked": {"signal": "engagement_opportunity", "strength": 0.50},
        "cta_dismissed": {"signal": "churn_risk", "strength": 0.35},
        "paste_attempted": {"signal": "friction", "strength": 0.40},
        "milestone_achieved": {"signal": "achievement", "strength": 0.80},
        "word_accumulated": {"signal": "progress", "strength": 0.20},
        "trial_expiry_warning": {"signal": "trial_engagement", "strength": 0.70},
        "input_submitted": {"signal": "content_created", "strength": 0.30},
    }

    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self._event_log = []
        logger.info("StretchObserver initialized")

    def observe(self, event_type: str, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Process a STRETCH event and generate a signal if applicable.

        Args:
            event_type: One of the tracked event types
            data: Event payload (user_id, tier, exercise_id, etc.)

        Returns:
            Signal dict if signal generated, None otherwise
        """
        timestamp = datetime.utcnow().isoformat()

        event = {
            "type": event_type,
            "data": data,
            "timestamp": timestamp
        }
        self._event_log.append(event)

        signal_config = self.SIGNAL_WEIGHTS.get(event_type)
        if not signal_config:
            logger.debug(f"No signal mapping for event: {event_type}")
            return None

        signal = {
            "signal": signal_config["signal"],
            "strength": signal_config["strength"],
            "source": "stretch_observer",
            "event_type": event_type,
            "user_id": data.get("user_id"),
            "tier": data.get("tier", "free"),
            "timestamp": timestamp,
            "metadata": data
        }

        # Boost conversion_ready signal for trial users
        if signal["signal"] == "conversion_ready" and data.get("tier") == "trial":
            signal["strength"] = min(1.0, signal["strength"] * 1.1)
            signal["priority"] = "urgent"

        # Emit to orchestrator if connected
        if self.orchestrator:
            try:
                self.orchestrator.receive_signal(signal)
            except Exception as e:
                logger.error(f"Failed to emit signal to orchestrator: {e}")

        logger.info(
            f"Signal emitted: {signal['signal']} "
            f"(strength={signal['strength']:.2f}) "
            f"from event={event_type} "
            f"user={data.get('user_id', 'anon')}"
        )

        return signal

    def on_eligibility_changed(self, user_id: str, tier: str, eligible: bool):
        """User became eligible for STRETCH."""
        return self.observe("eligibility_changed", {
            "user_id": user_id,
            "tier": tier,
            "eligible": eligible
        })

    def on_cta_shown(self, user_id: str, tier: str, variant: str):
        """STRETCH CTA displayed to user."""
        return self.observe("cta_shown", {
            "user_id": user_id,
            "tier": tier,
            "variant": variant
        })

    def on_cta_clicked(self, user_id: str, tier: str, variant: str):
        """User clicked STRETCH CTA."""
        return self.observe("cta_clicked", {
            "user_id": user_id,
            "tier": tier,
            "variant": variant
        })

    def on_exercise_started(self, user_id: str, tier: str, exercise_id: str,
                             profile_from: str, profile_to: str):
        """User started a STRETCH exercise."""
        return self.observe("exercise_started", {
            "user_id": user_id,
            "tier": tier,
            "exercise_id": exercise_id,
            "profile_from": profile_from,
            "profile_to": profile_to
        })

    def on_exercise_completed(self, user_id: str, tier: str, exercise_id: str,
                               total_words: int, duration_seconds: int):
        """User completed a full STRETCH exercise (5 cycles)."""
        return self.observe("exercise_completed", {
            "user_id": user_id,
            "tier": tier,
            "exercise_id": exercise_id,
            "total_words": total_words,
            "duration_seconds": duration_seconds
        })

    def on_exercise_abandoned(self, user_id: str, tier: str, exercise_id: str,
                               cycles_completed: int):
        """User abandoned a STRETCH exercise mid-way."""
        return self.observe("exercise_abandoned", {
            "user_id": user_id,
            "tier": tier,
            "exercise_id": exercise_id,
            "cycles_completed": cycles_completed
        })

    def on_cycle_completed(self, user_id: str, exercise_id: str, cycle_number: int,
                            words_written: int):
        """User completed one cycle (3 prompts) of a STRETCH."""
        return self.observe("cycle_completed", {
            "user_id": user_id,
            "exercise_id": exercise_id,
            "cycle_number": cycle_number,
            "words_written": words_written
        })

    def on_paste_attempted(self, user_id: str, exercise_id: str,
                            method: str, blocked: bool = True):
        """User attempted to paste text (blocked by KeystrokeValidator)."""
        return self.observe("paste_attempted", {
            "user_id": user_id,
            "exercise_id": exercise_id,
            "method": method,
            "blocked": blocked
        })

    def on_milestone_achieved(self, user_id: str, milestone: str, tier: str):
        """User hit a STRETCH milestone (first_stretch, week_streak, etc.)."""
        return self.observe("milestone_achieved", {
            "user_id": user_id,
            "milestone": milestone,
            "tier": tier
        })

    def on_trial_expiry_warning(self, user_id: str, days_remaining: int,
                                 stretch_in_progress: bool):
        """Trial user approaching expiry with/without STRETCH in progress."""
        return self.observe("trial_expiry_warning", {
            "user_id": user_id,
            "days_remaining": days_remaining,
            "stretch_in_progress": stretch_in_progress
        })

    def get_event_log(self) -> list:
        """Return the event log for debugging."""
        return self._event_log.copy()

    def get_stats(self) -> Dict[str, Any]:
        """Return observer statistics."""
        event_counts = {}
        for event in self._event_log:
            t = event["type"]
            event_counts[t] = event_counts.get(t, 0) + 1
        return {
            "total_events": len(self._event_log),
            "event_counts": event_counts
        }
