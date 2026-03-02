#!/usr/bin/env python3
"""
LNCP Scheduler v1.0
Automated optimization cycle runner.

Supports multiple scheduling backends:
1. Simple loop (for development/testing)
2. APScheduler (for production)
3. Cron-compatible CLI (for system cron)

Usage:
    # Run once (for cron)
    python scheduler.py --once
    
    # Run continuously (for daemon)
    python scheduler.py --daemon --interval 60
    
    # Run with APScheduler
    python scheduler.py --scheduler
"""

import argparse
import os
import sys
import time
import signal
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from pathlib import Path

# Add LNCP to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lncp.meta import (
    get_unified_orchestrator,
    UnifiedMode,
    Domain,
)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SchedulerConfig:
    """Configuration for the scheduler."""
    
    # Cycle settings
    cycle_interval_minutes: int = 60  # Run every hour
    domains: str = "all"  # "all", "app", "blog"
    mode: str = "auto_safe"  # "observe_only", "suggest", "auto_safe", "full_auto"
    
    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # State persistence
    state_file: str = "scheduler_state.json"
    
    # Notifications (placeholders for future implementation)
    notify_on_error: bool = True
    notify_on_insights: bool = True
    slack_webhook: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)
    
    @classmethod
    def from_env(cls) -> 'SchedulerConfig':
        """Create config from environment variables."""
        return cls(
            cycle_interval_minutes=int(os.environ.get('LNCP_CYCLE_INTERVAL', '60')),
            domains=os.environ.get('LNCP_DOMAINS', 'all'),
            mode=os.environ.get('LNCP_MODE', 'auto_safe'),
            log_level=os.environ.get('LNCP_LOG_LEVEL', 'INFO'),
            log_file=os.environ.get('LNCP_LOG_FILE'),
            state_file=os.environ.get('LNCP_STATE_FILE', 'scheduler_state.json'),
            slack_webhook=os.environ.get('LNCP_SLACK_WEBHOOK'),
        )


# ═══════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════

def setup_logging(config: SchedulerConfig) -> logging.Logger:
    """Set up logging for the scheduler."""
    logger = logging.getLogger('lncp_scheduler')
    logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (if configured)
    if config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


