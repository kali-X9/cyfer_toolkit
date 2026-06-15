import os
import socket
import logging
import random
from typing import Tuple, Set, Optional

class PortManager:
    """
    Advanced Port Management System
    Manages port allocation and conflict resolution
    """

    def __init__(self, min_port: int = 30000, max_port: int =
50000):
        self.min_port = min_port
        self.max_port = max_port
        self.used_ports: Set[int] = set()
        self.logger = logging.getLogger("cyfer.port_manager")
        self.lock = threading.Lock()

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available for use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as
s:
            try:
                s.bind(('127.0.0.1', port))
                return True
            except:
                return False

    def get_available_port(self, preferred_port: int = None) ->
Optional[int]:
        """Get an available port, optionally preferring a
specific one"""
        with self.lock:
            # Try preferred port first
            if preferred_port and preferred_port not in
self.used_ports and self._is_port_available(preferred_port):
                self.used_ports.add(preferred_port)
                return preferred_port

            # Find random available port
            for _ in range(100):  # Try 100 times max
                port = random.randint(self.min_port,
self.max_port)
                if port not in self.used_ports and
self._is_port_available(port):
                    self.used_ports.add(port)
                    return port

            self.logger.error("No available ports in range")
            return None

    def release_port(self, port: int) -> bool:
        """Release a port back to the pool"""
        with self.lock:
            if port in self.used_ports:
                self.used_ports.remove(port)
                return True
            return False

    def get_port_range(self, count: int) -> Optional[Tuple[int,
int]]:
        """Get a contiguous range of available ports"""
        with self.lock:
            for start_port in range(self.min_port, self.max_port
- count):
                if all(self._is_port_available(p) and p not in
self.used_ports
                      for p in range(start_port, start_port +
count)):
                    # Reserve all ports in the range
                    for p in range(start_port, start_port +
count):
                        self.used_ports.add(p)
                    return (start_port, start_port + count - 1)
            return None

    def get_service_port(self, service_name: str) ->
Optional[int]:
        """Get a persistent port for a named service"""
        # This is a simplified version - in production, you'd
want to persist this mapping
        port = self.get_available_port()
        if port:
            self.logger.info(f"Assigned port {port} to service
{service_name}")
            return port
        return None
```
