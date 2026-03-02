#!/usr/bin/env python3
"""
LNCP META: ML MODELS v5.0
Simple regression models for prediction and signal discovery.

Models:
- SuccessPredictor: Logistic regression for action success
- ImpactPredictor: Linear regression for expected impact

Signal Discovery:
- Correlation analysis between signals and outcomes
- Feature importance ranking
- Signal proposal generation
"""

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# MODEL TYPES
# ═══════════════════════════════════════════════════════════════════════════

class ModelType(str, Enum):
    SUCCESS_PREDICTOR = "success_predictor"
    IMPACT_PREDICTOR = "impact_predictor"


class ModelStatus(str, Enum):
    UNTRAINED = "untrained"
    TRAINED = "trained"
    STALE = "stale"


@dataclass
class ModelMetadata:
    model_type: ModelType
    version: str
    trained_at: datetime
    training_samples: int
    accuracy: float
    mse: float
    features_used: List[str]
    status: ModelStatus = ModelStatus.TRAINED


@dataclass
class FeatureImportance:
    feature_name: str
    importance: float
    direction: str


@dataclass
class Prediction:
    model_type: ModelType
    input_features: Dict[str, float]
    prediction: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════
# SIMPLE REGRESSION
# ═══════════════════════════════════════════════════════════════════════════

class SimpleLinearRegression:
    def __init__(self):
        self.weights: List[float] = []
        self.bias: float = 0.0
        self.feature_names: List[str] = []
        self.is_trained = False
    
    def fit(self, X: List[Dict[str, float]], y: List[float], lr: float = 0.01, iters: int = 1000):
        if not X or not y:
            return
        self.feature_names = list(X[0].keys())
        n_features = len(self.feature_names)
        n_samples = len(X)
        self.weights = [0.0] * n_features
        self.bias = 0.0
        X_matrix = [[x.get(f, 0) for f in self.feature_names] for x in X]
        
        for _ in range(iters):
            preds = [self.bias + sum(w * x for w, x in zip(self.weights, row)) for row in X_matrix]
            errors = [p - a for p, a in zip(preds, y)]
            self.bias -= lr * (sum(errors) / n_samples)
            for j in range(n_features):
                grad = sum(errors[i] * X_matrix[i][j] for i in range(n_samples)) / n_samples
                self.weights[j] -= lr * grad
        self.is_trained = True
    
    def predict(self, X: Dict[str, float]) -> float:
        if not self.is_trained:
            return 0.0
        features = [X.get(f, 0) for f in self.feature_names]
        return self.bias + sum(w * x for w, x in zip(self.weights, features))
    
    def get_feature_importance(self) -> List[FeatureImportance]:
        if not self.is_trained:
            return []
        max_w = max(abs(w) for w in self.weights) or 1
        return [FeatureImportance(n, abs(w)/max_w, "positive" if w > 0 else "negative") 
                for n, w in zip(self.feature_names, self.weights)]


class SimpleLogisticRegression:
    def __init__(self):
        self.weights: List[float] = []
        self.bias: float = 0.0
        self.feature_names: List[str] = []
        self.is_trained = False
    
    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1 / (1 + math.exp(-max(-500, min(500, x))))
    
    def fit(self, X: List[Dict[str, float]], y: List[int], lr: float = 0.1, iters: int = 1000):
        if not X or not y:
            return
        self.feature_names = list(X[0].keys())
        n_features = len(self.feature_names)
        n_samples = len(X)
        self.weights = [0.0] * n_features
        self.bias = 0.0
        X_matrix = [[x.get(f, 0) for f in self.feature_names] for x in X]
        
        for _ in range(iters):
            preds = [self._sigmoid(self.bias + sum(w * x for w, x in zip(self.weights, row))) for row in X_matrix]
            self.bias -= lr * sum(preds[i] - y[i] for i in range(n_samples)) / n_samples
            for j in range(n_features):
                grad = sum((preds[i] - y[i]) * X_matrix[i][j] for i in range(n_samples)) / n_samples
                self.weights[j] -= lr * grad
        self.is_trained = True
    
    def predict_proba(self, X: Dict[str, float]) -> float:
        if not self.is_trained:
            return 0.5
        features = [X.get(f, 0) for f in self.feature_names]
        return self._sigmoid(self.bias + sum(w * x for w, x in zip(self.weights, features)))
    
    def predict(self, X: Dict[str, float], threshold: float = 0.5) -> int:
        return 1 if self.predict_proba(X) >= threshold else 0
    
    def get_feature_importance(self) -> List[FeatureImportance]:
        if not self.is_trained:
            return []
        max_w = max(abs(w) for w in self.weights) or 1
        return [FeatureImportance(n, abs(w)/max_w, "positive" if w > 0 else "negative")
                for n, w in zip(self.feature_names, self.weights)]


