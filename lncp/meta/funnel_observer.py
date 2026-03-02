#!/usr/bin/env python3
"""
LNCP META: FUNNEL OBSERVER v1.0.0
Tracks the full user acquisition and conversion funnel.

This observer monitors:
- Landing → Analysis → Save → Signup conversion rates
- Free → Trial → Pro → Authority tier progression
- Drop-off points across the funnel
- STRETCH completion → upgrade signal strength
- Cohort conversion velocity

It provides:
- Real-time funnel metrics per stage
- Conversion rate per tier transition
- Funnel health scoring
- Optimization proposals for underperforming stages
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# FUNNEL ENUMS
# ═══════════════════════════════════════════════════════════════════════════

class FunnelStage(str, Enum):
    """Stages in the Quirrely acquisition funnel."""
    LANDING         = "landing"
    FIRST_ANALYSIS  = "first_analysis"
    SAVE_PROMPT     = "save_prompt"
    SIGNUP          = "signup"
    TRIAL_ACTIVATED = "trial_activated"
    STRETCH_STARTED = "stretch_started"
    STRETCH_DONE    = "stretch_completed"
    PRO_UPGRADE     = "pro_upgrade"
    AUTHORITY       = "authority"


class FunnelEvent(str, Enum):
    """Events that advance or indicate drop-off in the funnel."""
    PAGE_LOAD            = "page_load"
    ANALYSIS_RUN         = "analysis_run"
    RESULT_VIEWED        = "result_viewed"
    SHARE_CLICKED        = "share_clicked"
    SAVE_CLICKED         = "save_clicked"
    SIGNUP_STARTED       = "signup_started"
    SIGNUP_COMPLETED     = "signup_completed"
    TRIAL_CTA_SHOWN      = "trial_cta_shown"
    TRIAL_CTA_CLICKED    = "trial_cta_clicked"
    STRETCH_CTA_SHOWN    = "stretch_cta_shown"
    STRETCH_CTA_CLICKED  = "stretch_cta_clicked"
    STRETCH_COMPLETED    = "stretch_completed"
    UPGRADE_CTA_SHOWN    = "upgrade_cta_shown"
    UPGRADE_CLICKED      = "upgrade_clicked"
    PAYMENT_COMPLETED    = "payment_completed"


# ═══════════════════════════════════════════════════════════════════════════
# FUNNEL METRICS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class StageMetrics:
    """Metrics for a single funnel stage."""
    stage: FunnelStage
    entered: int = 0
    exited: int = 0
    converted: int = 0
    avg_time_seconds: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    @property
    def conversion_rate(self) -> float:
        if self.entered == 0:
            return 0.0
        return round(self.converted / self.entered * 100, 2)

    @property
    def drop_off_rate(self) -> float:
        if self.entered == 0:
            return 0.0
        return round((self.entered - self.converted) / self.entered * 100, 2)


@dataclass
class FunnelSnapshot:
    """Full funnel state snapshot."""
    timestamp: datetime
    stages: Dict[str, StageMetrics]
    overall_conversion: float          # landing → pro
    stretch_conversion_lift: float     # extra conversion from STRETCH completions
    weekly_cohort_size: int
    health_score: float                # 0–100


# ═══════════════════════════════════════════════════════════════════════════
# FUNNEL OBSERVER
# ═══════════════════════════════════════════════════════════════════════════

class FunnelObserver:
    """
    Observes and analyses the Quirrely conversion funnel.
    Registered with MetaOrchestrator as 'funnel_observer'.
    """

    OBSERVER_ID = "funnel_observer"
    VERSION     = "1.0.0"

    # Benchmark conversion rates (target)
    BENCHMARKS: Dict[str, float] = {
        "landing_to_analysis":    60.0,   # 60% of visitors run at least 1 analysis
        "analysis_to_signup":     25.0,   # 25% of analyzers sign up
        "signup_to_trial":        80.0,   # 80% of signups activate trial
        "trial_to_stretch":       45.0,   # 45% of trial users attempt STRETCH
        "stretch_to_upgrade":     65.0,   # 65% of STRETCH completers upgrade
        "trial_to_pro":           18.0,   # 18% overall trial → Pro
        "pro_to_authority":        8.0,   # 8% of Pro → Authority
    }

    def __init__(self):
        self._stages: Dict[FunnelStage, StageMetrics] = {
            s: StageMetrics(stage=s) for s in FunnelStage
        }
        self._event_log: List[Dict[str, Any]] = []
        self._proposals: List[Dict[str, Any]] = []
        self._stretch_conversion_lift: float = 0.0

    # ── PUBLIC INTERFACE ────────────────────────────────────────────────────

    def on_event(self, event: FunnelEvent, user_id: str,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """Process a funnel event."""
        ts = datetime.utcnow()
        self._event_log.append({
            "event": event.value,
            "user_id": user_id,
            "ts": ts.isoformat(),
            "meta": metadata or {}
        })
        self._advance_stages(event)
        self._check_health()

    def on_stretch_completed(self, user_id: str, tier: str,
                              profile_from: str, profile_to: str) -> Dict[str, Any]:
        """
        Called by stretch_observer when a STRETCH exercise is completed.
        Calculates and emits the conversion signal strength.
        """
        stage = self._stages[FunnelStage.STRETCH_DONE]
        stage.converted += 1

        # Compute conversion signal: stronger if trial tier (highest intent)
        base_strength = 0.75
        tier_boost = 0.20 if tier == "trial" else 0.10
        signal_strength = min(base_strength + tier_boost, 1.0)

        self._stretch_conversion_lift += 0.5   # MRR impact per completion

        signal = {
            "type":             "conversion_ready",
            "user_id":          user_id,
            "source":           "stretch_completion",
            "signal_strength":  round(signal_strength, 3),
            "priority":         "urgent" if tier == "trial" else "high",
            "tier_current":     tier,
            "profile_from":     profile_from,
            "profile_to":       profile_to,
            "recommended_cta":  "pro_upgrade" if tier == "trial" else "authority_upgrade",
            "timestamp":        datetime.utcnow().isoformat(),
        }
        return signal

    def get_snapshot(self) -> FunnelSnapshot:
        """Return current funnel state snapshot."""
        landing  = self._stages[FunnelStage.LANDING].entered or 1
        pro      = self._stages[FunnelStage.PRO_UPGRADE].converted

        return FunnelSnapshot(
            timestamp=datetime.utcnow(),
            stages={s.name: self._stages[s] for s in FunnelStage},
            overall_conversion=round(pro / landing * 100, 2),
            stretch_conversion_lift=self._stretch_conversion_lift,
            weekly_cohort_size=landing,
            health_score=self._compute_health(),
        )

    def get_proposals(self) -> List[Dict[str, Any]]:
        """Return pending optimisation proposals."""
        return list(self._proposals)

    def get_status(self) -> Dict[str, Any]:
        """Status summary for admin dashboard."""
        snap = self.get_snapshot()
        return {
            "observer":           self.OBSERVER_ID,
            "version":            self.VERSION,
            "health_score":       snap.health_score,
            "overall_conversion": snap.overall_conversion,
            "stretch_lift":       snap.stretch_conversion_lift,
            "proposals_pending":  len(self._proposals),
            "events_processed":   len(self._event_log),
        }

    # ── PRIVATE ─────────────────────────────────────────────────────────────

    def _advance_stages(self, event: FunnelEvent) -> None:
        """Update stage counters based on event."""
        mapping: Dict[FunnelEvent, FunnelStage] = {
            FunnelEvent.PAGE_LOAD:          FunnelStage.LANDING,
            FunnelEvent.ANALYSIS_RUN:       FunnelStage.FIRST_ANALYSIS,
            FunnelEvent.SAVE_CLICKED:       FunnelStage.SAVE_PROMPT,
            FunnelEvent.SIGNUP_COMPLETED:   FunnelStage.SIGNUP,
            FunnelEvent.TRIAL_CTA_CLICKED:  FunnelStage.TRIAL_ACTIVATED,
            FunnelEvent.STRETCH_CTA_CLICKED:FunnelStage.STRETCH_STARTED,
            FunnelEvent.STRETCH_COMPLETED:  FunnelStage.STRETCH_DONE,
            FunnelEvent.PAYMENT_COMPLETED:  FunnelStage.PRO_UPGRADE,
        }
        stage = mapping.get(event)
        if stage:
            self._stages[stage].entered += 1
            self._stages[stage].converted += 1

    def _check_health(self) -> None:
        """Generate proposals when metrics fall below benchmark."""
        for key, benchmark in self.BENCHMARKS.items():
            actual = self._get_rate(key)
            if actual > 0 and actual < benchmark * 0.8:   # >20% below benchmark
                self._proposals.append({
                    "type":      "funnel_underperformance",
                    "stage":     key,
                    "actual":    actual,
                    "benchmark": benchmark,
                    "gap":       round(benchmark - actual, 1),
                    "priority":  "high" if actual < benchmark * 0.6 else "medium",
                    "ts":        datetime.utcnow().isoformat(),
                })

    def _get_rate(self, key: str) -> float:
        """Compute named conversion rate."""
        rates = {
            "landing_to_analysis": self._rate(FunnelStage.FIRST_ANALYSIS, FunnelStage.LANDING),
            "analysis_to_signup":  self._rate(FunnelStage.SIGNUP, FunnelStage.FIRST_ANALYSIS),
            "signup_to_trial":     self._rate(FunnelStage.TRIAL_ACTIVATED, FunnelStage.SIGNUP),
            "trial_to_stretch":    self._rate(FunnelStage.STRETCH_STARTED, FunnelStage.TRIAL_ACTIVATED),
            "stretch_to_upgrade":  self._rate(FunnelStage.PRO_UPGRADE, FunnelStage.STRETCH_DONE),
            "trial_to_pro":        self._rate(FunnelStage.PRO_UPGRADE, FunnelStage.TRIAL_ACTIVATED),
            "pro_to_authority":    self._rate(FunnelStage.AUTHORITY, FunnelStage.PRO_UPGRADE),
        }
        return rates.get(key, 0.0)

    def _rate(self, numerator: FunnelStage, denominator: FunnelStage) -> float:
        d = self._stages[denominator].entered
        n = self._stages[numerator].converted
        if d == 0:
            return 0.0
        return round(n / d * 100, 2)

    def _compute_health(self) -> float:
        """0–100 health score based on benchmark attainment."""
        scores = []
        for key, benchmark in self.BENCHMARKS.items():
            actual = self._get_rate(key)
            if actual > 0:
                scores.append(min(actual / benchmark * 100, 100))
        if not scores:
            return 100.0
        return round(sum(scores) / len(scores), 1)


# Singleton for MetaOrchestrator registration
funnel_observer = FunnelObserver()
