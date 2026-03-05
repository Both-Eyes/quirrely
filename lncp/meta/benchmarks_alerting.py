#!/usr/bin/env python3
"""
LNCP META: BENCHMARKS & ALERTING v5.0
External benchmarks and production alerting system.

Benchmarks:
- Static industry benchmarks for SaaS
- Comparison with current metrics
- Benchmark-aware prioritization

Alerting:
- Slack integration
- Email for critical alerts
- Alert deduplication
- Escalation tracking
"""

import os
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

SLACK_WEBHOOK_URL = os.environ.get("LNCP_SLACK_WEBHOOK", "")
ALERT_EMAIL = os.environ.get("LNCP_ALERT_EMAIL", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))


# ═══════════════════════════════════════════════════════════════════════════
# BENCHMARKS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Benchmark:
    """A single benchmark metric."""
    metric_name: str
    category: str
    
    # Values
    low: float      # Below average
    average: float  # Industry average
    high: float     # Above average
    excellent: float  # Top performers
    
    # Context
    unit: str = ""
    source: str = ""
    updated_at: str = "2026-02"


@dataclass
class BenchmarkComparison:
    """Comparison of a metric to benchmark."""
    metric_name: str
    current_value: float
    benchmark_average: float
    
    # Assessment
    percentile: str  # "below", "average", "above", "excellent"
    gap_to_average: float
    gap_percent: float
    
    # Recommendation
    priority: str  # "high", "medium", "low"
    recommendation: str


# Industry benchmarks for SaaS
SAAS_BENCHMARKS: Dict[str, Benchmark] = {
    "ctr_search": Benchmark(
        metric_name="CTR (Search)",
        category="seo",
        low=1.5, average=3.0, high=5.0, excellent=8.0,
        unit="%",
        source="Industry research 2025",
    ),
    "ctr_display": Benchmark(
        metric_name="CTR (Display)",
        category="marketing",
        low=0.2, average=0.5, high=1.0, excellent=2.0,
        unit="%",
    ),
    "trial_conversion": Benchmark(
        metric_name="Trial Conversion",
        category="revenue",
        low=10, average=20, high=30, excellent=40,
        unit="%",
    ),
    "monthly_churn": Benchmark(
        metric_name="Monthly Churn",
        category="revenue",
        low=8, average=5, high=3, excellent=1,  # Lower is better
        unit="%",
    ),
    "blog_signup_rate": Benchmark(
        metric_name="Blog Signup Rate",
        category="content",
        low=0.5, average=1.5, high=3.0, excellent=5.0,
        unit="%",
    ),
    "ltv_cac_ratio": Benchmark(
        metric_name="LTV/CAC Ratio",
        category="revenue",
        low=1.5, average=3.0, high=5.0, excellent=7.0,
        unit="x",
    ),
    "mrr_growth": Benchmark(
        metric_name="MRR Growth",
        category="revenue",
        low=3, average=8, high=15, excellent=25,
        unit="% monthly",
    ),
}


class BenchmarkStore:
    """Manages and applies benchmarks."""
    
    def __init__(self):
        self.benchmarks = SAAS_BENCHMARKS.copy()
    
    def get_benchmark(self, metric_name: str) -> Optional[Benchmark]:
        """Get benchmark for a metric."""
        return self.benchmarks.get(metric_name)
    
    def compare(self, metric_name: str, current_value: float) -> Optional[BenchmarkComparison]:
        """Compare current value to benchmark."""
        benchmark = self.get_benchmark(metric_name)
        if not benchmark:
            return None
        
        # Handle "lower is better" metrics
        lower_is_better = metric_name in ["monthly_churn"]
        
        # Determine percentile
        if lower_is_better:
            if current_value <= benchmark.excellent:
                percentile = "excellent"
            elif current_value <= benchmark.high:
                percentile = "above"
            elif current_value <= benchmark.average:
                percentile = "average"
            else:
                percentile = "below"
        else:
            if current_value >= benchmark.excellent:
                percentile = "excellent"
            elif current_value >= benchmark.high:
                percentile = "above"
            elif current_value >= benchmark.average:
                percentile = "average"
            else:
                percentile = "below"
        
        # Calculate gap
        gap = benchmark.average - current_value if lower_is_better else current_value - benchmark.average
        gap_pct = (gap / benchmark.average * 100) if benchmark.average != 0 else 0
        
        # Priority and recommendation
        if percentile == "below":
            priority = "high"
            rec = f"Improve {benchmark.metric_name} to reach industry average of {benchmark.average}{benchmark.unit}"
        elif percentile == "average":
            priority = "medium"
            rec = f"Good baseline. Target top performers at {benchmark.excellent}{benchmark.unit}"
        else:
            priority = "low"
            rec = f"Performing above average. Maintain current approach."
        
        return BenchmarkComparison(
            metric_name=metric_name,
            current_value=current_value,
            benchmark_average=benchmark.average,
            percentile=percentile,
            gap_to_average=gap,
            gap_percent=gap_pct,
            priority=priority,
            recommendation=rec,
        )
    
    def compare_all(self, metrics: Dict[str, float]) -> List[BenchmarkComparison]:
        """Compare all provided metrics to benchmarks."""
        comparisons = []
        for name, value in metrics.items():
            comp = self.compare(name, value)
            if comp:
                comparisons.append(comp)
        return sorted(comparisons, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.priority, 3))
    
    def get_priority_actions(self, metrics: Dict[str, float]) -> List[Dict]:
        """Get prioritized actions based on benchmark gaps."""
        comparisons = self.compare_all(metrics)
        actions = []
        
        for comp in comparisons:
            if comp.priority == "high":
                actions.append({
                    "metric": comp.metric_name,
                    "current": comp.current_value,
                    "target": comp.benchmark_average,
                    "gap_percent": comp.gap_percent,
                    "recommendation": comp.recommendation,
                })
        
        return actions


