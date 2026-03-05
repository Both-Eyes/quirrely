#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# QUIRRELY SECURITY MONITORING SETUP v1.0
# Setup automated security monitoring and alerting system
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail
RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; BLD='\033[1m'; RST='\033[0m'

ok()   { echo -e "${GRN}✓${RST} $1"; }
info() { echo -e "${CYN}→${RST} $1"; }
warn() { echo -e "${YLW}⚠${RST} $1"; }
die()  { echo -e "${RED}✗ $1${RST}"; exit 1; }
hdr()  { echo -e "\n${BLD}${CYN}$1${RST}"; }

# Configuration
PROJECT_DIR="/opt/quirrely/quirrely_v313_integrated"
LOG_DIR="/var/log/quirrely"
SCRIPTS_DIR="${PROJECT_DIR}/scripts"
DEPLOY_DIR="${PROJECT_DIR}/deploy"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    die "This script must be run as root"
fi

hdr "🛡️  Setting up Quirrely Security Monitoring System"

# ═══════════════════════════════════════════════════════════════════════════
# PREREQUISITES
# ═══════════════════════════════════════════════════════════════════════════

hdr "📋 Installing Prerequisites"

# Update system
info "Updating package lists..."
apt-get update -qq

# Install required packages
info "Installing required packages..."
apt-get install -y -qq \
    python3-pip \
    python3-venv \
    redis-tools \
    ufw \
    fail2ban \
    logrotate \
    cron \
    curl \
    jq

# Install Python packages
info "Installing Python packages..."
pip3 install -qq \
    psutil \
    redis \
    requests \
    structlog \
    python-json-logger \
    cryptography

ok "Prerequisites installed"

# ═══════════════════════════════════════════════════════════════════════════
# DIRECTORY SETUP
# ═══════════════════════════════════════════════════════════════════════════

hdr "📁 Setting up directories"

# Ensure directories exist
mkdir -p "${LOG_DIR}"
mkdir -p "${LOG_DIR}/archive"
mkdir -p "/etc/quirrely"
mkdir -p "/var/lib/quirrely"

# Set permissions
chown -R quirrely:quirrely "${LOG_DIR}"
chown -R quirrely:quirrely "/var/lib/quirrely"
chmod 750 "${LOG_DIR}"
chmod 750 "/var/lib/quirrely"

ok "Directory structure created"

# ═══════════════════════════════════════════════════════════════════════════
# SECURITY TOOLS INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════

hdr "🔧 Installing Security Tools"

# Make scripts executable
chmod +x "${SCRIPTS_DIR}/security_monitoring.py"
chmod +x "${SCRIPTS_DIR}/security_dashboard.py"
chmod +x "${SCRIPTS_DIR}/security_check.sh"

# Create security check script
cat > /usr/local/bin/quirrely-security-check << 'EOF'
#!/bin/bash
exec /opt/quirrely/quirrely_v313_integrated/scripts/security_check.sh "$@"
EOF
chmod +x /usr/local/bin/quirrely-security-check

# Create security dashboard script
cat > /usr/local/bin/quirrely-security-dashboard << 'EOF'
#!/bin/bash
exec python3 /opt/quirrely/quirrely_v313_integrated/scripts/security_dashboard.py "$@"
EOF
chmod +x /usr/local/bin/quirrely-security-dashboard

# Create IP blocking script
cat > /usr/local/bin/quirrely-block-ip << 'EOF'
#!/bin/bash
IP=$1
REASON=${2:-"Manual block via security tools"}

if [ -z "$IP" ]; then
    echo "Usage: quirrely-block-ip <IP_ADDRESS> [REASON]"
    exit 1
fi

