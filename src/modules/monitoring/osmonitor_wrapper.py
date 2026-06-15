import os
import re
import time
import subprocess
import logging
from threading import Thread, Event
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import psutil

@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    connections: int
    suspicious: bool = False
                                                                       class OSMonitor:                                                           """
    Advanced OS monitoring with behavioral analysis and anomaly
detection
    Tracks processes, resources, and suspicious activities in          real-time                                                                  """
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.osmonitor")
        self.running = Event()
        self.whitelist = self._load_whitelist()
        self.baseline = self._establish_baseline()
        self.suspicious_processes: Set[int] = set()
        self.monitor_thread: Optional[Thread] = None

    def _load_whitelist(self) -> Set[str]:
        """Load whitelisted processes from config"""
        try:
            whitelist_path = self.config.get('whitelist_path',
'')
            if os.path.exists(whitelist_path):
                with open(whitelist_path, 'r') as f:
                    return {line.strip() for line in f if
line.strip()}
            return set()
        except Exception as e:
            self.logger.error(f"Failed to load whitelist:
{str(e)}")
            return set()

    def _establish_baseline(self, duration: int = 30) ->
Dict[str, float]:
        """Establish baseline system metrics"""
        self.logger.info("Establishing system baseline...")
        metrics = {
            'cpu_avg': 0.0,
            'memory_avg': 0.0,
            'process_count': 0,
            'network_avg': 0.0
        }

        samples = []
        end_time = time.time() + duration

        while time.time() < end_time:
            sample = {
                'cpu': psutil.cpu_percent(interval=1.0),
                'memory': psutil.virtual_memory().percent,
                'process_count': len(psutil.pids()),
                'network': self._get_network_usage()
            }
            samples.append(sample)
            time.sleep(1)

        # Calculate averages
        if samples:
            metrics['cpu_avg'] = sum(s['cpu'] for s in samples) /
len(samples)
            metrics['memory_avg'] = sum(s['memory'] for s in
samples) / len(samples)
            metrics['process_count'] = max(s['process_count'] for
s in samples)
            metrics['network_avg'] = sum(s['network'] for s in
samples) / len(samples)

        self.logger.info(f"Baseline established: {metrics}")
        return metrics

    def _get_network_usage(self) -> float:
        """Get current network usage in KB/s"""
        try:
            net_io = psutil.net_io_counters()
            return (net_io.bytes_sent + net_io.bytes_recv) /
1024.0
        except:
            return 0.0

    def _analyze_process(self, proc: psutil.Process) ->
Optional[ProcessInfo]:
        """Analyze process for suspicious behavior"""
        try:
            with proc.oneshot():
                name = proc.name()
                pid = proc.pid

                # Skip whitelisted processes
                if name in self.whitelist:
                    return None

                # Get process metrics
                cpu = proc.cpu_percent(interval=0.1)
                memory = proc.memory_percent()
                connections = len(proc.connections())

                # Behavioral analysis
                suspicious = False

                # High resource usage
                if (cpu > self.baseline['cpu_avg'] * 3 or
                    memory > self.baseline['memory_avg'] * 3):
                    self.logger.warning(f"High resource usage:
{name} (PID: {pid})")
                    suspicious = True

                # Unusual network activity
                if connections > 10:  # Arbitrary threshold
                    self.logger.warning(f"Excessive connections:
{name} (PID: {pid})")
                    suspicious = True

                # Suspicious process names
                suspicious_patterns = [
                    r'[0-9]{5}',  # Random numbers
                    r'^(.)\1+$',  # Repeated characters
                    r'system32', 'bash', 'sh', 'python', 'perl'
                ]

                if any(re.search(p, name, re.IGNORECASE) for p in
suspicious_patterns):
                    self.logger.warning(f"Suspicious process
name: {name} (PID: {pid})")
                    suspicious = True

                return ProcessInfo(
                    pid=pid,
                    name=name,
                    cpu_percent=cpu,
                    memory_percent=memory,
                    connections=connections,
                    suspicious=suspicious
                )

        except (psutil.NoSuchProcess, psutil.AccessDenied,
psutil.ZombieProcess):
            return None

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running.is_set():
            try:
                # System-wide metrics
                cpu_usage = psutil.cpu_percent(interval=1.0)
                memory_usage = psutil.virtual_memory().percent
                process_count = len(psutil.pids())

                # Check for anomalies
                if (cpu_usage > self.baseline['cpu_avg'] * 2 or
                    memory_usage > self.baseline['memory_avg'] *
2 or
                    process_count >
self.baseline['process_count'] * 1.5):
                    self.logger.warning(f"System anomaly
detected: CPU={cpu_usage}%, MEM={memory_usage}%,
PROCS={process_count}")

                # Process monitoring
                for proc in psutil.process_iter(['pid', 'name',
'username']):
                    process_info = self._analyze_process(proc)                             if process_info and process_info.suspicious:       
self.suspicious_processes.add(process_info.pid)

self._handle_suspicious_process(process_info)                                                                                                                 time.sleep(5)  # Adjustable interval

            except Exception as e:
                self.logger.error(f"Monitoring error: {str(e)}")                       time.sleep(10)                                         
    def _handle_suspicious_process(self, proc_info: ProcessInfo):
        """Handle suspicious process detection"""
        try:
            self.logger.warning(f"Taking action against
suspicious process: {proc_info.name} (PID: {proc_info.pid})")

            # Kill the process
            try:
                proc = psutil.Process(proc_info.pid)
                proc.terminate()
                proc.wait(timeout=3)
                self.logger.info(f"Terminated process:
{proc_info.name} (PID: {proc_info.pid})")
            except:
                try:
                    proc.kill()
                    self.logger.info(f"Killed process:
{proc_info.name} (PID: {proc_info.pid})")
                except:
                    self.logger.error(f"Failed to kill process:
{proc_info.name} (PID: {proc_info.pid})")

            # Log the incident
            incident = {
                'timestamp': time.time(),
                'process': proc_info.name,
                'pid': proc_info.pid,
                'cpu': proc_info.cpu_percent,
                'memory': proc_info.memory_percent,
                'connections': proc_info.connections
            }
            self.logger.critical(f"Suspicious process handled:
{incident}")

        except Exception as e:
            self.logger.error(f"Error handling suspicious
process: {str(e)}")

    def start(self):
        """Start the OS monitor"""
        if not self.running.is_set():
            self.running.set()
            self.monitor_thread =
Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("OS Monitor started")

    def stop(self):
        """Stop the OS monitor"""
        if self.running.is_set():
            self.running.clear()
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            self.logger.info("OS Monitor stopped")

    def get_suspicious_processes(self) -> List[ProcessInfo]:
        """Get list of currently suspicious processes"""
        results = []
        for pid in list(self.suspicious_processes):
            try:
                proc = psutil.Process(pid)
                if proc.is_running():
                    results.append(self._analyze_process(proc))
            except:
                self.suspicious_processes.remove(pid)
        return [r for r in results if r]
```
