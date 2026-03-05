#!/usr/bin/env python3
"""
LNCP META: COMMAND CENTER v5.1.1
The nerve center of the virtuous cycle.

Aggregates all system signals into actionable proposals,
prioritized by impact on UX → Health → MRR.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════

class Domain(str, Enum):
    USER_EXPERIENCE = "ux"
    SYSTEM_HEALTH = "health"
    MRR_PERFORMANCE = "mrr"
    SAFETY = "safety"  # v5.2.0 - HALO integration


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class InjectionTier(str, Enum):
    IMMEDIATE = "immediate"  # < 1 hour, low risk
    HOUR_24 = "24hour"       # Next deploy cycle, medium risk
    DAY_30 = "30day"         # Next sprint, high risk


class ProposalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    APPLIED = "applied"


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Metric:
    """A measurable system metric."""
    name: str
    value: float
    unit: str = ""
    target: Optional[float] = None
    trend: float = 0  # Change from previous period
    
    @property
    def on_target(self) -> bool:
        if self.target is None:
            return True
        return self.value >= self.target
    
    @property
    def trend_direction(self) -> str:
        if self.trend > 0.01:
            return "up"
        elif self.trend < -0.01:
            return "down"
        return "neutral"
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "target": self.target,
            "trend": self.trend,
            "on_target": self.on_target,
            "trend_direction": self.trend_direction
        }


@dataclass
class Alert:
    """A system alert requiring attention."""
    id: str
    severity: AlertSeverity
    domain: Domain
    title: str
    description: str
    detected_at: datetime
    impact: str
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "domain": self.domain.value,
            "title": self.title,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "age": self._age_str(),
            "impact": self.impact,
            "metadata": self.metadata
        }
    
    def _age_str(self) -> str:
        delta = datetime.now(timezone.utc) - self.detected_at
        hours = delta.total_seconds() / 3600
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        else:
            return f"{int(hours / 24)}d ago"


@dataclass
class ProposalImpact:
    """Expected impact of a proposal on the virtuous cycle."""
    ux_percent: float = 0       # % improvement to UX metrics
    health_percent: float = 0   # % improvement to health metrics
    mrr_dollars: float = 0      # $ impact on MRR
    
    def to_dict(self) -> Dict:
        return {
            "ux": self.ux_percent,
            "health": self.health_percent,
            "mrr": self.mrr_dollars
        }
    
    @property
    def total_score(self) -> float:
        """Weighted score for prioritization."""
        # Normalize: UX and health as %, MRR as equivalent %
        # $100 MRR ~ 1% UX improvement
        mrr_normalized = self.mrr_dollars / 100
        return self.ux_percent * 0.35 + self.health_percent * 0.25 + mrr_normalized * 0.40


@dataclass
class Proposal:
    """An actionable improvement proposal."""
    id: str
    domain: Domain
    tier: InjectionTier
    title: str
    description: str
    impact: ProposalImpact
    confidence: float  # 0-1
    evidence: str
    trust_score: float  # From trust store
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    @property
    def priority_score(self) -> int:
        """Calculate priority 0-100 based on impact, confidence, and trust."""
        base = self.impact.total_score * 10
        confidence_factor = self.confidence
        trust_factor = 0.5 + (self.trust_score * 0.5)  # Trust adds up to 50%
        
        # Urgency boost for critical issues
        urgency = 1.0
        if self.tier == InjectionTier.IMMEDIATE:
            urgency = 1.1
        
        score = base * confidence_factor * trust_factor * urgency
        return min(100, max(0, int(score)))
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "domain": self.domain.value,
            "tier": self.tier.value,
            "title": self.title,
            "description": self.description,
            "impact": self.impact.to_dict(),
            "confidence": self.confidence,
            "evidence": self.evidence,
            "trust_score": self.trust_score,
            "priority": self.priority_score,
            "status": self.status.value,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class DomainState:
    """Current state of a domain."""
    domain: Domain
    metrics: List[Metric]
    alerts: List[Alert]
    proposals: List[Proposal]
    
    def to_dict(self) -> Dict:
        return {
            "domain": self.domain.value,
            "metrics": [m.to_dict() for m in self.metrics],
            "alerts": [a.to_dict() for a in self.alerts],
            "proposal_count": len(self.proposals),
            "critical_alerts": len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL])
        }


# ═══════════════════════════════════════════════════════════════════════════
# COMMAND CENTER
# ═══════════════════════════════════════════════════════════════════════════

class CommandCenter:
    """
    The nerve center of the LNCP Meta system.
    
    Aggregates signals from all domains, generates proposals,
    and manages the surgical code injection queue.
    """
    
    def __init__(self):
        self.domains: Dict[Domain, DomainState] = {}
        self.proposals: List[Proposal] = []
        self.injection_queue: Dict[InjectionTier, List[Proposal]] = {
            InjectionTier.IMMEDIATE: [],
            InjectionTier.HOUR_24: [],
            InjectionTier.DAY_30: []
        }
        self.audit_trail: List[Dict] = []
        self._last_refresh = None
        
        # Initialize with current state
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize with current system state."""
        self._refresh_ux_domain()
        self._refresh_health_domain()
        self._refresh_mrr_domain()
        self._refresh_safety_domain()  # v5.2.0 - HALO integration
        self._generate_proposals()
        self._last_refresh = datetime.now(timezone.utc)
    
    # ─────────────────────────────────────────────────────────────────────
    # DOMAIN REFRESH
    # ─────────────────────────────────────────────────────────────────────
    
    def _refresh_ux_domain(self):
        """Refresh User Experience domain state."""
        # In production, these would come from real observers
        metrics = [
            Metric("activation_rate", 0.324, "%", target=0.30, trend=0.042),
            Metric("time_to_value", 18.3, "hours", trend=-2.1),
            Metric("friction_rate", 0.42, "", trend=0.08),
            Metric("active_users", 847, "", trend=0.12)
        ]
        
        alerts = [
            Alert(
                id="ux_001",
                severity=AlertSeverity.WARNING,
                domain=Domain.USER_EXPERIENCE,
                title="Onboarding Step 3 Drop-off Spike",
                description="42% of users abandoning at profile customization step",
                detected_at=datetime.now(timezone.utc) - timedelta(hours=2),
                impact="activation"
            ),
            Alert(
                id="ux_002",
                severity=AlertSeverity.INFO,
                domain=Domain.USER_EXPERIENCE,
                title="Help Button Usage Increasing",
                description="15% increase in help access on analysis results page",
                detected_at=datetime.now(timezone.utc) - timedelta(hours=6),
                impact="friction"
            )
        ]
        
        self.domains[Domain.USER_EXPERIENCE] = DomainState(
            domain=Domain.USER_EXPERIENCE,
            metrics=metrics,
            alerts=alerts,
            proposals=[p for p in self.proposals if p.domain == Domain.USER_EXPERIENCE]
        )
    
    def _refresh_health_domain(self):
        """Refresh System Health domain state."""
        metrics = [
            Metric("engine_accuracy", 0.872, "%", trend=0.021),
            Metric("auto_apply_rate", 0.34, "%", trend=0.08),
            Metric("test_pass_rate", 0.926, "%", trend=0),
            Metric("system_score", 78, "", trend=3)
        ]
        
        alerts = [
            Alert(
                id="health_001",
                severity=AlertSeverity.INFO,
                domain=Domain.SYSTEM_HEALTH,
                title="Core Engine API Signatures",
                description="4 test failures due to API signature mismatches",
                detected_at=datetime.now(timezone.utc) - timedelta(hours=24),
                impact="tests"
            )
        ]
        
        self.domains[Domain.SYSTEM_HEALTH] = DomainState(
            domain=Domain.SYSTEM_HEALTH,
            metrics=metrics,
            alerts=alerts,
            proposals=[p for p in self.proposals if p.domain == Domain.SYSTEM_HEALTH]
        )
    
    def _refresh_mrr_domain(self):
        """Refresh MRR Performance domain state."""
        metrics = [
            Metric("mrr", 16170, "USD", trend=890),
            Metric("trial_conversion", 0.182, "%", target=0.25, trend=-0.021),
            Metric("churn_rate", 0.028, "%", target=0.03, trend=0),
            Metric("ltv_cac", 6.1, "x", trend=0.3)
        ]
        
        alerts = [
            Alert(
                id="mrr_001",
                severity=AlertSeverity.CRITICAL,
                domain=Domain.MRR_PERFORMANCE,
                title="Trial Conversion Below Target",
                description="18.2% vs 25% target - significant gap",
                detected_at=datetime.now(timezone.utc) - timedelta(weeks=3),
                impact="mrr_growth",
                metadata={"potential_loss": 2100}
            ),
            Alert(
                id="mrr_002",
                severity=AlertSeverity.WARNING,
                domain=Domain.MRR_PERFORMANCE,
                title="3 Enterprise Accounts At Risk",
                description="Usage declined 40%+ over past 2 weeks",
                detected_at=datetime.now(timezone.utc) - timedelta(days=3),
                impact="churn",
                metadata={"mrr_at_risk": 2400}
            )
        ]
        
        self.domains[Domain.MRR_PERFORMANCE] = DomainState(
            domain=Domain.MRR_PERFORMANCE,
            metrics=metrics,
            alerts=alerts,
            proposals=[p for p in self.proposals if p.domain == Domain.MRR_PERFORMANCE]
        )
    
    def _refresh_safety_domain(self):
        """Refresh Safety domain state (HALO integration)."""
        # Try to get real data from HALO Observer
        try:
            from lncp.meta.halo_observer import get_halo_observer
            observer = get_halo_observer()
            health = observer.get_health_inputs()
            cc_metrics = observer.get_command_center_metrics()
            
            metrics = [
                Metric("safety_score", health.get("health_score", 98), "%", target=98, trend=0),
                Metric("violation_rate", health.get("violation_rate", 0.002) * 100, "%", target=0.5, trend=0),
                Metric("false_positive_rate", health.get("false_positive_rate", 0.01) * 100, "%", target=2.0, trend=0),
                Metric("checks_24h", health.get("total_checks_24h", 0), "", trend=0)
            ]
            
            alerts = [
                Alert(
                    id=f"safety_{i}",
                    severity=AlertSeverity.WARNING if a.get("severity") == "warning" else AlertSeverity.INFO,
                    domain=Domain.SAFETY,
                    title=a.get("title", ""),
                    description=a.get("message", ""),
                    detected_at=datetime.now(timezone.utc),
                    impact="safety"
                )
                for i, a in enumerate(cc_metrics.get("alerts", []))
            ]
        except ImportError:
            # Fallback to simulated data
            metrics = [
                Metric("safety_score", 97.8, "%", target=98, trend=0.5),
                Metric("violation_rate", 0.3, "%", target=0.5, trend=-0.1),
                Metric("false_positive_rate", 1.2, "%", target=2.0, trend=-0.3),
                Metric("checks_24h", 1247, "", trend=89)
            ]
            
            alerts = [
                Alert(
                    id="safety_001",
                    severity=AlertSeverity.INFO,
                    domain=Domain.SAFETY,
                    title="HALO Patterns Performing Well",
                    description="All patterns above 90% precision threshold",
                    detected_at=datetime.now(timezone.utc) - timedelta(hours=6),
                    impact="safety"
                )
            ]
        
        self.domains[Domain.SAFETY] = DomainState(
            domain=Domain.SAFETY,
            metrics=metrics,
            alerts=alerts,
            proposals=[p for p in self.proposals if p.domain == Domain.SAFETY]
        )
    
    # ─────────────────────────────────────────────────────────────────────
    # PROPOSAL GENERATION
    # ─────────────────────────────────────────────────────────────────────
    
    def _generate_proposals(self):
        """Generate proposals based on current alerts and metrics."""
        self.proposals = [
            Proposal(
                id="prop_001",
                domain=Domain.MRR_PERFORMANCE,
                tier=InjectionTier.HOUR_24,
                title="Increase trial reminder frequency",
                description="Add 2 additional reminder emails during trial period",
                impact=ProposalImpact(ux_percent=0, health_percent=0, mrr_dollars=485),
                confidence=0.78,
                evidence="47% of churned trials had no reminder interaction. Industry avg: 3 reminders vs our 1.",
                trust_score=0.72
            ),
            Proposal(
                id="prop_002",
                domain=Domain.USER_EXPERIENCE,
                tier=InjectionTier.IMMEDIATE,
                title="Add skip option to onboarding step 3",
                description="Allow users to skip profile customization and do it later",
                impact=ProposalImpact(ux_percent=15, health_percent=0, mrr_dollars=0),
                confidence=0.82,
                evidence="42% drop-off at step 3. A/B test of skip option showed 18% activation improvement.",
                trust_score=0.85
            ),
            Proposal(
                id="prop_003",
                domain=Domain.MRR_PERFORMANCE,
                tier=InjectionTier.IMMEDIATE,
                title="Trigger at-risk outreach for enterprise accounts",
                description="Send personalized outreach to 3 declining enterprise accounts",
                impact=ProposalImpact(ux_percent=0, health_percent=0, mrr_dollars=2400),
                confidence=0.65,
                evidence="3 accounts with 40%+ usage decline. Proactive outreach saves 60% historically.",
                trust_score=0.68
            ),
            Proposal(
                id="prop_004",
                domain=Domain.USER_EXPERIENCE,
                tier=InjectionTier.HOUR_24,
                title="Simplify results page explanation",
                description="Reduce text, add visual indicators for profile match",
                impact=ProposalImpact(ux_percent=8, health_percent=5, mrr_dollars=0),
                confidence=0.71,
                evidence="15% increase in help button usage on results page indicates confusion.",
                trust_score=0.74
            ),
            Proposal(
                id="prop_005",
                domain=Domain.SYSTEM_HEALTH,
                tier=InjectionTier.DAY_30,
                title="Adjust profile confidence threshold",
                description="Raise confidence threshold from 0.7 to 0.75 for profile assignment",
                impact=ProposalImpact(ux_percent=5, health_percent=12, mrr_dollars=0),
                confidence=0.68,
                evidence="23% profile switch rate suggests threshold too low for accurate predictions.",
                trust_score=0.55
            ),
            Proposal(
                id="prop_006",
                domain=Domain.USER_EXPERIENCE,
                tier=InjectionTier.IMMEDIATE,
                title="Update CTA button color on blog",
                description="Change CTA from blue to green based on A/B test results",
                impact=ProposalImpact(ux_percent=3, health_percent=0, mrr_dollars=120),
                confidence=0.88,
                evidence="A/B test (n=2,400) showed 12% CTR improvement with green vs blue.",
                trust_score=0.91
            )
        ]
        
        # Sort by priority
        self.proposals.sort(key=lambda p: p.priority_score, reverse=True)
    
    # ─────────────────────────────────────────────────────────────────────
    # PROPOSAL ACTIONS
    # ─────────────────────────────────────────────────────────────────────
    
    def approve_proposal(self, proposal_id: str, approved_by: str = "admin") -> Dict:
        """Approve a proposal and add to injection queue."""
        proposal = next((p for p in self.proposals if p.id == proposal_id), None)
        if not proposal:
            return {"error": "Proposal not found"}
        
        proposal.status = ProposalStatus.APPROVED
        proposal.approved_at = datetime.now(timezone.utc)
        proposal.approved_by = approved_by
        
        # Add to injection queue
        self.injection_queue[proposal.tier].append(proposal)
        
        # Log to audit trail
        self.audit_trail.append({
            "action": "approve",
            "proposal_id": proposal_id,
            "proposal_title": proposal.title,
            "tier": proposal.tier.value,
            "impact": proposal.impact.to_dict(),
            "approved_by": approved_by,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "success": True,
            "proposal": proposal.to_dict(),
            "injection_tier": proposal.tier.value,
            "queue_position": len(self.injection_queue[proposal.tier])
        }
    
    def reject_proposal(self, proposal_id: str, reason: str = "") -> Dict:
        """Reject a proposal and log for learning."""
        proposal = next((p for p in self.proposals if p.id == proposal_id), None)
        if not proposal:
            return {"error": "Proposal not found"}
        
        proposal.status = ProposalStatus.REJECTED
        
        self.audit_trail.append({
            "action": "reject",
            "proposal_id": proposal_id,
            "proposal_title": proposal.title,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {"success": True, "proposal_id": proposal_id}
    
    def defer_proposal(self, proposal_id: str, defer_until: datetime) -> Dict:
        """Defer a proposal to a later time."""
        proposal = next((p for p in self.proposals if p.id == proposal_id), None)
        if not proposal:
            return {"error": "Proposal not found"}
        
        proposal.status = ProposalStatus.DEFERRED
        
        self.audit_trail.append({
            "action": "defer",
            "proposal_id": proposal_id,
            "defer_until": defer_until.isoformat(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {"success": True, "defer_until": defer_until.isoformat()}
    
    # ─────────────────────────────────────────────────────────────────────
    # INJECTION CONTROL
    # ─────────────────────────────────────────────────────────────────────
    
    def get_injection_queue(self) -> Dict:
        """Get current injection queue status."""
        return {
            "immediate": {
                "count": len(self.injection_queue[InjectionTier.IMMEDIATE]),
                "proposals": [p.to_dict() for p in self.injection_queue[InjectionTier.IMMEDIATE]]
            },
            "24hour": {
                "count": len(self.injection_queue[InjectionTier.HOUR_24]),
                "next_deploy": "18h",
                "proposals": [p.to_dict() for p in self.injection_queue[InjectionTier.HOUR_24]]
            },
            "30day": {
                "count": len(self.injection_queue[InjectionTier.DAY_30]),
                "next_sprint": "2026-03-01",
                "proposals": [p.to_dict() for p in self.injection_queue[InjectionTier.DAY_30]]
            }
        }
    
    def execute_immediate(self) -> List[Dict]:
        """Execute all immediate tier injections."""
        results = []
        for proposal in self.injection_queue[InjectionTier.IMMEDIATE]:
            # In production, this would actually apply the change
            result = {
                "proposal_id": proposal.id,
                "title": proposal.title,
                "executed_at": datetime.now(timezone.utc).isoformat(),
                "status": "applied"
            }
            proposal.status = ProposalStatus.APPLIED
            results.append(result)
            
            self.audit_trail.append({
                "action": "execute",
                "proposal_id": proposal.id,
                "tier": "immediate",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Clear queue
        self.injection_queue[InjectionTier.IMMEDIATE] = []
        
        return results
    
    # ─────────────────────────────────────────────────────────────────────
    # STATE EXPORT
    # ─────────────────────────────────────────────────────────────────────
    
    def get_full_state(self) -> Dict:
        """Export complete system state as JSON."""
        return {
            "version": "5.1.1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "OPERATIONAL",
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None,
            "domains": {
                d.value: self.domains[d].to_dict() 
                for d in Domain if d in self.domains
            },
            "proposals": {
                "total": len(self.proposals),
                "by_domain": {
                    "ux": len([p for p in self.proposals if p.domain == Domain.USER_EXPERIENCE]),
                    "health": len([p for p in self.proposals if p.domain == Domain.SYSTEM_HEALTH]),
                    "mrr": len([p for p in self.proposals if p.domain == Domain.MRR_PERFORMANCE])
                },
                "by_tier": {
                    "immediate": len([p for p in self.proposals if p.tier == InjectionTier.IMMEDIATE]),
                    "24hour": len([p for p in self.proposals if p.tier == InjectionTier.HOUR_24]),
                    "30day": len([p for p in self.proposals if p.tier == InjectionTier.DAY_30])
                },
                "items": [p.to_dict() for p in self.proposals]
            },
            "injection_queue": self.get_injection_queue(),
            "audit_trail": {
                "total_actions": len(self.audit_trail),
                "recent": self.audit_trail[-10:] if self.audit_trail else []
            }
        }
    
    def get_summary(self) -> Dict:
        """Get summary for dashboard display."""
        all_alerts = []
        for domain in self.domains.values():
            all_alerts.extend(domain.alerts)
        
        critical = len([a for a in all_alerts if a.severity == AlertSeverity.CRITICAL])
        warning = len([a for a in all_alerts if a.severity == AlertSeverity.WARNING])
        
        return {
            "status": "OPERATIONAL",
            "alerts": {"critical": critical, "warning": warning, "total": len(all_alerts)},
            "proposals": {"pending": len([p for p in self.proposals if p.status == ProposalStatus.PENDING])},
            "injection_queue": {
                "immediate": len(self.injection_queue[InjectionTier.IMMEDIATE]),
                "24hour": len(self.injection_queue[InjectionTier.HOUR_24]),
                "30day": len(self.injection_queue[InjectionTier.DAY_30])
            }
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_command_center: Optional[CommandCenter] = None

def get_command_center() -> CommandCenter:
    """Get the global command center instance."""
    global _command_center
    if _command_center is None:
        _command_center = CommandCenter()
    return _command_center


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "Domain",
    "AlertSeverity",
    "InjectionTier",
    "ProposalStatus",
    "Metric",
    "Alert",
    "ProposalImpact",
    "Proposal",
    "DomainState",
    "CommandCenter",
    "get_command_center"
]
