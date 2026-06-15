import os
import time
import logging
import threading
from pyinotify import WatchManager, Notifier, ProcessEvent,
IN_DELETE, IN_CREATE, IN_MODIFY, IN_MOVED_TO, IN_MOVED_FROM

class FileSystemEventHandler(ProcessEvent):
    """Handle filesystem events with advanced filtering"""
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.suspicious_patterns =
self._load_suspicious_patterns()
        self.last_alert = {}
        self.alert_threshold = 5  # Max alerts per minute per
path

    def _load_suspicious_patterns(self):
        """Load patterns for suspicious file activities"""
        return [
            r'\.encrypted$', r'\.locked$', r'\.crypt$',  #
Ransomware patterns
            r'\.exe$', r'\.dll$', r'\.so$', r'\.sh$',    #
Executables
            r'\/\.ssh\/', r'\/.aws\/', r'\/.config\/',    #
Sensitive directories
            r'passw', r'secret', r'key', r'credential'    #
Sensitive keywords
        ]

    def _is_suspicious(self, path: str) -> bool:
        """Check if path matches suspicious patterns"""
        return any(re.search(pattern, path, re.IGNORECASE)
                  for pattern in self.suspicious_patterns)

    def _should_alert(self, path: str) -> bool:
        """Rate limiting for alerts"""
        now = time.time()
        if path in self.last_alert:
            if now - self.last_alert[path] < 60:  # 1 minute
cooldown
                return False
        self.last_alert[path] = now
        return True

    def process_IN_CREATE(self, event):
        self._handle_event(event, "CREATED")

    def process_IN_DELETE(self, event):
        self._handle_event(event, "DELETED")

    def process_IN_MODIFY(self, event):
        self._handle_event(event, "MODIFIED")

    def process_IN_MOVED_TO(self, event):
        self._handle_event(event, "MOVED_TO")

    def process_IN_MOVED_FROM(self, event):
        self._handle_event(event, "MOVED_FROM")

    def _handle_event(self, event, action):
        """Process filesystem event"""
        try:
            path = os.path.join(event.path, event.name)

            if not self._is_suspicious(path):
                return

            if not self._should_alert(path):
                return

            # Log the event
            self.logger.warning(f"File {action}: {path}")

            # Take action if suspicious
            if self._is_suspicious(path):
                self._handle_suspicious_file(path, action)

        except Exception as e:
            self.logger.error(f"Error handling filesystem event:
{str(e)}")

    def _handle_suspicious_file(self, path: str, action: str):
        """Handle suspicious file activity"""
        try:
            # Quarantine the file
            if os.path.exists(path) and action in ["CREATED",
"MODIFIED", "MOVED_TO"]:
                quarantine_dir =
self.config.get('quarantine_dir', '/data/data/com.termux/files/homself.config.get('quarantine_dir','/data/data/com.termux/files/home/.cyfer_quarantine')
                os.makedirs(quarantine_dir, exist_ok=True)

                # Move file to quarantine
                import shutil
                dest = os.path.join(quarantine_dir,
os.path.basename(path))
                shutil.move(path, dest)

                self.logger.critical(f"Quarantined suspicious
file: {path} -> {dest}")

                # Alert via notification
                self._send_alert(f"Suspicious file activity:
{os.path.basename(path)}")

        except Exception as e:
            self.logger.error(f"Error handling suspicious file:
{str(e)}")

    def _send_alert(self, message: str):
        """Send system alert"""
        try:
            subprocess.run([
                'termux-notification',
                '--title', 'CYFER ALERT',
                '--content', message,
                '--alert-once',
                '--priority', 'max',
                '--vibrate', '500,500,500'
            ])
        except:
            pass

class INotifyMonitor:
    """Real-time filesystem monitoring using inotify"""
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.inotify")
        self.watch_manager = WatchManager()
        self.notifier = None
        self.running = False
        self.mask = IN_DELETE | IN_CREATE | IN_MODIFY |
IN_MOVED_TO | IN_MOVED_FROM

    def start(self):
        """Start filesystem monitoring"""
        if self.running:
            return

        try:
            # Watch important directories
            watch_dirs = self.config.get('watch_dirs', [
                '/data/data/com.termux/files/home',
                '/data/data/com.termux/files/usr',
                '/sdcard'
            ])

            for directory in watch_dirs:
                if os.path.exists(directory):
                    self.watch_manager.add_watch(
                        directory,
                        self.mask,
                        rec=True,
                        auto_add=True
                    )
                    self.logger.info(f"Monitoring directory:
{directory}")

            # Start notifier in a separate thread
            self.notifier = Notifier(
                self.watch_manager,
                FileSystemEventHandler(self.config, self.logger)
            )

            self.running = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True
            )
            self.monitor_thread.start()
            self.logger.info("INotify monitor started")

        except Exception as e:
            self.logger.error(f"Failed to start INotify monitor:
{str(e)}")
            raise

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running and self.notifier:
            try:
                self.notifier.process_events()
                if self.notifier.check_events(timeout=1000):
                    self.notifier.read_events()
            except Exception as e:
                self.logger.error(f"INotify error: {str(e)}")
                time.sleep(1)

    def stop(self):
        """Stop filesystem monitoring"""
        self.running = False
        if self.notifier:
            self.notifier.stop()
        self.logger.info("INotify monitor stopped")
```
