# LNCP Scheduler Setup Guide

## Overview

The LNCP scheduler runs optimization cycles automatically. You can run it in several ways:

1. **Cron** - Simple, reliable, OS-level scheduling
2. **Daemon** - Long-running process with built-in loop
3. **APScheduler** - Python-based scheduler with advanced features
4. **Systemd** - Modern Linux service management

## Option 1: Cron (Recommended for simple setups)

### Basic Setup

Edit crontab:
```bash
crontab -e
```

Add this line to run every hour:
```cron
0 * * * * cd /path/to/lncp-web-app && /usr/bin/python3 backend/scheduler.py --once >> /var/log/lncp-scheduler.log 2>&1
```

### Cron Examples

```cron
# Every hour
0 * * * * cd /path/to/lncp-web-app && python3 backend/scheduler.py --once

# Every 30 minutes
*/30 * * * * cd /path/to/lncp-web-app && python3 backend/scheduler.py --once

# Every 4 hours
0 */4 * * * cd /path/to/lncp-web-app && python3 backend/scheduler.py --once

# Every day at 6 AM
0 6 * * * cd /path/to/lncp-web-app && python3 backend/scheduler.py --once

# Weekdays at 9 AM
0 9 * * 1-5 cd /path/to/lncp-web-app && python3 backend/scheduler.py --once
```

### With Environment Variables

```cron
0 * * * * cd /path/to/lncp-web-app && GSC_CREDENTIALS_PATH=/path/to/creds.json python3 backend/scheduler.py --once
```

### With Virtual Environment

```cron
0 * * * * cd /path/to/lncp-web-app && /path/to/venv/bin/python backend/scheduler.py --once
```

## Option 2: Daemon Mode

Run as a long-running process:

```bash
# Start in foreground
python3 backend/scheduler.py --daemon --interval 60

# Start in background
nohup python3 backend/scheduler.py --daemon --interval 60 > scheduler.log 2>&1 &

# With all options
python3 backend/scheduler.py --daemon \
    --interval 60 \
    --domains all \
    --mode auto_safe \
    --log-level INFO \
    --log-file /var/log/lncp-scheduler.log
```

## Option 3: Systemd Service (Recommended for production)

### Create Service File

```bash
sudo nano /etc/systemd/system/lncp-scheduler.service
```

Add:
```ini
[Unit]
Description=LNCP Optimization Scheduler
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/lncp-web-app
Environment="GSC_CREDENTIALS_PATH=/path/to/credentials/gsc-service-account.json"
Environment="GSC_SITE_URL=https://quirrely.io"
Environment="LNCP_LOG_LEVEL=INFO"
ExecStart=/usr/bin/python3 backend/scheduler.py --daemon --interval 60
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable lncp-scheduler

# Start service
sudo systemctl start lncp-scheduler

# Check status
sudo systemctl status lncp-scheduler

# View logs
sudo journalctl -u lncp-scheduler -f
```

### Service Commands

```bash
# Stop
sudo systemctl stop lncp-scheduler

# Restart
sudo systemctl restart lncp-scheduler

# Disable
sudo systemctl disable lncp-scheduler
```

## Option 4: APScheduler

For more control, use APScheduler:

```bash
# Install APScheduler
pip install apscheduler

# Run
python3 backend/scheduler.py --scheduler --interval 60
```

## CLI Options

```
usage: scheduler.py [-h] [--once] [--daemon] [--scheduler] [--status]
                    [--interval INTERVAL] [--domains {all,app,blog}]
                    [--mode {observe_only,suggest,auto_safe,full_auto}]
                    [--log-level {DEBUG,INFO,WARNING,ERROR}]
                    [--log-file LOG_FILE]

LNCP Optimization Scheduler

options:
  --once            Run once and exit (for cron)
  --daemon          Run as daemon with simple loop
  --scheduler       Run with APScheduler
  --status          Show scheduler status
  --interval        Cycle interval in minutes (default: 60)
  --domains         Domains to optimize: all, app, blog (default: all)
  --mode            Orchestrator mode (default: auto_safe)
  --log-level       Log level (default: INFO)
  --log-file        Log file path
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LNCP_CYCLE_INTERVAL` | Minutes between cycles | 60 |
| `LNCP_DOMAINS` | Domains to optimize | all |
| `LNCP_MODE` | Orchestrator mode | auto_safe |
| `LNCP_LOG_LEVEL` | Log level | INFO |
| `LNCP_LOG_FILE` | Log file path | None |
| `LNCP_STATE_FILE` | State persistence file | scheduler_state.json |
| `GSC_CREDENTIALS_PATH` | GSC credentials file | credentials/gsc-service-account.json |
| `GSC_SITE_URL` | Site URL in GSC | https://quirrely.io |

## Monitoring

### Check Status

```bash
python3 backend/scheduler.py --status
```

Output:
```json
{
  "last_run": "2026-02-14T20:00:00",
  "last_success": "2026-02-14T20:00:00",
  "last_error": null,
  "total_runs": 24,
  "successful_runs": 24,
  "failed_runs": 0,
  "success_rate": 1.0,
  "total_actions_applied": 48,
  "config": {
    "interval_minutes": 60,
    "domains": "all",
    "mode": "auto_safe"
  }
}
```

### State File

The scheduler persists state to `scheduler_state.json`:

```json
{
  "last_run": "2026-02-14T20:00:00",
  "last_success": "2026-02-14T20:00:00",
  "last_error": null,
  "total_runs": 24,
  "successful_runs": 24,
  "failed_runs": 0,
  "total_actions_applied": 48
}
```

### Log Rotation

For long-running deployments, set up log rotation:

```bash
sudo nano /etc/logrotate.d/lncp-scheduler
```

```
/var/log/lncp-scheduler.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
}
```

## Troubleshooting

### Scheduler not running

1. Check if process is running:
   ```bash
   ps aux | grep scheduler.py
   ```

2. Check logs:
   ```bash
   tail -f /var/log/lncp-scheduler.log
   ```

3. Run manually to see errors:
   ```bash
   python3 backend/scheduler.py --once --log-level DEBUG
   ```

### GSC errors

1. Check credentials:
   ```bash
   python3 -c "from lncp.meta.blog import check_gsc_credentials; print(check_gsc_credentials())"
   ```

2. Verify environment variables:
   ```bash
   echo $GSC_CREDENTIALS_PATH
   echo $GSC_SITE_URL
   ```

### Permission issues

```bash
# Fix permissions
chown -R www-data:www-data /path/to/lncp-web-app
chmod -R 755 /path/to/lncp-web-app
```

## Recommended Production Setup

1. Use **systemd** for service management
2. Set **interval to 60 minutes** (balance between responsiveness and API limits)
3. Enable **log rotation**
4. Monitor with **status endpoint** or external monitoring
5. Set up **alerts** for failed runs

```bash
# Complete production setup
sudo systemctl enable lncp-scheduler
sudo systemctl start lncp-scheduler
sudo systemctl status lncp-scheduler
```
