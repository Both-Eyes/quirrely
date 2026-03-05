#!/usr/bin/env python3
"""
QUIRRELY CLOSED-LOOP: ACTION CLASSIFIER v1.0
Classifies prescriptive actions into auto-apply vs human-review lanes.

The Three Laws:
1. Do no harm — Never auto-apply changes that could damage trust/revenue/UX
2. Small steps — One change at a time, measure, decide
3. Always reversible — Every auto-change must be rollback-able
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
# CLASSIFICATION TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ActionLane(str, Enum):
    """Which lane an action goes to."""
    AUTO_APPLY = "auto_apply"       # System can apply without human
    HUMAN_REVIEW = "human_review"   # Requires human approval
    BLOCKED = "blocked"             # Never auto-apply, needs careful review


class ActionDomain(str, Enum):
    """What domain the action affects."""
    COPY = "copy"                   # Text, messaging, labels
    TIMING = "timing"               # Delays, intervals, durations
    THRESHOLD = "threshold"         # Numeric limits, percentages
    FEATURE_FLAG = "feature_flag"   # On/off toggles
    LAYOUT = "layout"               # UI arrangement
    PRICING = "pricing"             # Money-related
    POLICY = "policy"               # Rules, terms, restrictions
    DATA = "data"                   # User data handling
    INTEGRATION = "integration"     # Third-party connections


class RiskLevel(str, Enum):
    """Risk level of the action."""
    MINIMAL = "minimal"             # Can't really hurt anything
    LOW = "low"                     # Small potential downside
    MEDIUM = "medium"               # Notable potential downside
    HIGH = "high"                   # Significant potential downside
    CRITICAL = "critical"           # Could damage business/trust


# ═══════════════════════════════════════════════════════════════════════════
# CLASSIFICATION RULES
# ═══════════════════════════════════════════════════════════════════════════

# Domains that are ALWAYS human review
ALWAYS_HUMAN_DOMAINS: Set[ActionDomain] = {
    ActionDomain.PRICING,
    ActionDomain.POLICY,
    ActionDomain.DATA,
    ActionDomain.INTEGRATION,
}

# Domains that CAN be auto-applied (with constraints)
AUTO_ELIGIBLE_DOMAINS: Set[ActionDomain] = {
    ActionDomain.COPY,
    ActionDomain.TIMING,
    ActionDomain.THRESHOLD,
    ActionDomain.FEATURE_FLAG,
    ActionDomain.LAYOUT,
}

# Maximum allowed change magnitude for auto-apply (percentage)
MAX_AUTO_CHANGE: Dict[ActionDomain, float] = {
    ActionDomain.COPY: 100.0,       # Can change copy fully
    ActionDomain.TIMING: 25.0,      # Max 25% timing change
    ActionDomain.THRESHOLD: 15.0,   # Max 15% threshold change
    ActionDomain.FEATURE_FLAG: 100.0,  # On/off is binary
    ActionDomain.LAYOUT: 10.0,      # Max 10% layout change (conservative)
}

# Minimum confidence score required for auto-apply
MIN_AUTO_CONFIDENCE: float = 0.75

# Minimum priority score required for auto-apply
MIN_AUTO_PRIORITY: int = 100

# Maximum number of auto-changes per day
MAX_AUTO_CHANGES_PER_DAY: int = 3


# ═══════════════════════════════════════════════════════════════════════════
# ACTION CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ClassifiedAction:
    """An action with its classification."""
    
    # Original action data
    action_id: str
    title: str
    description: str
    category: str
    severity: str
    
    # Classification results
    lane: ActionLane
    domain: ActionDomain
    risk_level: RiskLevel
    confidence: float
    
    # Auto-apply specifics (if applicable)
    config_key: Optional[str] = None
    current_value: Optional[any] = None
    proposed_value: Optional[any] = None
    change_magnitude: Optional[float] = None
    
    # Constraints
    requires_ab_test: bool = False
    rollback_window_hours: int = 24
    success_metric: Optional[str] = None
    success_threshold: Optional[float] = None
    
    # Reasoning
    classification_reason: str = ""
    blocking_reasons: List[str] = None
    
    def __post_init__(self):
        if self.blocking_reasons is None:
            self.blocking_reasons = []
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "title": self.title,
            "lane": self.lane.value,
            "domain": self.domain.value,
            "risk_level": self.risk_level.value,
            "confidence": self.confidence,
            "config_key": self.config_key,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "change_magnitude": self.change_magnitude,
            "requires_ab_test": self.requires_ab_test,
            "rollback_window_hours": self.rollback_window_hours,
            "success_metric": self.success_metric,
            "success_threshold": self.success_threshold,
            "classification_reason": self.classification_reason,
            "blocking_reasons": self.blocking_reasons,
        }


class ActionClassifier:
    """
    Classifies prescriptive actions into auto-apply vs human-review lanes.
    
    This is the gatekeeper. It must be conservative.
    When in doubt, route to human review.
    """
    
    def __init__(self):
        self.auto_changes_today = 0
        self.last_reset_date = datetime.utcnow().date()
    
    def classify(self, action: Dict) -> ClassifiedAction:
        """Classify a single action."""
        
        # Reset daily counter if new day
        today = datetime.utcnow().date()
        if today > self.last_reset_date:
            self.auto_changes_today = 0
            self.last_reset_date = today
        
        # Extract action info
        action_id = action.get("action_id", f"action_{id(action)}")
        title = action.get("title", "")
        description = action.get("description", "")
        category = action.get("category", "")
        severity = action.get("severity", "")
        
        # Determine domain
        domain = self._infer_domain(action)
        
        # Determine risk level
        risk_level = self._assess_risk(action, domain)
        
        # Check for blocking conditions
        blocking_reasons = self._check_blocking_conditions(action, domain, risk_level)
        
        # Determine lane
        if blocking_reasons:
            lane = ActionLane.HUMAN_REVIEW
            if risk_level == RiskLevel.CRITICAL:
                lane = ActionLane.BLOCKED
        elif domain in ALWAYS_HUMAN_DOMAINS:
            lane = ActionLane.HUMAN_REVIEW
            blocking_reasons.append(f"Domain '{domain.value}' always requires human review")
        elif self.auto_changes_today >= MAX_AUTO_CHANGES_PER_DAY:
            lane = ActionLane.HUMAN_REVIEW
            blocking_reasons.append(f"Daily auto-change limit reached ({MAX_AUTO_CHANGES_PER_DAY})")
        else:
            lane = ActionLane.AUTO_APPLY
        
        # Calculate confidence
        confidence = self._calculate_confidence(action, domain, risk_level)
        
        # If confidence too low, route to human
        if lane == ActionLane.AUTO_APPLY and confidence < MIN_AUTO_CONFIDENCE:
            lane = ActionLane.HUMAN_REVIEW
            blocking_reasons.append(f"Confidence {confidence:.2f} below threshold {MIN_AUTO_CONFIDENCE}")
        
        # Determine if A/B test required
        requires_ab_test = self._should_ab_test(action, domain, risk_level)
        
        # Build config key and values if auto-applicable
        config_key, current_value, proposed_value, change_magnitude = None, None, None, None
        if lane == ActionLane.AUTO_APPLY:
            config_key, current_value, proposed_value = self._extract_config_change(action)
            if current_value is not None and proposed_value is not None:
                change_magnitude = self._calculate_change_magnitude(current_value, proposed_value)
                
                # Check if change magnitude exceeds limit
                max_change = MAX_AUTO_CHANGE.get(domain, 10.0)
                if change_magnitude > max_change:
                    lane = ActionLane.HUMAN_REVIEW
                    blocking_reasons.append(f"Change magnitude {change_magnitude:.1f}% exceeds limit {max_change}%")
        
        # Determine success metric
        success_metric, success_threshold = self._determine_success_criteria(action, category)
        
        # Build classification reason
        if lane == ActionLane.AUTO_APPLY:
            classification_reason = f"Auto-eligible: {domain.value} domain, {risk_level.value} risk, {confidence:.0%} confidence"
        else:
            classification_reason = f"Human review: {'; '.join(blocking_reasons)}"
        
        return ClassifiedAction(
            action_id=action_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            lane=lane,
            domain=domain,
            risk_level=risk_level,
            confidence=confidence,
            config_key=config_key,
            current_value=current_value,
            proposed_value=proposed_value,
            change_magnitude=change_magnitude,
            requires_ab_test=requires_ab_test,
            rollback_window_hours=24 if risk_level in [RiskLevel.MINIMAL, RiskLevel.LOW] else 48,
            success_metric=success_metric,
            success_threshold=success_threshold,
            classification_reason=classification_reason,
            blocking_reasons=blocking_reasons,
        )
    
    def classify_batch(self, actions: List[Dict]) -> List[ClassifiedAction]:
        """Classify multiple actions."""
        return [self.classify(a) for a in actions]
    
    def _infer_domain(self, action: Dict) -> ActionDomain:
        """Infer the domain from action content."""
        title = action.get("title", "").lower()
        desc = action.get("description", "").lower()
        category = action.get("category", "").lower()
        
        # Keyword matching
        if any(kw in title + desc for kw in ["price", "cost", "payment", "subscription", "$"]):
            return ActionDomain.PRICING
        if any(kw in title + desc for kw in ["policy", "terms", "privacy", "legal"]):
            return ActionDomain.POLICY
        if any(kw in title + desc for kw in ["copy", "text", "message", "wording", "label"]):
            return ActionDomain.COPY
        if any(kw in title + desc for kw in ["timing", "delay", "interval", "days", "hours"]):
            return ActionDomain.TIMING
        if any(kw in title + desc for kw in ["threshold", "limit", "rate", "percentage", "%"]):
            return ActionDomain.THRESHOLD
        if any(kw in title + desc for kw in ["enable", "disable", "toggle", "flag", "feature"]):
            return ActionDomain.FEATURE_FLAG
        if any(kw in title + desc for kw in ["layout", "position", "order", "arrange"]):
            return ActionDomain.LAYOUT
        if any(kw in title + desc for kw in ["data", "export", "delete", "gdpr"]):
            return ActionDomain.DATA
        if any(kw in title + desc for kw in ["integration", "api", "webhook", "connect"]):
            return ActionDomain.INTEGRATION
        
        # Default based on category
        category_map = {
            "conversion": ActionDomain.THRESHOLD,
            "retention": ActionDomain.TIMING,
            "funnel": ActionDomain.THRESHOLD,
            "value": ActionDomain.THRESHOLD,
            "velocity": ActionDomain.TIMING,
            "country": ActionDomain.THRESHOLD,
            "entry": ActionDomain.THRESHOLD,
        }
        return category_map.get(category, ActionDomain.THRESHOLD)
    
    def _assess_risk(self, action: Dict, domain: ActionDomain) -> RiskLevel:
        """Assess the risk level of an action."""
        severity = action.get("severity", "").lower()
        delta = abs(action.get("delta_percent", 0))
        
        # Critical domains
        if domain in [ActionDomain.PRICING, ActionDomain.POLICY, ActionDomain.DATA]:
            return RiskLevel.CRITICAL
        
        # High severity actions
        if severity == "risk" and delta > 50:
            return RiskLevel.HIGH
        if severity == "risk":
            return RiskLevel.MEDIUM
        
        # Medium actions
        if severity == "watch":
            return RiskLevel.LOW
        
        # Opportunities are generally low risk
        if severity == "opportunity":
            if delta > 100:
                return RiskLevel.LOW  # Big opportunity, still verify
            return RiskLevel.MINIMAL
        
        return RiskLevel.MEDIUM
    
    def _check_blocking_conditions(
        self, 
        action: Dict, 
        domain: ActionDomain, 
        risk_level: RiskLevel
    ) -> List[str]:
        """Check for conditions that block auto-apply."""
        reasons = []
        
        # Critical risk always blocked from auto
        if risk_level == RiskLevel.CRITICAL:
            reasons.append("Critical risk level")
        
        # High risk requires review
        if risk_level == RiskLevel.HIGH:
            reasons.append("High risk level")
        
        # Check priority score
        priority = action.get("priority_score", 0)
        if priority < MIN_AUTO_PRIORITY and domain in AUTO_ELIGIBLE_DOMAINS:
            reasons.append(f"Priority {priority} below threshold {MIN_AUTO_PRIORITY}")
        
        # Check if action affects multiple countries
        if action.get("country_code") is None and "country" in action.get("category", ""):
            reasons.append("Affects multiple countries - needs review")
        
        # Check if this is a regression (fixing something that broke)
        if "below baseline" in action.get("description", "").lower():
            if action.get("severity") == "risk":
                reasons.append("Regression detected - needs human investigation")
        
        return reasons
    
    def _calculate_confidence(
        self, 
        action: Dict, 
        domain: ActionDomain, 
        risk_level: RiskLevel
    ) -> float:
        """Calculate confidence score for auto-apply."""
        confidence = 1.0
        
        # Risk penalty
        risk_penalties = {
            RiskLevel.MINIMAL: 0.0,
            RiskLevel.LOW: 0.1,
            RiskLevel.MEDIUM: 0.25,
            RiskLevel.HIGH: 0.5,
            RiskLevel.CRITICAL: 1.0,
        }
        confidence -= risk_penalties.get(risk_level, 0.25)
        
        # Domain bonus/penalty
        if domain in AUTO_ELIGIBLE_DOMAINS:
            confidence += 0.1
        else:
            confidence -= 0.3
        
        # Priority bonus
        priority = action.get("priority_score", 0)
        if priority >= 140:
            confidence += 0.1
        elif priority < 100:
            confidence -= 0.2
        
        # Delta magnitude penalty (very large changes need scrutiny)
        delta = abs(action.get("delta_percent", 0))
        if delta > 100:
            confidence -= 0.15
        elif delta > 50:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _should_ab_test(
        self, 
        action: Dict, 
        domain: ActionDomain, 
        risk_level: RiskLevel
    ) -> bool:
        """Determine if action should be A/B tested."""
        # Always A/B test layout changes
        if domain == ActionDomain.LAYOUT:
            return True
        
        # A/B test medium risk changes
        if risk_level == RiskLevel.MEDIUM:
            return True
        
        # A/B test copy changes (they can have unexpected effects)
        if domain == ActionDomain.COPY:
            return True
        
        # A/B test large threshold changes
        if domain == ActionDomain.THRESHOLD:
            delta = abs(action.get("delta_percent", 0))
            if delta > 20:
                return True
        
        return False
    
    def _extract_config_change(self, action: Dict) -> tuple:
        """Extract config key and values from action."""
        # This would map to actual config keys in production
        funnel_stage = action.get("funnel_stage")
        category = action.get("category")
        
        if funnel_stage:
            config_key = f"funnel.{funnel_stage}.threshold"
        elif category:
            config_key = f"config.{category}.default"
        else:
            config_key = None
        
        current = action.get("current_value")
        baseline = action.get("baseline_value")
        
        # Propose moving halfway toward baseline (conservative)
        if current is not None and baseline is not None:
            proposed = current + (baseline - current) * 0.5
        else:
            proposed = None
        
        return config_key, current, proposed
    
    def _calculate_change_magnitude(self, current: any, proposed: any) -> float:
        """Calculate percentage change magnitude."""
        try:
            current = float(current)
            proposed = float(proposed)
            if current == 0:
                return 100.0 if proposed != 0 else 0.0
            return abs((proposed - current) / current) * 100
        except (TypeError, ValueError):
            return 0.0
    
    def _determine_success_criteria(self, action: Dict, category: str) -> tuple:
        """Determine how to measure success of the change."""
        metric_map = {
            "conversion": ("conversion_rate", 0.05),
            "retention": ("churn_rate", -0.02),
            "funnel": ("funnel_completion_rate", 0.03),
            "value": ("avg_user_value", 0.1),
            "velocity": ("token_velocity", 0.05),
        }
        
        if category in metric_map:
            return metric_map[category]
        
        return ("overall_health", 0.01)


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def classify_actions(actions: List[Dict]) -> Dict:
    """Classify a list of actions and return summary."""
    classifier = ActionClassifier()
    classified = classifier.classify_batch(actions)
    
    auto_apply = [c for c in classified if c.lane == ActionLane.AUTO_APPLY]
    human_review = [c for c in classified if c.lane == ActionLane.HUMAN_REVIEW]
    blocked = [c for c in classified if c.lane == ActionLane.BLOCKED]
    
    return {
        "summary": {
            "total": len(classified),
            "auto_apply": len(auto_apply),
            "human_review": len(human_review),
            "blocked": len(blocked),
        },
        "auto_apply": [c.to_dict() for c in auto_apply],
        "human_review": [c.to_dict() for c in human_review],
        "blocked": [c.to_dict() for c in blocked],
    }


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test with sample actions
    sample_actions = [
        {
            "action_id": "act_001",
            "title": "First Analysis conversion exceeds baseline",
            "description": "First Analysis converting at 122.6% vs 60.0% baseline (+104.4%)",
            "category": "funnel",
            "severity": "opportunity",
            "current_value": 1.226,
            "baseline_value": 0.6,
            "delta_percent": 104.4,
            "priority_score": 145,
        },
        {
            "action_id": "act_002",
            "title": "Trial Start conversion below baseline",
            "description": "Trial Start converting at 4.8% vs 70.0% baseline (-93.2%)",
            "category": "funnel",
            "severity": "risk",
            "current_value": 0.048,
            "baseline_value": 0.7,
            "delta_percent": -93.2,
            "funnel_stage": "hit_limit_to_trial_started",
            "priority_score": 160,
        },
        {
            "action_id": "act_003",
            "title": "Churn rate better than expected",
            "description": "Churn at 5.0% vs 15.0% expected (-66.9%)",
            "category": "retention",
            "severity": "opportunity",
            "current_value": 0.05,
            "baseline_value": 0.15,
            "delta_percent": -66.9,
            "priority_score": 145,
        },
    ]
    
    result = classify_actions(sample_actions)
    
    print("=" * 60)
    print("ACTION CLASSIFICATION RESULTS")
    print("=" * 60)
    print(f"\nTotal: {result['summary']['total']}")
    print(f"  Auto-Apply:    {result['summary']['auto_apply']}")
    print(f"  Human Review:  {result['summary']['human_review']}")
    print(f"  Blocked:       {result['summary']['blocked']}")
    
    print("\n--- AUTO-APPLY ---")
    for a in result["auto_apply"]:
        print(f"  ✅ {a['title']}")
        print(f"     Confidence: {a['confidence']:.0%}, A/B Test: {a['requires_ab_test']}")
    
    print("\n--- HUMAN REVIEW ---")
    for a in result["human_review"]:
        print(f"  👤 {a['title']}")
        print(f"     Reasons: {', '.join(a['blocking_reasons'])}")
    
    print("\n--- BLOCKED ---")
    for a in result["blocked"]:
        print(f"  🚫 {a['title']}")
        print(f"     Reasons: {', '.join(a['blocking_reasons'])}")
