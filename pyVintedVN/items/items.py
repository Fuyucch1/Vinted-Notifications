from pyVintedVN.items.item import Item
from pyVintedVN.requester import requester
from urllib.parse import urlparse, parse_qsl
from requests.exceptions import HTTPError
from typing import List, Dict, Optional
from pyVintedVN.settings import Urls


class Items:
    """
    A class for searching and retrieving items from Vinted.

    This class provides methods to search for items on Vinted using a search URL
    and to parse Vinted search URLs into API parameters.

    Example:
        >>> items = Items()
        >>> results = items.search("https://www.vinted.fr/catalog?search_text=shoes")
    """

    def search(
        self,
        url: str,
        nbr_items: int = 20,
        page: int = 1,
        time: Optional[int] = None,
        json: bool = False,
    ) -> List[Item]:
        """
        Retrieve items from a given search URL on Vinted.

        Args:
            url (str): The URL of the search on Vinted.
            nbr_items (int, optional): Number of items to be returned. Defaults to 20.
            page (int, optional): Page number to be returned. Defaults to 1.
            time (int, optional): Timestamp to filter items by time. Defaults to None. Looks like it doesn't work though.
            json (bool, optional): Whether to return raw JSON data instead of Item objects.
                Defaults to False.

        Returns:
            List[Item]: A list of Item objects.

        Raises:
            HTTPError: If the request to the Vinted API fails.
        """
        # Extract the domain from the URL and set the locale
        locale = urlparse(url).netloc
        requester.set_locale(locale)

        # Parse the URL to get the API parameters
        params = self.parse_url(url, nbr_items, page, time)

        # Construct the API URL
        api_url = (
            f"https://{locale}{Urls.VINTED_API_URL}/{Urls.VINTED_PRODUCTS_ENDPOINT}"
        )

        try:
            # Make the request to the Vinted API
            response = requester.get(url=api_url, params=params)
            response.raise_for_status()

            # Parse the response
            items = response.json()
            items = items["items"]

            # Return either Item objects or raw JSON data
            if not json:
                return [Item(_item) for _item in items]
            else:
                return items

        except HTTPError as err:
            raise err

    def parse_url(
        self, url: str, nbr_items: int = 20, page: int = 1, time: Optional[int] = None
    ) -> Dict:
        """
        Parse a Vinted search URL to get parameters for the API call.

        Args:
            url (str): The URL of the search on Vinted.
            nbr_items (int, optional): Number of items to be returned. Defaults to 20.
            page (int, optional): Page number to be returned. Defaults to 1.
            time (int, optional): Timestamp to filter items by time. Defaults to None.

        Returns:
            Dict: A dictionary of parameters for the Vinted API.
        """
        # Parse the query parameters from the URL
        queries = parse_qsl(urlparse(url).query)

        # Construct the parameters dictionary
        params = {
            "search_text": "+".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "search_text"])
            ),
            "video_game_platform_ids": ",".join(
                map(
                    str,
                    [
                        tpl[1]
                        for tpl in queries
                        if tpl[0] == "video_game_platform_ids[]"
                    ],
                )
            ),
            "catalog_ids": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "catalog[]"])
            ),
            "color_ids": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "color_ids[]"])
            ),
            "brand_ids": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "brand_ids[]"])
            ),
            "size_ids": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "size_ids[]"])
            ),
            "material_ids": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "material_ids[]"])
            ),
            "status_ids": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "status_ids[]"])
            ),
            "country_ids": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "country_ids[]"])
            ),
            "city_ids": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "city_ids[]"])
            ),
            "is_for_swap": ",".join(
                map(str, [1 for tpl in queries if tpl[0] == "disposal[]"])
            ),
            "currency": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "currency"])
            ),
            "price_to": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "price_to"])
            ),
            "price_from": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "price_from"])
            ),
            "page": page,
            "per_page": nbr_items,
            "order": ",".join(
                map(str, [tpl[1] for tpl in queries if tpl[0] == "order"])
            ),
            "time": time,
        }

        return params

    # Aliases for backward compatibility
    parseUrl = parse_url
