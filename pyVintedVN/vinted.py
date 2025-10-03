from pyVintedVN.items import Items


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

    def __init__(self):
        """
        Initialize the Vinted class with optional proxy settings.

        Args: None
        """

        # Initialize Items instance for searching Vinted listings
        self.items = Items()
