from pyVintedVN.items import Items
from pyVintedVN.requester import requester


class Vinted:
    """
    This class is built to connect with the Vinted API.

    It serves as a wrapper around the Items class, providing a convenient interface
    for searching Vinted listings with optional proxy support.

    Attributes:
        items (Items): An instance of the Items class for searching Vinted listings.

    Example:
        >>> vinted = Vinted()
        >>> items = vinted.items.search("https://www.vinted.fr/catalog?search_text=shoes")
    """

    def __init__(self, proxy=None, proxy_username=None, proxy_password=None):
        """
        Initialize the Vinted class with optional proxy settings.

        Args:
            proxy (str or dict, optional): Proxy to be used to bypass Vinted's rate limits.
                Can be a string (e.g., "http://127.0.0.1:8080") or a dictionary
                (e.g., {"http": "http://127.0.0.1:8080", "https": "https://127.0.0.1:8080"}).
            proxy_username (str, optional): Username for proxy authentication (for squid proxy).
            proxy_password (str, optional): Password for proxy authentication (for squid proxy).
        """
        # Configure proxy if provided
        if proxy is not None:
            self._configure_proxy(proxy, proxy_username, proxy_password)

        # Initialize Items instance for searching Vinted listings
        self.items = Items()

    def _configure_proxy(self, proxy, proxy_username=None, proxy_password=None):
        """
        Configure the proxy settings for the requester.

        Args:
            proxy (str or dict): Proxy to be used.
            proxy_username (str, optional): Username for proxy authentication.
            proxy_password (str, optional): Password for proxy authentication.
        """
        # Handle proxy with authentication
        if proxy_username is not None and proxy_password is not None:
            proxy = self._configure_authenticated_proxy(proxy, proxy_username, proxy_password)
        # Handle string proxy without authentication
        elif isinstance(proxy, str):
            proxy = self._convert_proxy_string_to_dict(proxy)

        # Update the requester's session with the proxy settings
        requester.session.proxies.update(proxy)

    def _configure_authenticated_proxy(self, proxy, username, password):
        """
        Configure a proxy with authentication.

        Args:
            proxy (str): Proxy to be used.
            username (str): Username for proxy authentication.
            password (str): Password for proxy authentication.

        Returns:
            dict: Proxy configuration dictionary.
        """
        if isinstance(proxy, str):
            proxy_parts = proxy.split('://')
            if len(proxy_parts) == 2:
                # Protocol is specified (e.g., "http://127.0.0.1:8080")
                protocol, address = proxy_parts
                auth_proxy = f"{protocol}://{username}:{password}@{address}"
                return {protocol: auth_proxy}
            else:
                # Protocol is not specified, default to http
                auth_proxy = f"http://{username}:{password}@{proxy}"
                return {"http": auth_proxy, "https": auth_proxy}
        return proxy

    def _convert_proxy_string_to_dict(self, proxy):
        """
        Convert a proxy string to a dictionary format.

        Args:
            proxy (str): Proxy string to convert.

        Returns:
            dict: Proxy configuration dictionary.
        """
        if '://' in proxy:
            # Protocol is specified (e.g., "http://127.0.0.1:8080")
            protocol, address = proxy.split('://')
            return {protocol: proxy}
        else:
            # Protocol is not specified, default to http
            return {"http": f"http://{proxy}", "https": f"https://{proxy}"}
