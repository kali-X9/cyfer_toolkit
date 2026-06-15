import os
import time
import subprocess
import logging
import json
import random
from typing import Dict, Any
from pathlib import Path

class TorManager:
    def __init__(self, port_manager, config):
        self.port_manager = port_manager
        self.config = config
        self.logger = logging.getLogger("cyfer.tor")
        self.process = None
        self.tor_data_dir = os.path.expanduser("~/.tor")
        self.torrc_path = os.path.expanduser("~/.torrc")
        self.control_password = self._generate_control_password()
        self.ports = {
            'socks': self.port_manager.get_port(),
            'control': self.port_manager.get_port()
        }

    def _generate_control_password(self) -> str:
        """Generate a secure control password for Tor"""
        try:
            result = subprocess.run(
                ['tor', '--hash-password',
'cyfer_ultimate_ghost'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return
"16:872860B76453A77D60CA2BB8C1A7042072093276A3D701AD684053EC4C"

    def _generate_torrc(self):
        """Generate torrc configuration file"""
        torrc_template = self.config.get('torrc_template', {})
        bridges = self.config.get('bridges', {}).get('obfs4', [])

        config = {
            "SOCKSPort": f"127.0.0.1:{self.ports['socks']}",
            "ControlPort": f"127.0.0.1:{self.ports['control']}",
            "HashedControlPassword": self.control_password,
            "CookieAuthentication": ,"1",
            "DataDirectory": self.tor_data_dir,
            "Log": "notice file /dev/null",
            "RunAsDaemon": "1",
            "ClientTransportPlugin": "obfs4 exec
/data/data/com.termux/files/usr/bin/obfs4proxy",
            "UseBridges": "1",
            "Bridge": bridges[:3] if bridges else [],
            "DisableDebuggerAttachment": "1",
            "SafeLogging": "1",
            "StrictNodes": "1",
            "ExcludeNodes": "{},{},{},{},{}".format(
                self.config.get('blocked_countries', ['us', 'gb',
'ca']))
        }

        # Write torrc
        with open(self.torrc_path, 'w') as f:
            for key, value in config.items():
                if isinstance(value, list):
                    for item in value:
                        f.write(f"{key} {item}\n")
                else:
                    f.write(f"{key} {value}\n")

    def start(self):
        """Start Tor service"""
        try:
            # Ensure data directory exists
            os.makedirs(self.tor_data_dir, exist_ok=True)

            # Generate configuration
            self._generate_torrc()

            # Start Tor
            self.logger.info(f"Starting Tor on port
{self.ports['socks']}")
            self.process = subprocess.Popen(
                ['tor', '-f', self.torrc_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for Tor to bootstrap
            time.sleep(5)

            # Verify Tor is running
            if self.test_connection():
                self.logger.info("Tor started successfully")
                return True
            else:
                self.logger.error("Tor failed to start")
                return False

        except Exception as e:
            self.logger.error(f"Tor start failed: {str(e)}")
            return False

    def stop(self):
        """Stop Tor service"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=10)
                self.logger.info("Tor stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping Tor: {str(e)}")
            return False

    def rotate_ports(self):
        """Rotate Tor ports"""
        self.ports = {
            'socks': self.port_manager.get_port(),
            'control': self.port_manager.get_port()
        }
        self.stop()
        return self.start()

    def test_connection(self) -> bool:
        """Test Tor connection"""
        try:
            result = subprocess.run(
                ['curl', '--socks5',
f"127.0.0.1:{self.ports['socks']}",
                 '-s', 'https://check.torproject.org/api/ip'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('IsTor', False)
        except Exception:
            pass
        return False

    def get_current_ip(self) -> str:
        """Get current exit IP"""
        try:
            result = subprocess.run(
                ['curl', '--socks5',
f"127.0.0.1:{self.ports['socks']}",
                 '-s', 'https://api.ipify.org'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "Unknown"
```
