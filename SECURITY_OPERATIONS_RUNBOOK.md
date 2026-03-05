# 🛡️ Quirrely Security Operations Runbook

**Version:** 1.0  
**Created:** 2025-03-05  
**Classification:** Internal Use  
**Owner:** Security Operations Team  

---

## 📋 Quick Reference

### Emergency Contacts
- **Security Incidents**: security-incidents@quirrely.com
- **On-Call Security**: [Phone Number]
- **CTO**: [Phone Number]
- **CEO**: [Phone Number]

### Critical Commands
```bash
# Check system security status
sudo /opt/quirrely/scripts/security_check.sh

# View security logs
sudo tail -f /var/log/quirrely/security.log

# Block suspicious IP
sudo ufw deny from [IP_ADDRESS]

# Restart security services
sudo systemctl restart nginx
sudo pm2 restart quirrely
```

---

## 🚨 Incident Response Playbooks

### 1. Suspected Data Breach

#### Immediate Response (0-15 minutes)
```bash
# 1. Preserve evidence
sudo cp /var/log/quirrely/*.log /tmp/incident-$(date +%Y%m%d-%H%M%S)/

# 2. Check for ongoing compromise
sudo netstat -tulpn | grep ESTABLISHED
ps aux | grep -E '(nc|netcat|wget|curl)' | grep -v grep

# 3. Block suspicious IPs (if identified)
sudo ufw deny from [SUSPICIOUS_IP]

# 4. Enable enhanced logging
echo "DEBUG" | sudo tee /opt/quirrely/log_level.conf
sudo systemctl reload nginx
```

#### Investigation Checklist
- [ ] Identify scope of data accessed
- [ ] Determine attack vector
- [ ] Check for data exfiltration
- [ ] Verify user account integrity
- [ ] Review admin access logs
- [ ] Assess payment system impact

#### Communication Template
```
SECURITY INCIDENT ALERT

Incident ID: INC-[YYYYMMDD-HHMMSS]
Severity: [P1/P2/P3/P4]
Status: [DETECTED/INVESTIGATING/CONTAINED/RESOLVED]

Initial Assessment:
- Detection Time: [UTC Timestamp]
- Affected Systems: [List]
- Potential Impact: [Description]
- Immediate Actions: [List]

Next Update: [Time]
Response Team: [Names]
```

### 2. Unauthorized Admin Access

#### Detection Indicators
```bash
# Check for unauthorized admin logins
grep "admin_access" /var/log/quirrely/security.log | tail -20

# Verify admin session integrity  
redis-cli KEYS "quirrely:session:*" | xargs redis-cli MGET

# Check for privilege escalation
grep "privilege_escalation" /var/log/quirrely/security.log

# Review admin actions
grep "admin_action" /var/log/quirrely/security.log | tail -50
```

#### Response Actions
1. **Immediate Containment**
   ```bash
   # Disable admin accounts (except incident response account)
   python3 /opt/quirrely/scripts/disable_admin_accounts.py --except security-team
   
   # Force logout all admin sessions
   redis-cli FLUSHDB
   
   # Enable admin IP restrictions
   sudo nginx -s reload
   ```

2. **Investigation**
   - Review authentication logs
   - Check VPN access logs
   - Verify admin account integrity
   - Examine configuration changes

3. **Recovery**
   - Reset admin passwords
   - Regenerate admin session tokens
   - Review and update admin IP whitelist
   - Enable additional monitoring

### 3. DDoS Attack

#### Detection
```bash
# Monitor connection counts
netstat -ntu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -n

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Monitor system resources
htop
iotop
```

#### Response Actions
```bash
# 1. Enable Cloudflare "Under Attack" mode
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/[ZONE_ID]/settings/security_level" \
     -H "Authorization: Bearer [API_TOKEN]" \
     -H "Content-Type: application/json" \
     --data '{"value":"under_attack"}'

# 2. Implement emergency rate limiting
sudo cp /etc/nginx/sites-available/quirrely-emergency.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 3. Monitor and adjust
watch 'ss -tuln | wc -l'
```

### 4. Malware Detection

#### System Scan
```bash
# Install and run ClamAV
sudo apt-get install clamav clamav-daemon
sudo freshclam
sudo clamscan -r /opt/quirrely/ --infected --remove

# Check for unusual processes
ps aux --sort=-%cpu | head -20
lsof -i

# Monitor file changes
sudo find /opt/quirrely/ -type f -mtime -1 -ls

# Check for unauthorized network connections
sudo netstat -tulpn | grep -v '127.0.0.1\|::1'
```

