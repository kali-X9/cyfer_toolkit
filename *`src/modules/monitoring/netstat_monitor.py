import psutil
import socket
import time
import logging
from threading import Thread, Event
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class ConnectionInfo:
    pid: int
    name: str
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: int
    status: str
    protocol: str
    suspicious: bool = False

class NetstatMonitor:
    """Advanced network connection monitor with threat
detection"""
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.netstat")
        self.running = Event()
        self.whitelist = self._load_whitelist()
        self.suspicious_connections: Set[tuple] = set()
        self.monitor_thread: Optional[Thread] = None
        self.port_whitelist = {22, 80, 443, 53}  # Common ports
to ignore

    def _load_whitelist(self) -> Set[str]:
        """Load whitelisted processes and IPs"""
        whitelist = set()
        try:
            # Add local IP ranges
            whitelist.update([
                '127.0.0.1', '::1', '0.0.0.0',
                '192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12'
            ])

            # Add configured whitelist
            whitelist.update(self.config.get('whitelist_ips',
[]))
            return whitelist
        except Exception as e:
            self.logger.error(f"Failed to load whitelist:
{str(e)}")
            return whitelist

    def _is_suspicious_connection(self, conn: ConnectionInfo) ->
bool:
        """Determine if a connection is suspicious"""
        # Check whitelisted processes
        if conn.name in self.whitelist:
            return False

        # Check whitelisted IPs
        if any(self._ip_in_network(conn.remote_addr, net) for net
in self.whitelist):
            return False

        # Check for suspicious ports
        if conn.remote_port in self.port_whitelist:
            return False

        # Suspicious patterns
        suspicious_patterns = [
            r'\.onion$',  # Tor hidden services
            r'^(?!\d+\.\d+\.\d+\.\d+$)',  # Non-IP hostnames
            r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'  # IP addresses
(could be C2)
        ]

        # Check for suspicious remote addresses
        if any(re.search(pattern, conn.remote_addr) for pattern
in suspicious_patterns):
            return True

        # Check for unusual ports
        if conn.remote_port > 49152:  # Dynamic/private ports
            return True

        return False

    def _ip_in_network(self, ip: str, network: str) -> bool:
        """Check if IP is in network range"""
        try:
            ipaddr = int(''.join([f"{int(i):08b}" for i in
ip.split('.')]), 2)
            net, bits = network.split('/')
            network_addr = int(''.join([f"{int(i):08b}" for i in
net.split('.')]), 2)
            mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
            return (ipaddr & mask) == (network_addr & mask)
        except:
            return False

    def get_connections(self) -> List[ConnectionInfo]:
        """Get all active network connections"""
        connections = []

        try:
            for conn in psutil.net_connections(kind='inet'):
                try:
                    if conn.status == 'NONE':
                        continue

                    # Get process info
                    proc = psutil.Process(conn.pid) if conn.pid
else None
                    proc_name = proc.name() if proc else
'unknown'

                    # Format addresses
                    local_addr =
f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ''
                    remote_addr =
f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ''

                    # Create connection info
                    conn_info = ConnectionInfo(
                        pid=conn.pid or -1,
                        name=proc_name,
                        local_addr=conn.laddr.ip if conn.laddr
else '',
                        local_port=conn.laddr.port if conn.laddr
else -1,
                        remote_addr=conn.raddr.ip if conn.raddr
else '',
                        remote_port=conn.raddr.port if conn.raddr
else -1,
                        status=conn.status,
                        protocol='tcp' if conn.type ==
socket.SOCK_STREAM else 'udp'
                    )

                    # Check if suspicious
                    conn_info.suspicious =
self._is_suspicious_connection(conn_info)
                    connections.append(conn_info)

                except (psutil.NoSuchProcess,
psutil.AccessDenied):
                    continue

        except Exception as e:
            self.logger.error(f"Error getting network
connections: {str(e)}")

        return connections

    def _monitor_loop(self):
        """Main monitoring loop"""
        known_connections = set()

        while self.running.is_set():
            try:
                current_connections = self.get_connections()
                current_conn_set = {
                    (c.pid, c.local_addr, c.local_port,
c.remote_addr, c.remote_port)
                    for c in current_connections
                }

                # Detect new connections
                new_connections = current_conn_set -
known_connections
                for conn_tuple in new_connections:
                    conn = next(c for c in current_connections if

                              (c.pid, c.local_addr, c.local_port,
c.remote_addr, c.remote_port) == conn_tuple)

                    if conn.suspicious:

self.suspicious_connections.add(conn_tuple)
                        self._handle_suspicious_connection(conn)

                # Update known connections
                known_connections = current_conn_set
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Network monitoring error:
{str(e)}")
                time.sleep(5)

    def _handle_suspicious_connection(self, conn:
ConnectionInfo):
        """Handle suspicious network
connection"""
        try:
            self.logger.critical(
                f"Suspicious connection detected: {conn.name}
(PID: {conn.pid}) "
                f"to {conn.remote_addr}:{conn.remote_port}
({conn.protocol})"
            )

            # Kill the process
            if conn.pid > 0:
                try:
                    proc = psutil.Process(conn.pid)
                    proc.terminate()
                    proc.wait(timeout=3)
                    self.logger.info(f"Terminated suspicious
process: {conn.name} (PID: {conn.pid})")
                except:
                    try:
                        proc.kill()
                        self.logger.info(f"Killed suspicious
process: {conn.name} (PID: {conn.pid})")
                    except:
                        self.logger.error(f"Failed to kill
suspicious process: {conn.name} (PID: {conn.pid})")

            # Block the connection (requires root, so just log
for now)
            self.logger.warning(f"Would block connection to
{conn.remote_addr}:{conn.remote_port}")

            # Send alert
            self._send_alert(f"Suspicious connection:
{conn.remote_addr}:{conn.remote_port}")

        except Exception as e:
            self.logger.error(f"Error handling suspicious
connection: {str(e)}")

    def _send_alert(self, message: str):
        """Send system alert"""
        try:
            subprocess.run([
                'termux-notification',
                '--title', 'CYFER NETWORK ALERT',
                '--content', message,
                '--alert-once',
                '--priority', 'max',
                '--vibrate', '1000,1000,1000'
            ])
        except:
            pass

    def start(self):
        """Start network monitoring"""
        if not self.running.is_set():
            self.running.set()
            self.monitor_thread =
Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Network monitor started")

    def stop(self):
        """Stop network monitoring"""
        if self.running.is_set():
            self.running.clear()
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            self.logger.info("Network monitor stopped")

    def get_suspicious_connections(self) -> List[ConnectionInfo]:
        """Get list of currently suspicious connections"""
        current_connections = self.get_connections()
        return [c for c in current_connections
                if (c.pid, c.local_addr, c.local_port,
c.remote_addr, c.remote_port)
                in self.suspicious_connections]
```