# ═══════════════════════════════════════════════════════════════════════════
# PREDICTORS
# ═══════════════════════════════════════════════════════════════════════════

class SuccessPredictor:
    def __init__(self):
        self.model = SimpleLogisticRegression()
        self.metadata: Optional[ModelMetadata] = None
        self._version = 0
    
    def train(self, data: List[Dict]) -> ModelMetadata:
        X = [d["features"] for d in data]
        y = [d["success"] for d in data]
        self.model.fit(X, y)
        self._version += 1
        correct = sum(1 for d in data if self.model.predict(d["features"]) == d["success"])
        acc = correct / len(data) if data else 0
        self.metadata = ModelMetadata(ModelType.SUCCESS_PREDICTOR, f"v{self._version}",
            datetime.utcnow(), len(data), acc, 0, self.model.feature_names)
        return self.metadata
    
    def predict(self, features: Dict[str, float]) -> Prediction:
        proba = self.model.predict_proba(features)
        return Prediction(ModelType.SUCCESS_PREDICTOR, features, proba, abs(proba - 0.5) * 2)
    
    def get_feature_importance(self) -> List[FeatureImportance]:
        return self.model.get_feature_importance()


class ImpactPredictor:
    def __init__(self):
        self.model = SimpleLinearRegression()
        self.metadata: Optional[ModelMetadata] = None
        self._version = 0
    
    def train(self, data: List[Dict]) -> ModelMetadata:
        X = [d["features"] for d in data]
        y = [d["impact"] for d in data]
        self.model.fit(X, y)
        self._version += 1
        preds = [self.model.predict(d["features"]) for d in data]
        mse = sum((p - a) ** 2 for p, a in zip(preds, y)) / len(y) if y else 0
        self.metadata = ModelMetadata(ModelType.IMPACT_PREDICTOR, f"v{self._version}",
            datetime.utcnow(), len(data), 0, mse, self.model.feature_names)
        return self.metadata
    
    def predict(self, features: Dict[str, float]) -> Prediction:
        pred = self.model.predict(features)
        return Prediction(ModelType.IMPACT_PREDICTOR, features, pred, 0.7)
    
    def get_feature_importance(self) -> List[FeatureImportance]:
        return self.model.get_feature_importance()


