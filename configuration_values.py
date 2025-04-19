#### TELEGRAM ####
TOKEN = "#####-#####" # Token given by BotFather
CHAT_ID = "#####" # Chat ID of your chat with the bot

#### NOTIFICATION ####
MESSAGE = '''\
🆕 Title : {title}
💶 Price : {price}
🛍️ Brand : {brand}
<a href='{image}'>&#8205;</a>
'''

#### PROXY SETTINGS ####
# Free proxy list (used if SQUID_PROXY is not set)
PROXY_LIST = ""

# Squid proxy settings (leave empty to disable)
SQUID_PROXY = ""  # Example: "http://proxy.example.com:3128" or just "proxy.example.com:3128"
SQUID_USERNAME = ""  # Username for squid proxy authentication
SQUID_PASSWORD = ""  # Password for squid proxy authentication

#### HTTP HEADERS ####
# User agents for rotating to avoid detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0"
]

# Default headers for HTTP requests
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}