# ═══════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SchedulerState:
    """Persistent state for the scheduler."""
    last_run: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_actions_applied: int = 0
    
    def save(self, path: str):
        """Save state to file."""
        data = {
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'last_success': self.last_success.isoformat() if self.last_success else None,
            'last_error': self.last_error,
            'total_runs': self.total_runs,
            'successful_runs': self.successful_runs,
            'failed_runs': self.failed_runs,
            'total_actions_applied': self.total_actions_applied,
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'SchedulerState':
        """Load state from file."""
        if not os.path.exists(path):
            return cls()
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            return cls(
                last_run=datetime.fromisoformat(data['last_run']) if data.get('last_run') else None,
                last_success=datetime.fromisoformat(data['last_success']) if data.get('last_success') else None,
                last_error=data.get('last_error'),
                total_runs=data.get('total_runs', 0),
                successful_runs=data.get('successful_runs', 0),
                failed_runs=data.get('failed_runs', 0),
                total_actions_applied=data.get('total_actions_applied', 0),
            )
        except Exception:
            return cls()


# ═══════════════════════════════════════════════════════════════════════════
# CYCLE RUNNER
# ═══════════════════════════════════════════════════════════════════════════

class CycleRunner:
    """
    Runs optimization cycles with retry logic and state tracking.
    """
    
    def __init__(self, config: SchedulerConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.state = SchedulerState.load(config.state_file)
        self.orchestrator = get_unified_orchestrator()
        
        # Set orchestrator mode
        mode_map = {
            'observe_only': UnifiedMode.OBSERVE_ONLY,
            'suggest': UnifiedMode.SUGGEST,
            'auto_safe': UnifiedMode.AUTO_SAFE,
            'full_auto': UnifiedMode.FULL_AUTO,
        }
        self.orchestrator.set_mode(mode_map.get(config.mode, UnifiedMode.AUTO_SAFE))
        
        # Set domain
        self.domain = {
            'all': Domain.ALL,
            'app': Domain.APP,
            'blog': Domain.BLOG,
        }.get(config.domains, Domain.ALL)
    
    def run_cycle(self) -> Dict:
        """Run a single optimization cycle with retry logic."""
        self.state.total_runs += 1
        self.state.last_run = datetime.utcnow()
        
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.info(f"Starting optimization cycle (attempt {attempt + 1}/{self.config.max_retries})")
                
                # Run the cycle
                result = self.orchestrator.run_cycle(force=True, domains=self.domain)
                
                # Update state
                self.state.successful_runs += 1
                self.state.last_success = datetime.utcnow()
                self.state.last_error = None
                self.state.total_actions_applied += result.total_applied
                
                self.logger.info(f"Cycle complete: {result.total_applied} applied, {len(result.pending_review)} pending review")
                
                # Save state
                self.state.save(self.config.state_file)
                
                return {
                    'success': True,
                    'cycle_id': result.cycle_id,
                    'applied': result.total_applied,
                    'pending_review': len(result.pending_review),
                    'insights': len(result.insights),
                }
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Cycle failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.config.max_retries - 1:
                    self.logger.info(f"Retrying in {self.config.retry_delay_seconds} seconds...")
                    time.sleep(self.config.retry_delay_seconds)
        
        # All retries failed
        self.state.failed_runs += 1
        self.state.last_error = last_error
        self.state.save(self.config.state_file)
        
        self.logger.error(f"Cycle failed after {self.config.max_retries} attempts")
        
        return {
            'success': False,
            'error': last_error,
        }
    
    def should_run(self) -> bool:
        """Check if enough time has passed since last run."""
        if self.state.last_run is None:
            return True
        
        elapsed = datetime.utcnow() - self.state.last_run
        return elapsed >= timedelta(minutes=self.config.cycle_interval_minutes)
    
    def get_status(self) -> Dict:
        """Get current scheduler status."""
        return {
            'last_run': self.state.last_run.isoformat() if self.state.last_run else None,
            'last_success': self.state.last_success.isoformat() if self.state.last_success else None,
            'last_error': self.state.last_error,
            'total_runs': self.state.total_runs,
            'successful_runs': self.state.successful_runs,
            'failed_runs': self.state.failed_runs,
            'success_rate': self.state.successful_runs / self.state.total_runs if self.state.total_runs > 0 else 0,
            'total_actions_applied': self.state.total_actions_applied,
            'config': {
                'interval_minutes': self.config.cycle_interval_minutes,
                'domains': self.config.domains,
                'mode': self.config.mode,
            },
        }


# ═══════════════════════════════════════════════════════════════════════════
# SCHEDULER BACKENDS
# ═══════════════════════════════════════════════════════════════════════════

class SimpleLoopScheduler:
    """
    Simple loop-based scheduler for development and simple deployments.
    """
    
    def __init__(self, runner: CycleRunner, logger: logging.Logger):
        self.runner = runner
        self.logger = logger
        self.running = False
    
    def start(self):
        """Start the scheduler loop."""
        self.running = True
        self.logger.info("Starting simple loop scheduler")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
        while self.running:
            if self.runner.should_run():
                self.runner.run_cycle()
            
            # Sleep for 1 minute between checks
            time.sleep(60)
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        self.logger.info("Scheduler stopped")
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()


class APSchedulerBackend:
    """
    APScheduler-based scheduler for production use.
    
    Requires: pip install apscheduler
    """
    
    def __init__(self, runner: CycleRunner, config: SchedulerConfig, logger: logging.Logger):
        self.runner = runner
        self.config = config
        self.logger = logger
        self.scheduler = None
    
    def start(self):
        """Start the APScheduler."""
        try:
            from apscheduler.schedulers.blocking import BlockingScheduler
            from apscheduler.triggers.interval import IntervalTrigger
        except ImportError:
            self.logger.error("APScheduler not installed. Run: pip install apscheduler")
            return
        
        self.scheduler = BlockingScheduler()
        
        # Add job
        self.scheduler.add_job(
            self.runner.run_cycle,
            trigger=IntervalTrigger(minutes=self.config.cycle_interval_minutes),
            id='optimization_cycle',
            name='LNCP Optimization Cycle',
            replace_existing=True,
        )
        
        self.logger.info(f"Starting APScheduler (interval: {self.config.cycle_interval_minutes} minutes)")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Scheduler stopped")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='LNCP Optimization Scheduler')
    
    # Run modes
    parser.add_argument('--once', action='store_true', help='Run once and exit (for cron)')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon with simple loop')
    parser.add_argument('--scheduler', action='store_true', help='Run with APScheduler')
    parser.add_argument('--status', action='store_true', help='Show scheduler status')
    
    # Configuration
    parser.add_argument('--interval', type=int, default=60, help='Cycle interval in minutes')
    parser.add_argument('--domains', choices=['all', 'app', 'blog'], default='all', help='Domains to optimize')
    parser.add_argument('--mode', choices=['observe_only', 'suggest', 'auto_safe', 'full_auto'], default='auto_safe', help='Orchestrator mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
    parser.add_argument('--log-file', type=str, help='Log file path')
    
    args = parser.parse_args()
    
    # Create config
    config = SchedulerConfig(
        cycle_interval_minutes=args.interval,
        domains=args.domains,
        mode=args.mode,
        log_level=args.log_level,
        log_file=args.log_file,
    )
    
    # Set up logging
    logger = setup_logging(config)
    
    # Create runner
    runner = CycleRunner(config, logger)
    
    # Handle commands
    if args.status:
        status = runner.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.once:
        # Run once and exit (for cron)
        logger.info("Running single optimization cycle")
        result = runner.run_cycle()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['success'] else 1)
    
    if args.scheduler:
        # Run with APScheduler
        backend = APSchedulerBackend(runner, config, logger)
        backend.start()
        return
    
    if args.daemon:
        # Run as daemon with simple loop
        scheduler = SimpleLoopScheduler(runner, logger)
        scheduler.start()
        return
    
    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
