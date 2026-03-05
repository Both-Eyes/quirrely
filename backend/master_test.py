#!/usr/bin/env python3
"""
QUIRRELY MASTER TEST v1.0
Orchestrates the full simulation and generates prescriptive actions.

The Master Test:
1. Runs 4667 synthetic users through 90-day simulation
2. Compares results to baseline expectations
3. Identifies opportunities, watches, and risks
4. Generates specific, actionable recommendations

This is designed to run:
- On demand (manual refresh)
- On schedule (daily/weekly)
- After significant changes (deployments, config updates)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

from simulation_engine import SimulationEngine, SimulationConfig
from value_functions import (
    calculate_funnel_health,
    calculate_system_value,
    calculate_generation_distribution,
    calculate_country_comparison,
)


# ═══════════════════════════════════════════════════════════════════════════
# BASELINE EXPECTATIONS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class BaselineExpectations:
    """Expected metrics for comparison."""
    
    # Funnel conversion rates
    signup_rate: float = 0.30
    first_analysis_rate: float = 0.60
    trial_start_rate: float = 0.70
    trial_convert_rate: float = 0.25
    featured_approve_rate: float = 0.70
    
    # Value metrics
    avg_user_value: float = 3.5
    value_per_subscriber: float = 8.0
    
    # Behavioral metrics
    avg_streak_length: float = 5.0
    exploration_rate: float = 0.20
    
    # Health metrics
    monthly_churn_rate: float = 0.05
    token_velocity: float = 0.5  # events per user per day
    
    # Country parity (deviation tolerance)
    country_deviation_tolerance: float = 0.15  # 15% deviation acceptable
    
    # Entry type parity
    entry_type_deviation_tolerance: float = 0.10  # 10% deviation acceptable


# ═══════════════════════════════════════════════════════════════════════════
# PRESCRIPTIVE ACTION
# ═══════════════════════════════════════════════════════════════════════════

class ActionSeverity(str, Enum):
    OPPORTUNITY = "opportunity"  # 🟢 Green - exploit
    WATCH = "watch"              # 🟡 Yellow - monitor
    RISK = "risk"                # 🔴 Red - mitigate


class ActionCategory(str, Enum):
    CONVERSION = "conversion"
    RETENTION = "retention"
    VALUE = "value"
    VELOCITY = "velocity"
    FUNNEL = "funnel"
    COUNTRY = "country"
    ENTRY = "entry"


@dataclass
class PrescriptiveAction:
    """A specific, actionable recommendation."""
    
    # Required fields first
    severity: ActionSeverity
    category: ActionCategory
    title: str
    description: str
    current_value: float
    baseline_value: float
    delta_percent: float
    action_recommended: str
    action_impact: str
    action_effort: str  # low, medium, high
    
    # Optional fields with defaults
    country_code: Optional[str] = None
    funnel_stage: Optional[str] = None
    token_generation: Optional[int] = None
    priority_score: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "delta_percent": self.delta_percent,
            "country_code": self.country_code,
            "funnel_stage": self.funnel_stage,
            "token_generation": self.token_generation,
            "action_recommended": self.action_recommended,
            "action_impact": self.action_impact,
            "action_effort": self.action_effort,
            "priority_score": self.priority_score,
        }


# ═══════════════════════════════════════════════════════════════════════════
# PRESCRIPTIVE ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class PrescriptiveEngine:
    """
    Analyzes simulation results and generates prescriptive actions.
    """
    
    def __init__(self, baseline: BaselineExpectations = None):
        self.baseline = baseline or BaselineExpectations()
        self.actions: List[PrescriptiveAction] = []
    
    def analyze(self, results: Dict) -> List[PrescriptiveAction]:
        """Analyze simulation results and generate actions."""
        self.actions = []
        
        # Analyze each area
        self._analyze_funnel(results)
        self._analyze_country_parity(results)
        self._analyze_entry_type_parity(results)
        self._analyze_value_metrics(results)
        self._analyze_churn(results)
        self._analyze_token_distribution(results)
        
        # Calculate priority scores
        self._calculate_priorities()
        
        # Sort by severity then priority
        self.actions.sort(key=lambda a: (
            {"risk": 0, "watch": 1, "opportunity": 2}[a.severity.value],
            -a.priority_score
        ))
        
        return self.actions
    
    def _analyze_funnel(self, results: Dict):
        """Analyze funnel conversion rates."""
        funnel = results.get("funnel_rates", {})
        
        # Check each conversion step
        checks = [
            ("visitor_to_signed_up", self.baseline.signup_rate, "Signup"),
            ("signed_up_to_first_analysis", self.baseline.first_analysis_rate, "First Analysis"),
            ("hit_limit_to_trial_started", self.baseline.trial_start_rate, "Trial Start"),
            ("trial_started_to_subscribed", self.baseline.trial_convert_rate, "Trial Conversion"),
            ("featured_submitted_to_featured_approved", self.baseline.featured_approve_rate, "Featured Approval"),
        ]
        
        for key, baseline, name in checks:
            current = funnel.get(key, 0)
            delta = (current - baseline) / baseline if baseline > 0 else 0
            
            if delta > 0.10:  # 10% above baseline
                self.actions.append(PrescriptiveAction(
                    severity=ActionSeverity.OPPORTUNITY,
                    category=ActionCategory.FUNNEL,
                    title=f"{name} conversion exceeds baseline",
                    description=f"{name} converting at {current:.1%} vs {baseline:.1%} baseline (+{delta:.1%})",
                    current_value=current,
                    baseline_value=baseline,
                    delta_percent=delta * 100,
                    funnel_stage=key,
                    action_recommended=f"Investigate what's driving {name.lower()} success and amplify",
                    action_impact="Could increase downstream conversions",
                    action_effort="low",
                ))
            elif delta < -0.15:  # 15% below baseline
                self.actions.append(PrescriptiveAction(
                    severity=ActionSeverity.RISK,
                    category=ActionCategory.FUNNEL,
                    title=f"{name} conversion below baseline",
                    description=f"{name} converting at {current:.1%} vs {baseline:.1%} baseline ({delta:.1%})",
                    current_value=current,
                    baseline_value=baseline,
                    delta_percent=delta * 100,
                    funnel_stage=key,
                    action_recommended=f"Audit {name.lower()} flow for friction points",
                    action_impact="Blocking user progression",
                    action_effort="medium",
                ))
            elif delta < -0.08:  # 8% below baseline
                self.actions.append(PrescriptiveAction(
                    severity=ActionSeverity.WATCH,
                    category=ActionCategory.FUNNEL,
                    title=f"{name} conversion trending down",
                    description=f"{name} at {current:.1%} vs {baseline:.1%} baseline ({delta:.1%})",
                    current_value=current,
                    baseline_value=baseline,
                    delta_percent=delta * 100,
                    funnel_stage=key,
                    action_recommended=f"Monitor {name.lower()} for 48 hours",
                    action_impact="May need intervention if continues",
                    action_effort="low",
                ))
    
    def _analyze_country_parity(self, results: Dict):
        """Analyze performance parity across countries."""
        country_stats = results.get("country_stats", {})
        
        if not country_stats:
            return
        
        # Calculate averages
        avg_conversion = sum(
            c.get("subscribed", 0) / c.get("total_users", 1) 
            for c in country_stats.values()
        ) / len(country_stats)
        
        avg_value = sum(
            c.get("avg_value", 0) for c in country_stats.values()
        ) / len(country_stats)
        
        for country, stats in country_stats.items():
            total = stats.get("total_users", 1)
            subscribed = stats.get("subscribed", 0)
            conversion = subscribed / total if total > 0 else 0
            value = stats.get("avg_value", 0)
            
            # Check conversion parity
            conv_delta = (conversion - avg_conversion) / avg_conversion if avg_conversion > 0 else 0
            
            if conv_delta > self.baseline.country_deviation_tolerance:
                self.actions.append(PrescriptiveAction(
                    severity=ActionSeverity.OPPORTUNITY,
                    category=ActionCategory.COUNTRY,
                    title=f"{country.upper()} conversion outperforming",
                    description=f"{country.upper()} converting at {conversion:.1%} vs {avg_conversion:.1%} average (+{conv_delta:.1%})",
                    current_value=conversion,
                    baseline_value=avg_conversion,
                    delta_percent=conv_delta * 100,
                    country_code=country,
                    action_recommended=f"Study {country.upper()} user behavior for insights to apply elsewhere",
                    action_impact="Could lift other countries",
                    action_effort="medium",
                ))
            elif conv_delta < -self.baseline.country_deviation_tolerance:
                self.actions.append(PrescriptiveAction(
                    severity=ActionSeverity.RISK,
                    category=ActionCategory.COUNTRY,
                    title=f"{country.upper()} conversion underperforming",
                    description=f"{country.upper()} converting at {conversion:.1%} vs {avg_conversion:.1%} average ({conv_delta:.1%})",
                    current_value=conversion,
                    baseline_value=avg_conversion,
                    delta_percent=conv_delta * 100,
                    country_code=country,
                    action_recommended=f"Audit {country.upper()} user experience, pricing, and localization",
                    action_impact="Revenue opportunity being missed",
                    action_effort="medium",
                ))
    
    def _analyze_entry_type_parity(self, results: Dict):
        """Analyze direct vs .com entry performance."""
        entry_stats = results.get("entry_stats", {})
        
        direct = entry_stats.get("direct", {})
        via_com = entry_stats.get("via_com", {})
        
        if not direct or not via_com:
            return
        
        direct_conv = direct.get("conversion_rate", 0)
        com_conv = via_com.get("conversion_rate", 0)
        
        if direct_conv > 0:
            delta = (com_conv - direct_conv) / direct_conv
            
            if delta < -self.baseline.entry_type_deviation_tolerance:
                self.actions.append(PrescriptiveAction(
                    severity=ActionSeverity.WATCH,
                    category=ActionCategory.ENTRY,
                    title="quirrely.com redirect users converting lower",
                    description=f"Via .com: {com_conv:.1%} vs direct: {direct_conv:.1%} ({delta:.1%})",
                    current_value=com_conv,
                    baseline_value=direct_conv,
                    delta_percent=delta * 100,
                    action_recommended="Review geo-redirect experience and landing page continuity",
                    action_impact="Friction in redirect flow may be losing users",
                    action_effort="low",
                ))
    
    def _analyze_value_metrics(self, results: Dict):
        """Analyze token value metrics."""
        value_metrics = results.get("value_metrics", {})
        
        avg_value = value_metrics.get("mean_value", 0)
        delta = (avg_value - self.baseline.avg_user_value) / self.baseline.avg_user_value if self.baseline.avg_user_value > 0 else 0
        
        if delta > 0.20:  # 20% above
            self.actions.append(PrescriptiveAction(
                severity=ActionSeverity.OPPORTUNITY,
                category=ActionCategory.VALUE,
                title="User value exceeding expectations",
                description=f"Avg value {avg_value:.2f} vs {self.baseline.avg_user_value:.2f} baseline (+{delta:.1%})",
                current_value=avg_value,
                baseline_value=self.baseline.avg_user_value,
                delta_percent=delta * 100,
                action_recommended="Users are highly engaged - consider premium tier or additional monetization",
                action_impact="Revenue upside potential",
                action_effort="high",
            ))
        elif delta < -0.20:  # 20% below
            self.actions.append(PrescriptiveAction(
                severity=ActionSeverity.RISK,
                category=ActionCategory.VALUE,
                title="User value below expectations",
                description=f"Avg value {avg_value:.2f} vs {self.baseline.avg_user_value:.2f} baseline ({delta:.1%})",
                current_value=avg_value,
                baseline_value=self.baseline.avg_user_value,
                delta_percent=delta * 100,
                action_recommended="Focus on engagement features, streak mechanics, and exploration prompts",
                action_impact="Low value users more likely to churn",
                action_effort="medium",
            ))
    
    def _analyze_churn(self, results: Dict):
        """Analyze churn metrics."""
        churn_stats = results.get("churn_stats", {})
        
        churn_rate = churn_stats.get("churn_rate", 0)
        # Annualize monthly baseline for comparison with simulation
        sim_days = results.get("summary", {}).get("simulation_days", 90)
        expected_churn = self.baseline.monthly_churn_rate * (sim_days / 30)
        
        delta = (churn_rate - expected_churn) / expected_churn if expected_churn > 0 else 0
        
        if delta > 0.25:  # 25% above expected
            self.actions.append(PrescriptiveAction(
                severity=ActionSeverity.RISK,
                category=ActionCategory.RETENTION,
                title="Churn rate elevated",
                description=f"Churn at {churn_rate:.1%} vs {expected_churn:.1%} expected (+{delta:.1%})",
                current_value=churn_rate,
                baseline_value=expected_churn,
                delta_percent=delta * 100,
                action_recommended="Implement win-back campaigns, review recent changes that may have impacted retention",
                action_impact="Direct revenue loss",
                action_effort="high",
            ))
        elif delta < -0.15:  # 15% below expected
            self.actions.append(PrescriptiveAction(
                severity=ActionSeverity.OPPORTUNITY,
                category=ActionCategory.RETENTION,
                title="Churn rate better than expected",
                description=f"Churn at {churn_rate:.1%} vs {expected_churn:.1%} expected ({delta:.1%})",
                current_value=churn_rate,
                baseline_value=expected_churn,
                delta_percent=delta * 100,
                action_recommended="Document retention drivers, consider sharing as marketing proof point",
                action_impact="Strong foundation for growth",
                action_effort="low",
            ))
    
    def _analyze_token_distribution(self, results: Dict):
        """Analyze token generation distribution."""
        gen_dist = results.get("generation_distribution", {})
        
        # Check for blockages (too many users stuck at a generation)
        total_users = sum(g.get("count", 0) for g in gen_dist.values())
        
        if total_users == 0:
            return
        
        for gen, data in gen_dist.items():
            gen_int = int(gen)
            count = data.get("count", 0)
            pct = count / total_users
            
            # Gen 1 blockage (not progressing to behavioral)
            if gen_int == 1 and pct > 0.50:
                self.actions.append(PrescriptiveAction(
                    severity=ActionSeverity.WATCH,
                    category=ActionCategory.VELOCITY,
                    title="Users stuck at Gen 1 (Structured Profile)",
                    description=f"{pct:.1%} of users haven't progressed beyond initial profile",
                    current_value=pct,
                    baseline_value=0.40,
                    delta_percent=(pct - 0.40) * 100,
                    token_generation=gen_int,
                    action_recommended="Improve onboarding prompts, streak education, exploration CTAs",
                    action_impact="Users not building behavioral patterns won't convert",
                    action_effort="medium",
                ))
            
            # Gen 3 to Gen 4 blockage (not getting Featured)
            if gen_int == 3:
                gen4_count = gen_dist.get(4, {}).get("count", 0) + gen_dist.get("4", {}).get("count", 0)
                if count > 0 and gen4_count / count < 0.10:
                    self.actions.append(PrescriptiveAction(
                        severity=ActionSeverity.WATCH,
                        category=ActionCategory.FUNNEL,
                        title="Gen 3→4 progression low (Featured)",
                        description=f"Only {gen4_count/count:.1%} of behavioral users becoming Featured",
                        current_value=gen4_count / count if count > 0 else 0,
                        baseline_value=0.15,
                        delta_percent=-30,
                        token_generation=3,
                        action_recommended="Review Featured eligibility criteria, submission friction, review queue speed",
                        action_impact="Limiting recognition program effectiveness",
                        action_effort="medium",
                    ))
    
    def _calculate_priorities(self):
        """Calculate priority scores for all actions."""
        for action in self.actions:
            # Base score from severity
            severity_score = {
                ActionSeverity.RISK: 100,
                ActionSeverity.WATCH: 50,
                ActionSeverity.OPPORTUNITY: 75,
            }[action.severity]
            
            # Adjust by delta magnitude
            delta_score = min(abs(action.delta_percent) * 2, 50)
            
            # Adjust by effort (lower effort = higher priority)
            effort_score = {
                "low": 20,
                "medium": 10,
                "high": 0,
            }.get(action.action_effort, 10)
            
            action.priority_score = int(severity_score + delta_score + effort_score)


# ═══════════════════════════════════════════════════════════════════════════
# MASTER TEST
# ═══════════════════════════════════════════════════════════════════════════

class MasterTest:
    """
    The Master Test orchestrates the full simulation and analysis.
    
    Default configuration:
    - 4667 users (1000 per country + .com overflow)
    - 90-day simulation
    - 60% direct traffic, 40% via .com
    - Compares against baseline expectations
    - Generates prioritized prescriptive actions
    """
    
    def __init__(
        self,
        config: SimulationConfig = None,
        baseline: BaselineExpectations = None,
    ):
        self.config = config or SimulationConfig(
            total_users=4667,
            simulation_days=90,
            seed=42,
            direct_traffic_pct=0.60,
            com_traffic_pct=0.40,
        )
        self.baseline = baseline or BaselineExpectations()
        
        self.engine: Optional[SimulationEngine] = None
        self.prescriptive_engine: Optional[PrescriptiveEngine] = None
        self.results: Optional[Dict] = None
        self.actions: List[PrescriptiveAction] = []
        
        self.run_started_at: Optional[datetime] = None
        self.run_completed_at: Optional[datetime] = None
    
    def run(self) -> Dict:
        """Run the complete Master Test."""
        self.run_started_at = datetime.utcnow()
        
        # Run simulation
        self.engine = SimulationEngine(self.config)
        self.results = self.engine.run()
        
        # Generate prescriptive actions
        self.prescriptive_engine = PrescriptiveEngine(self.baseline)
        self.actions = self.prescriptive_engine.analyze(self.results)
        
        self.run_completed_at = datetime.utcnow()
        
        return self.get_full_report()
    
    def get_full_report(self) -> Dict:
        """Get the complete test report."""
        return {
            "meta": {
                "run_started_at": self.run_started_at.isoformat() if self.run_started_at else None,
                "run_completed_at": self.run_completed_at.isoformat() if self.run_completed_at else None,
                "duration_seconds": (self.run_completed_at - self.run_started_at).total_seconds() if self.run_completed_at and self.run_started_at else None,
            },
            "config": asdict(self.config),
            "baseline": asdict(self.baseline),
            "simulation_results": self.results,
            "prescriptive_actions": {
                "total": len(self.actions),
                "by_severity": {
                    "opportunity": len([a for a in self.actions if a.severity == ActionSeverity.OPPORTUNITY]),
                    "watch": len([a for a in self.actions if a.severity == ActionSeverity.WATCH]),
                    "risk": len([a for a in self.actions if a.severity == ActionSeverity.RISK]),
                },
                "actions": [a.to_dict() for a in self.actions],
            },
            "system_pulse": self._generate_system_pulse(),
        }
    
    def _generate_system_pulse(self) -> Dict:
        """Generate the system pulse summary for dashboard."""
        if not self.results:
            return {}
        
        value_metrics = self.results.get("value_metrics", {})
        churn_stats = self.results.get("churn_stats", {})
        funnel_rates = self.results.get("funnel_rates", {})
        
        # Calculate health scores (0-100)
        conversion_health = min(100, int(
            (funnel_rates.get("trial_started_to_subscribed", 0) / self.baseline.trial_convert_rate) * 100
        ))
        
        value_health = min(100, int(
            (value_metrics.get("mean_value", 0) / self.baseline.avg_user_value) * 100
        ))
        
        retention_health = min(100, int(
            (1 - churn_stats.get("churn_rate", 0) / 0.20) * 100  # 20% churn = 0 health
        ))
        
        overall_health = int((conversion_health + value_health + retention_health) / 3)
        
        return {
            "overall_health": overall_health,
            "health_breakdown": {
                "conversion": conversion_health,
                "value": value_health,
                "retention": retention_health,
            },
            "key_metrics": {
                "total_users": self.results.get("summary", {}).get("total_users", 0),
                "total_value": value_metrics.get("total_value", 0),
                "avg_value": value_metrics.get("mean_value", 0),
                "trial_conversion": funnel_rates.get("trial_started_to_subscribed", 0),
                "churn_rate": churn_stats.get("churn_rate", 0),
            },
            "top_actions": [
                {
                    "severity": a.severity.value,
                    "title": a.title,
                    "action": a.action_recommended,
                }
                for a in self.actions[:5]
            ],
        }
    
    def get_opportunities(self) -> List[PrescriptiveAction]:
        """Get only opportunity actions."""
        return [a for a in self.actions if a.severity == ActionSeverity.OPPORTUNITY]
    
    def get_watches(self) -> List[PrescriptiveAction]:
        """Get only watch actions."""
        return [a for a in self.actions if a.severity == ActionSeverity.WATCH]
    
    def get_risks(self) -> List[PrescriptiveAction]:
        """Get only risk actions."""
        return [a for a in self.actions if a.severity == ActionSeverity.RISK]


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def run_master_test(seed: int = None) -> Dict:
    """Run the Master Test with optional seed override."""
    config = SimulationConfig(
        total_users=4667,
        simulation_days=90,
        seed=seed or 42,
    )
    
    test = MasterTest(config=config)
    return test.run()


def run_quick_test(users: int = 500, days: int = 30) -> Dict:
    """Run a quick test with fewer users and days."""
    config = SimulationConfig(
        total_users=users,
        simulation_days=days,
        seed=42,
    )
    
    test = MasterTest(config=config)
    return test.run()


def run_scenario_test(
    name: str,
    config_overrides: Dict,
) -> Dict:
    """Run a scenario test with custom configuration."""
    base_config = SimulationConfig()
    
    # Apply overrides
    for key, value in config_overrides.items():
        if hasattr(base_config, key):
            setattr(base_config, key, value)
    
    test = MasterTest(config=base_config)
    results = test.run()
    results["scenario_name"] = name
    
    return results


# ═══════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("QUIRRELY MASTER TEST")
    print("=" * 70)
    print()
    
    # Run the test
    print("Running simulation with 4667 users over 90 days...")
    print()
    
    results = run_master_test()
    
    # Print summary
    pulse = results.get("system_pulse", {})
    
    print(f"Overall System Health: {pulse.get('overall_health', 0)}%")
    print()
    print("Health Breakdown:")
    health = pulse.get("health_breakdown", {})
    print(f"  Conversion: {health.get('conversion', 0)}%")
    print(f"  Value:      {health.get('value', 0)}%")
    print(f"  Retention:  {health.get('retention', 0)}%")
    print()
    
    # Print key metrics
    metrics = pulse.get("key_metrics", {})
    print("Key Metrics:")
    print(f"  Total Users:      {metrics.get('total_users', 0):,}")
    print(f"  Total Value:      {metrics.get('total_value', 0):,.2f}")
    print(f"  Avg User Value:   {metrics.get('avg_value', 0):.2f}")
    print(f"  Trial Conversion: {metrics.get('trial_conversion', 0):.1%}")
    print(f"  Churn Rate:       {metrics.get('churn_rate', 0):.1%}")
    print()
    
    # Print prescriptive actions
    actions = results.get("prescriptive_actions", {})
    print(f"Prescriptive Actions: {actions.get('total', 0)}")
    by_severity = actions.get("by_severity", {})
    print(f"  🟢 Opportunities: {by_severity.get('opportunity', 0)}")
    print(f"  🟡 Watches:       {by_severity.get('watch', 0)}")
    print(f"  🔴 Risks:         {by_severity.get('risk', 0)}")
    print()
    
    # Print top actions
    print("Top Actions:")
    for i, action in enumerate(pulse.get("top_actions", [])[:5], 1):
        severity_icon = {"opportunity": "🟢", "watch": "🟡", "risk": "🔴"}.get(action.get("severity"), "⚪")
        print(f"  {i}. {severity_icon} {action.get('title')}")
        print(f"     → {action.get('action')}")
        print()
    
    print("=" * 70)
    print("Test complete.")
    print("=" * 70)
