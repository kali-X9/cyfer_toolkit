import os
import hashlib
import logging
import shutil
from typing import Optional, List, Tuple, Generator
from cryptography.fernet import Fernet

class FileManager:
    """
    Secure File Management
    Encrypted file operations and secure deletion
    """

    def __init__(self, encryption_key: bytes = None):
        self.encryption_key = encryption_key or
Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.logger = logging.getLogger("cyfer.file_manager")

    def encrypt_file(self, input_path: str, output_path: str =
None) -> bool:
        """Encrypt a file"""
        try:
            if not output_path:
                output_path = input_path + '.enc'

            with open(input_path, 'rb') as f:
                data = f.read()

            encrypted_data = self.cipher_suite.encrypt(data)

            with open(output_path, 'wb') as f:
                f.write(encrypted_data)

            return True
        except Exception as e:
            self.logger.error(f"File encryption failed:
{str(e)}")
            return False

    def decrypt_file(self, input_path: str, output_path: str) ->
bool:
        """Decrypt a file"""
        try:
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data =
self.cipher_suite.decrypt(encrypted_data)

            with open(output_path, 'wb') as f:
                f.write(decrypted_data)

            return True
        except Exception as e:
            self.logger.error(f"File decryption failed:
{str(e)}")
            return False

    def secure_delete(self, path: str, passes: int = 7) -> bool:
        """Securely delete a file"""
        try:
            if not os.path.exists(path):
                return False

            # Overwrite with random data multiple times
            file_size = os.path.getsize(path)
            with open(path, 'r+b') as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())

            # Delete the file
            os.remove(path)
            return True
        except Exception as e:
            self.logger.error(f"Secure delete failed: {str(e)}")
            return False

    def recursive_secure_delete(self, directory: str):
        """Recursively and securely delete a directory"""
        try:
            for root, dirs, files in os.walk(directory,
topdown=False):
                for name in files:
                    self.secure_delete(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(directory)
            return True
        except Exception as e:
            self.logger.error(f"Recursive secure delete failed:
{str(e)}")
            return False

    def calculate_checksum(self, file_path: str, algorithm: str =
'sha256') -> Optional[str]:
        """Calculate file checksum"""
        try:
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self.logger.error(f"Checksum calculation failed:
{str(e)}")
            return None
```
