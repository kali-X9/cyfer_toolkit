import os
import time
import logging
import subprocess
import threading
from typing import List, Dict, Optional
from stem import Signal
from stem.control import Controller

class MultiHopManager:
    """
    Advanced Multi-Hop Routing System
    Implements dynamic circuit creation and management for Tor
    """

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.multihop")
        self.tor_control_port = config.get('tor_control_port',
9051)
        self.tor_control_password =
config.get('tor_control_password', '')
        self.circuits: List[Dict] = []
        self.current_circuit: Optional[Dict] = None
        self.controller: Optional[Controller] = None
        self.rotation_interval = config.get('rotation_interval',
300)  # 5 minutes
        self.rotation_thread: Optional[threading.Thread] = None
        self.running = threading.Event()

    def connect_controller(self) -> bool:
        """Connect to Tor control port"""
        try:
            self.controller =
Controller.from_port(port=self.tor_control_port)

self.controller.authenticate(password=self.tor_control_password)
            self.logger.info("Connected to Tor control port")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Tor
controller: {str(e)}")
            return False

    def build_circuit(self, entry_node: str = None, middle_node:
str = None,
                     exit_node: str = None) -> Optional[str]:
        """Build a custom Tor circuit"""
        try:
            if not self.controller:
                if not self.connect_controller():
                    return None

            # Build circuit specification
            circuit_spec = []

            # Add entry node
            if entry_node:
                circuit_spec.append(entry_node)
            else:
                circuit_spec.append('')

            # Add middle node
            if middle_node:
                circuit_spec.append(middle_node)

            # Add exit node
            if exit_node:
                circuit_spec.append(exit_node)

            # Create new circuit
            circuit_id =
self.controller.new_circuit(circuit_spec, await_build=True)

            # Get circuit information
            circuit = {
                'id': circuit_id,
                'entry': entry_node or 'random',
                'middle': middle_node or 'random',
                'exit': exit_node or 'random',
                'created_at': time.time(),
                'bytes_sent': 0,
                'bytes_received': 0
            }

            self.circuits.append(circuit)
            self.current_circuit = circuit

            self.logger.info(f"Built new circuit: {circuit_id}")
            return circuit_id

        except Exception as e:
            self.logger.error(f"Failed to build circuit:
{str(e)}")
            return None

    def rotate_circuit(self):
        """Rotate to a new circuit"""
        try:
            if not self.controller:
                return

            # Signal Tor for new identity
            self.controller.signal(Signal.NEWNYM)

            # Build new circuit
            self.build_circuit()

            # Close old circuits (keep last 3)
            while len(self.circuits) > 3:
                old_circuit = self.circuits.pop(0)
                try:

self.controller.close_circuit(old_circuit['id'])
                except:
                    pass

            self.logger.info("Rotated to new circuit")

        except Exception as e:
            self.logger.error(f"Circuit rotation failed:
{str(e)}")

    def _rotation_loop(self):
        """Automatic circuit rotation loop"""
        while self.running.is_set():
            try:
                time.sleep(self.rotation_interval)
                self.rotate_circuit()
            except Exception as e:
                self.logger.error(f"Rotation loop error:
{str(e)}")
                time.sleep(30)

    def start_auto_rotation(self):
        """Start automatic circuit rotation"""
        if not self.running.is_set():
            self.running.set()
            self.rotation_thread =
threading.Thread(target=self._rotation_loop, daemon=True)
            self.rotation_thread.start()
            self.logger.info("Automatic circuit rotation
started")

    def stop_auto_rotation(self):
        """Stop automatic circuit rotation"""
        if self.running.is_set():
            self.running.clear()
            if self.rotation_thread:
                self.rotation_thread.join(timeout=5)
            self.logger.info("Automatic circuit rotation
stopped")

    def get_circuit_info(self, circuit_id: str) ->
Optional[Dict]:
        """Get information about a specific
circuit"""
        try:
            if not self.controller:
                return None

            circuit = self.controller.get_circuit(circuit_id)
            return {
                'id': circuit_id,
                'status': circuit.status,
                'path': [hop[0] for hop in circuit.path],
                'bytes_sent': circuit.bytes_sent,
                'bytes_received': circuit.bytes_received,
                'created_at': circuit.created_utc
            }
        except:
            return None

    def close_all_circuits(self):
        """Close all active circuits"""
        try:
            if not self.controller:
                return

            for circuit in self.circuits:
                try:
                    self.controller.close_circuit(circuit['id'])
                except:
                    pass

            self.circuits.clear()
            self.current_circuit = None
            self.logger.info("All circuits closed")

        except Exception as e:
            self.logger.error(f"Failed to close circuits:
{str(e)}")
```
