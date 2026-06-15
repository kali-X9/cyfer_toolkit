                while True:
                    chunk = f_in.read(chunk_size)
                    if not chunk:
                        break

                    # Encrypt chunk
                    encrypted_chunk = encryptor.update(chunk)
                    f_out.write(encrypted_chunk)

                    # Update HMAC
                    hmac_engine.update(encrypted_chunk)

                # Finalize encryption
                final_chunk = encryptor.finalize()
                f_out.write(final_chunk)
                hmac_engine.update(final_chunk)

                # Write tag and HMAC
                tag = encryptor.tag
                f_out.write(tag)
                f_out.write(hmac_engine.digest())

            self.logger.info(f"File encrypted: {input_path} ->
{output_path}")
            return True

        except Exception as e:
            self.logger.error(f"File encryption failed:
{str(e)}")
            # Cleanup partial output on failure
            if os.path.exists(output_path):
                os.remove(output_path)
            raise

    def generate_secure_container(self, container_path: str,
size_mb: int, password: str):
        """
        Create a secure encrypted container (virtual encrypted
disk)
        """
        try:
            # Generate random container content
            container_size = size_mb * 1024 * 1024
            salt = os.urandom(self.SALT_SIZE)
            key = self._derive_key(password, salt)

            # Create container file
            with open(container_path, 'wb') as f:
                # Write header with salt and random data
                f.write(salt)
                f.write(os.urandom(container_size - len(salt)))

            # Encrypt the container in place
            temp_path = f"{container_path}.tmp"
            if self.encrypt_file(container_path, temp_path,
password):
                os.replace(temp_path, container_path)
                self.logger.info(f"Secure container created:
{container_path}")
                return True
            return False

        except Exception as e:
            self.logger.error(f"Container creation failed:
{str(e)}")
            if os.path.exists(container_path):
                os.remove(container_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
```