# ═══════════════════════════════════════════════════════════════════════════
# ALERTING
# ═══════════════════════════════════════════════════════════════════════════

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    DASHBOARD = "dashboard"
    SLACK = "slack"
    EMAIL = "email"


@dataclass
class Alert:
    """A system alert."""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Status
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    # Delivery
    channels_sent: List[AlertChannel] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "alert_id": self.alert_id,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
        }


class AlertManager:
    """
    Manages alerts with deduplication and delivery.
    
    Delivery rules:
    - INFO: Dashboard only
    - WARNING: Dashboard + Slack
    - CRITICAL: Dashboard + Slack + Email
    """
    
    # Deduplication window
    DEDUP_WINDOW_MINUTES = 60
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.recent_hashes: Dict[str, datetime] = {}  # For deduplication
        self._alert_counter = 0
    
    def _generate_id(self) -> str:
        """Generate unique alert ID."""
        self._alert_counter += 1
        return f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M')}_{self._alert_counter:04d}"
    
    def _hash_alert(self, title: str, source: str) -> str:
        """Generate hash for deduplication."""
        content = f"{title}:{source}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _is_duplicate(self, title: str, source: str) -> bool:
        """Check if this is a duplicate alert."""
        hash_key = self._hash_alert(title, source)
        
        if hash_key in self.recent_hashes:
            last_sent = self.recent_hashes[hash_key]
            if datetime.utcnow() - last_sent < timedelta(minutes=self.DEDUP_WINDOW_MINUTES):
                return True
        
        return False
    
    def create_alert(
        self,
        level: AlertLevel,
        title: str,
        message: str,
        source: str,
        force: bool = False,
    ) -> Optional[Alert]:
        """
        Create and deliver an alert.
        
        Returns None if deduplicated.
        """
        # Check deduplication
        if not force and self._is_duplicate(title, source):
            return None
        
        alert = Alert(
            alert_id=self._generate_id(),
            level=level,
            title=title,
            message=message,
            source=source,
        )
        
        # Store alert
        self.alerts[alert.alert_id] = alert
        self.recent_hashes[self._hash_alert(title, source)] = datetime.utcnow()
        
        # Deliver based on level
        self._deliver(alert)
        
        return alert
    
    def _deliver(self, alert: Alert):
        """Deliver alert to appropriate channels."""
        # Always add to dashboard
        alert.channels_sent.append(AlertChannel.DASHBOARD)
        
        # Slack for WARNING and CRITICAL
        if alert.level in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
            if self._send_slack(alert):
                alert.channels_sent.append(AlertChannel.SLACK)
        
        # Email for CRITICAL
        if alert.level == AlertLevel.CRITICAL:
            if self._send_email(alert):
                alert.channels_sent.append(AlertChannel.EMAIL)
    
    def _send_slack(self, alert: Alert) -> bool:
        """Send alert to Slack."""
        if not SLACK_WEBHOOK_URL:
            return False
        
        try:
            import urllib.request
            
            # Format message
            emoji = "🔴" if alert.level == AlertLevel.CRITICAL else "🟡"
            payload = {
                "text": f"{emoji} *{alert.title}*",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{emoji} *{alert.title}*\n{alert.message}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {"type": "mrkdwn", "text": f"Source: {alert.source} | Level: {alert.level.value}"}
                        ]
                    }
                ]
            }
            
            req = urllib.request.Request(
                SLACK_WEBHOOK_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception as e:
            print(f"Slack send error: {e}")
            return False
    
    def _send_email(self, alert: Alert) -> bool:
        """Send alert via email."""
        if not ALERT_EMAIL or not SMTP_HOST:
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(f"{alert.message}\n\nSource: {alert.source}\nTime: {alert.created_at}")
            msg['Subject'] = f"[LNCP {alert.level.value.upper()}] {alert.title}"
            msg['From'] = "alerts@lncp.io"
            msg['To'] = ALERT_EMAIL
            
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False
    
    def acknowledge(self, alert_id: str, by: str = "system") -> bool:
        """Acknowledge an alert."""
        if alert_id not in self.alerts:
            return False
        
        alert = self.alerts[alert_id]
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = by
        return True
    
    def get_active(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """Get active (unacknowledged) alerts."""
        active = [a for a in self.alerts.values() if not a.acknowledged]
        if level:
            active = [a for a in active if a.level == level]
        return sorted(active, key=lambda a: a.created_at, reverse=True)
    
    def get_recent(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [a for a in self.alerts.values() if a.created_at >= cutoff]
    
    def cleanup_old(self, days: int = 30):
        """Remove old acknowledged alerts."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        to_remove = [
            aid for aid, alert in self.alerts.items()
            if alert.acknowledged and alert.created_at < cutoff
        ]
        for aid in to_remove:
            del self.alerts[aid]
    
    def get_summary(self) -> Dict:
        """Get alert summary."""
        all_alerts = list(self.alerts.values())
        active = [a for a in all_alerts if not a.acknowledged]
        
        return {
            "total": len(all_alerts),
            "active": len(active),
            "by_level": {
                "critical": len([a for a in active if a.level == AlertLevel.CRITICAL]),
                "warning": len([a for a in active if a.level == AlertLevel.WARNING]),
                "info": len([a for a in active if a.level == AlertLevel.INFO]),
            },
            "channels_configured": {
                "slack": bool(SLACK_WEBHOOK_URL),
                "email": bool(ALERT_EMAIL and SMTP_HOST),
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH ALERT RULES
# ═══════════════════════════════════════════════════════════════════════════

class HealthAlertRules:
    """Rules for generating alerts from health metrics."""
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
    
    def check_health(self, health_score: float, domain_scores: Dict[str, float]) -> List[Alert]:
        """Check health and create alerts as needed."""
        alerts = []
        
        # System-wide health
        if health_score < 30:
            alert = self.alert_manager.create_alert(
                AlertLevel.CRITICAL,
                "System Health Critical",
                f"System health dropped to {health_score:.1f}%. Pausing all automated actions.",
                "health_calculator"
            )
            if alert:
                alerts.append(alert)
        elif health_score < 50:
            alert = self.alert_manager.create_alert(
                AlertLevel.WARNING,
                "System Health Degraded",
                f"System health at {health_score:.1f}%. Reducing automated actions.",
                "health_calculator"
            )
            if alert:
                alerts.append(alert)
        
        # Domain-specific
        for domain, score in domain_scores.items():
            if score < 40:
                alert = self.alert_manager.create_alert(
                    AlertLevel.WARNING,
                    f"{domain.title()} Health Low",
                    f"{domain.title()} health dropped to {score:.1f}%.",
                    "health_calculator"
                )
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def check_revenue(self, churn_rate: float, mrr_growth: float) -> List[Alert]:
        """Check revenue metrics and alert."""
        alerts = []
        
        if churn_rate > 10:
            alert = self.alert_manager.create_alert(
                AlertLevel.CRITICAL,
                "Churn Rate Spike",
                f"Monthly churn rate at {churn_rate:.1f}%, significantly above normal.",
                "revenue_observer"
            )
            if alert:
                alerts.append(alert)
        
        if mrr_growth < -5:
            alert = self.alert_manager.create_alert(
                AlertLevel.CRITICAL,
                "MRR Declining",
                f"MRR growth at {mrr_growth:.1f}%. Revenue is declining.",
                "revenue_observer"
            )
            if alert:
                alerts.append(alert)
        
        return alerts


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCES
# ═══════════════════════════════════════════════════════════════════════════

_benchmark_store: Optional[BenchmarkStore] = None
_alert_manager: Optional[AlertManager] = None

def get_benchmark_store() -> BenchmarkStore:
    global _benchmark_store
    if _benchmark_store is None:
        _benchmark_store = BenchmarkStore()
    return _benchmark_store

def get_alert_manager() -> AlertManager:
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "Benchmark",
    "BenchmarkComparison",
    "SAAS_BENCHMARKS",
    "BenchmarkStore",
    "get_benchmark_store",
    "AlertLevel",
    "AlertChannel",
    "Alert",
    "AlertManager",
    "get_alert_manager",
    "HealthAlertRules",
]
