#!/usr/bin/env python3
"""
BASE AGENT FRAMEWORK
Foundation for all Quirrely batch intelligence agents.
"""

import asyncio
import json
import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import asyncpg
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResults:
    """Results from agent analysis phase."""
    agent_name: str
    analysis_period: Tuple[datetime, datetime]
    findings: Dict[str, Any]
    confidence_score: float  # 0-1
    data_quality: float      # 0-1
    recommendations: List[Dict[str, Any]]
    raw_metrics: Dict[str, float]

@dataclass 
class OptimizationActions:
    """Actions to take based on analysis."""
    agent_name: str
    actions: List[Dict[str, Any]]
    expected_impact: Dict[str, float]
    risk_assessment: float   # 0-1
    rollback_plan: Optional[Dict[str, Any]]

@dataclass
class ExecutionReport:
    """Report from executing optimization actions."""
    agent_name: str
    actions_taken: List[Dict[str, Any]]
    actions_failed: List[Dict[str, Any]]
    execution_time: float
    immediate_impact: Dict[str, float]
    success_rate: float

@dataclass
class PerformanceMetrics:
    """Performance metrics for agent execution."""
    agent_name: str
    execution_duration: float
    analysis_accuracy: float
    optimization_impact: float
    system_improvement: Dict[str, float]
    roi_estimate: float