#### Remediation
1. Isolate affected system
2. Kill suspicious processes
3. Remove malware files
4. Update all software
5. Restore from clean backup if needed

### 5. Payment System Compromise

#### Immediate Actions
```bash
# 1. Disable payment processing
echo "MAINTENANCE_MODE=true" >> /opt/quirrely/quirrely_v313_integrated/backend/.env
sudo systemctl restart quirrely

# 2. Notify payment processor
# Call Stripe immediately: [Phone Number]

# 3. Preserve evidence
sudo cp -R /opt/quirrely/quirrely_v313_integrated/backend/logs/ /tmp/payment-incident-$(date +%Y%m%d)/
```

#### Investigation Steps
- [ ] Review payment transaction logs
- [ ] Check for unauthorized transactions
- [ ] Verify webhook integrity
- [ ] Assess customer data exposure
- [ ] Contact Stripe security team
- [ ] Prepare breach notifications

---

## 🔍 Daily Security Operations

### Morning Security Checklist
```bash
#!/bin/bash
# Daily security status check

echo "=== DAILY SECURITY CHECK - $(date) ==="

# 1. Check system status
systemctl status nginx quirrely redis-server postgresql

# 2. Review overnight security events
grep -E "(CRITICAL|HIGH)" /var/log/quirrely/security.log | tail -20

# 3. Check for failed authentication attempts
grep "auth_failure" /var/log/quirrely/security.log | wc -l

# 4. Verify backup status
ls -la /backup/quirrely/ | tail -5

# 5. Check SSL certificate expiry
openssl s509 -in /etc/letsencrypt/live/quirrely.com/cert.pem -text -noout | grep "Not After"

# 6. Review admin access
grep "admin_access" /var/log/quirrely/security.log | tail -10

# 7. Check disk space
df -h

# 8. Monitor memory usage
free -m

echo "=== CHECK COMPLETE ==="
```

### Weekly Security Tasks

#### Monday - Infrastructure Review
- [ ] Review firewall rules
- [ ] Check SSL certificate status
- [ ] Verify backup integrity
- [ ] Update system packages
- [ ] Review DNS configuration

#### Tuesday - Access Control Audit
- [ ] Review user accounts
- [ ] Check admin access logs
- [ ] Verify VPN user list
- [ ] Review API key usage
- [ ] Update IP whitelists

#### Wednesday - Vulnerability Management
- [ ] Run vulnerability scans
- [ ] Review dependency updates
- [ ] Check security advisories
- [ ] Update security tools
- [ ] Review penetration test results

#### Thursday - Monitoring & Alerting
- [ ] Test alert mechanisms
- [ ] Review log retention
- [ ] Check monitoring thresholds
- [ ] Verify log aggregation
- [ ] Update monitoring rules

#### Friday - Documentation & Training
- [ ] Update security procedures
- [ ] Review incident reports
- [ ] Plan security training
- [ ] Update contact lists
- [ ] Review compliance status

---

## 📊 Security Monitoring Dashboard

### Key Security Metrics
```bash
# Authentication metrics
echo "Failed logins (last 24h):"
grep "auth_failure" /var/log/quirrely/security.log | grep "$(date +%Y-%m-%d)" | wc -l

echo "Admin access events (last 24h):"
grep "admin_access" /var/log/quirrely/security.log | grep "$(date +%Y-%m-%d)" | wc -l

echo "Blocked IPs (current):"
ufw status | grep DENY | wc -l

echo "Active sessions:"
redis-cli DBSIZE

echo "System load:"
uptime

echo "Disk usage:"
df -h / | tail -1
```

### Log Analysis Commands
```bash
# Top source IPs
grep "ip_address" /var/log/quirrely/security.log | \
  sed 's/.*"ip_address": "\([^"]*\)".*/\1/' | \
  sort | uniq -c | sort -nr | head -10

# Attack attempts by type
grep "attack_attempt" /var/log/quirrely/security.log | \
  sed 's/.*"event_type": "\([^"]*\)".*/\1/' | \
  sort | uniq -c | sort -nr

# Failed authentication by user
grep "auth_failure" /var/log/quirrely/security.log | \
  sed 's/.*"user_id": "\([^"]*\)".*/\1/' | \
  sort | uniq -c | sort -nr | head -10
```

