import os
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher,
algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional
import logging

class DecryptionEngine:
    """
    Military-grade decryption engine with authentication and
integrity verification
    """
    def __init__(self, master_key: Optional[bytes] = None):
        self.logger = logging.getLogger("cyfer.crypto")
        self.master_key = master_key
        self.KEY_SIZE = 32
        self.SALT_SIZE = 16
        self.NONCE_SIZE = 12
        self.TAG_SIZE = 16
        self.HMAC_SIZE = 64  # SHA-512
        self.PBKDF2_ITERATIONS = 600000

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive decryption key using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
        )
        return kdf.derive(password.encode('utf-8'))

    def decrypt_data(self, ciphertext: bytes, nonce: bytes, tag:
bytes,
                   salt: bytes = None, password: str = None) ->
bytes:
        """
        Decrypt data with AES-256-GCM
        """
        try:
            # Derive key
            if password and salt:
                key = self._derive_key(password, salt)
            elif self.master_key:
                key = self.master_key
            else:
                raise ValueError("Either password+salt or master
key required")

            # Decrypt
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
            )
            decryptor = cipher.decryptor()

            # Decrypt and remove padding
            padded_plaintext = decryptor.update(ciphertext) +
decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) +
unpadder.finalize()

            return plaintext

        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise

    def decrypt_file(self, input_path: str, output_path: str,
password: str = None,
                    chunk_size: int = 64 * 1024) -> bool:
        """
        Decrypt a file in chunks with integrity verification
        """
        try:
            with open(input_path, 'rb') as f:
                # Read salt if password is provided
                salt = f.read(self.SALT_SIZE) if password else
b''

                # Read nonce
                nonce = f.read(self.NONCE_SIZE)

                # Derive key
                key = self._derive_key(password, salt) if
password else self.master_key

                # Initialize HMAC
                hmac_key = hashlib.sha256(key + b"HMAC").digest()
                hmac_engine = hmac.new(hmac_key,
digestmod='sha512')

                # Get file size and calculate encrypted data size
                f.seek(0, 2)
                file_size = f.tell()
                encrypted_size = file_size - len(salt) -
self.NONCE_SIZE - self.TAG_SIZE - self.HMAC_SIZE
                f.seek(len(salt) + self.NONCE_SIZE)

                # Read and verify HMAC
                f.seek(-self.HMAC_SIZE, 2)
                stored_hmac = f.read(self.HMAC_SIZE)
                f.seek(len(salt) + self.NONCE_SIZE)

                # Calculate HMAC of encrypted data
                while f.tell() < file_size - self.TAG_SIZE -
self.HMAC_SIZE:
                    chunk = f.read(min(chunk_size, file_size -
f.tell() - self.TAG_SIZE - self.HMAC_SIZE))
                    hmac_engine.update(chunk)

                # Read tag and final chunk
                tag = f.read(self.TAG_SIZE)
                calculated_hmac = hmac_engine.digest()

                # Verify HMAC
                if not hmac.compare_digest(calculated_hmac,
stored_hmac):
                    self.logger.error("HMAC verification failed -
file tampered")
                    raise ValueError("File integrity check
failed")

                # Reset file pointer and decrypt
                f.seek(len(salt) + self.NONCE_SIZE)
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.GCM(nonce, tag),
                )
                decryptor = cipher.decryptor()

                with open(output_path, 'wb') as f_out:
                    # Process in chunks
                    remaining = encrypted_size
                    while remaining > 0:
                        chunk = f.read(min(chunk_size,
remaining))
                        if not chunk:
                            break
                        decrypted_chunk = decryptor.update(chunk)
                        f_out.write(decrypted_chunk)
                        remaining -= len(chunk)

                    # Finalize
                    f_out.write(decryptor.finalize())

            self.logger.info(f"File decrypted: {input_path} ->
{output_path}")
            return True

        except Exception as e:
            self.logger.error(f"File decryption failed:
{str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)
            raise
