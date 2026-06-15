import os
import time
import logging
import subprocess
from typing import List
from dataclasses import asdict
from .anomaly_detector import Anomaly

class ResponseEngine:
    """
    Automated Response Engine
    Implements real-time countermeasures against detected threats
    """

    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.response_engine")
        self.actions_taken = []

    def handle_anomalies(self, anomalies: List[Anomaly]):
        """Handle a list of detected anomalies"""
        for anomaly in anomalies:
            try:
                if anomaly.category == 'process':
                    self._handle_process_anomaly(anomaly)
                elif anomaly.category == 'network':
                    self._handle_network_anomaly(anomaly)
                elif anomaly.category == 'file':
                    self._handle_file_anomaly(anomaly)

                # Log the action
                self.actions_taken.append({
                    'timestamp': time.time(),
                    'anomaly': asdict(anomaly),
                    'action': 'handled'
                })

            except Exception as e:
                self.logger.error(f"Failed to handle anomaly:
{str(e)}")
                self.actions_taken.append({
                    'timestamp': time.time(),
                    'anomaly': asdict(anomaly),
                    'action': 'failed',
                    'error': str(e)
                })

    def _handle_process_anomaly(self, anomaly: Anomaly):
        """Handle process-related anomalies"""
        pid = anomaly.details.get('pid')
        process_name = anomaly.details.get('process', 'unknown')

        if pid:
            try:
                # Kill the suspicious process
                self.logger.warning(f"Terminating suspicious
process: {process_name} (PID: {pid})")
                subprocess.run(['kill', '-9', str(pid)],
check=True)

                # Additional containment
                self._contain_threat(anomaly)

            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to kill process {pid}:
{str(e)}")
                raise

    def _handle_network_anomaly(self, anomaly: Anomaly):
        """Handle network-related anomalies"""
        remote_ip = anomaly.details.get('remote_ip')
        remote_port = anomaly.details.get('remote_port')
        pid = anomaly.details.get('pid')

        if pid:
            try:
                # Kill the process making suspicious connections
                self.logger.warning(f"Terminating process with
suspicious connection: PID {pid}")
                subprocess.run(['kill', '-9', str(pid)],
check=True)
            except subprocess.CalledProcessError:
                pass

        if remote_ip:
            try:
                # Block the suspicious IP
                self.logger.warning(f"Blocking suspicious IP:
{remote_ip}")
                subprocess.run(['iptables', '-A', 'INPUT', '-s',
remote_ip, '-j', 'DROP'], check=True)
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to block IP
{remote_ip}: {str(e)}")

    def _handle_file_anomaly(self, anomaly: Anomaly):
        """Handle file-related anomalies"""
        file_path = anomaly.details.get('file_path')

        if file_path and os.path.exists(file_path):
            try:
                # Quarantine the suspicious file
                quarantine_dir =
self.config.get('quarantine_dir', '/data/data/com.termux/files/homself.config.get('quarantine_dir','/data/data/com.termux/files/home/.cyfer_quarantine')
                os.makedirs(quarantine_dir, exist_ok=True)

                # Move file to quarantine
                import shutil
                dest = os.path.join(quarantine_dir,
os.path.basename(file_path))
                shutil.move(file_path, dest)

                self.logger.warning(f"Quarantined suspicious
file: {file_path} -> {dest}")

            except Exception as e:
                self.logger.error(f"Failed to quarantine file
{file_path}: {str(e)}")
                # Attempt to delete the file as last resort
                try:
                    os.remove(file_path)
                except:
                    pass

    def _contain_threat(self, anomaly: Anomaly):
        """Contain the threat by isolating affected components"""
        # Implement additional containment measures here
        pass

    def trigger_kill_switch(self):
        """Activate the kill switch in case of critical threat"""
        from .kill_switch import KillSwitch
        kill_switch = KillSwitch(self.config)
        kill_switch.activate()
```