class BatchAgent(ABC):
    """Base class for all Quirrely batch agents."""
    
    def __init__(
        self, 
        name: str, 
        schedule_cron: str, 
        data_sources: List[str],
        db_pool: asyncpg.Pool,
        config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.schedule_cron = schedule_cron
        self.data_sources = data_sources
        self.db = db_pool
        self.config = config or {}
        self.execution_history = []
        
    async def run_full_cycle(self) -> PerformanceMetrics:
        """Execute complete agent cycle: analyze → optimize → execute → report."""
        
        start_time = datetime.now()
        logger.info(f"Starting {self.name} agent cycle")
        
        try:
            # Phase 1: Analyze
            logger.info(f"{self.name}: Starting analysis phase")
            analysis_results = await self.analyze()
            
            # Phase 2: Optimize  
            logger.info(f"{self.name}: Starting optimization phase")
            optimization_actions = await self.optimize(analysis_results)
            
            # Phase 3: Execute
            logger.info(f"{self.name}: Starting execution phase")
            execution_report = await self.execute(optimization_actions)
            
            # Phase 4: Report
            logger.info(f"{self.name}: Generating performance report")
            performance_metrics = await self.report(
                analysis_results, optimization_actions, execution_report
            )
            
            # Store execution history
            await self._store_execution_record(
                start_time, analysis_results, optimization_actions, 
                execution_report, performance_metrics
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{self.name} completed successfully in {execution_time:.2f}s")
            
            return performance_metrics
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{self.name} failed after {execution_time:.2f}s: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Store failure record
            await self._store_failure_record(start_time, str(e))
            raise
    
    @abstractmethod
    async def analyze(self) -> AnalysisResults:
        """Analyze current state and identify optimization opportunities."""
        pass
    
    @abstractmethod  
    async def optimize(self, results: AnalysisResults) -> OptimizationActions:
        """Generate optimization actions based on analysis."""
        pass
    
    @abstractmethod
    async def execute(self, actions: OptimizationActions) -> ExecutionReport:
        """Execute the optimization actions."""
        pass
    
    async def report(
        self, 
        analysis: AnalysisResults,
        actions: OptimizationActions, 
        execution: ExecutionReport
    ) -> PerformanceMetrics:
        """Generate performance metrics and reports."""
        
        # Calculate ROI estimate
        roi_estimate = self._calculate_roi(analysis, actions, execution)
        
        # Calculate system improvement
        system_improvement = await self._measure_system_improvement(analysis, execution)
        
        return PerformanceMetrics(
            agent_name=self.name,
            execution_duration=execution.execution_time,
            analysis_accuracy=analysis.confidence_score,
            optimization_impact=execution.success_rate,
            system_improvement=system_improvement,
            roi_estimate=roi_estimate
        )
    
    async def _store_execution_record(
        self,
        start_time: datetime,
        analysis: AnalysisResults,
        actions: OptimizationActions,
        execution: ExecutionReport,
        metrics: PerformanceMetrics
    ) -> None:
        """Store complete execution record in database."""
        
        execution_record = {
            "agent_name": self.name,
            "execution_start": start_time.isoformat(),
            "execution_end": datetime.now().isoformat(),
            "analysis_results": {
                "findings": analysis.findings,
                "confidence_score": analysis.confidence_score,
                "recommendations_count": len(analysis.recommendations),
                "data_quality": analysis.data_quality
            },
            "optimization_actions": {
                "actions_count": len(actions.actions),
                "expected_impact": actions.expected_impact,
                "risk_assessment": actions.risk_assessment
            },
            "execution_results": {
                "actions_taken": len(execution.actions_taken),
                "actions_failed": len(execution.actions_failed),
                "success_rate": execution.success_rate,
                "immediate_impact": execution.immediate_impact
            },
            "performance_metrics": {
                "roi_estimate": metrics.roi_estimate,
                "system_improvement": metrics.system_improvement,
                "optimization_impact": metrics.optimization_impact
            }
        }
        
        await self.db.execute("""
            INSERT INTO agent_execution_history (
                agent_name, execution_start, execution_data, 
                success, performance_score, created_at
            ) VALUES ($1, $2, $3, $4, $5, NOW())
        """, 
        self.name, 
        start_time, 
        json.dumps(execution_record),
        True,
        metrics.roi_estimate
        )
    
    async def _store_failure_record(self, start_time: datetime, error: str) -> None:
        """Store failure record in database."""
        
        failure_record = {
            "agent_name": self.name,
            "execution_start": start_time.isoformat(),
            "execution_end": datetime.now().isoformat(),
            "error": error,
            "traceback": traceback.format_exc()
        }
        
        await self.db.execute("""
            INSERT INTO agent_execution_history (
                agent_name, execution_start, execution_data, 
                success, performance_score, created_at
            ) VALUES ($1, $2, $3, $4, $5, NOW())
        """,
        self.name,
        start_time, 
        json.dumps(failure_record),
        False,
        0.0
        )
    
    def _calculate_roi(
        self, 
        analysis: AnalysisResults, 
        actions: OptimizationActions, 
        execution: ExecutionReport
    ) -> float:
        """Calculate estimated ROI for this agent execution."""
        
        # Base ROI calculation - can be overridden by specific agents
        expected_improvement = sum(actions.expected_impact.values())
        actual_improvement = sum(execution.immediate_impact.values()) 
        confidence = analysis.confidence_score
        success_rate = execution.success_rate
        
        # ROI = (actual_improvement / expected_improvement) * confidence * success_rate
        if expected_improvement > 0:
            roi = (actual_improvement / expected_improvement) * confidence * success_rate
        else:
            roi = 0.0
            
        return max(0.0, min(10.0, roi))  # Clamp to 0-10 range
    
    async def _measure_system_improvement(
        self, 
        analysis: AnalysisResults, 
        execution: ExecutionReport
    ) -> Dict[str, float]:
        """Measure actual system improvement after execution."""
        
        # Base implementation - specific agents should override
        return {
            "general_improvement": execution.success_rate,
            "data_quality_improvement": 0.0,
            "user_experience_improvement": 0.0,
            "revenue_impact": 0.0
        }
    
    async def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history for this agent."""
        
        records = await self.db.fetch("""
            SELECT execution_start, execution_data, success, performance_score
            FROM agent_execution_history 
            WHERE agent_name = $1 
            ORDER BY execution_start DESC 
            LIMIT $2
        """, self.name, limit)
        
        return [
            {
                "execution_start": record["execution_start"],
                "execution_data": json.loads(record["execution_data"]),
                "success": record["success"],
                "performance_score": record["performance_score"]
            }
            for record in records
        ]
    
    async def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get performance trends over specified period."""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        records = await self.db.fetch("""
            SELECT execution_start, performance_score, success
            FROM agent_execution_history 
            WHERE agent_name = $1 AND execution_start >= $2
            ORDER BY execution_start ASC
        """, self.name, cutoff_date)
        
        if not records:
            return {"trend": "no_data", "executions": 0}
        
        scores = [r["performance_score"] for r in records if r["success"]]
        success_rate = len([r for r in records if r["success"]]) / len(records)
        
        trend = "stable"
        if len(scores) >= 3:
            recent_avg = sum(scores[-3:]) / 3
            historical_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else recent_avg
            
            if recent_avg > historical_avg * 1.1:
                trend = "improving"
            elif recent_avg < historical_avg * 0.9:
                trend = "declining"
        
        return {
            "trend": trend,
            "executions": len(records),
            "success_rate": success_rate,
            "avg_performance": sum(scores) / len(scores) if scores else 0,
            "recent_performance": sum(scores[-3:]) / 3 if len(scores) >= 3 else (scores[-1] if scores else 0)
        }


# ═══════════════════════════════════════════════════════════════════════════
# DATABASE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

async def initialize_agent_system(db_pool: asyncpg.Pool) -> None:
    """Initialize database tables for agent system."""
    
    # Agent execution history
    await db_pool.execute("""
        CREATE TABLE IF NOT EXISTS agent_execution_history (
            id SERIAL PRIMARY KEY,
            agent_name TEXT NOT NULL,
            execution_start TIMESTAMP NOT NULL,
            execution_data JSONB NOT NULL,
            success BOOLEAN NOT NULL,
            performance_score NUMERIC DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Agent configuration
    await db_pool.execute("""
        CREATE TABLE IF NOT EXISTS agent_configurations (
            id SERIAL PRIMARY KEY,
            agent_name TEXT UNIQUE NOT NULL,
            config_data JSONB NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Agent performance summaries (for quick dashboard access)
    await db_pool.execute("""
        CREATE TABLE IF NOT EXISTS agent_performance_summary (
            agent_name TEXT PRIMARY KEY,
            total_executions INTEGER DEFAULT 0,
            successful_executions INTEGER DEFAULT 0,
            last_execution TIMESTAMP,
            avg_performance_score NUMERIC DEFAULT 0.0,
            trend TEXT DEFAULT 'stable',
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Create indexes for performance
    await db_pool.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_history_name_date 
        ON agent_execution_history(agent_name, execution_start DESC);
    """)
    
    await db_pool.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_history_performance 
        ON agent_execution_history(performance_score DESC, success);
    """)


# ═══════════════════════════════════════════════════════════════════════════
# AGENT REGISTRY AND MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

class AgentRegistry:
    """Central registry for managing all batch agents."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool
        self.agents = {}
        
    def register_agent(self, agent: BatchAgent) -> None:
        """Register an agent with the system."""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    async def run_agent(self, agent_name: str) -> PerformanceMetrics:
        """Run a specific agent by name."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        return await agent.run_full_cycle()
    
    async def run_all_agents(self) -> Dict[str, PerformanceMetrics]:
        """Run all registered agents."""
        results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                results[agent_name] = await agent.run_full_cycle()
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {str(e)}")
                results[agent_name] = None
        
        return results
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall agent system health metrics."""
        
        # Get summary stats
        summary_stats = await self.db.fetch("""
            SELECT 
                agent_name,
                COUNT(*) as total_executions,
                COUNT(*) FILTER (WHERE success) as successful_executions,
                MAX(execution_start) as last_execution,
                AVG(performance_score) FILTER (WHERE success) as avg_performance
            FROM agent_execution_history 
            WHERE execution_start >= NOW() - INTERVAL '30 days'
            GROUP BY agent_name
        """)
        
        agent_health = {}
        for stat in summary_stats:
            success_rate = stat["successful_executions"] / stat["total_executions"]
            agent_health[stat["agent_name"]] = {
                "success_rate": success_rate,
                "avg_performance": float(stat["avg_performance"]) if stat["avg_performance"] else 0.0,
                "last_execution": stat["last_execution"],
                "total_executions": stat["total_executions"],
                "status": "healthy" if success_rate > 0.8 else "degraded" if success_rate > 0.5 else "unhealthy"
            }
        
        overall_health = "healthy"
        if any(agent["status"] == "unhealthy" for agent in agent_health.values()):
            overall_health = "unhealthy"
        elif any(agent["status"] == "degraded" for agent in agent_health.values()):
            overall_health = "degraded"
        
        return {
            "overall_health": overall_health,
            "registered_agents": len(self.agents),
            "active_agents": len(agent_health),
            "agent_details": agent_health
        }