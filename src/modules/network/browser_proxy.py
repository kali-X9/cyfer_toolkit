import os
import sys
import time
import logging
import subprocess
from typing import Dict, List, Optional
from threading import Thread, Event                                    from selenium import webdriver                                         from selenium.webdriver.firefox.options import Options as
FirefoxOptions
from selenium.webdriver.chrome.options import Options as
ChromeOptions                                                          from selenium.webdriver.common.proxy import Proxy, ProxyType           import stem.process
from stem import Signal
from stem.control import Controller
import requests                                                                                                                               class BrowserProxyManager:
    """
    Advanced Browser Proxy Management
    Automatically configures browsers to use Tor/V2Ray proxy
chains
    """

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger("cyfer.browser_proxy")
        self.tor_port = config.get('tor_socks_port', 9050)
        self.v2ray_port = config.get('v2ray_socks_port', 1080)
        self.proxy_chain = self._build_proxy_chain()
        self.browser_process = None

    def _build_proxy_chain(self) -> List[Dict]:
        """Build proxy chain configuration"""
        return [
            {
                'type': 'socks5',
                'host': '127.0.0.1',
                'port': self.tor_port,
                'username': '',
                'password': ''
            },
            {
                'type': 'socks5',
                'host': '127.0.0.1',
                'port': self.v2ray_port,
                'username': '',
                'password': ''
            }
        ]

    def configure_firefox(self, profile_path: str = None) ->
Optional[webdriver.Firefox]:
        """Configure Firefox with proxy settings"""
        try:
            firefox_options = FirefoxOptions()

            # Set proxy configuration
            proxy = Proxy()
            proxy.proxy_type = ProxyType.MANUAL

            # Configure proxy chain
            proxy_chain = ";".join(
                [f"{p['type']}={p['host']}:{p['port']}" for p in
self.proxy_chain]
            )

            proxy.http_proxy = proxy_chain
            proxy.ssl_proxy = proxy_chain
            proxy.socks_proxy = proxy_chain
            proxy.socks_version = 5

            # Add proxy to capabilities
            firefox_options.set_proxy(proxy)

            # Additional privacy settings

firefox_options.set_preference("network.proxy.socks_remote_dns",
True)
            firefox_options.set_preference("network.trr.mode", 2)
 # DNS-over-HTTPS

firefox_options.set_preference("privacy.trackingprotection.enabledfirefox_options.set_preference("privacy.trackingprotecion.enabled", True)

firefox_options.set_preference("privacy.resistFingerprinting",
True)

            # Disable WebRTC

firefox_options.set_preference("media.peerconnection.enabled",
False)

firefox_options.set_preference("media.navigator.enabled", False)

            # Create or use existing profile
            if profile_path:
                firefox_options.add_argument(f"-profile
{profile_path}")
            else:
                firefox_options.add_argument("--private")

            # Start browser
            driver = webdriver.Firefox(options=firefox_options)
            self.browser_process = driver.service.process

            self.logger.info("Firefox configured with proxy
chain")
            return driver

        except Exception as e:
            self.logger.error(f"Failed to configure Firefox:
{str(e)}")
            return None

    def configure_chrome(self, user_data_dir: str = None) ->
Optional[webdriver.Chrome]:
        """Configure Chrome with proxy settings"""
        try:
            chrome_options = ChromeOptions()

            # Build proxy configuration string
            proxy_chain = ";".join(
                [f"{p['type']}={p['host']}:{p['port']}" for p in
self.proxy_chain]
            )

            # Set proxy arguments

chrome_options.add_argument(f"--proxy-server={proxy_chain}")

chrome_options.add_argument("--proxy-bypass-list=<-loopback>")

chrome_options.add_argument("--disable-features=WebRtcHideLocalIpschrome_options.add_argument("--disable-features=WebRtcideLocalIpsWithMdns")

            # Privacy enhancements

chrome_options.add_argument("--disable-blink-features=AutomationCochrome_options.add_argument("--disable-blink-features=utomationControlled")

chrome_options.add_experimental_option("excludeSwitches",
["enable-automation"])

chrome_options.add_experimental_option('useAutomationExtension',
False)

            # User data directory
            if user_data_dir:

chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

            # Start browser
            driver = webdriver.Chrome(options=chrome_options)
            self.browser_process = driver.service.process

            # Execute CDP commands for additional privacy
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd("Network.setBlockedURLs", {
                "urls": [
                    "*://*.google-analytics.com/*",
                    "*://*.doubleclick.net/*",
                    "*://*.googletagmanager.com/*"
                ]
            })

            self.logger.info("Chrome configured with proxy
chain")
            return driver

        except Exception as e:
            self.logger.error(f"Failed to configure Chrome:
{str(e)}")
            return None

    def verify_anonymity(self, driver) -> bool:
        """Verify browser anonymity"""
        try:
            # Test WebRTC leak                                                     driver.get("https://browserleaks.com/webrtc")                          time.sleep(5)
            webrtc_leak = "Real IP Address" not in
driver.page_source

            # Test DNS leak
            driver.get("https://dnsleaktest.com")
            time.sleep(5)
            dns_leak = "DNS Leak Test" in driver.page_source and
"Congratulations" in driver.page_source

            # Test IP leak
            driver.get("https://api.ipify.org?format=json")
            time.sleep(2)
            ip_data = driver.find_element_by_tag_name("pre").text
            ip_leak = "error" not in ip_data.lower()

            return webrtc_leak and dns_leak and ip_leak

        except Exception as e:
            self.logger.error(f"Anonymity verification failed:
{str(e)}")
            return False

    def close_browser(self):
        """Close the browser instance"""
        if self.browser_process:
            try:
                self.browser_process.terminate()
                self.browser_process.wait(timeout=5)
            except:
                try:
                    self.browser_process.kill()
                except:
                    pass
            finally:
                self.browser_process = None
                self.logger.info("Browser instance terminated")
```
