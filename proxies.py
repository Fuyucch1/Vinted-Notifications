import random
import requests
import time
from requests.exceptions import RequestException
import configuration_values
import concurrent.futures
from typing import List, Optional

# Cache for proxy list
_PROXY_CACHE = None
_PROXY_CACHE_INITIALIZED = False
_SINGLE_PROXY = None
_LAST_PROXY_CHECK_TIME = 0  # Timestamp of the last proxy check

# URL to test proxies against
_TEST_URL = "https://www.vinted.fr/"
_TEST_TIMEOUT = 2  # seconds


def check_proxies_parallel(proxies_list: List[str]) -> List[str]:
    """
    Check multiple proxies in parallel using a thread pool.

    Args:
        proxies_list (List[str]): List of proxy strings to check.

    Returns:
        List[str]: List of working proxies.
    """
    working_proxies = []

    # Use ThreadPoolExecutor to check proxies in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=configuration_values.MAX_PROXY_WORKERS) as executor:
        # Submit all proxy checking tasks
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies_list}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                is_working = future.result()
                if is_working:
                    working_proxies.append(proxy)
            except Exception:
                # If an exception occurred during checking, consider the proxy not working
                pass

    return working_proxies


def get_random_proxy() -> Optional[str]:
    """
    Get a random proxy from the configuration values.

    Uses a cache to minimize I/O operations:
    - If there are no proxies on first check, never checks again
    - If there is only one proxy, always returns that one
    - Otherwise, returns a random proxy from the cached list

    Proxies are checked in parallel to avoid blocking the main thread.
    Proxies are rechecked if they were checked more than PROXY_RECHECK_INTERVAL seconds ago.

    Returns:
        Optional[str]: A randomly selected proxy string or None if no working proxies are found.
    """
    global _PROXY_CACHE, _PROXY_CACHE_INITIALIZED, _SINGLE_PROXY, _LAST_PROXY_CHECK_TIME

    current_time = time.time()

    # Check if we need to recheck proxies (if more than PROXY_RECHECK_INTERVAL seconds have passed)
    if (_PROXY_CACHE_INITIALIZED and
            _LAST_PROXY_CHECK_TIME > 0 and
            current_time - _LAST_PROXY_CHECK_TIME > configuration_values.PROXY_RECHECK_INTERVAL):
        # Reset cache to force recheck
        _PROXY_CACHE_INITIALIZED = False
        _PROXY_CACHE = None
        _SINGLE_PROXY = None

    # If cache is already initialized
    if _PROXY_CACHE_INITIALIZED:
        # If we determined there are no proxies, always return None
        if _PROXY_CACHE is None:
            return None
        # If we have a single proxy, always return that one
        if _SINGLE_PROXY is not None:
            return _SINGLE_PROXY
        # Otherwise, return a random proxy from the cache
        if _PROXY_CACHE:
            return random.choice(_PROXY_CACHE)
        return None

    # Initialize cache on first call or after recheck interval
    _PROXY_CACHE_INITIALIZED = True
    _LAST_PROXY_CHECK_TIME = current_time  # Update the last check time

    # Check if PROXY_LIST is configured
    if configuration_values.PROXY_LIST:
        # If PROXY_LIST is a string with multiple proxies separated by semicolons
        all_proxies = [p.strip() for p in configuration_values.PROXY_LIST.split(';') if p.strip()]

        # Check proxies in parallel
        working_proxies = check_proxies_parallel(all_proxies)

        if working_proxies:
            _PROXY_CACHE = working_proxies
            # If there's only one working proxy, cache it separately
            if len(working_proxies) == 1:
                _SINGLE_PROXY = working_proxies[0]
                return _SINGLE_PROXY
            return random.choice(working_proxies)

    # No working proxies found
    _PROXY_CACHE = None
    return None


def check_proxy(proxy: str) -> bool:
    """
    Check if a proxy is working by making a request to the test URL.

    This function is thread-safe as it creates a new session for each check.
    Uses a random user agent to avoid detection.

    Args:
        proxy (str): Proxy string to check.

    Returns:
        bool: True if the proxy is working, False otherwise.
    """
    if proxy is None:
        return False

    # Convert proxy string to dictionary format
    proxy_dict = convert_proxy_string_to_dict(proxy)

    try:
        # Create a new session for testing (ensures thread safety)
        session = requests.Session()

        # Set random user agent and default headers
        headers = {
            "User-Agent": random.choice(configuration_values.USER_AGENTS),
            **configuration_values.DEFAULT_HEADERS
        }
        session.headers.update(headers)

        # Make a HEAD request to the test URL with the proxy
        response = session.head(_TEST_URL, proxies=proxy_dict, timeout=_TEST_TIMEOUT)

        # Check if the request was successful
        return response.status_code == 200
    except (RequestException, ConnectionError, TimeoutError) as e:
        # Any exception means the proxy is not working
        return False
    finally:
        # Ensure the session is closed to prevent resource leaks
        if 'session' in locals():
            session.close()


def convert_proxy_string_to_dict(proxy: Optional[str]) -> dict:
    """
    Convert a proxy string to a dictionary format.

    Args:
        proxy (Optional[str]): Proxy string to convert.

    Returns:
        dict: Proxy configuration dictionary.
    """
    if proxy is None:
        return {}

    if '://' in proxy:
        # Protocol is specified (e.g., "http://127.0.0.1:8080")
        protocol, address = proxy.split('://')
        return {protocol: proxy}
    else:
        # Protocol is not specified, default to http
        return {"http": f"http://{proxy}", "https": f"https://{proxy}"}


def configure_proxy(session: requests.Session, proxy: Optional[str] = None) -> bool:
    """
    Configure the proxy settings for a requests session.

    Args:
        session (requests.Session): The session to configure.
        proxy (Optional[str], optional): Proxy to be used. If None, a random proxy will be selected.

    Returns:
        bool: True if proxy was configured, False otherwise.
    """
    # If no proxy is provided, get a random one
    if proxy is None:
        proxy = get_random_proxy()

    # If we still don't have a proxy, return False
    if proxy is None:
        return False

    # Handle string proxy
    if isinstance(proxy, str):
        proxy = convert_proxy_string_to_dict(proxy)

    # Update the session with the proxy settings
    session.proxies.update(proxy)
    return True
