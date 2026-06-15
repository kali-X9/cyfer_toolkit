import os
import psutil
import signal
import logging
import subprocess
from typing import List, Dict, Optional, Set
import time

class ProcessManager:
    """
    Advanced Process Management
    Provides fine-grained control over system processes
    """

    def __init__(self):
        self.logger = logging.getLogger("cyfer.process_manager")
        self.whitelist: Set[str] = self._load_whitelist()

    def _load_whitelist(self) -> Set[str]:
        """Load whitelisted processes"""
        return {
            'system_server', 'zygote', 'surfaceflinger',
'servicemanager',
            'vold', 'netd', 'debuggerd', 'lmkd', 'logd', 'adbd',
            'healthd', 'installd', 'keystore', 'mediaserver',
            'termux', 'sshd', 'bash', 'sh', 'cyfer'
        }

    def get_process_info(self, pid: int) -> Optional[Dict]:
        """Get detailed information about a process"""
        try:
            proc = psutil.Process(pid)
            with proc.oneshot():
                return {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'status': proc.status(),
                    'create_time': proc.create_time(),
                    'cpu_percent':
proc.cpu_percent(interval=0.1),

'memory_percent': proc.memory_percent(),
                    'cmdline': proc.cmdline(),
                    'connections': [conn._asdict() for conn in
proc.connections()],
                    'threads': proc.num_threads(),
                    'open_files': [f.path for f in
proc.open_files()],
                    'environ': proc.environ()
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied,
psutil.ZombieProcess):
            return None

    def find_processes(self, name: str = None, cmdline: str =
None) -> List[Dict]:
        """Find processes matching criteria"""
        results = []
        for proc in psutil.process_iter(['pid', 'name',
'cmdline']):
            try:
                match = True
                if name and name.lower() not in
proc.info['name'].lower():
                    match = False
                if cmdline and cmdline not in '
'.join(proc.info['cmdline'] or []):
                    match = False
                if match:

results.append(self.get_process_info(proc.info['pid']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return results

    def terminate_process(self, pid: int, force: bool = False) ->
bool:
        """Terminate a process"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def start_process(self, command: List[str], **kwargs) ->
Optional[subprocess.Popen]:
        """Start a new process"""
        try:
            return subprocess.Popen(command, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to start process:
{str(e)}")
            return None

    def monitor_process(self, pid: int, callback=None) ->
threading.Thread:
        """Monitor a process and execute callback on
termination"""
        def monitor():
            proc = psutil.Process(pid)
            proc.wait()
            if callback:
                callback(pid)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread

    def kill_non_whitelisted(self):
        """Kill all non-whitelisted processes"""
        killed = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] not in self.whitelist:
                    self.terminate_process(proc.info['pid'],
force=True)
                    killed.append(proc.info['name'])
            except:
                continue
        return killed
```
