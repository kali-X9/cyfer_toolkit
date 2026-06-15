import os
import time
import logging
import threading
import json
import psutil
import yara
from dataclasses import dataclass
from typing import Dict, List, Set, Optional
from datetime import datetime

@dataclass
class Anomaly:
    timestamp: float
    category: str
    severity: str
    details: Dict
    process_info: Optional[Dict] = None
    network_info: Optional[Dict] = None
    file_info: Optional[Dict] = None

class AnomalyDetector:
    """
    Advanced Anomaly Detection Engine
    Implements machine learning and signature-based detection
    """

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.anomaly_detector")
        self.anomalies: List[Anomaly] = []
        self.running = threading.Event()
        self.monitor_thread: Optional[threading.Thread] = None
        self.baseline = self._establish_baseline()
        self.yara_rules = self._load_yara_rules()
        self.suspicious_patterns =
self._load_suspicious_patterns()
        self.last_checked = time.time()

    def _establish_baseline(self, duration: int = 300) -> Dict:
        """Establish system behavior baseline"""
        self.logger.info("Establishing system baseline...")
        metrics = {
            'cpu_avg': 0.0,
            'memory_avg': 0.0,
            'process_count': 0,
            'network_conns': 0,
            'file_ops': 0
        }

        samples = []
        end_time = time.time() + duration

        while time.time() < end_time:
            sample = {
                'cpu': psutil.cpu_percent(interval=1.0),
                'memory': psutil.virtual_memory().percent,
                'process_count': len(psutil.pids()),
                'network_conns': len(psutil.net_connections()),
                'file_ops': self._get_file_activity()
            }
            samples.append(sample)
            time.sleep(5)

        # Calculate baseline metrics
        if samples:
            metrics['cpu_avg'] = sum(s['cpu'] for s in samples) /
