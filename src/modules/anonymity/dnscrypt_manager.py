import os
import subprocess
import time
import logging
from typing import Dict, Any

class DNSCryptManager:
    def __init__(self, port_manager, config):
        self.port_manager = port_manager
        self.config = config
        self.logger = logging.getLogger("cyfer.dnscrypt")
        self.process = None
        self.port = self.port_manager.get_port()
        self.config_path =
os.path.expanduser("~/.dnscrypt-proxy.toml")

    def _generate_config(self):
        """Generate dnscrypt-proxy configuration"""
        config = f"""
listen_addresses = ['127.0.0.1:{self.port}']
server_names = ['cloudflare', 'quad9-dnscrypt-ip4-filter-pri']
require_dnssec = true
require_nolog = true
require_nofilter = true
proxy = 'socks5://127.0.0.1:{self.config.get('tor_socks_port',
9050)}'
timeout = 5000
keepalive = 30
lb_strategy = 'p2'
offline_mode = false
tls_disable_session_tickets = true
cache = true
cache_size = 256
cache_min_ttl = 600
cache_max_ttl = 86400
        """

        with open(self.config_path, 'w') as f:
            f.write(config)

    def start(self):
        """Start DNSCrypt service"""
        try:
            self._generate_config()

            self.logger.info(f"Starting DNSCrypt on port
{self.port}")
            self.process = subprocess.Popen(
                ['dnscrypt-proxy', '-config', self.config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for startup
            time.sleep(2)

            if self.test_dns_leak()['success']:
                self.logger.info("DNSCrypt started successfully")
                return True
            return False

        except Exception as e:
            self.logger.error(f"DNSCrypt start failed: {str(e)}")
            return False

    def stop(self):
        """Stop DNSCrypt service"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.logger.info("DNSCrypt stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping DNSCrypt:
{str(e)}")
            return False

    def rotate_ports(self):
        """Rotate DNSCrypt port"""
        self.port = self.port_manager.get_port()
        self.stop()
        return self.start()

    def test_dns_leak(self) -> Dict[str, Any]:
        """Test for DNS leaks"""
        try:
            # Test with DNS leak test service
            result = subprocess.run(
                ['dig', '+short', 'o-o.myaddr.l.google.com',
'TXT',
                 f'@{self.port}'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return {
                    'success': True,
                    'dns_server': result.stdout.strip()
                }
        except Exception as e:
            self.logger.error(f"DNS leak test failed: {str(e)}")

        return {
            'success': False,
            'error': 'DNS leak test failed'
          }
