import os
import json
import subprocess
import logging
from typing import Dict, Any

class V2RayManager:
    def __init__(self, port_manager, config):
        self.port_manager = port_manager
        self.config = config
        self.logger = logging.getLogger("cyfer.v2ray")
        self.process = None
        self.config_path =
os.path.expanduser("~/.v2ray/config.json")
        self.port = self.port_manager.get_port()

    def _generate_config(self):
        """Generate V2Ray configuration"""
        config = {
            "log": {
                "loglevel": "warning",
                "access": "/dev/null",
                "error": "/dev/null"
            },
            "inbounds": [{
                "port": self.port,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True,
                    "ip": "127.0.0.1"
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "none",
                    "wsSettings": {
                        "path": "/cyfer-ghost",
                        "headers": {
                            "Host": "www.google.com",
                            "User-Agent": "Mozilla/5.0 (Windows
NT 10.0; Win64; x64) AppleWebKit/537.36"
                        }
                    }
                }
            }],
            "outbounds": [{
                "protocol": "freedom",
                "settings": {},
                "tag": "direct"
            }]
        }

        os.makedirs(os.path.dirname(self.config_path),
exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def start(self):
        """Start V2Ray service"""
        try:
            self._generate_config()

            self.logger.info(f"Starting V2Ray on port
{self.port}")
            self.process = subprocess.Popen(
                ['v2ray', '-config', self.config_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Simple test to verify it's running
            time.sleep(2)
            if self.process.poll() is None:
                self.logger.info("V2Ray started successfully")
                return True
            return False

        except Exception as e:
            self.logger.error(f"V2Ray start failed: {str(e)}")
            return False

    def stop(self):
        """Stop V2Ray service"""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.logger.info("V2Ray stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping V2Ray: {str(e)}")
            return False

    def rotate_ports(self):
        """Rotate V2Ray port"""
        self.port = self.port_manager.get_port()
        self.stop()
        return self.start()
```
