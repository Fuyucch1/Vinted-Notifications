from urllib.parse import urlparse, parse_qsl
import requests
from .items.item import Item
from pyVintedVN.items import Items
from pyVintedVN.requester import requester


class Vinted:
    """
    This class is built to connect with the pyVinted API.

    It's main goal is to be able to retrieve items from a given url search.\n

    """

    def __init__(self, proxy=None, proxy_username=None, proxy_password=None):
        """
        Args:
            proxy : proxy to be used to bypass vinted's limite rate
            proxy_username : username for proxy authentication (for squid proxy)
            proxy_password : password for proxy authentication (for squid proxy)

        """

        if proxy is not None:
            if proxy_username is not None and proxy_password is not None:
                # Format proxy with authentication for squid proxy
                proxy_parts = proxy.split('://')
                if len(proxy_parts) == 2:
                    protocol, address = proxy_parts
                    auth_proxy = f"{protocol}://{proxy_username}:{proxy_password}@{address}"
                    proxy = {protocol: auth_proxy}
                else:
                    # Default to http if protocol not specified
                    auth_proxy = f"http://{proxy_username}:{proxy_password}@{proxy}"
                    proxy = {"http": auth_proxy, "https": auth_proxy}
            elif isinstance(proxy, str):
                # Convert string proxy to dictionary format
                if '://' in proxy:
                    protocol, address = proxy.split('://')
                    proxy = {protocol: proxy}
                else:
                    # Default to http if protocol not specified
                    proxy = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
            print(proxy)
            requester.session.proxies.update(proxy)

        self.items = Items()
