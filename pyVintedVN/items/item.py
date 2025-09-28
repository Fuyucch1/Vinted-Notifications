from datetime import datetime, timezone


class Item:
    """
    Represents a single item from Vinted.

    This class parses and stores various attributes of a Vinted item,
    such as id, title, brand, size, price, etc.

    Attributes:
        raw_data (dict): The raw data of the item as received from the API.
        id (str): The unique identifier of the item.
        title (str): The title of the item.
        brand_title (str): The brand of the item.
        size_title (str): The size of the item, or None if not available.
        currency (str): The currency code of the item's price.
        price (float): The price of the item.
        photo (str): The URL of the item's photo.
        url (str): The URL of the item on Vinted.
        created_at_ts (datetime): The timestamp when the item was created.
        raw_timestamp (int): The raw timestamp value from the API.
    """

    def __init__(self, data):
        """
        Initialize an Item with data from the Vinted API.

        Args:
            data (dict): The item data from the Vinted API.
        """
        self.raw_data = data
        self.id = data["id"]
        self.title = data["title"]
        self.brand_title = data["brand_title"]
        try:
            self.size_title = data["size_title"]
        except KeyError:
            # If size_title is not available, set it to None
            self.size_title = None
        self.currency = data["price"]["currency_code"]
        self.price = data["price"]["amount"]
        self.photo = data["photo"]["url"]
        self.url = data["url"]
        # We keep everything before the "items"
        self.buy_url = (
                data["url"].split("items")[0]
                + "transaction/buy/new?source_screen=item&transaction%5Bitem_id%5D="
                + str(data["id"])
        )
        self.created_at_ts = datetime.fromtimestamp(
            data["photo"]["high_resolution"]["timestamp"], tz=timezone.utc
        )
        self.raw_timestamp = data["photo"]["high_resolution"]["timestamp"]

    def __eq__(self, other):
        """
        Compare this item with another one.

        Two items are considered the same if they have the same ID.

        Args:
            other (Item): The other item to compare with.

        Returns:
            bool: True if the items have the same ID, False otherwise.
        """
        if not isinstance(other, Item):
            return False
        return self.id == other.id

    def __hash__(self):
        """
        Return a hash value for this item.

        The hash is based on the item's ID, which allows items to be used
        as keys in dictionaries and elements in sets.

        Returns:
            int: A hash value for the item.
        """
        return hash(("id", self.id))

    def is_new_item(self, minutes=20):
        """
        Check if this item is newly listed.

        An item is considered new if it was created within the specified
        number of minutes from the current time.

        Args:
            minutes (int, optional): The number of minutes to consider an item as new.
                Defaults to 5.

        Returns:
            bool: True if the item is new, False otherwise.
        """
        delta = datetime.now(timezone.utc) - self.created_at_ts
        return delta.total_seconds() < minutes * 60

    # Alias for backward compatibility
    isNewItem = is_new_item