# Validate IP
if ! [[ $IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    echo "Error: Invalid IP address format"
    exit 1
fi

echo "Blocking IP: $IP"
echo "Reason: $REASON"

# Block with UFW
ufw deny from $IP

# Log the action
logger -t quirrely-security "IP $IP blocked by $(whoami). Reason: $REASON"
echo "$(date '+%Y-%m-%d %H:%M:%S') - $IP - $REASON - $(whoami)" >> /var/log/quirrely/blocked_ips.log

echo "IP $IP blocked successfully"
EOF
chmod +x /usr/local/bin/quirrely-block-ip

ok "Security tools installed"

# ═══════════════════════════════════════════════════════════════════════════
# SYSTEMD SERVICE SETUP
# ═══════════════════════════════════════════════════════════════════════════

hdr "⚙️  Setting up systemd services"

# Install security monitoring service
cp "${DEPLOY_DIR}/security-monitoring.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable security-monitoring.service

# Create security log monitoring service
cat > /etc/systemd/system/quirrely-logwatch.service << 'EOF'
[Unit]
Description=Quirrely Log Monitoring
After=network.target

[Service]
Type=exec
User=quirrely
Group=quirrely
ExecStart=/bin/bash -c 'tail -F /var/log/quirrely/security.log | while read line; do echo "$(date): $line" >> /var/log/quirrely/logwatch.log; done'
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl enable quirrely-logwatch.service

ok "Systemd services configured"

# ═══════════════════════════════════════════════════════════════════════════
# LOG ROTATION SETUP
# ═══════════════════════════════════════════════════════════════════════════

hdr "📊 Setting up log rotation"

cat > /etc/logrotate.d/quirrely << 'EOF'
/var/log/quirrely/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 quirrely quirrely
    postrotate
        systemctl reload quirrely-logwatch.service 2>/dev/null || true
    endscript
}

/var/log/quirrely/security.log {
    daily
    rotate 365
    compress
    delaycompress
    missingok
    notifempty
    create 644 quirrely quirrely
    copytruncate
}
EOF

ok "Log rotation configured"

# ═══════════════════════════════════════════════════════════════════════════
# FAIL2BAN INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════

hdr "🚫 Configuring Fail2Ban"

# Create custom filter for Quirrely
cat > /etc/fail2ban/filter.d/quirrely-auth.conf << 'EOF'
[Definition]
failregex = ^.*"event_type": "auth_failure".*"ip_address": "<HOST>".*$
ignoreregex =
EOF

# Create jail configuration
cat > /etc/fail2ban/jail.d/quirrely.conf << 'EOF'
[quirrely-auth]
enabled = true
port = 80,443
protocol = tcp
filter = quirrely-auth
logpath = /var/log/quirrely/security.log
maxretry = 5
bantime = 3600
findtime = 600
action = ufw

[quirrely-admin]
enabled = true
port = 80,443
protocol = tcp
filter = quirrely-auth
logpath = /var/log/quirrely/security.log
maxretry = 3
bantime = 86400
findtime = 300
action = ufw
EOF

# Restart fail2ban
systemctl enable fail2ban
systemctl restart fail2ban

ok "Fail2Ban configured for Quirrely"

# ═══════════════════════════════════════════════════════════════════════════
# MONITORING SCRIPTS AND CRON JOBS
# ═══════════════════════════════════════════════════════════════════════════

hdr "⏰ Setting up scheduled monitoring"

# Create daily security check cron job
cat > /etc/cron.d/quirrely-security << 'EOF'
# Quirrely Security Monitoring Cron Jobs
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Daily security check at 2 AM
0 2 * * * quirrely /usr/local/bin/quirrely-security-check >> /var/log/quirrely/daily_check.log 2>&1

# Backup security logs at 3 AM
0 3 * * * quirrely tar -czf /var/lib/quirrely/security_logs_$(date +\%Y\%m\%d).tar.gz /var/log/quirrely/*.log

# Clean old backups (keep 30 days)
0 4 * * * quirrely find /var/lib/quirrely/security_logs_*.tar.gz -mtime +30 -delete

# Generate weekly security report on Sundays at 5 AM
0 5 * * 0 quirrely python3 /opt/quirrely/quirrely_v313_integrated/scripts/security_monitoring.py --mode report > /var/log/quirrely/weekly_report_$(date +\%Y\%m\%d).json

# Check for configuration changes every hour
0 * * * * quirrely /bin/bash -c 'find /etc/nginx /opt/quirrely -name "*.conf" -o -name ".env" | xargs -I {} sh -c "ls -l {} >> /var/log/quirrely/config_changes.log"'
EOF

# Create system health monitoring script
cat > /usr/local/bin/quirrely-health-check << 'EOF'
#!/bin/bash

# Get current metrics
CPU=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
MEMORY=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
DISK=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

# Log metrics
echo "$(date -I),${CPU},${MEMORY},${DISK}" >> /var/log/quirrely/health_metrics.csv

# Check thresholds and alert if needed
if (( $(echo "$CPU > 90" | bc -l) )); then
    logger -t quirrely-health "HIGH CPU: ${CPU}%"
fi

if (( $(echo "$MEMORY > 90" | bc -l) )); then
    logger -t quirrely-health "HIGH MEMORY: ${MEMORY}%"
fi

if [ "$DISK" -gt 85 ]; then
    logger -t quirrely-health "HIGH DISK: ${DISK}%"
fi
EOF

chmod +x /usr/local/bin/quirrely-health-check

# Add health check to cron
echo "*/5 * * * * quirrely /usr/local/bin/quirrely-health-check" >> /etc/cron.d/quirrely-security

ok "Scheduled monitoring configured"

# ═══════════════════════════════════════════════════════════════════════════
# ALERT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

hdr "📧 Configuring alerting"

# Create alert configuration template
cat > /etc/quirrely/alerts.conf << 'EOF'
# Quirrely Security Alerting Configuration
# Update these settings for your environment

# Slack webhook URL for security alerts
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Email settings for alerts
# EMAIL_ALERTS_ENABLED=false
# ALERT_EMAIL=security@yourdomain.com
# SMTP_SERVER=smtp.yourdomain.com
# SMTP_PORT=587
# SMTP_USERNAME=alerts@yourdomain.com
# SMTP_PASSWORD=your_smtp_password

# PagerDuty integration
# PAGERDUTY_INTEGRATION_KEY=your_integration_key

# Alert thresholds
MAX_FAILED_LOGINS_PER_MINUTE=10
MAX_ADMIN_SESSIONS=5
MAX_CPU_USAGE=90
MAX_MEMORY_USAGE=90
MAX_DISK_USAGE=85

# Automated responses
AUTO_BLOCK_IPS=true
AUTO_RESTART_SERVICES=false
QUARANTINE_SUSPICIOUS_FILES=true
EOF

chown quirrely:quirrely /etc/quirrely/alerts.conf
chmod 600 /etc/quirrely/alerts.conf

# Create simple alerting script
cat > /usr/local/bin/quirrely-send-alert << 'EOF'
#!/bin/bash

ALERT_TYPE=$1
MESSAGE=$2
SEVERITY=${3:-"medium"}

# Log the alert
logger -t quirrely-alert "[$SEVERITY] $ALERT_TYPE: $MESSAGE"

# Simple console alert for now
echo "🚨 SECURITY ALERT: $MESSAGE" | wall

# Add webhook integration here when configured
# if [ -n "$SLACK_WEBHOOK_URL" ]; then
#     curl -X POST "$SLACK_WEBHOOK_URL" -H 'Content-type: application/json' \
#          --data '{"text":"🚨 '"$MESSAGE"'"}'
# fi
EOF

chmod +x /usr/local/bin/quirrely-send-alert

ok "Alerting system configured"

# ═══════════════════════════════════════════════════════════════════════════
# FIREWALL ENHANCEMENT
# ═══════════════════════════════════════════════════════════════════════════

hdr "🔥 Enhancing firewall configuration"

# Ensure UFW is enabled
ufw --force enable

# Add some basic security rules
ufw default deny incoming
ufw default allow outgoing

# Allow essential services
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS

# Rate limiting for SSH
ufw limit 22/tcp

# Create IP whitelist script
cat > /usr/local/bin/quirrely-whitelist-ip << 'EOF'
#!/bin/bash

IP=$1
COMMENT=${2:-"Whitelisted IP"}

if [ -z "$IP" ]; then
    echo "Usage: quirrely-whitelist-ip <IP_ADDRESS> [COMMENT]"
    exit 1
fi

echo "Whitelisting IP: $IP"
ufw allow from $IP comment "$COMMENT"
logger -t quirrely-security "IP $IP whitelisted by $(whoami). Comment: $COMMENT"
EOF

chmod +x /usr/local/bin/quirrely-whitelist-ip

ok "Firewall enhanced"

# ═══════════════════════════════════════════════════════════════════════════
# START SERVICES
# ═══════════════════════════════════════════════════════════════════════════

hdr "🚀 Starting security monitoring services"

# Start the security monitoring service
systemctl start security-monitoring.service
systemctl start quirrely-logwatch.service

# Verify services are running
sleep 3

if systemctl is-active --quiet security-monitoring.service; then
    ok "Security monitoring service started"
else
    warn "Security monitoring service failed to start - check logs"
fi

if systemctl is-active --quiet quirrely-logwatch.service; then
    ok "Log monitoring service started"
else
    warn "Log monitoring service failed to start - check logs"
fi

if systemctl is-active --quiet fail2ban.service; then
    ok "Fail2Ban service running"
else
    warn "Fail2Ban service not running"
fi

# ═══════════════════════════════════════════════════════════════════════════
# FINAL VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

hdr "✅ Validating installation"

# Check if all components are working
VALIDATION_ERRORS=0

# Check log directory
if [ ! -d "${LOG_DIR}" ] || [ ! -w "${LOG_DIR}" ]; then
    warn "Log directory not accessible"
    ((VALIDATION_ERRORS++))
fi

# Check scripts
for script in security_monitoring.py security_dashboard.py; do
    if [ ! -x "${SCRIPTS_DIR}/${script}" ]; then
        warn "Script not executable: ${script}"
        ((VALIDATION_ERRORS++))
    fi
done

# Check systemd services
for service in security-monitoring quirrely-logwatch; do
    if ! systemctl is-enabled --quiet ${service}.service; then
        warn "Service not enabled: ${service}"
        ((VALIDATION_ERRORS++))
    fi
done

# Check cron jobs
if ! crontab -l -u quirrely | grep -q quirrely-security; then
    warn "Cron jobs not installed"
    ((VALIDATION_ERRORS++))
fi

if [ $VALIDATION_ERRORS -eq 0 ]; then
    ok "All components validated successfully"
else
    warn "$VALIDATION_ERRORS validation errors found"
fi

# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION MESSAGE
# ═══════════════════════════════════════════════════════════════════════════

hdr "🎉 Security Monitoring Setup Complete"

echo ""
echo -e "${BLD}${GRN}Quirrely Security Monitoring System v1.0 has been installed successfully!${RST}"
echo ""
echo -e "${BLD}Available Commands:${RST}"
echo "  quirrely-security-check          - Run manual security check"
echo "  quirrely-security-dashboard      - Launch real-time dashboard"
echo "  quirrely-block-ip <ip> [reason]  - Block an IP address"
echo "  quirrely-whitelist-ip <ip>       - Whitelist an IP address"
echo "  quirrely-send-alert <type> <msg> - Send manual alert"
echo ""
echo -e "${BLD}Service Management:${RST}"
echo "  systemctl status security-monitoring  - Check monitoring status"
echo "  systemctl logs security-monitoring    - View monitoring logs"
echo "  systemctl restart security-monitoring - Restart monitoring"
echo ""
echo -e "${BLD}Log Locations:${RST}"
echo "  Security Events: /var/log/quirrely/security.log"
echo "  Monitor Logs:    /var/log/quirrely/security_monitor.log"
echo "  Daily Checks:    /var/log/quirrely/daily_check.log"
echo "  Health Metrics:  /var/log/quirrely/health_metrics.csv"
echo ""
echo -e "${BLD}Configuration:${RST}"
echo "  Alert Config:    /etc/quirrely/alerts.conf"
echo "  Fail2Ban:        /etc/fail2ban/jail.d/quirrely.conf"
echo "  Cron Jobs:       /etc/cron.d/quirrely-security"
echo ""
echo -e "${YLW}Next Steps:${RST}"
echo "  1. Configure alert settings in /etc/quirrely/alerts.conf"
echo "  2. Set up Slack webhook for notifications"
echo "  3. Test the security dashboard: quirrely-security-dashboard"
echo "  4. Review and customize monitoring rules as needed"
echo "  5. Schedule regular security reviews"
echo ""
echo -e "${BLD}Getting Started:${RST}"
echo "  Run 'quirrely-security-dashboard' to see the live monitoring interface"
echo "  Run 'quirrely-security-check' for an immediate security status check"
echo ""

# Display current status
echo -e "${BLD}Current Status:${RST}"
systemctl is-active security-monitoring.service && echo "✓ Security monitoring: ACTIVE" || echo "✗ Security monitoring: INACTIVE"
systemctl is-active fail2ban.service && echo "✓ Fail2Ban: ACTIVE" || echo "✗ Fail2Ban: INACTIVE"
ufw status | grep -q "Status: active" && echo "✓ Firewall: ACTIVE" || echo "✗ Firewall: INACTIVE"

echo ""
echo -e "${CYN}Security monitoring system is now protecting your Quirrely installation!${RST}"
echo ""