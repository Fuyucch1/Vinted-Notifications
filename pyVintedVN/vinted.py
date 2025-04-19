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

    def __init__(self, proxy=None):
        """
        Initialize the Vinted class with optional proxy settings.

        Args:
            proxy (str or dict, optional): Proxy to be used to bypass Vinted's rate limits.
                Can be a string (e.g., "http://127.0.0.1:8080") or a dictionary
                (e.g., {"http": "http://127.0.0.1:8080", "https": "https://127.0.0.1:8080"}).
        """
        # Configure proxy if provided
        if proxy is not None:
            self._configure_proxy(proxy)

        # Initialize Items instance for searching Vinted listings
        self.items = Items()

    def _configure_proxy(self, proxy):
        """
        Configure the proxy settings for the requester.

        Args:
            proxy (str or dict): Proxy to be used.
        """
        # Handle string proxy
        if isinstance(proxy, str):
            proxy = self._convert_proxy_string_to_dict(proxy)

        # Update the requester's session with the proxy settings
        requester.session.proxies.update(proxy)

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
