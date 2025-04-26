#### NOTIFICATION ####
MESSAGE = '''\
🆕 Title : {title}
💶 Price : {price}
🛍️ Brand : {brand}
<a href='{image}'>&#8205;</a>
'''

#### PROXY SETTINGS ####
# Proxy list
PROXY_LIST = ""
# Proxy list link. Only one.
PROXY_LIST_LINK = ""
# Should we check proxies? Defaults to False bcs ffs I hate working with proxies
CHECK_PROXIES = False

#### WEB UI SETTINGS ####
# Web UI port
WEB_UI_PORT = 8000

#### RSS FEED SETTINGS ####
# RSS feed port
RSS_PORT = 8001
# Maximum number of items to keep in the RSS feed
RSS_MAX_ITEMS = 50
# Enable/disable RSS feed
RSS_ENABLED = True

#### HTTP HEADERS ####
# User agents for rotating to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/536.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.14 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.1.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E147 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/111.0"
]

# Default headers for HTTP requests
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}
