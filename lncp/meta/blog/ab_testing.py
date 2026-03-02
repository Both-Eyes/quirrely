#!/usr/bin/env python3
"""
LNCP META/BLOG: A/B TESTING v1.0
Live variant testing for blog optimization.

Tests:
- Meta title/description variants
- CTA copy variants
- CTA placement variants
- Content intro variants

Features:
- Deterministic user assignment (consistent experience)
- Statistical significance calculation
- Auto-conclusion when winner found
- Rollback capability
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import hashlib
import math


# ═══════════════════════════════════════════════════════════════════════════
# EXPERIMENT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ExperimentType(str, Enum):
    META_TITLE = "meta_title"
    META_DESCRIPTION = "meta_description"
    CTA_COPY = "cta_copy"
    CTA_PLACEMENT = "cta_placement"
    CTA_STYLE = "cta_style"
    INTRO_VARIANT = "intro_variant"


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    CONCLUDED = "concluded"
    ROLLED_BACK = "rolled_back"


class ExperimentResult(str, Enum):
    PENDING = "pending"
    VARIANT_WINS = "variant_wins"
    CONTROL_WINS = "control_wins"
    NO_DIFFERENCE = "no_difference"
    INCONCLUSIVE = "inconclusive"


# ═══════════════════════════════════════════════════════════════════════════
# VARIANT & EXPERIMENT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Variant:
    """A single variant in an experiment."""
    variant_id: str
    name: str
    value: Any  # The actual content (title, description, CTA text, etc.)
    is_control: bool = False
    
    # Metrics
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    
    @property
    def click_rate(self) -> float:
        return self.clicks / self.impressions if self.impressions > 0 else 0
    
    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.impressions if self.impressions > 0 else 0
    
    @property
    def click_to_conversion(self) -> float:
        return self.conversions / self.clicks if self.clicks > 0 else 0


@dataclass
class Experiment:
    """An A/B test experiment."""
    experiment_id: str
    name: str
    experiment_type: ExperimentType
    
    # Target
    page_url: str  # "*" for site-wide
    profile_style: Optional[str] = None
    profile_certitude: Optional[str] = None
    
    # Variants
    control: Variant = None
    variant: Variant = None
    
    # Configuration
    traffic_split: float = 0.5  # % to variant (rest to control)
    min_sample_size: int = 100  # Per variant
    min_duration_hours: int = 48
    max_duration_hours: int = 336  # 14 days
    significance_threshold: float = 0.95  # 95% confidence
    minimum_improvement: float = 0.05  # 5% improvement to declare winner
    
    # State
    status: ExperimentStatus = ExperimentStatus.DRAFT
    result: ExperimentResult = ExperimentResult.PENDING
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    concluded_at: Optional[datetime] = None
    
    # Winner (set when concluded)
    winner_variant_id: Optional[str] = None
    confidence_level: float = 0.0
    improvement_percent: float = 0.0
    
    def get_variant_for_user(self, user_id: str) -> Variant:
        """
        Deterministically assign user to variant.
        Same user always gets same variant.
        """
        hash_input = f"{self.experiment_id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Use hash to determine bucket
        bucket = (hash_value % 100) / 100
        
        if bucket < self.traffic_split:
            return self.variant
        return self.control
    
    def record_impression(self, variant_id: str):
        """Record an impression for a variant."""
        if self.control and self.control.variant_id == variant_id:
            self.control.impressions += 1
        elif self.variant and self.variant.variant_id == variant_id:
            self.variant.impressions += 1
    
    def record_click(self, variant_id: str):
        """Record a click for a variant."""
        if self.control and self.control.variant_id == variant_id:
            self.control.clicks += 1
        elif self.variant and self.variant.variant_id == variant_id:
            self.variant.clicks += 1
    
    def record_conversion(self, variant_id: str):
        """Record a conversion for a variant."""
        if self.control and self.control.variant_id == variant_id:
            self.control.conversions += 1
        elif self.variant and self.variant.variant_id == variant_id:
            self.variant.conversions += 1
    
    def can_conclude(self) -> Tuple[bool, str]:
        """Check if experiment can be concluded."""
        if self.status != ExperimentStatus.RUNNING:
            return False, "Experiment not running"
        
        # Check minimum duration
        if self.started_at:
            hours_running = (datetime.utcnow() - self.started_at).total_seconds() / 3600
            if hours_running < self.min_duration_hours:
                return False, f"Need {self.min_duration_hours - hours_running:.1f} more hours"
        
        # Check sample size
        if self.control.impressions < self.min_sample_size:
            return False, f"Control needs {self.min_sample_size - self.control.impressions} more impressions"
        if self.variant.impressions < self.min_sample_size:
            return False, f"Variant needs {self.min_sample_size - self.variant.impressions} more impressions"
        
        return True, "Ready to evaluate"
    
    def evaluate(self) -> ExperimentResult:
        """Evaluate the experiment and determine result."""
        can_conclude, reason = self.can_conclude()
        if not can_conclude:
            return ExperimentResult.PENDING
        
        # Calculate conversion rates
        control_rate = self.control.conversion_rate
        variant_rate = self.variant.conversion_rate
        
        # Calculate statistical significance
        significance = self._calculate_significance(
            self.control.conversions, self.control.impressions,
            self.variant.conversions, self.variant.impressions,
        )
        
        self.confidence_level = significance
        
        # Determine winner
        if significance >= self.significance_threshold:
            if variant_rate > control_rate:
                improvement = (variant_rate - control_rate) / control_rate if control_rate > 0 else 0
                self.improvement_percent = improvement
                
                if improvement >= self.minimum_improvement:
                    self.result = ExperimentResult.VARIANT_WINS
                    self.winner_variant_id = self.variant.variant_id
                else:
                    self.result = ExperimentResult.NO_DIFFERENCE
            else:
                improvement = (control_rate - variant_rate) / variant_rate if variant_rate > 0 else 0
                self.improvement_percent = -improvement
                self.result = ExperimentResult.CONTROL_WINS
                self.winner_variant_id = self.control.variant_id
        else:
            # Check if max duration exceeded
            if self.started_at:
                hours_running = (datetime.utcnow() - self.started_at).total_seconds() / 3600
                if hours_running >= self.max_duration_hours:
                    self.result = ExperimentResult.INCONCLUSIVE
                else:
                    self.result = ExperimentResult.PENDING
            else:
                self.result = ExperimentResult.PENDING
        
        return self.result
    
    def _calculate_significance(
        self,
        control_successes: int,
        control_trials: int,
        variant_successes: int,
        variant_trials: int,
    ) -> float:
        """
        Calculate statistical significance using Z-test.
        Returns confidence level (0-1).
        """
        if control_trials == 0 or variant_trials == 0:
            return 0.0
        
        p1 = control_successes / control_trials
        p2 = variant_successes / variant_trials
        
        # Pooled probability
        p_pool = (control_successes + variant_successes) / (control_trials + variant_trials)
        
        # Standard error
        if p_pool == 0 or p_pool == 1:
            return 0.0
        
        se = math.sqrt(p_pool * (1 - p_pool) * (1/control_trials + 1/variant_trials))
        
        if se == 0:
            return 0.0
        
        # Z-score
        z = abs(p2 - p1) / se
        
        # Convert to confidence (using normal CDF approximation)
        confidence = self._normal_cdf(z)
        
        return confidence
    
    def _normal_cdf(self, z: float) -> float:
        """Approximate normal CDF for z-score."""
        # Approximation using error function
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    
    def to_dict(self) -> Dict:
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "type": self.experiment_type.value,
            "page_url": self.page_url,
            "status": self.status.value,
            "result": self.result.value,
            "control": {
                "id": self.control.variant_id if self.control else None,
                "impressions": self.control.impressions if self.control else 0,
                "clicks": self.control.clicks if self.control else 0,
                "conversions": self.control.conversions if self.control else 0,
                "conversion_rate": self.control.conversion_rate if self.control else 0,
            },
            "variant": {
                "id": self.variant.variant_id if self.variant else None,
                "impressions": self.variant.impressions if self.variant else 0,
                "clicks": self.variant.clicks if self.variant else 0,
                "conversions": self.variant.conversions if self.variant else 0,
                "conversion_rate": self.variant.conversion_rate if self.variant else 0,
            },
            "confidence_level": self.confidence_level,
            "improvement_percent": self.improvement_percent,
            "winner": self.winner_variant_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "concluded_at": self.concluded_at.isoformat() if self.concluded_at else None,
        }


# ═══════════════════════════════════════════════════════════════════════════
# EXPERIMENT MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class BlogExperimentManager:
    """
    Manages all blog A/B experiments.
    
    Provides:
    - Experiment creation and lifecycle
    - User assignment to variants
    - Result tracking
    - Auto-conclusion
    """
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.experiment_counter = 0
        
        # Index by page for fast lookup
        self.experiments_by_page: Dict[str, List[str]] = {}
    
    def _generate_id(self) -> str:
        self.experiment_counter += 1
        return f"exp_{datetime.utcnow().strftime('%Y%m%d')}_{self.experiment_counter:04d}"
    
    # ─────────────────────────────────────────────────────────────────────
    # EXPERIMENT LIFECYCLE
    # ─────────────────────────────────────────────────────────────────────
    
    def create_experiment(
        self,
        name: str,
        experiment_type: ExperimentType,
        page_url: str,
        control_value: Any,
        variant_value: Any,
        control_name: str = "Control",
        variant_name: str = "Variant",
        traffic_split: float = 0.5,
        min_sample_size: int = 100,
    ) -> Experiment:
        """Create a new experiment."""
        exp_id = self._generate_id()
        
        experiment = Experiment(
            experiment_id=exp_id,
            name=name,
            experiment_type=experiment_type,
            page_url=page_url,
            control=Variant(
                variant_id=f"{exp_id}_control",
                name=control_name,
                value=control_value,
                is_control=True,
            ),
            variant=Variant(
                variant_id=f"{exp_id}_variant",
                name=variant_name,
                value=variant_value,
                is_control=False,
            ),
            traffic_split=traffic_split,
            min_sample_size=min_sample_size,
        )
        
        self.experiments[exp_id] = experiment
        
        # Index by page
        if page_url not in self.experiments_by_page:
            self.experiments_by_page[page_url] = []
        self.experiments_by_page[page_url].append(exp_id)
        
        return experiment
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start an experiment."""
        if experiment_id not in self.experiments:
            return False
        
        exp = self.experiments[experiment_id]
        if exp.status != ExperimentStatus.DRAFT:
            return False
        
        exp.status = ExperimentStatus.RUNNING
        exp.started_at = datetime.utcnow()
        return True
    
    def pause_experiment(self, experiment_id: str) -> bool:
        """Pause an experiment."""
        if experiment_id not in self.experiments:
            return False
        
        exp = self.experiments[experiment_id]
        if exp.status != ExperimentStatus.RUNNING:
            return False
        
        exp.status = ExperimentStatus.PAUSED
        return True
    
    def resume_experiment(self, experiment_id: str) -> bool:
        """Resume a paused experiment."""
        if experiment_id not in self.experiments:
            return False
        
        exp = self.experiments[experiment_id]
        if exp.status != ExperimentStatus.PAUSED:
            return False
        
        exp.status = ExperimentStatus.RUNNING
        return True
    
    def conclude_experiment(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Conclude an experiment and determine winner."""
        if experiment_id not in self.experiments:
            return None
        
        exp = self.experiments[experiment_id]
        
        can_conclude, reason = exp.can_conclude()
        if not can_conclude:
            return None
        
        result = exp.evaluate()
        
        if result != ExperimentResult.PENDING:
            exp.status = ExperimentStatus.CONCLUDED
            exp.concluded_at = datetime.utcnow()
        
        return result
    
    def rollback_experiment(self, experiment_id: str) -> bool:
        """Rollback an experiment (revert to control)."""
        if experiment_id not in self.experiments:
            return False
        
        exp = self.experiments[experiment_id]
        exp.status = ExperimentStatus.ROLLED_BACK
        exp.winner_variant_id = exp.control.variant_id
        return True
    
    # ─────────────────────────────────────────────────────────────────────
    # VARIANT ASSIGNMENT
    # ─────────────────────────────────────────────────────────────────────
    
    def get_variant_for_page(
        self,
        page_url: str,
        user_id: str,
        experiment_type: Optional[ExperimentType] = None,
    ) -> Optional[Tuple[Experiment, Variant]]:
        """Get the active variant for a user on a page."""
        
        # Check page-specific experiments
        exp_ids = self.experiments_by_page.get(page_url, [])
        
        # Also check site-wide experiments
        exp_ids.extend(self.experiments_by_page.get("*", []))
        
        for exp_id in exp_ids:
            exp = self.experiments.get(exp_id)
            if not exp:
                continue
            
            if exp.status != ExperimentStatus.RUNNING:
                continue
            
            if experiment_type and exp.experiment_type != experiment_type:
                continue
            
            variant = exp.get_variant_for_user(user_id)
            return exp, variant
        
        return None
    
    # ─────────────────────────────────────────────────────────────────────
    # TRACKING
    # ─────────────────────────────────────────────────────────────────────
    
    def track_impression(
        self,
        experiment_id: str,
        variant_id: str,
    ):
        """Track an impression."""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].record_impression(variant_id)
    
    def track_click(
        self,
        experiment_id: str,
        variant_id: str,
    ):
        """Track a click."""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].record_click(variant_id)
    
    def track_conversion(
        self,
        experiment_id: str,
        variant_id: str,
    ):
        """Track a conversion."""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].record_conversion(variant_id)
    
    # ─────────────────────────────────────────────────────────────────────
    # EVALUATION
    # ─────────────────────────────────────────────────────────────────────
    
    def evaluate_all(self) -> List[Dict]:
        """Evaluate all running experiments."""
        results = []
        
        for exp_id, exp in self.experiments.items():
            if exp.status != ExperimentStatus.RUNNING:
                continue
            
            can_conclude, reason = exp.can_conclude()
            result = exp.evaluate()
            
            results.append({
                "experiment_id": exp_id,
                "name": exp.name,
                "can_conclude": can_conclude,
                "reason": reason,
                "result": result.value,
                "confidence": exp.confidence_level,
                "improvement": exp.improvement_percent,
            })
        
        return results
    
    def auto_conclude(self) -> List[str]:
        """Auto-conclude experiments that have reached significance."""
        concluded = []
        
        for exp_id, exp in self.experiments.items():
            if exp.status != ExperimentStatus.RUNNING:
                continue
            
            can_conclude, _ = exp.can_conclude()
            if not can_conclude:
                continue
            
            result = exp.evaluate()
            
            if result in [ExperimentResult.VARIANT_WINS, ExperimentResult.CONTROL_WINS]:
                exp.status = ExperimentStatus.CONCLUDED
                exp.concluded_at = datetime.utcnow()
                concluded.append(exp_id)
        
        return concluded
    
    # ─────────────────────────────────────────────────────────────────────
    # QUERIES
    # ─────────────────────────────────────────────────────────────────────
    
    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        return self.experiments.get(experiment_id)
    
    def get_running_experiments(self) -> List[Experiment]:
        return [e for e in self.experiments.values() if e.status == ExperimentStatus.RUNNING]
    
    def get_concluded_experiments(self) -> List[Experiment]:
        return [e for e in self.experiments.values() if e.status == ExperimentStatus.CONCLUDED]
    
    def get_experiments_for_page(self, page_url: str) -> List[Experiment]:
        exp_ids = self.experiments_by_page.get(page_url, [])
        return [self.experiments[eid] for eid in exp_ids if eid in self.experiments]
    
    def get_summary(self) -> Dict:
        """Get summary of all experiments."""
        by_status = {}
        by_type = {}
        
        for exp in self.experiments.values():
            status = exp.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            exp_type = exp.experiment_type.value
            by_type[exp_type] = by_type.get(exp_type, 0) + 1
        
        winners = [
            e for e in self.experiments.values()
            if e.result == ExperimentResult.VARIANT_WINS
        ]
        
        return {
            "total_experiments": len(self.experiments),
            "by_status": by_status,
            "by_type": by_type,
            "variant_wins": len(winners),
            "avg_improvement": (
                sum(e.improvement_percent for e in winners) / len(winners)
                if winners else 0
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_experiment_manager: Optional[BlogExperimentManager] = None

def get_experiment_manager() -> BlogExperimentManager:
    """Get the global experiment manager."""
    global _experiment_manager
    if _experiment_manager is None:
        _experiment_manager = BlogExperimentManager()
    return _experiment_manager


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "ExperimentType",
    "ExperimentStatus",
    "ExperimentResult",
    "Variant",
    "Experiment",
    "BlogExperimentManager",
    "get_experiment_manager",
]
