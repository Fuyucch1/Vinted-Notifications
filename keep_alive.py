#!/usr/bin/env python3
"""
Keep-Alive Component for Vinted Notifications

This module provides functionality to keep the application alive on free hosting platforms
like Render, Heroku, Railway, etc. that shut down applications after periods of inactivity.

The component works by:
1. Making periodic HTTP requests to the application's own web UI
2. Running in a separate thread to avoid blocking the main application
3. Using configurable intervals and retry logic
4. Gracefully handling errors and network issues
"""

import time
import threading
import requests
from datetime import datetime
from logger import get_logger
import configuration_values

# Get logger for this module
logger = get_logger(__name__)

class KeepAlive:
    """
    Keep-alive service that periodically pings the application to prevent
    hosting platforms from shutting it down due to inactivity.
    """
    
    def __init__(self, 
                 ping_interval=300,  # 5 minutes default
                 base_url=None,
                 timeout=30,
                 max_retries=3,
                 retry_delay=60):
        """
        Initialize the keep-alive service.
        
        Args:
            ping_interval (int): Seconds between ping requests (default: 300 = 5 minutes)
            base_url (str): Base URL to ping. If None, uses localhost with WEB_UI_PORT
            timeout (int): Request timeout in seconds (default: 30)
            max_retries (int): Maximum retry attempts on failure (default: 3)
            retry_delay (int): Delay between retries in seconds (default: 60)
        """
        self.ping_interval = ping_interval
        self.base_url = base_url or f"http://localhost:{configuration_values.WEB_UI_PORT}"
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.running = False
        self.thread = None
        self.last_ping_time = None
        self.ping_count = 0
        self.error_count = 0
        
        # Create a session for connection reuse
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Vinted-Notifications-KeepAlive/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
    
    def ping(self):
        """
        Send a ping request to the application.
        
        Returns:
            bool: True if ping was successful, False otherwise
        """
        try:
            response = self.session.get(
                self.base_url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.ping_count += 1
                self.last_ping_time = datetime.now()
                logger.debug(f"Keep-alive ping #{self.ping_count} successful (status: {response.status_code})")
                return True
            else:
                logger.warning(f"Keep-alive ping returned status code: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Keep-alive ping failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during keep-alive ping: {e}")
            return False
    
    def ping_with_retry(self):
        """
        Ping with retry logic.
        
        Returns:
            bool: True if any ping attempt was successful, False if all failed
        """
        for attempt in range(self.max_retries):
            if self.ping():
                if attempt > 0:
                    logger.info(f"Keep-alive ping succeeded on attempt {attempt + 1}")
                return True
            
            if attempt < self.max_retries - 1:
                logger.info(f"Keep-alive ping attempt {attempt + 1} failed, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        self.error_count += 1
        logger.error(f"Keep-alive ping failed after {self.max_retries} attempts (total errors: {self.error_count})")
        return False
    
    def _run_loop(self):
        """
        Main loop that runs in a separate thread.
        """
        logger.info(f"Keep-alive service started - pinging {self.base_url} every {self.ping_interval} seconds")
        
        while self.running:
            try:
                # Perform ping with retry logic
                self.ping_with_retry()
                
                # Wait for the next ping interval
                for _ in range(self.ping_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Unexpected error in keep-alive loop: {e}", exc_info=True)
                # Continue running even if there's an error
                time.sleep(60)  # Wait a minute before trying again
        
        logger.info("Keep-alive service stopped")
    
    def start(self):
        """
        Start the keep-alive service in a background thread.
        """
        if self.running:
            logger.warning("Keep-alive service is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Keep-alive service thread started")
    
    def stop(self):
        """
        Stop the keep-alive service.
        """
        if not self.running:
            logger.warning("Keep-alive service is not running")
            return
        
        logger.info("Stopping keep-alive service...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
            if self.thread.is_alive():
                logger.warning("Keep-alive thread did not stop gracefully")
        
        # Close the session
        self.session.close()
        logger.info("Keep-alive service stopped")
    
    def get_status(self):
        """
        Get the current status of the keep-alive service.
        
        Returns:
            dict: Status information including ping count, errors, last ping time, etc.
        """
        return {
            'running': self.running,
            'ping_count': self.ping_count,
            'error_count': self.error_count,
            'last_ping_time': self.last_ping_time.isoformat() if self.last_ping_time else None,
            'ping_interval': self.ping_interval,
            'base_url': self.base_url
        }


# Global keep-alive instance
_keep_alive_instance = None

def start_keep_alive(ping_interval=300, base_url=None, **kwargs):
    """
    Start the global keep-alive service.
    
    Args:
        ping_interval (int): Seconds between ping requests (default: 300 = 5 minutes)
        base_url (str): Base URL to ping. If None, uses localhost with WEB_UI_PORT
        **kwargs: Additional arguments passed to KeepAlive constructor
    """
    global _keep_alive_instance
    
    if _keep_alive_instance and _keep_alive_instance.running:
        logger.warning("Keep-alive service is already running")
        return
    
    _keep_alive_instance = KeepAlive(
        ping_interval=ping_interval,
        base_url=base_url,
        **kwargs
    )
    _keep_alive_instance.start()

def stop_keep_alive():
    """
    Stop the global keep-alive service.
    """
    global _keep_alive_instance
    
    if _keep_alive_instance:
        _keep_alive_instance.stop()
        _keep_alive_instance = None

def get_keep_alive_status():
    """
    Get the status of the global keep-alive service.
    
    Returns:
        dict: Status information or None if service is not initialized
    """
    global _keep_alive_instance
    
    if _keep_alive_instance:
        return _keep_alive_instance.get_status()
    return None

def is_keep_alive_running():
    """
    Check if the keep-alive service is running.
    
    Returns:
        bool: True if running, False otherwise
    """
    global _keep_alive_instance
    
    return _keep_alive_instance and _keep_alive_instance.running