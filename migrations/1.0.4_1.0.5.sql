BEGIN TRANSACTION;

-- Add banwords parameter
INSERT INTO parameters (key, value)
VALUES ('banwords', '');

INSERT OR IGNORE INTO parameters (key, value)
VALUES ('message_template', '🆕 Title : {title}
💶 Price : {price}
🛍️ Brand : {brand}
<a href="{image}">&#8205;</a>'),
       ('web_ui_port', '8000'),
       ('user_agents', '[
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/536.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.14 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.1.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E147 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/111.0"
]'),
       ('default_headers',
        '{"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"}');


UPDATE parameters
SET value = '1.0.5'
WHERE key = 'version';

COMMIT;
