import os
import sys
import time
import logging
import curses
from typing import Dict, Any, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from modules.self_healing.kill_switch import KillSwitch
from modules.network.ip_rotator import IPRotator
from modules.anonymity.tor_manager import TorManager

class InteractiveMenu:
    """
    Advanced Interactive Command Menu
    Provides intuitive control over CYFER Toolkit
    """

    def __init__(self, config: Dict):
        self.config = config
        self.console = Console()
        self.logger = logging.getLogger("cyfer.menu")
        self.kill_switch = KillSwitch(config)
        self.ip_rotator = IPRotator(config)                                    self.tor_manager = TorManager(PortManager(), config)
        self.running = False

    def display_main_menu(self):
        """Display the main menu"""                                            self.console.clear()

        while True:
            title = Panel.fit(
                "CYFER ULTIMATE GHOST TOOLKIT v3.0 - OMEGA MODE",
                style="bold blue"
            )

            menu = Table(show_header=False, show_lines=True)
            menu.add_column("Option", style="cyan")
            menu.add_column("Description", style="white")

            menu.add_row("1", "Start Anonymity Services")
            menu.add_row("2", "Stop Anonymity Services")
            menu.add_row("3", "Rotate IP Address")
            menu.add_row("4", "Test Anonymity")
            menu.add_row("5", "Launch Secure Browser")
            menu.add_row("6", "System Status")
            menu.add_row("7", "Kill Switch (EMERGENCY)")
            menu.add_row("0", "Exit")

            self.console.print(title)
            self.console.print(menu)

            choice = Prompt.ask("Select an option",
choices=[str(i) for i in range(8)])

            if choice == "1":
                self.start_services()
            elif choice == "2":
                self.stop_services()
            elif choice == "3":
                self.rotate_ip()
            elif choice == "4":
                self.test_anonymity()
            elif choice == "5":
                self.launch_browser()
            elif choice == "6":
                self.system_status()
            elif choice == "7":                                                        self.activate_kill_switch()                                        elif choice == "0":
                self.console.print("[bold green]Exiting...[/]")
                sys.exit(0)

    def start_services(self):
        """Start anonymity services"""
        with self.console.status("[bold green]Starting
services...") as status:
            try:
                # Start Tor
                if not self.tor_manager.start():
                    raise Exception("Failed to start Tor")

                # Start IP rotation
                self.ip_rotator.start_auto_rotation()

                self.console.print("[bold green]All services
started successfully![/]")
            except Exception as e:
                self.console.print(f"[bold red]Error starting
services: {str(e)}[/]")
                self.logger.error(f"Service start failed:
{str(e)}")

    def stop_services(self):
        """Stop anonymity services"""
        if Confirm.ask("Are you sure you want to stop all
services?"):
            with self.console.status("[bold yellow]Stopping
services...") as status:
                try:
                    self.ip_rotator.stop_auto_rotation()
                    self.tor_manager.stop()
                    self.console.print("[bold green]All services
stopped![/]")
                except Exception as e:
                    self.console.print(f"[bold red]Error stopping
services: {str(e)}[/]")
                    self.logger.error(f"Service stop failed:
{str(e)}")

    def rotate_ip(self):
        """Rotate IP address"""
        with self.console.status("[bold blue]Rotating IP
address...") as status:
            try:
                if self.ip_rotator.rotate_ip():
                    self.console.print("[bold green]IP address
rotated successfully![/]")
                else:
                    raise Exception("IP rotation failed")
            except Exception as e:
                self.console.print(f"[bold red]Error rotating IP:
{str(e)}[/]")
                self.logger.error(f"IP rotation failed:
{str(e)}")

    def test_anonymity(self):
        """Test anonymity settings"""
        with self.console.status("[bold cyan]Testing
anonymity...") as status:
            try:
                results = self.ip_rotator.verify_anonymity()

                table = Table(title="Anonymity Test Results")
                table.add_column("Test", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Details", style="white")

                table.add_row("IP Leak", "PASSED" if
results['ip_leak'] else "FAILED",
                            "No IP leaks detected" if
results['ip_leak'] else "IP leak detected")
                table.add_row("DNS Leak", "PASSED" if
results['dns_leak'] else "FAILED",
                            "No DNS leaks detected" if
results['dns_leak'] else "DNS leak detected")
                table.add_row("WebRTC Leak", "PASSED" if not
results['webrtc_leak'] else "FAILED",
                            "No WebRTC leaks" if not
results['webrtc_leak'] else "WebRTC leak detected")

                self.console.print(table)

                if all([results['ip_leak'], results['dns_leak'],
not results['webrtc_leak']]):
                    self.console.print("[bold green]All anonymity
tests passed![/]")
                else:
                    self.console.print("[bold red]Anonymity
compromised! Take action immediately![/]")

            except Exception as e:
                self.console.print(f"[bold red]Anonymity test
failed: {str(e)}[/]")
                self.logger.error(f"Anonymity test failed:
{str(e)}")

    def launch_browser(self):
        """Launch secure browser"""
        from modules.network.browser_proxy import BrowserProxy
        try:
            browser = BrowserProxy(self.config)
            driver = browser.configure_firefox()
            if driver:
                self.console.print("[bold green]Secure browser
launched![/]")
                input("Press Enter when done...")
                browser.close_browser()
            else:
                raise Exception("Failed to launch browser")
        except Exception as e:
            self.console.print(f"[bold red]Failed to launch
browser: {str(e)}[/]")
            self.logger.error(f"Browser launch failed: {str(e)}")

    def system_status(self):
        """Display system status"""
        try:
            # Get system information
            import psutil

            # Create status table
            status_table = Table(title="System Status")
            status_table.add_column("Metric", style="cyan")
            status_table.add_column("Value", style="white")

            # Add system info
            status_table.add_row("CPU Usage",
f"{psutil.cpu_percent()}%")
            status_table.add_row("Memory Usage",
f"{psutil.virtual_memory().percent}%")
            status_table.add_row("Disk Usage",
f"{psutil.disk_usage('/').percent}%")
            status_table.add_row("Current IP",
self.ip_rotator.current_ip or "Unknown")
            status_table.add_row("Uptime", str(datetime.now() -
datetime.fromtimestamp(psutil.boot_time())))

            self.console.print(status_table)
            input("\nPress Enter to continue...")

        except Exception as e:
            self.console.print(f"[bold red]Failed to get system
status: {str(e)}[/]")
            self.logger.error(f"Status check failed: {str(e)}")

    def activate_kill_switch(self):
        """Activate emergency kill switch"""
        if Confirm.ask("[bold red]WARNING: This will terminate
all connections and clear system state. Continue?[/]"):
            with self.console.status("[bold red]Activating kill
switch...") as status:
                try:
                    self.kill_switch.activate()
                    self.console.print("[bold red]KILL SWITCH
ACTIVATED! System is now isolated.[/]")
                except Exception as e:
                    self.console.print(f"[bold red]Kill switch
activation failed: {str(e)}[/]")
                    self.logger.critical(f"Kill switch failed:
{str(e)}")
```
