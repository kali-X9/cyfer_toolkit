import os
import subprocess
import logging
from typing import Dict, Any

class ProxychainsManager:
    def __init__(self, port_manager, config):
        self.port_manager = port_manager
        self.config = config
        self.logger = logging.getLogger("cyfer.proxychains")
        self.config_path =
os.path.expanduser("~/.proxychains/proxychains.conf")
        self.port = self.port_manager.get_port()

    def _generate_config(self):
        """Generate proxychains configuration"""
        config = f"""
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 {self.config.get('tor_socks_port', 9050)}
socks5 127.0.0.1 {self.config.get('v2ray_port', 10808)}
        """

        os.makedirs(os.path.dirname(self.config_path),
exist_ok=True)
        with open(self.config_path, 'w') as f:
            f.write(config)

    def start(self):
        """Configure proxychains"""
        try:
            self._generate_config()
            self.logger.info("Proxychains configured")
            return True
        except Exception as e:
            self.logger.error(f"Proxychains config failed:
{str(e)}")
            return False

    def stop(self):
        """Cleanup proxychains config"""
        try:
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            self.logger.info("Proxychains config cleaned")
            return True
        except Exception as e:
            self.logger.error(f"Proxychains cleanup failed:
{str(e)}")
            return False

    def rotate_ports(self):
        """Rotate proxychains ports"""
        self.port = self.port_manager.get_port()
        return self.start()

    def test_ip_leak(self) -> Dict[str, Any]:
        """Test for IP leaks through proxychains"""
        try:
            result = subprocess.run(
                ['proxychains', '-q', '-f', self.config_path,
                 'curl', '-s', 'https://api.ipify.org'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'ip': result.stdout.strip(),
                    'leak': False  # Would compare against known
Tor IPs
                }
        except Exception as e:
            self.logger.error(f"IP leak test failed: {str(e)}")

        return {
            'success': False,
            'error': 'IP leak test failed'
        }
```
