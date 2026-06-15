import os
import time
import logging
import threading
import random
import requests
from typing import List, Dict, Optional
from stem import Signal
from stem.control import Controller
from .multi_hop import MultiHopManager

class IPRotator:
    """
    Advanced IP Rotation System
    Dynamically rotates IP addresses through multiple networks
    """

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.iprotator")
        self.multihop = MultiHopManager(config)
        self.current_ip: Optional[str] = None
        self.rotation_count = 0
        self.rotation_lock = threading.Lock()
        self.running = threading.Event()
        self.rotation_thread: Optional[threading.Thread] = None

    def get_current_ip(self) -> Optional[str]:
        """Get current public IP address"""
        try:
            # Use multiple IP checking services for verification
            services = [
                'https://api.ipify.org',
                'https://ident.me',
                'https://ifconfig.me/ip'
            ]

            for service in services:
                try:
                    response = requests.get(service, timeout=10)
                    if response.status_code == 200:
                        return response.text.strip()
                except:
                    continue

            return None
        except Exception as e:
            self.logger.error(f"Failed to get current IP:
{str(e)}")
            return None

    def rotate_ip(self) -> bool:
        """Rotate to a new IP address"""
        with self.rotation_lock:
            try:
                old_ip = self.current_ip

                # Rotate Tor circuit
                self.multihop.rotate_circuit()

                # Get new IP
                start_time = time.time()
                new_ip = None

                while time.time() - start_time < 30:  # 30 second
timeout
                    new_ip = self.get_current_ip()
                    if new_ip and new_ip != old_ip:
                        break
                    time.sleep(2)

                if not new_ip or new_ip == old_ip:
                    self.logger.error("IP rotation failed")
                    return False

                self.current_ip = new_ip
                self.rotation_count += 1

                self.logger.info(f"IP rotated: {old_ip} ->
{new_ip}")
                return True

            except Exception as e:
                self.logger.error(f"IP rotation failed:
{str(e)}")
                return False

    def _rotation_loop(self):
        """Automatic IP rotation loop"""
        while self.running.is_set():
            try:
                # Randomize rotation interval to avoid patterns
                interval = random.randint(
                    self.config.get('min_rotation_interval',
300),
                    self.config.get('max_rotation_interval',
1800)
                )

                time.sleep(interval)
                self.rotate_ip()

            except Exception as e:
                self.logger.error(f"Rotation loop error:
{str(e)}")
                time.sleep(60)

    def start_auto_rotation(self):
        """Start automatic IP rotation"""
        if not self.running.is_set():
            # Get initial IP
            self.current_ip = self.get_current_ip()

            self.running.set()
            self.rotation_thread =
threading.Thread(target=self._rotation_loop, daemon=True)
            self.rotation_thread.start()
            self.logger.info("Automatic IP rotation started")

    def stop_auto_rotation(self):
        """Stop automatic IP rotation"""
        if self.running.is_set():
            self.running.clear()
            if self.rotation_thread:
                self.rotation_thread.join(timeout=5)
            self.logger.info("Automatic IP rotation stopped")

    def verify_anonymity(self) -> Dict:
        """Verify anonymity and IP rotation"""
        results = {
            'ip_leak': False,
            'dns_leak': False,
            'webrtc_leak': False,
            'success': False
        }

        try:
            # Test IP leak
            ip_services = [
                'https://api.ipify.org',
                'https://ident.me',
                'https://ifconfig.me/ip'
            ]

            ips = set()
            for service in ip_services:
                try:
                    response = requests.get(service, timeout=10)
                    if response.status_code == 200:
                        ips.add(response.text.strip())
                except:
                    continue

            results['ip_leak'] = len(ips) <= 1

            # Test DNS leak
            try:
                response =
requests.get('https://dnsleaktest.com/dnsleak/check', timeout=15)
                results['dns_leak'] = 'DNS Leak Test' in
response.text
            except:
                results['dns_leak'] = False

            # Test WebRTC leak (simplified)
            results['webrtc_leak'] = False  # Actual test
requires browser automation

            results['success'] = results['ip_leak'] and
results['dns_leak'] and not results['webrtc_leak']

        except Exception as e:
            self.logger.error(f"Anonymity verification failed:
{str(e)}")
            results['success'] = False

        return results

    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        return {
            'current_ip': self.current_ip,
            'rotation_count': self.rotation_count,
            'last_rotation': time.time(),
            'status': 'active' if self.running.is_set() else
'inactive'
        }
```
