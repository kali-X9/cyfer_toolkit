import os
import time
import logging
import curses
from typing import Dict, Any, List
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from modules.monitoring.netstat_monitor import NetstatMonitor
from modules.anonymity.tor_manager import TorManager
from modules.anonymity.v2ray_manager import V2RayManager

class CyberOpsDashboard:
    """
    Advanced Real-time Dashboard for CYFER Toolkit
    Provides comprehensive system monitoring and control
    """

    def __init__(self, config: Dict):
        self.config = config
        self.console = Console()
        self.logger = logging.getLogger("cyfer.dashboard")
        self.net_monitor = NetstatMonitor(config)
        self.tor_manager = TorManager(PortManager(), config)
        self.v2ray_manager = V2RayManager(PortManager(), config)
        self.running = False
        self.layout = self._create_layout()

    def _create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()

        # Split into main sections
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )

        # Split main section
        layout["main"].split_row(
            Layout(name="left_panel", ratio=1),
            Layout(name="right_panel", ratio=1)
        )

        # Split left panel
        layout["left_panel"].split(
            Layout(name="anonymity", size=10),
            Layout(name="network", ratio=1)
        )

        # Split right panel
        layout["right_panel"].split(
            Layout(name="threats", size=10),
            Layout(name="logs", ratio=1)
        )

        return layout

    def _update_header(self) -> Panel:
        """Update header panel"""
        current_time = datetime.now().strftime("%Y-%m-%d
%H:%M:%S")
        title = Text(f"CYFER ULTIMATE GHOST TOOLKIT v3.0 - OMEGA
MODE", style="bold blue")
        status = Text(f"Status: ACTIVE | Time: {current_time}",
style="green")

        header = Table.grid(expand=True)
        header.add_column(justify="center")
        header.add_row(title)
        header.add_row(status)

        return Panel(header, style="bold white")

    def _update_anonymity_panel(self) -> Panel:
        """Update anonymity status panel"""
        tor_status = self.tor_manager.test_connection()
        v2ray_status = self.v2ray_manager.test_connection()

        table = Table(show_header=False, show_lines=True)
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green" if tor_status
else "red")
        table.add_column("IP", width=20)

        table.add_row("Tor",
                     "ONLINE" if tor_status else "OFFLINE",
                     self.tor_manager.get_current_ip() or "N/A")
        table.add_row("V2Ray",
                     "ONLINE" if v2ray_status else "OFFLINE",                               "N/A")                                            
        return Panel(table, title="Anonymity Status",
border_style="blue")
                                                                           def _update_network_panel(self) -> Panel:                                  """Update network activity panel"""
        connections = self.net_monitor.get_connections()[:10]  #
Show top 10
                                                                               table = Table(show_header=True)                                        table.add_column("Process", style="cyan")
        table.add_column("Local", style="magenta")
        table.add_column("Remote", style="yellow")
        table.add_column("Status", style="green")

        for conn in connections:
            table.add_row(
                conn.name[:15],
                f"{conn.local_addr}:{conn.local_port}",
                f"{conn.remote_addr}:{conn.remote_port}",
                conn.status
            )

        return Panel(table, title="Network Activity",
border_style="green")

    def _update_threats_panel(self) -> Panel:
        """Update threats panel"""
        # This would interface with your threat detection system
        threats = []  # Get from your threat detection

        table = Table(show_header=True)
        table.add_column("Time", style="cyan")
        table.add_column("Threat", style="red")
        table.add_column("Severity", style="yellow")

        for threat in threats[:5]:  # Show top 5 threats
            table.add_row(

datetime.fromtimestamp(threat['timestamp']).strftime("%H:%M:%S"),
                threat['description'][:30],
                threat['severity']
            )

        return Panel(table, title="Active Threats",
border_style="red")

    def _update_logs_panel(self) -> Panel:
        """Update logs panel"""
        # This would read from your encrypted log file
        logs = ["Log entry 1", "Log entry 2"]  # Get from your
log system

        log_text = Text()
        for log in logs[-10:]:  # Show last 10 logs
            log_text.append(f"{log}\n", style="white")

        return Panel(log_text, title="System Logs",
border_style="yellow")

    def _update_footer(self) -> Panel:
        """Update footer panel"""
        commands = "[Q]uit  [R]otate IP  [S]tatus  [L]ogs
[T]hreats  [E]xit"
        return Panel(commands, style="bold white on blue")

    def update_dashboard(self) -> Layout:
        """Update all dashboard panels"""
        self.layout["header"].update(self._update_header())

self.layout["anonymity"].update(self._update_anonymity_panel())

self.layout["network"].update(self._update_network_panel())

self.layout["threats"].update(self._update_threats_panel())
        self.layout["logs"].update(self._update_logs_panel())                  self.layout["footer"].update(self._update_footer())
        return self.layout

    def start(self):
        """Start the dashboard"""
        self.running = True
        self.net_monitor.start()

        try:
            with Live(self.layout, refresh_per_second=2,
screen=True) as live:
                while self.running:
                    try:
                        live.update(self.update_dashboard())
                        time.sleep(0.5)
                    except KeyboardInterrupt:
                        self.running = False
        except Exception as e:
            self.logger.error(f"Dashboard error: {str(e)}")
        finally:
            self.net_monitor.stop()
