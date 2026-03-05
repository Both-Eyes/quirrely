#!/usr/bin/env python3
"""
LNCP META/BLOG v1.0
Blog optimization system for top-of-funnel SEO.

Components:
- config: Tunable blog parameters (meta, CTA, content)
- tracker: Page view and engagement tracking
- cta_tracker: CTA performance tracking

Usage:
    from lncp.meta.blog import (
        get_blog_config,
        get_blog_tracker,
        get_cta_tracker,
    )
    
    # Track a page view
    tracker = get_blog_tracker()
    view = tracker.track_page_view(
        page_url="/blog/how-assertive-open-writers-write",
        session_id="sess_123",
        visitor_id="vis_abc",
        source=TrafficSource.ORGANIC,
        profile_style="assertive",
        profile_certitude="open",
    )
    
    # Track CTA click
    cta = get_cta_tracker()
    cta.track_click(
        page_url="/blog/how-assertive-open-writers-write",
        view_id=view.view_id,
        session_id="sess_123",
        visitor_id="vis_abc",
        variant_id="discover",
        placement=CTAPlacement.AFTER_INTRO,
    )
"""

__version__ = "1.0.0"

# Config
from .config import (
    CTAPlacement,
    CTAStyle,
    MetaTemplate,
    CTAVariant,
    ContentConfig,
    SEOConfig,
    BlogConfigStore,
    META_TEMPLATES,
    CTA_VARIANTS,
    get_blog_config,
)

# Tracker
from .tracker import (
    TrafficSource,
    DeviceType,
    PageView,
    PageMetrics,
    BlogTracker,
    get_blog_tracker,
)

# CTA Tracker
from .cta_tracker import (
    CTAEventType,
    CTAEvent,
    CTAPerformance,
    CTATracker,
    get_cta_tracker,
)

# GSC Integration
from .gsc import (
    SearchType,
    DeviceDimension,
    SearchMetrics,
    PageSearchData,
    QuerySearchData,
    GSCSiteData,
    GSCClient,
    GSCSimulator,
    GSCDataStore,
    GSCAnalyzer,
    fetch_gsc_data,
    get_gsc_store,
)

# GSC Real API (optional - requires google-api-python-client)
try:
    from .gsc_real import (
        GSCConfig,
        RealGSCClient,
        GSCDataFetcher,
        fetch_real_gsc_data,
        check_gsc_credentials,
    )
    GSC_REAL_AVAILABLE = True
except ImportError:
    GSC_REAL_AVAILABLE = False
    # Provide stubs
    GSCConfig = None
    RealGSCClient = None
    GSCDataFetcher = None
    fetch_real_gsc_data = None
    check_gsc_credentials = None

# Blog Action Classifier
from .classifier import (
    BlogActionLane,
    BlogActionDomain,
    BlogActionType,
    RiskLevel,
    Priority,
    BlogAction,
    BlogActionClassifier,
    BlogActionGenerator,
    BlogActionOrchestrator,
    get_blog_orchestrator,
)

# A/B Testing
from .ab_testing import (
    ExperimentType,
    ExperimentStatus,
    ExperimentResult,
    Variant,
    Experiment,
    BlogExperimentManager,
    get_experiment_manager,
)

# Feedback Loop
from .feedback import (
    MetricType,
    PredictionAccuracy,
    Prediction,
    CalibrationFactor,
    ActionOutcome,
    BlogFeedbackCollector,
    BlogCalibrator,
    BlogInsightGenerator,
    BlogFeedbackLoop,
    get_blog_feedback_loop,
)

__all__ = [
    # Version
    "__version__",
    
    # Config
    "CTAPlacement",
    "CTAStyle",
    "MetaTemplate",
    "CTAVariant",
    "ContentConfig",
    "SEOConfig",
    "BlogConfigStore",
    "META_TEMPLATES",
    "CTA_VARIANTS",
    "get_blog_config",
    
    # Tracker
    "TrafficSource",
    "DeviceType",
    "PageView",
    "PageMetrics",
    "BlogTracker",
    "get_blog_tracker",
    
    # CTA Tracker
    "CTAEventType",
    "CTAEvent",
    "CTAPerformance",
    "CTATracker",
    "get_cta_tracker",
    
    # GSC Integration
    "SearchType",
    "DeviceDimension",
    "SearchMetrics",
    "PageSearchData",
    "QuerySearchData",
    "GSCSiteData",
    "GSCClient",
    "GSCSimulator",
    "GSCDataStore",
    "GSCAnalyzer",
    "fetch_gsc_data",
    "get_gsc_store",
    
    # GSC Real API
    "GSC_REAL_AVAILABLE",
    "GSCConfig",
    "RealGSCClient",
    "GSCDataFetcher",
    "fetch_real_gsc_data",
    "check_gsc_credentials",
    
    # Blog Action Classifier
    "BlogActionLane",
    "BlogActionDomain",
    "BlogActionType",
    "RiskLevel",
    "Priority",
    "BlogAction",
    "BlogActionClassifier",
    "BlogActionGenerator",
    "BlogActionOrchestrator",
    "get_blog_orchestrator",
    
    # A/B Testing
    "ExperimentType",
    "ExperimentStatus",
    "ExperimentResult",
    "Variant",
    "Experiment",
    "BlogExperimentManager",
    "get_experiment_manager",
    
    # Feedback Loop
    "MetricType",
    "PredictionAccuracy",
    "Prediction",
    "CalibrationFactor",
    "ActionOutcome",
    "BlogFeedbackCollector",
    "BlogCalibrator",
    "BlogInsightGenerator",
    "BlogFeedbackLoop",
    "get_blog_feedback_loop",
]
