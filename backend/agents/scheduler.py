#!/usr/bin/env python3
"""
BATCH AGENT SCHEDULER
Manages scheduling and execution of all Quirrely batch agents.
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any
import asyncpg

from .base_agent import initialize_agent_system, AgentRegistry
from .conversion_optimizer import ConversionOptimizationAgent
from .lncp_pattern_discovery import LNCPPatternDiscoveryAgent
from .usage_pattern_analyzer import UsagePatternAnalyzer

logger = logging.getLogger(__name__)

class BatchAgentScheduler:
    """Centralized scheduler for all batch agents."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool
        self.registry = AgentRegistry(db_pool)
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the agent system and register all agents."""
        
        if self.initialized:
            return
        
        logger.info("Initializing batch agent system")
        
        # Initialize database tables
        await initialize_agent_system(self.db)
        
        # Create missing tables for agent operations
        await self._create_agent_tables()
        
        # Register Phase 1 agents (revenue-critical)
        self.registry.register_agent(ConversionOptimizationAgent(self.db))
        self.registry.register_agent(LNCPPatternDiscoveryAgent(self.db))
        self.registry.register_agent(UsagePatternAnalyzer(self.db))
        
        self.initialized = True
        logger.info("Agent system initialized successfully")
    
    async def run_agent_by_name(self, agent_name: str) -> Dict[str, Any]:
        """Run a specific agent by name."""
        
        await self.initialize()
        
        logger.info(f"Starting execution of {agent_name}")
        
        try:
            performance_metrics = await self.registry.run_agent(agent_name)
            
            result = {
                "status": "success",
                "agent_name": agent_name,
                "execution_time": datetime.now().isoformat(),
                "performance_metrics": {
                    "roi_estimate": performance_metrics.roi_estimate,
                    "optimization_impact": performance_metrics.optimization_impact,
                    "system_improvement": performance_metrics.system_improvement
                }
            }
            
            logger.info(f"{agent_name} completed successfully (ROI: {performance_metrics.roi_estimate:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"{agent_name} execution failed: {str(e)}")
            
            result = {
                "status": "failed",
                "agent_name": agent_name,
                "execution_time": datetime.now().isoformat(),
                "error": str(e)
            }
            
            return result
    
    async def run_all_agents(self) -> Dict[str, Any]:
        """Run all registered agents."""
        
        await self.initialize()
        
        logger.info("Starting execution of all agents")
        
        results = await self.registry.run_all_agents()
        
        summary = {
            "execution_time": datetime.now().isoformat(),
            "total_agents": len(results),
            "successful_agents": len([r for r in results.values() if r is not None]),
            "failed_agents": len([r for r in results.values() if r is None]),
            "agent_results": {}
        }
        
        for agent_name, metrics in results.items():
            if metrics:
                summary["agent_results"][agent_name] = {
                    "status": "success",
                    "roi_estimate": metrics.roi_estimate,
                    "optimization_impact": metrics.optimization_impact
                }
            else:
                summary["agent_results"][agent_name] = {
                    "status": "failed"
                }
        
        logger.info(f"All agents completed: {summary['successful_agents']}/{summary['total_agents']} successful")
        return summary
    
    async def get_agent_health_status(self) -> Dict[str, Any]:
        """Get health status of all agents."""
        
        await self.initialize()
        return await self.registry.get_system_health()
    
    async def _create_agent_tables(self) -> None:
        """Create additional tables needed for agent operations."""
        
        # Agent configuration changes tracking
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS agent_configuration_changes (
                id SERIAL PRIMARY KEY,
                agent_name TEXT NOT NULL,
                change_type TEXT NOT NULL,
                change_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # A/B tests tracking
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS ab_tests (
                id SERIAL PRIMARY KEY,
                test_name TEXT UNIQUE NOT NULL,
                agent_name TEXT NOT NULL,
                test_config JSONB NOT NULL,
                status TEXT DEFAULT 'active',
                results JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP
            )
        """)
        
        # LNCP patterns storage
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS lncp_patterns (
                id SERIAL PRIMARY KEY,
                pattern_id TEXT UNIQUE NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data JSONB NOT NULL,
                confidence_score NUMERIC NOT NULL,
                sample_size INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # LNCP model updates tracking
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS lncp_model_updates (
                id SERIAL PRIMARY KEY,
                update_type TEXT NOT NULL,
                update_data JSONB NOT NULL,
                agent_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Tier transition history (if not exists)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS tier_transition_history (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                from_tier TEXT NOT NULL,
                to_tier TEXT NOT NULL,
                transition_date TIMESTAMP NOT NULL,
                trigger_event TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Progression optimizations
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS progression_optimizations (
                id SERIAL PRIMARY KEY,
                from_tier TEXT NOT NULL,
                to_tier TEXT NOT NULL,
                optimization_data JSONB NOT NULL,
                agent_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Temporal optimizations
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS temporal_optimizations (
                id SERIAL PRIMARY KEY,
                optimization_type TEXT NOT NULL,
                optimization_data JSONB NOT NULL,
                agent_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # LNCP analysis results (if not exists)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS lncp_analysis_results (
                id SERIAL PRIMARY KEY,
                writing_sample_id TEXT NOT NULL,
                confidence_score NUMERIC NOT NULL,
                analysis_results JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Writing samples table (if not exists)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS writing_samples (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                content TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes for performance
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_config_changes_name_date 
            ON agent_configuration_changes(agent_name, created_at DESC);
        """)
        
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_lncp_patterns_type_active 
            ON lncp_patterns(pattern_type, is_active);
        """)
        
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_tier_transitions_user_date 
            ON tier_transition_history(user_id, transition_date DESC);
        """)
        
        logger.info("Agent database tables created successfully")


# ═══════════════════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    """Command line interface for agent execution."""
    
    if len(sys.argv) < 2:
        print("Usage: python scheduler.py <command> [agent_name]")
        print("Commands:")
        print("  run <agent_name>  - Run specific agent")
        print("  run-all          - Run all agents")
        print("  status           - Get agent health status")
        print("  list             - List available agents")
        return
    
    command = sys.argv[1]
    
    # Database connection (would come from environment)
    try:
        db_pool = await asyncpg.create_pool(
            "postgresql://quirrely_user:quirrely_pass@localhost/quirrely"
        )
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        print("Using default connection string - update for your environment")
        return
    
    scheduler = BatchAgentScheduler(db_pool)
    
    try:
        if command == "run" and len(sys.argv) >= 3:
            agent_name = sys.argv[2]
            result = await scheduler.run_agent_by_name(agent_name)
            print(f"Agent execution result: {result}")
            
        elif command == "run-all":
            result = await scheduler.run_all_agents()
            print(f"All agents execution result: {result}")
            
        elif command == "status":
            health = await scheduler.get_agent_health_status()
            print(f"Agent system health: {health}")
            
        elif command == "list":
            await scheduler.initialize()
            agents = list(scheduler.registry.agents.keys())
            print(f"Available agents: {agents}")
            
        else:
            print(f"Unknown command: {command}")
            
    except Exception as e:
        print(f"Execution failed: {str(e)}")
        
    finally:
        await db_pool.close()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())