import os
import logging
import subprocess
from typing import Dict, Any

class NotificationManager:
    """
    Cross-platform Notification System
    Provides alerts and status updates
    """

    def __init__(self):
        self.logger =
logging.getLogger("cyfer.notification_manager")

    def send_notification(self, title: str, message: str,
priority: str = 'normal',
                         vibration: str = None, led_color: str =
None) -> bool:
        """Send a system notification"""
        try:
            if self._is_termux():
                return self._send_termux_notification(title,
message, priority, vibration, led_color)
            elif self._is_linux():
                return self._send_linux_notification(title,
message, priority)
            else:
                self.logger.warning("Notification system not
supported on this platform")
                return False
        except Exception as e:
            self.logger.error(f"Notification failed: {str(e)}")
            return False

    def _is_termux(self) -> bool:
        """Check if running in Termux"""
        return 'com.termux' in os.environ.get('PREFIX', '')

    def _is_linux(self) -> bool:
        """Check if running on Linux"""
        return os.name == 'posix' and 'linux' in
os.uname().sysname.lower()

    def _send_termux_notification(self, title: str, message: str,
priority: str,
                                vibration: str, led_color: str)
-> bool:
        """Send notification using Termux API"""
        cmd = ['termux-notification', '-t', title, '-c', message]

        # Set priority
        priority_map = {
            'min': 'min',
            'low': 'low',
            'default': 'default',
            'high': 'high',
            'max': 'max'
        }
        cmd.extend(['--priority', priority_map.get(priority,
'default')])

        # Set vibration pattern
        if vibration:
            cmd.extend(['--vibrate', vibration])

        # Set LED color
        if led_color:
            cmd.extend(['--led-color', led_color])

        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _send_linux_notification(self, title: str, message: str,
priority: str) -> bool:
        """Send notification using notify-send (Linux)"""
        try:
            urgency = priority if priority in ['low', 'normal',
'critical'] else 'normal'
            subprocess.run(                                                            ['notify-send', '-u', urgency, title, message],
                check=True
            )
            return True
        except (subprocess.CalledProcessError,
FileNotFoundError):
            return False

    def send_alert(self, message: str, critical: bool = False):
        """Send a high-priority alert"""
        return self.send_notification(
            "CYFER ALERT" if critical else "CYFER NOTICE",
            message,
            priority='max' if critical else 'high',
            vibration='500,500,500,500,500' if critical else
'200,200',
            led_color='FF0000' if critical else '00FF00'
        )

    def clear_all_notifications(self) -> bool:
        """Clear all notifications"""
        if self._is_termux():
            try:
                subprocess.run(['termux-notification-remove',
'all'], check=True)
                return True
            except subprocess.CalledProcessError:
                return False
        return False
```                                    