len(samples)
            metrics['memory_avg'] = sum(s['memory'] for s in
samples) / len(samples)
            metrics['process_count'] = max(s['process_count'] for
s in samples)
            metrics['network_conns'] = max(s['network_conns'] for
s in samples)
            metrics['file_ops'] = max(s['file_ops'] for s in
samples)

        self.logger.info(f"Baseline established: {metrics}")
        return metrics

    def _load_yara_rules(self):
        """Load YARA rules for pattern matching"""
        try:
            rules_dir = self.config.get('yara_rules_dir',
'config/yara_rules')
            rules = {}
            for root, _, files in os.walk(rules_dir):
                for file in files:                                                         if file.endswith(('.yar', '.yara')):
                        rule_path = os.path.join(root, file)                                   try:
                            rules[file] = yara.compile(rule_path)                              except Exception as e:
                            self.logger.error(f"Failed to compile      YARA rule {file}: {str(e)}")
            return rules                                                       except Exception as e:
            self.logger.error(f"Failed to load YARA rules:             {str(e)}")                                                                         return {}                                                  
    def _load_suspicious_patterns(self) -> Dict:                               """Load suspicious behavior patterns"""
        return {                                                                   'process': [                                                               {'pattern': r'[0-9a-f]{16}', 'description':            'Hex-encoded payload'},
                {'pattern': r'(eval\(|base64_decode|exec\()',          'description': 'Code execution'},
                {'pattern': r'\.onion', 'description': 'Tor
hidden service'}
            ],
            'network': [
                {'pattern':
r':(6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{4}|[1-9]r':(6553[0-5]|655[0-2]\d|65[0-4]\d{2}|[0-4]\d{3}|[1-5]\d{4}|[1-9]\d{0,3}|0)$',
                 'description': 'Suspicious port'}
            ],
            'file': [
                {'pattern': r'\.encrypted$', 'description':
'Ransomware artifact'},
                {'pattern': r'\.miner$', 'description':
'Cryptominer'},
                {'pattern': r'passw', 'description': 'Sensitive
data'}
            ]
        }

    def _detect_process_anomalies(self) -> List[Anomaly]:
        """Detect suspicious processes"""
        anomalies = []
        try:
            for proc in psutil.process_iter(['pid', 'name',
'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    # Check CPU usage
                    if proc.info['cpu_percent'] >
self.baseline['cpu_avg'] * 3:
                        anomalies.append(Anomaly(
                            timestamp=time.time(),
                            category='process',
                            severity='high',
                            details={
                                'type': 'high_cpu',
                                'process': proc.info['name'],
                                'pid': proc.info['pid'],
                                'cpu_usage':
proc.info['cpu_percent']
                            },
                            process_info=proc.info
                        ))

                    # Check for suspicious command line
                    cmdline = ' '.join(proc.info['cmdline']) if
proc.info['cmdline'] else ''
                    for pattern in
self.suspicious_patterns['process']:
                        if re.search(pattern['pattern'], cmdline,
re.IGNORECASE):
                            anomalies.append(Anomaly(
                                timestamp=time.time(),
                                category='process',
                                severity='critical',
                                details={
                                    'type': 'suspicious_cmdline',
                                    'process': proc.info['name'],
                                    'pid': proc.info['pid'],
                                    'pattern':
pattern['description'],
                                    'cmdline': cmdline
                                },
                                process_info=proc.info
                            ))

                    # Check for hidden processes
                    if proc.info['name'].startswith('.') or '..'
in proc.info['name']:
                        anomalies.append(Anomaly(
                            timestamp=time.time(),
                            category='process',
                            severity='medium',
                            details={
                                'type': 'hidden_process',
                                'process': proc.info['name'],
                                'pid': proc.info['pid']
                            },
                            process_info=proc.info
                        ))

                except (psutil.NoSuchProcess,
psutil.AccessDenied):
                    continue

        except Exception as e:
            self.logger.error(f"Process anomaly detection failed:
{str(e)}")

        return anomalies

    def _detect_network_anomalies(self) -> List[Anomaly]:
        """Detect suspicious network activity"""
        anomalies = []
        try:
            whitelist = self.config.get('network_whitelist', [])

            for conn in psutil.net_connections(kind='inet'):
                try:
                    if not conn.raddr:
                        continue

                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port

                    # Check for connections to suspicious IPs
                    if any(self._ip_in_network(remote_ip, net)
for net in whitelist):
                        continue

                    # Check for suspicious ports
                    if remote_port > 49152:  # Dynamic/private
ports
                        proc = psutil.Process(conn.pid) if
conn.pid else None
                        anomalies.append(Anomaly(
                            timestamp=time.time(),
                            category='network',
                            severity='medium',
                            details={
                                'type': 'suspicious_port',
                                'remote_ip': remote_ip,
                                'remote_port': remote_port,
                                'pid': conn.pid,
                                'process': proc.name() if proc
else 'unknown'
                            },
                            network_info={
                                'local_addr':
f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else '',
                                'remote_addr':
f"{remote_ip}:{remote_port}",
                                'status': conn.status
                            }
                        ))

                except (psutil.NoSuchProcess,
psutil.AccessDenied):
                    continue

        except Exception as e:
            self.logger.error(f"Network anomaly detection failed:
{str(e)}")

        return anomalies

    def _detect_file_anomalies(self) -> List[Anomaly]:
        """Detect suspicious file activities"""
        anomalies = []
        try:
            # Check for recently modified sensitive files
            sensitive_dirs = [
                '/data/data/com.termux/files/home',
                '/data/data/com.termux/files/usr',
                '/sdcard/Android'
            ]

            for directory in sensitive_dirs:
                if not os.path.exists(directory):
                    continue

                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Check file modification time
                            stat = os.stat(file_path)
                            if time.time() - stat.st_mtime < 300:
 # Modified in last 5 minutes
                                # Check for suspicious patterns
                                for pattern in
self.suspicious_patterns['file']:
                                    if
re.search(pattern['pattern'], file, re.IGNORECASE):
                                        anomalies.append(Anomaly(

timestamp=time.time(),

category='file',
                                            severity='high',
                                            details={
                                                'type':
'suspicious_file',
                                                'file_path':
file_path,
                                                'pattern':
pattern['description'],
                                                'modified_time':
stat.st_mtime
                                            },
                                            file_info={
                                                'size':
stat.st_size,
                                                'permissions':
stat.st_mode
                                            }
                                        ))

                        except (OSError, PermissionError):
                            continue

        except Exception as e:
            self.logger.error(f"File anomaly detection failed:
{str(e)}")

        return anomalies

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running.is_set():
            try:
                # Detect anomalies
                process_anomalies =
self._detect_process_anomalies()
                network_anomalies =
self._detect_network_anomalies()
                file_anomalies = self._detect_file_anomalies()

                # Add to anomaly log
                all_anomalies = process_anomalies +
network_anomalies + file_anomalies
                self.anomalies.extend(all_anomalies)

                # Trigger response for critical anomalies
                critical_anomalies = [a for a in all_anomalies if
a.severity in ['high', 'critical']]
                if critical_anomalies:
                    self._trigger_response(critical_anomalies)

                # Log all anomalies
                for anomaly in all_anomalies:
                    self.logger.warning(f"Anomaly detected:
{anomaly}")

                time.sleep(5)  # Adjustable interval

            except Exception as e:
                self.logger.error(f"Anomaly detection loop
failed: {str(e)}")
                time.sleep(10)

    def _trigger_response(self, anomalies: List[Anomaly]):
        """Trigger response actions for detected anomalies"""
        from .response_engine import ResponseEngine
        response_engine = ResponseEngine(self.config)
        response_engine.handle_anomalies(anomalies)

    def start(self):
        """Start anomaly detection"""
        if not self.running.is_set():
            self.running.set()
            self.monitor_thread =
threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Anomaly detector started")

    def stop(self):
        """Stop anomaly detection"""
        if self.running.is_set():
            self.running.clear()
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            self.logger.info("Anomaly detector stopped")

    def get_recent_anomalies(self, minutes: int = 60) ->
List[Anomaly]:
        """Get anomalies from the last N minutes"""
        cutoff = time.time() - (minutes * 60)
        return [a for a in self.anomalies if a.timestamp >=
cutoff]
```
