import os
import json
import logging
import threading
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64

class ConfigManager:
    """
    Secure Configuration Management
    Encrypted configuration with version control and validation
    """

    def __init__(self, config_path: str = None, encryption_key:
bytes = None):
        self.config_path = config_path or
os.path.expanduser('~/.cyfer_config.json')
        self.encryption_key = encryption_key or
self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.config: Dict[str, Any] = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger("cyfer.config_manager")
        self._load_config()

    def _generate_encryption_key(self) -> bytes:
        """Generate a new encryption key"""
        return Fernet.generate_key()
                                                                           def _encrypt_value(self, value: Any) -> str:                               """Encrypt a configuration value"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value).encode()
        elif not isinstance(value, bytes):
            value = str(value).encode()
        return self.cipher_suite.encrypt(value).decode()

    def _decrypt_value(self, encrypted_value: str) -> Any:
        """Decrypt a configuration value"""
        try:
            decrypted =
self.cipher_suite.decrypt(encrypted_value.encode())
            try:
                return json.loads(decrypted)
            except:
                return decrypted.decode()
        except:
            return None

    def _load_config(self):
        """Load configuration from file"""
        with self.lock:
            try:
                if os.path.exists(self.config_path):
                    with open(self.config_path, 'r') as f:
                        encrypted_config = json.load(f)
                        self.config = {
                            k: self._decrypt_value(v)
                            for k, v in encrypted_config.items()
                        }
                else:
                    self.config = {}
            except Exception as e:
                self.logger.error(f"Failed to load config:
{str(e)}")
                self.config = {}

    def save_config(self):
        """Save configuration to file"""
        with self.lock:
            try:
                encrypted_config = {
                    k: self._encrypt_value(v)
                    for k, v in self.config.items()
                }
                with open(self.config_path, 'w') as f:
                    json.dump(encrypted_config, f, indent=2)
                return True
            except Exception as e:
                self.logger.error(f"Failed to save config:
{str(e)}")
                return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        with self.lock:
            return self.config.get(key, default)

    def set(self, key: str, value: Any, save: bool = True):
        """Set a configuration value"""
        with self.lock:
            self.config[key] = value
            if save:
                return self.save_config()
            return True

    def delete(self, key: str, save: bool = True) -> bool:
        """Delete a configuration value"""
        with self.lock:
            if key in self.config:
                del self.config[key]
                if save:
                    return self.save_config()
                return True
            return False

    def get_encryption_key(self) -> str:
        """Get the base64-encoded encryption key"""
        return base64.b64encode(self.encryption_key).decode()
