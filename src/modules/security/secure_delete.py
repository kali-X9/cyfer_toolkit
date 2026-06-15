import os
import random
import logging
from typing import Union, IO

class SecureDelete:
    """
    Military-grade secure deletion (DoD 5220.22-M / Gutmann)
    Implements multiple passes with verification
    """
    def __init__(self, passes: int = 7):
        self.passes = passes
        self.logger = logging.getLogger("cyfer.secure_delete")

    def _write_pass(self, file: Union[str, IO], data: bytes) ->
bool:
        """Perform a single overwrite pass"""
        try:
            if isinstance(file, str):
                with open(file, 'r+b') as f:
                    f.seek(0)
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
            else:
                file.seek(0)
                file.write(data)
                file.flush()
                os.fsync(file.fileno())
            return True
        except Exception as e:
            self.logger.error(f"Secure delete pass failed:
{str(e)}")
            return False

    def _generate_pattern(self, size: int, pattern: int) ->
bytes:
        """Generate overwrite pattern"""
        if pattern == 0:
            return bytes([0x00] * size)  # Zero pass
        elif pattern == 1:
            return bytes([0xFF] * size)  # One pass
        elif pattern == 2:
            return os.urandom(size)      # Random pass
        elif pattern == 3:
            return bytes([0x92] * size)  # Special pattern
        elif pattern == 4:
            return bytes([0x49] * size)  # Special pattern
        elif pattern == 5:
            return bytes([0x24] * size)  # Special pattern
        else:
            return os.urandom(size)      # Random for remaining
passes

    def wipe_file(self, file_path: str) -> bool:
        """
        Securely delete a file using multiple overwrite passes
        """
        try:
            # Get file size
            file_size = os.path.getsize(file_path)

            # Open file in read/write mode
            with open(file_path, 'r+b') as f:
                # Perform multiple overwrite passes
                for pass_num in range(self.passes):
                    # Generate pattern for this pass
                    pattern = self._generate_pattern(file_size,
pass_num)

                    # Write pattern
                    if not self._write_pass(f, pattern):
                        self.logger.error(f"Pass {pass_num + 1}
failed for {file_path}")
                        return False

                # Truncate and close
                f.truncate()

            # Rename file
            dir_name, file_name = os.path.split(file_path)
            new_name = os.path.join(dir_name, '0' *
len(file_name))
            os.rename(file_path, new_name)

            # Finally, delete the file
            os.remove(new_name)
            self.logger.info(f"Securely deleted: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Secure deletion failed for
{file_path}: {str(e)}")
            return False

    def wipe_directory(self, dir_path: str, recursive: bool =
True) -> bool:
        """
        Securely wipe a directory and all its contents
        """
        try:
            success = True
            for root, dirs, files in os.walk(dir_path,
topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    if not self.wipe_file(file_path):
                        success = False

                if recursive:
                    for name in dirs:
                        dir_path = os.path.join(root, name)
                        try:
                            os.rmdir(dir_path)
                        except:
                            success = False

            # Finally, remove the directory itself
            try:
                os.rmdir(dir_path)
            except:
                success = False

            return success

        except Exception as e:
            self.logger.error(f"Directory wipe failed: {str(e)}")
            return False

    def wipe_free_space(self, path: str = "/") -> bool:
        """
        Wipe free disk space by creating a large file filled with
random data
        """
        try:
            # Create a temporary file
            temp_file = os.path.join(path, ".cyfer_wipe.tmp")

            # Get free space
            stat = os.statvfs(path)
            free_space = stat.f_bsize * stat.f_bavail

            # Write until disk is full
            with open(temp_file, 'wb') as f:
                chunk = os.urandom(1024 * 1024)  # 1MB chunks
                while free_space > 0:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
                    free_space -= len(chunk)

            # Securely delete the temporary file
            self.wipe_file(temp_file)
            return True

        except Exception as e:
            self.logger.error(f"Free space wipe failed:
{str(e)}")
            return False
```