---

## 🛠️ Security Tools & Scripts

### Security Health Check Script
```bash
#!/bin/bash
# File: /opt/quirrely/scripts/security_check.sh

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_ssl() {
    echo "Checking SSL certificates..."
    
    # Check certificate expiry
    CERT_EXPIRY=$(openssl s509 -in /etc/letsencrypt/live/quirrely.com/cert.pem -text -noout | \
                  grep "Not After" | cut -d ":" -f 2-)
    DAYS_LEFT=$(( ($(date -d "$CERT_EXPIRY" +%s) - $(date +%s)) / 86400 ))
    
    if [ $DAYS_LEFT -lt 30 ]; then
        echo -e "${RED}⚠️  SSL certificate expires in $DAYS_LEFT days${NC}"
    else
        echo -e "${GREEN}✅ SSL certificate valid for $DAYS_LEFT days${NC}"
    fi
}

check_services() {
    echo "Checking critical services..."
    
    SERVICES=("nginx" "quirrely" "postgresql" "redis-server")
    
    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet $service; then
            echo -e "${GREEN}✅ $service is running${NC}"
        else
            echo -e "${RED}❌ $service is not running${NC}"
        fi
    done
}

check_security_events() {
    echo "Checking recent security events..."
    
    CRITICAL_COUNT=$(grep -c "CRITICAL" /var/log/quirrely/security.log || echo "0")
    HIGH_COUNT=$(grep -c "HIGH" /var/log/quirrely/security.log || echo "0")
    
    echo "Critical events (last 24h): $CRITICAL_COUNT"
    echo "High severity events (last 24h): $HIGH_COUNT"
    
    if [ $CRITICAL_COUNT -gt 0 ] || [ $HIGH_COUNT -gt 5 ]; then
        echo -e "${RED}⚠️  High security activity detected${NC}"
    else
        echo -e "${GREEN}✅ Security events within normal range${NC}"
    fi
}

check_disk_space() {
    echo "Checking disk space..."
    
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ $DISK_USAGE -gt 90 ]; then
        echo -e "${RED}❌ Disk usage: ${DISK_USAGE}% (Critical)${NC}"
    elif [ $DISK_USAGE -gt 80 ]; then
        echo -e "${YELLOW}⚠️  Disk usage: ${DISK_USAGE}% (Warning)${NC}"
    else
        echo -e "${GREEN}✅ Disk usage: ${DISK_USAGE}%${NC}"
    fi
}

check_failed_logins() {
    echo "Checking authentication failures..."
    
    FAILED_LOGINS=$(grep "auth_failure" /var/log/quirrely/security.log | \
                   grep "$(date +%Y-%m-%d)" | wc -l || echo "0")
    
    if [ $FAILED_LOGINS -gt 100 ]; then
        echo -e "${RED}❌ High authentication failures: $FAILED_LOGINS${NC}"
    elif [ $FAILED_LOGINS -gt 50 ]; then
        echo -e "${YELLOW}⚠️  Elevated authentication failures: $FAILED_LOGINS${NC}"
    else
        echo -e "${GREEN}✅ Authentication failures: $FAILED_LOGINS${NC}"
    fi
}

# Main execution
echo "=== QUIRRELY SECURITY HEALTH CHECK ==="
echo "Time: $(date)"
echo "======================================="

check_services
echo ""
check_ssl
echo ""
check_security_events
echo ""
check_disk_space
echo ""
check_failed_logins
echo ""

echo "======================================="
echo "Security check completed."
```

### IP Blocking Script
```bash
#!/bin/bash
# File: /opt/quirrely/scripts/block_ip.sh

IP=$1
REASON=${2:-"Security incident"}

if [ -z "$IP" ]; then
    echo "Usage: $0 <IP_ADDRESS> [REASON]"
    exit 1
fi

# Validate IP address format
if ! [[ $IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    echo "Error: Invalid IP address format"
    exit 1
fi

echo "Blocking IP: $IP"
echo "Reason: $REASON"

# Add firewall rule
sudo ufw deny from $IP

# Log the action
logger -t quirrely-security "IP $IP blocked by $(whoami). Reason: $REASON"

# Add to blocked IPs list
echo "$(date '+%Y-%m-%d %H:%M:%S') - $IP - $REASON - $(whoami)" >> /var/log/quirrely/blocked_ips.log

echo "IP $IP has been blocked successfully."
```

