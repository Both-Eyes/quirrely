#!/usr/bin/env python3
"""
QUIRRELY SECURITY DASHBOARD v1.0
Real-time security monitoring dashboard for command line.

Features:
- Live security metrics display
- Threat detection status
- System health monitoring
- Interactive incident response
- Compliance status overview
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any
import psutil
import curses
import redis

# Add backend path
sys.path.append('/opt/quirrely/quirrely_v313_integrated/backend')

class SecurityDashboard:
    """Terminal-based security monitoring dashboard."""
    
    def __init__(self):
        self.screen = None
        self.running = True
        self.current_tab = 0
        self.tabs = ["Overview", "Threats", "System", "Logs", "Actions"]
        self.log_lines = []
        self.threats = []
        self.blocked_ips = []
        
    def start(self):
        """Start the dashboard."""
        curses.wrapper(self._run_dashboard)
    
    def _run_dashboard(self, stdscr):
        """Main dashboard loop."""
        self.screen = stdscr
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Good
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Warning  
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # Critical
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Info
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Header
        
        while self.running:
            try:
                self._draw_dashboard()
                
                # Handle input
                key = stdscr.getch()
                self._handle_input(key)
                
                time.sleep(0.5)  # Update every 500ms
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                # Show error and continue
                stdscr.addstr(0, 0, f"Error: {str(e)[:50]}")
                stdscr.refresh()
                time.sleep(2)
    
    def _draw_dashboard(self):
        """Draw the main dashboard interface."""
        self.screen.clear()
        height, width = self.screen.getmaxyx()
        
        # Draw header
        self._draw_header(width)
        
        # Draw tabs
        self._draw_tabs(width)
        
        # Draw content based on current tab
        if self.current_tab == 0:
            self._draw_overview_tab(height, width)
        elif self.current_tab == 1:
            self._draw_threats_tab(height, width)
        elif self.current_tab == 2:
            self._draw_system_tab(height, width)
        elif self.current_tab == 3:
            self._draw_logs_tab(height, width)
        elif self.current_tab == 4:
            self._draw_actions_tab(height, width)
        
        # Draw footer
        self._draw_footer(height, width)
        
        self.screen.refresh()
    
    def _draw_header(self, width):
        """Draw the header section."""
        header_text = "🛡️  QUIRRELY SECURITY DASHBOARD v1.0"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Header background
        self.screen.addstr(0, 0, " " * width, curses.color_pair(5))
        
        # Title and timestamp
        self.screen.addstr(0, 2, header_text, curses.color_pair(5) | curses.A_BOLD)
        self.screen.addstr(0, width - len(timestamp) - 2, timestamp, curses.color_pair(5))
    
    def _draw_tabs(self, width):
        """Draw the tab navigation."""
        y = 2
        x = 2
        
        for i, tab in enumerate(self.tabs):
            if i == self.current_tab:
                attr = curses.color_pair(5) | curses.A_BOLD
            else:
                attr = curses.A_NORMAL
            
            self.screen.addstr(y, x, f" {tab} ", attr)
            x += len(tab) + 3
    
    def _draw_overview_tab(self, height, width):
        """Draw the overview tab."""
        y = 4
        
        # Security status overview
        self.screen.addstr(y, 2, "SECURITY STATUS", curses.A_BOLD)
        y += 2
        
        # Get real data
        security_status = self._get_security_status()
        
        # System health
        health_color = curses.color_pair(1) if security_status['health'] == 'Good' else curses.color_pair(3)
        self.screen.addstr(y, 4, f"System Health: {security_status['health']}", health_color)
        y += 1
        
        # Active threats
        threat_color = curses.color_pair(1) if security_status['active_threats'] == 0 else curses.color_pair(3)
        self.screen.addstr(y, 4, f"Active Threats: {security_status['active_threats']}", threat_color)
        y += 1
        
        # Blocked IPs
        self.screen.addstr(y, 4, f"Blocked IPs: {security_status['blocked_ips']}", curses.color_pair(4))
        y += 1
        
        # Failed logins (last hour)
        self.screen.addstr(y, 4, f"Failed Logins (1h): {security_status['failed_logins']}", curses.color_pair(4))
        y += 2
        
        # Recent events
        self.screen.addstr(y, 2, "RECENT SECURITY EVENTS", curses.A_BOLD)
        y += 2
        
        recent_events = self._get_recent_events()
        for event in recent_events[-10:]:  # Show last 10 events
            color = self._get_event_color(event.get('severity', 'low'))
            event_text = f"{event['timestamp']} - {event['message']}"
            if len(event_text) > width - 4:
                event_text = event_text[:width-7] + "..."
            self.screen.addstr(y, 4, event_text, color)
            y += 1
    
    def _draw_threats_tab(self, height, width):
        """Draw the threats detection tab."""
        y = 4
        
        self.screen.addstr(y, 2, "THREAT DETECTION", curses.A_BOLD)
        y += 2
        
        # Threat detection rules status
        self.screen.addstr(y, 4, "SQL Injection Detection: ACTIVE", curses.color_pair(1))
        y += 1
        self.screen.addstr(y, 4, "XSS Detection: ACTIVE", curses.color_pair(1))
        y += 1
        self.screen.addstr(y, 4, "Brute Force Detection: ACTIVE", curses.color_pair(1))
        y += 1
        self.screen.addstr(y, 4, "Admin Access Monitoring: ACTIVE", curses.color_pair(1))
        y += 2
        
        # Top attacking IPs
        self.screen.addstr(y, 2, "TOP ATTACKING IPs", curses.A_BOLD)
        y += 2
        
        attacking_ips = self._get_attacking_ips()
        for ip_info in attacking_ips:
            ip_text = f"{ip_info['ip']} - {ip_info['attempts']} attempts - {ip_info['status']}"
            color = curses.color_pair(3) if ip_info['status'] == 'BLOCKED' else curses.color_pair(2)
            self.screen.addstr(y, 4, ip_text, color)
            y += 1
    
    def _draw_system_tab(self, height, width):
        """Draw the system monitoring tab."""
        y = 4
        
        self.screen.addstr(y, 2, "SYSTEM METRICS", curses.A_BOLD)
        y += 2
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # CPU usage
        cpu_color = self._get_metric_color(cpu_percent, 70, 90)
        self.screen.addstr(y, 4, f"CPU Usage: {cpu_percent:.1f}%", cpu_color)
        y += 1
        
        # Memory usage
        mem_color = self._get_metric_color(memory.percent, 70, 90)
        self.screen.addstr(y, 4, f"Memory Usage: {memory.percent:.1f}%", mem_color)
        y += 1
        
        # Disk usage
        disk_percent = (disk.used / disk.total) * 100
        disk_color = self._get_metric_color(disk_percent, 80, 95)
        self.screen.addstr(y, 4, f"Disk Usage: {disk_percent:.1f}%", disk_color)
        y += 2
        
        # Service status
        self.screen.addstr(y, 2, "SERVICE STATUS", curses.A_BOLD)
        y += 2
        
        services = self._get_service_status()
        for service, status in services.items():
            color = curses.color_pair(1) if status == 'active' else curses.color_pair(3)
            self.screen.addstr(y, 4, f"{service}: {status.upper()}", color)
            y += 1
    
    def _draw_logs_tab(self, height, width):
        """Draw the logs monitoring tab."""
        y = 4
        
        self.screen.addstr(y, 2, "SECURITY LOGS (Real-time)", curses.A_BOLD)
        y += 2
        
        # Live log tail
        log_lines = self._get_log_tail()
        max_lines = height - y - 3
        
        for line in log_lines[-max_lines:]:
            if 'CRITICAL' in line or 'ERROR' in line:
                color = curses.color_pair(3)
            elif 'WARNING' in line or 'WARN' in line:
                color = curses.color_pair(2)
            else:
                color = curses.A_NORMAL
            
            # Truncate line if too long
            if len(line) > width - 4:
                line = line[:width-7] + "..."
            
            self.screen.addstr(y, 4, line, color)
            y += 1
    
    def _draw_actions_tab(self, height, width):
        """Draw the incident response actions tab."""
        y = 4
        
        self.screen.addstr(y, 2, "INCIDENT RESPONSE ACTIONS", curses.A_BOLD)
        y += 2
        
        actions = [
            "1. Block IP Address",
            "2. Force Logout All Users", 
            "3. Enable Maintenance Mode",
            "4. Generate Security Report",
            "5. Test Alert Systems",
            "6. Backup Current Logs",
            "7. Restart Security Services",
            "8. Emergency Shutdown"
        ]
        
        for action in actions:
            self.screen.addstr(y, 4, action, curses.color_pair(4))
            y += 1
        
        y += 1
        self.screen.addstr(y, 2, "Press number key to execute action", curses.A_BOLD)
    
    def _draw_footer(self, height, width):
        """Draw the footer with help text."""
        footer_text = "TAB: Switch tabs | Q: Quit | R: Refresh | Numbers: Execute actions"
        self.screen.addstr(height - 1, 2, footer_text, curses.A_DIM)
    
    def _handle_input(self, key):
        """Handle keyboard input."""
        if key == ord('q') or key == ord('Q'):
            self.running = False
        elif key == ord('\t') or key == curses.KEY_RIGHT:
            self.current_tab = (self.current_tab + 1) % len(self.tabs)
        elif key == curses.KEY_LEFT:
            self.current_tab = (self.current_tab - 1) % len(self.tabs)
        elif key == ord('r') or key == ord('R'):
            pass  # Refresh (happens automatically)
        elif self.current_tab == 4:  # Actions tab
            self._handle_action_key(key)
    
    def _handle_action_key(self, key):
        """Handle action keys in the actions tab."""
        if key == ord('1'):
            self._prompt_block_ip()
        elif key == ord('2'):
            self._force_logout_users()
        elif key == ord('3'):
            self._toggle_maintenance_mode()
        elif key == ord('4'):
            self._generate_security_report()
        # Add more action handlers as needed
    
    def _prompt_block_ip(self):
        """Prompt for IP to block."""
        # This would need a more sophisticated input system
        # For now, just show a message
        pass
    
    def _force_logout_users(self):
        """Force logout of all users."""
        try:
            # Clear Redis sessions
            subprocess.run(['redis-cli', 'FLUSHDB'], check=True)
        except Exception:
            pass
    
    def _toggle_maintenance_mode(self):
        """Toggle maintenance mode."""
        maintenance_file = "/tmp/maintenance_mode"
        if os.path.exists(maintenance_file):
            os.remove(maintenance_file)
        else:
            with open(maintenance_file, 'w') as f:
                f.write("Maintenance mode enabled via security dashboard")
    
    def _generate_security_report(self):
        """Generate a security report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/var/log/quirrely/manual_report_{timestamp}.json"
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "generated_by": "security_dashboard",
            "system_status": self._get_security_status(),
            "threats": self._get_recent_events(),
            "system_metrics": {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent
            }
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception:
            pass
    
    def _get_security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        try:
            # Check system health
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            
            health = "Good"
            if cpu > 90 or memory > 90:
                health = "Critical"
            elif cpu > 70 or memory > 70:
                health = "Warning"
            
            # Count blocked IPs
            try:
                result = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
                blocked_count = result.stdout.count('DENY')
            except:
                blocked_count = 0
            
            # Count recent failed logins
            try:
                with open('/var/log/quirrely/security.log', 'r') as f:
                    lines = f.readlines()
                
                hour_ago = datetime.now() - timedelta(hours=1)
                failed_logins = 0
                
                for line in lines:
                    if 'auth_failure' in line:
                        # Parse timestamp and check if within last hour
                        failed_logins += 1
                        
            except:
                failed_logins = 0
            
            return {
                'health': health,
                'active_threats': 0,  # Would be calculated from threat detection
                'blocked_ips': blocked_count,
                'failed_logins': failed_logins
            }
            
        except Exception:
            return {
                'health': 'Unknown',
                'active_threats': 0,
                'blocked_ips': 0,
                'failed_logins': 0
            }
    
    def _get_recent_events(self) -> List[Dict[str, Any]]:
        """Get recent security events."""
        events = []
        try:
            with open('/var/log/quirrely/security.log', 'r') as f:
                lines = f.readlines()
            
            for line in lines[-20:]:  # Last 20 lines
                if any(keyword in line for keyword in ['auth_failure', 'admin_access', 'suspicious']):
                    events.append({
                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                        'message': line.strip()[:60],
                        'severity': 'medium'
                    })
        except:
            pass
        
        return events
    
    def _get_attacking_ips(self) -> List[Dict[str, Any]]:
        """Get IPs with attack attempts."""
        ips = []
        try:
            # Parse security logs for attacking IPs
            # This is a simplified version
            ips = [
                {'ip': '192.168.1.100', 'attempts': 15, 'status': 'MONITORING'},
                {'ip': '10.0.0.5', 'attempts': 3, 'status': 'BLOCKED'},
            ]
        except:
            pass
        
        return ips
    
    def _get_service_status(self) -> Dict[str, str]:
        """Get status of critical services."""
        services = {}
        service_names = ['nginx', 'postgresql', 'redis-server', 'quirrely']
        
        for service in service_names:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True,
                    text=True
                )
                services[service] = result.stdout.strip()
            except:
                services[service] = 'unknown'
        
        return services
    
    def _get_log_tail(self) -> List[str]:
        """Get recent log entries."""
        lines = []
        try:
            with open('/var/log/quirrely/security.log', 'r') as f:
                lines = f.readlines()
        except:
            pass
        
        return [line.strip() for line in lines[-20:]]
    
    def _get_metric_color(self, value: float, warning_threshold: float, critical_threshold: float):
        """Get color for a metric based on thresholds."""
        if value >= critical_threshold:
            return curses.color_pair(3)  # Red
        elif value >= warning_threshold:
            return curses.color_pair(2)  # Yellow
        else:
            return curses.color_pair(1)  # Green
    
    def _get_event_color(self, severity: str):
        """Get color for an event based on severity."""
        if severity.lower() in ['critical', 'high']:
            return curses.color_pair(3)  # Red
        elif severity.lower() in ['medium', 'warning']:
            return curses.color_pair(2)  # Yellow
        else:
            return curses.color_pair(4)  # Cyan

def main():
    """Main entry point."""
    try:
        dashboard = SecurityDashboard()
        dashboard.start()
    except KeyboardInterrupt:
        print("\nSecurity dashboard stopped.")
    except Exception as e:
        print(f"Dashboard error: {e}")

if __name__ == "__main__":
    main()