# ═══════════════════════════════════════════════════════════════════════════
# SIGNAL DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SignalProposal:
    signal_name: str
    signal_type: str
    description: str
    evidence: Dict[str, Any]
    expected_benefit: str
    priority: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class SignalAnalyzer:
    def __init__(self):
        self.signal_correlations: Dict[str, float] = {}
        self.proposals: List[SignalProposal] = []
    
    def analyze_correlations(self, data: List[Dict], outcome_key: str) -> Dict[str, float]:
        if not data:
            return {}
        signal_keys = {k for d in data for k in d.keys() if k != outcome_key and isinstance(d.get(k), (int, float))}
        outcomes = [d.get(outcome_key, 0) for d in data]
        o_mean = sum(outcomes) / len(outcomes)
        o_std = math.sqrt(sum((o - o_mean) ** 2 for o in outcomes) / len(outcomes)) or 1
        
        correlations = {}
        for sig in signal_keys:
            vals = [d.get(sig, 0) for d in data]
            v_mean = sum(vals) / len(vals)
            v_std = math.sqrt(sum((v - v_mean) ** 2 for v in vals) / len(vals)) or 1
            cov = sum((v - v_mean) * (o - o_mean) for v, o in zip(vals, outcomes)) / len(vals)
            correlations[sig] = cov / (v_std * o_std)
        
        self.signal_correlations = correlations
        return correlations
    
    def identify_weak_signals(self, threshold: float = 0.1) -> List[str]:
        return [s for s, c in self.signal_correlations.items() if abs(c) < threshold]
    
    def identify_strong_signals(self, threshold: float = 0.3) -> List[str]:
        return [s for s, c in self.signal_correlations.items() if abs(c) >= threshold]
    
    def generate_proposals(self, current_signals: List[str], importances: List[FeatureImportance]) -> List[SignalProposal]:
        proposals = []
        for sig in self.identify_weak_signals():
            if sig in current_signals:
                proposals.append(SignalProposal(sig, "removal", f"Weak correlation: {self.signal_correlations.get(sig, 0):.2f}",
                    {"correlation": self.signal_correlations.get(sig, 0)}, "Reduce noise", "low"))
        for imp in importances:
            if imp.importance > 0.5:
                proposals.append(SignalProposal(imp.feature_name, "weighting_change",
                    f"High importance: {imp.importance:.2f}", {"importance": imp.importance},
                    "Improve accuracy", "medium"))
        self.proposals.extend(proposals)
        return proposals


# ═══════════════════════════════════════════════════════════════════════════
# MODEL MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class ModelManager:
    def __init__(self):
        self.success_predictor = SuccessPredictor()
        self.impact_predictor = ImpactPredictor()
        self.signal_analyzer = SignalAnalyzer()
        self.training_history: List[Dict] = []
        self.prediction_log: List[Prediction] = []
    
    def train_all(self, success_data: List[Dict], impact_data: List[Dict]) -> Dict[str, ModelMetadata]:
        results = {}
        if success_data:
            results["success"] = self.success_predictor.train(success_data)
        if impact_data:
            results["impact"] = self.impact_predictor.train(impact_data)
        self.training_history.append({"timestamp": datetime.utcnow().isoformat(),
            "models": list(results.keys()), "samples": {"success": len(success_data), "impact": len(impact_data)}})
        return results
    
    def predict_action(self, features: Dict[str, float]) -> Dict[str, Prediction]:
        preds = {"success": self.success_predictor.predict(features),
                 "impact": self.impact_predictor.predict(features)}
        self.prediction_log.extend(preds.values())
        return preds
    
    def analyze_signals(self, outcome_data: List[Dict]) -> Dict:
        corrs = self.signal_analyzer.analyze_correlations(outcome_data, "success")
        imps = self.success_predictor.get_feature_importance() + self.impact_predictor.get_feature_importance()
        props = self.signal_analyzer.generate_proposals(list(corrs.keys()), imps)
        return {"correlations": corrs, "weak": self.signal_analyzer.identify_weak_signals(),
                "strong": self.signal_analyzer.identify_strong_signals(), "proposals": len(props)}
    
    def get_summary(self) -> Dict:
        return {"success_trained": self.success_predictor.model.is_trained,
                "impact_trained": self.impact_predictor.model.is_trained,
                "training_runs": len(self.training_history),
                "predictions": len(self.prediction_log),
                "signal_proposals": len(self.signal_analyzer.proposals)}


_model_manager: Optional[ModelManager] = None

def get_model_manager() -> ModelManager:
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


__all__ = ["ModelType", "ModelStatus", "ModelMetadata", "FeatureImportance", "Prediction",
           "SuccessPredictor", "ImpactPredictor", "SignalProposal", "SignalAnalyzer",
           "ModelManager", "get_model_manager"]