### Backup Verification Script
```bash
#!/bin/bash
# File: /opt/quirrely/scripts/verify_backups.sh

BACKUP_DIR="/backup/quirrely"
LOG_FILE="/var/log/quirrely/backup_verification.log"

echo "=== BACKUP VERIFICATION - $(date) ===" | tee -a $LOG_FILE

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "ERROR: Backup directory not found: $BACKUP_DIR" | tee -a $LOG_FILE
    exit 1
fi

# Check for recent backups (last 24 hours)
RECENT_BACKUPS=$(find $BACKUP_DIR -type f -name "*.sql.gz" -mtime -1 | wc -l)

if [ $RECENT_BACKUPS -eq 0 ]; then
    echo "ERROR: No recent backups found" | tee -a $LOG_FILE
    exit 1
else
    echo "SUCCESS: Found $RECENT_BACKUPS recent backup(s)" | tee -a $LOG_FILE
fi

# Test backup integrity
LATEST_BACKUP=$(find $BACKUP_DIR -type f -name "*.sql.gz" -mtime -1 | sort | tail -1)

if [ -n "$LATEST_BACKUP" ]; then
    echo "Testing backup integrity: $LATEST_BACKUP" | tee -a $LOG_FILE
    
    if gunzip -t "$LATEST_BACKUP" 2>/dev/null; then
        echo "SUCCESS: Backup integrity verified" | tee -a $LOG_FILE
    else
        echo "ERROR: Backup integrity check failed" | tee -a $LOG_FILE
        exit 1
    fi
fi

echo "Backup verification completed successfully" | tee -a $LOG_FILE
```

---

## 🔄 Automated Response Actions

### Auto-IP Blocking (Fail2Ban Configuration)
```ini
# File: /etc/fail2ban/jail.local

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
```

### Alert Webhooks
```bash
# Webhook for critical alerts
curl -X POST "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" \
     -H 'Content-type: application/json' \
     --data '{
         "text": "🚨 CRITICAL SECURITY ALERT",
         "blocks": [
             {
                 "type": "section",
                 "text": {
                     "type": "mrkdwn",
                     "text": "*Incident:* '"$INCIDENT_TYPE"'\n*Severity:* '"$SEVERITY"'\n*Time:* '"$(date)"'\n*Details:* '"$DETAILS"'"
                 }
             }
         ]
     }'
```

---

## 📝 Security Checklist Templates

### Incident Response Checklist
- [ ] Incident detected and classified
- [ ] Response team activated
- [ ] Initial containment performed
- [ ] Evidence preserved
- [ ] Stakeholders notified
- [ ] Investigation initiated
- [ ] Root cause identified
- [ ] Systems restored
- [ ] Post-incident review scheduled
- [ ] Documentation updated

### Monthly Security Review
- [ ] Vulnerability scan completed
- [ ] Penetration test results reviewed
- [ ] Security metrics analyzed
- [ ] Incident trends evaluated
- [ ] User access reviewed
- [ ] Security training updated
- [ ] Compliance status checked
- [ ] Security roadmap updated

### Quarterly Security Audit
- [ ] Security controls tested
- [ ] Risk assessment updated
- [ ] Policy compliance verified
- [ ] Security awareness measured
- [ ] Vendor security reviewed
- [ ] Business continuity tested
- [ ] Security budget reviewed
- [ ] Board reporting completed

---

## 📞 Escalation Matrix

### Incident Severity Escalation
```yaml
P1 - Critical (0-15 minutes):
  - Security Team Lead
  - CTO
  - CEO
  - Legal Counsel
  - Communications Team

P2 - High (0-1 hour):
  - Security Team Lead
  - CTO
  - Legal Counsel

P3 - Medium (0-4 hours):
  - Security Team Lead
  - Development Lead

P4 - Low (0-24 hours):
  - Security Team
  - Development Team
```

### Communication Channels
- **Immediate**: Phone calls + Slack #security-incidents
- **Updates**: Slack + Email
- **External**: Dedicated incident email
- **Public**: Status page + social media

---

**Document Control:**  
**Last Updated:** 2025-03-05  
**Next Review:** 2025-04-05  
**Owner:** Security Operations Team  
**Classification:** Internal Use Only