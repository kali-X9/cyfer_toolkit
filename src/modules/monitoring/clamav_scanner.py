import os
import pyclamd
import time
import logging
from threading import Thread, Event
from queue import Queue
from typing import List, Dict, Optional

class ClamAVScanner:
    """Advanced ClamAV scanner with real-time monitoring"""
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.clamav")
        self.cd = self._init_clamd()
        self.scan_queue = Queue()
        self.running = Event()
        self.worker_thread: Optional[Thread] = None

    def _init_clamd(self):
        """Initialize ClamAV daemon connection"""
        try:
            cd = pyclamd.ClamdAgnostic()
            cd.ping()
            self.logger.info("ClamAV daemon connected")
            return cd
        except Exception as e:
            self.logger.error(f"Failed to connect to ClamAV:
{str(e)}")
            return None

    def scan_file(self, file_path: str) -> Optional[Dict]:
        """Scan a single file with ClamAV"""
        if not self.cd or not os.path.exists(file_path):
            return None

        try:
            scan_result = self.cd.scan(file_path)
            if scan_result:
                for path, (virus_name, virus_id) in
scan_result.items():
                    result = {
                        'file': path,
                        'virus': virus_name,
                        'virus_id': virus_id,
                        'timestamp': time.time(),
                        'status': 'infected'
                    }
                    self.logger.critical(f"ClamAV: {virus_name}
detected in {path}")
                    return result
            return {'file': file_path, 'status': 'clean',
'timestamp': time.time()}

        except Exception as e:
            self.logger.error(f"ClamAV scan failed for
{file_path}: {str(e)}")
            return None

    def scan_directory(self, directory: str, recursive: bool =
True) -> List[Dict]:
        """Scan a directory with ClamAV"""
        results = []

        try:
            if recursive:
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        result = self.scan_file(file_path)
                        if result:
                            results.append(result)
            else:
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        result = self.scan_file(item_path)
                        if result:
                            results.append(result)

        except Exception as e:
            self.logger.error(f"Directory scan failed: {str(e)}")

        return results

    def _worker_loop(self):
        """Worker thread for processing scan queue"""
        while self.running.is_set() or not
self.scan_queue.empty():
            try:
                item = self.scan_queue.get(timeout=1)
                if isinstance(item, str):
                    self.scan_file(item)
                elif isinstance(item, tuple) and len(item) == 2:
                    path, recursive = item
                    self.scan_directory(path, recursive)
                self.scan_queue.task_done()
            except Exception as e:
                self.logger.error(f"Scan worker error: {str(e)}")
                time.sleep(1)

    def start(self):
        """Start the ClamAV scanner service"""
        if not self.running.is_set() and self.cd:
            self.running.set()
            self.worker_thread = Thread(target=self._worker_loop,
daemon=True)
            self.worker_thread.start()
            self.logger.info("ClamAV scanner started")

    def stop(self):
        """Stop the ClamAV scanner service"""
        if self.running.is_set():
            self.running.clear()
            if self.worker_thread:
                self.worker_thread.join(timeout=5)
            self.logger.info("ClamAV scanner stopped")

    def schedule_scan(self, target: str, recursive: bool =
False):
        """Schedule a file or directory for scanning"""
        if os.path.isfile(target):
            self.scan_queue.put(target)
        elif os.path.isdir(target):
            self.scan_queue.put((target, recursive))

    def update_signatures(self):
        """Update ClamAV virus signatures"""
        try:
            if self.cd:
                result = self.cd.reload()
                self.logger.info(f"ClamAV signatures updated:
{result}")
                return result
        except Exception as e:
            self.logger.error(f"Failed to update ClamAV
signatures: {str(e)}")
            return False
```
