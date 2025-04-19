import json
import requests
import re
import random
from requests.exceptions import HTTPError
import configuration_values


class Requester:

    def __init__(self):

        self.HEADER = {
            "User-Agent": random.choice(configuration_values.USER_AGENTS),
            **configuration_values.DEFAULT_HEADERS,
            "Host": "www.vinted.fr",
        }
        self.VINTED_AUTH_URL = "https://www.vinted.fr/"
        self.MAX_RETRIES = 3
        self.session = requests.Session()
        self.session.headers.update(self.HEADER)
        print(f"[DEBUG] Using User-Agent: {self.HEADER['User-Agent']}")

    def setLocale(self, locale):
        """
            Set the locale of the requester.
            :param locale: str
        """
        self.VINTED_AUTH_URL = f"https://{locale}/"
        self.HEADER = {
            "User-Agent": random.choice(configuration_values.USER_AGENTS),
            **configuration_values.DEFAULT_HEADERS,
            "Host": f"{locale}",
        }
        self.session.headers.update(self.HEADER)
        print(f"[DEBUG] Locale set to {locale} with User-Agent: {self.HEADER['User-Agent']}")

    def get(self, url, params=None):
        tried = 0
        print(self.session.headers)
        while tried < self.MAX_RETRIES:
            tried += 1
            with self.session.get(url, params=params) as response:
                if response.status_code == 401 and tried < self.MAX_RETRIES:
                    print(f"Cookies invalid retrying {tried}/{self.MAX_RETRIES}")
                    self.setCookies()
                elif response.status_code == 200 or tried == self.MAX_RETRIES:
                    return response
        return HTTPError

    def post(self, url, params=None):
        response = self.session.post(url, params)
        response.raise_for_status()
        return response

    def setCookies(self):
        self.session.cookies.clear_session_cookies()
        try:
            self.session.head(self.VINTED_AUTH_URL)
            print("Cookies set!")
        except Exception as e:
            print(f"There was an error fetching cookies for vinted\nError: {e}")

    def update_cookies(self, cookies: dict):
        self.session.cookies.update(cookies)
        print(f"[DEBUG] Cookies aggiornati manualmente ({len(cookies)} cookie ricevuti).")


requester = Requester()
