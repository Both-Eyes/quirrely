#!/bin/bash
"""
AGENT CRON SETUP SCRIPT
Sets up cron jobs for all batch agents.
"""

echo "Setting up Quirrely Batch Agent cron jobs..."

# Define the project directory
PROJECT_DIR="/root/quirrely_v313_integrated"
AGENT_DIR="$PROJECT_DIR/backend/agents"
LOG_DIR="$PROJECT_DIR/logs/agents"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Create a temporary crontab file with existing entries plus new agent jobs
crontab -l 2>/dev/null > /tmp/quirrely_cron_backup

# Add agent cron jobs
cat >> /tmp/quirrely_cron_backup << EOF

# ═══════════════════════════════════════════════════════════════════════════
# QUIRRELY BATCH AGENTS - PHASE 1 (Revenue Critical)
# ═══════════════════════════════════════════════════════════════════════════

# Conversion Optimization Agent - Daily at 3 AM EST
0 3 * * * cd $PROJECT_DIR && python3 $AGENT_DIR/scheduler.py run conversion_optimizer >> $LOG_DIR/conversion_optimizer.log 2>&1

# LNCP Pattern Discovery Agent - Weekly on Sundays at 2 AM EST  
0 2 * * 0 cd $PROJECT_DIR && python3 $AGENT_DIR/scheduler.py run lncp_pattern_discovery >> $LOG_DIR/lncp_pattern_discovery.log 2>&1

# Usage Pattern Analyzer - Bi-weekly (1st & 15th) at 4 AM EST
0 4 1,15 * * cd $PROJECT_DIR && python3 $AGENT_DIR/scheduler.py run usage_pattern_analyzer >> $LOG_DIR/usage_pattern_analyzer.log 2>&1

# Agent Health Check - Every 6 hours
0 */6 * * * cd $PROJECT_DIR && python3 $AGENT_DIR/scheduler.py status >> $LOG_DIR/agent_health.log 2>&1

EOF

# Install the new crontab
crontab /tmp/quirrely_cron_backup

echo "Cron jobs installed successfully!"
echo ""
echo "Scheduled agents:"
echo "  - Conversion Optimizer: Daily at 3 AM EST"
echo "  - LNCP Pattern Discovery: Sundays at 2 AM EST" 
echo "  - Usage Pattern Analyzer: 1st & 15th at 4 AM EST"
echo "  - Health Check: Every 6 hours"
echo ""
echo "Logs will be written to: $LOG_DIR"
echo ""
echo "To view current crontab: crontab -l"
echo "To remove agent crons: crontab -e (manually delete the agent section)"

# Create log rotation configuration
cat > /etc/logrotate.d/quirrely-agents << EOF
$LOG_DIR/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF

echo "Log rotation configured for agent logs."

# Test agent system initialization
echo ""
echo "Testing agent system initialization..."
cd "$PROJECT_DIR" && python3 "$AGENT_DIR/scheduler.py" list

echo ""
echo "Agent cron setup completed!"