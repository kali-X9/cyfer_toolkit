import os
import yara
import time
import logging
from threading import Thread, Event
from queue import Queue
from typing import Dict, List, Optional

class YARAScanner:
    """Advanced YARA scanner with real-time monitoring and threat
intelligence"""
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.yara")
        self.rules = self._load_rules()
        self.scanner = self._compile_rules()
        self.scan_queue = Queue()
        self.running = Event()
        self.worker_thread: Optional[Thread] = None

    def _load_rules(self) -> Dict[str, str]:
        """Load YARA rules from directory"""
        rules = {}
        rules_dir = self.config.get('yara_rules_dir',
'config/yara_rules')

        try:
            for root, _, files in os.walk(rules_dir):
                for file in files:
                    if file.endswith(('.yar', '.yara')):
                        rule_path = os.path.join(root, file)
                        rules[os.path.splitext(file)[0]] =
rule_path
            self.logger.info(f"Loaded {len(rules)} YARA rules")
            return rules
        except Exception as e:
            self.logger.error(f"Failed to load YARA rules:
{str(e)}")
            return {}

    def _compile_rules(self) -> Optional[yara.Rules]:
        """Compile YARA rules"""
        try:
            if not self.rules:
                raise ValueError("No YARA rules loaded")

            compiled_rules = yara.compile(filepaths=self.rules)
            self.logger.info("YARA rules compiled successfully")
            return compiled_rules
        except Exception as e:
            self.logger.error(f"Failed to compile YARA rules:
{str(e)}")
            return None

    def scan_file(self, file_path: str) -> List[Dict]:
        """Scan a single file with YARA rules"""
        if not self.scanner or not os.path.exists(file_path):
            return []

        try:
            matches = self.scanner.match(file_path)
            results = []

            for match in matches:
                result = {
                    'rule': match.rule,
                    'tags': match.tags,
                    'meta': match.meta,
                    'strings': [str(s) for s in match.strings],
                    'file': file_path,
                    'timestamp': time.time()
                }
                results.append(result)

                # Log critical matches
                if 'critical' in match.tags:
                    self.logger.critical(f"YARA CRITICAL:
{match.rule} detected in {file_path}")
                else:
                    self.logger.warning(f"YARA: {match.rule}
detected in {file_path}")

            return results

        except Exception as e:
            self.logger.error(f"YARA scan failed for {file_path}:
{str(e)}")
            return []

    def scan_directory(self, directory: str, recursive: bool =
True) -> List[Dict]:
        """Scan a directory with YARA rules"""
        results = []

        try:
            if recursive:
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        results.extend(self.scan_file(file_path))
            else:
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path):
                        results.extend(self.scan_file(item_path))

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
        """Start the YARA scanner service"""
        if not self.running.is_set():
            self.running.set()
            self.worker_thread = Thread(target=self._worker_loop,
daemon=True)
            self.worker_thread.start()
            self.logger.info("YARA scanner started")

    def stop(self):
        """Stop the YARA scanner service"""
        if self.running.is_set():
            self.running.clear()
            if self.worker_thread:
                self.worker_thread.join(timeout=5)
            self.logger.info("YARA scanner stopped")

    def schedule_scan(self, target: str, recursive: bool =
False):
        """Schedule a file or directory for scanning"""
        if os.path.isfile(target):
            self.scan_queue.put(target)
        elif os.path.isdir(target):
            self.scan_queue.put((target, recursive))

    def update_rules(self):
        """Update YARA rules from configured sources"""
        # Implementation for rule updates would go here
        pass
```
