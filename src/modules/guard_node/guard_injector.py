import os
import time
import logging
import threading
from typing import Dict, List, Optional
from stem.control import Controller
from stem import CircStatus
import stem.process
import stem.connection

class GuardInjector:
    """
    Advanced Guard Node Injection
    Forces Tor to use specific guard nodes
    """

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.guardinjector")
        self.tor_control_port = config.get('tor_control_port',
9051)
        self.tor_control_password =
config.get('tor_control_password', '')
        self.our_guard_nodes = config.get('our_guard_nodes', [])
        self.controller: Optional[Controller] = None
        self.running = threading.Event()
        self.inject_thread: Optional[threading.Thread] = None

    def _connect_controller(self) -> bool:
        """Connect to Tor control port"""
        try:
            self.controller =
Controller.from_port(port=self.tor_control_port)

self.controller.authenticate(password=self.tor_control_password)
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Tor
controller: {str(e)}")
            return False

    def _get_node_fingerprints(self) -> List[str]:
        """Get fingerprints of our guard nodes"""
        try:
            if not self.controller:
                return []

            fingerprints = []
            for nickname in self.our_guard_nodes:
                try:
                    desc =
self.controller.get_network_status(nickname)
                    if desc:
                        fingerprints.append(desc.fingerprint)
                except:
                    continue

            return fingerprints

        except Exception as e:
            self.logger.error(f"Failed to get node fingerprints:
{str(e)}")
            return []

    def _force_guard_selection(self):
        """Force Tor to use our guard nodes"""
        try:
            if not self.controller:
                return

            # Get fingerprints of our guard nodes
            guard_fingerprints = self._get_node_fingerprints()
            if not guard_fingerprints:
                self.logger.warning("No guard node fingerprints
available")
                return

            # Build EntryNodes configuration
            entry_nodes = ','.join(f'${fp}' for fp in
guard_fingerprints)

            # Set Tor configuration
            self.controller.set_conf('UseBridges', '1')
            self.controller.set_conf('EntryNodes', entry_nodes)
            self.controller.set_conf('StrictNodes', '1')

            # Signal Tor to reload configuration
            self.controller.signal('RELOAD')

            self.logger.info(f"Forced guard node selection:
{entry_nodes}")

        except Exception as e:
            self.logger.error(f"Guard injection failed:
{str(e)}")

    def _injection_loop(self):
        """Main injection loop"""
        while self.running.is_set():
            try:
                if not self.controller:
                    if not self._connect_controller():
                        time.sleep(10)
                        continue

                # Check current guard nodes
                guard_nodes =
self.controller.get_info('entry-guards')
                our_guards_used = any(
                    fp in guard_nodes for fp in
self._get_node_fingerprints()
                )

                # If our guards aren't being used, force
selection
                if not our_guards_used:
                    self._force_guard_selection()

                # Check every minute
                time.sleep(60)

            except Exception as e:
                self.logger.error(f"Injection error: {str(e)}")
                time.sleep(30)

    def start(self):
        """Start guard node injection"""
        if not self.running.is_set():
            self.running.set()
            self.inject_thread =
threading.Thread(target=self._injection_loop, daemon=True)
            self.inject_thread.start()
            self.logger.info("Guard injector started")

    def stop(self):
        """Stop guard node injection"""
        if self.running.is_set():
            self.running.clear()
            if self.inject_thread:
                self.inject_thread.join(timeout=5)

            # Reset Tor configuration
            try:
                if self.controller:
                    self.controller.reset_conf('EntryNodes')
                    self.controller.reset_conf('StrictNodes')
                    self.controller.set_conf('UseBridges', '0')
                    self.controller.signal('RELOAD')
            except:
                pass

            self.logger.info("Guard injector stopped")
```
