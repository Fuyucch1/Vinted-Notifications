BEGIN TRANSACTION;

INSERT OR IGNORE INTO parameters (key, value)
VALUES ('rss_public_url', '');

UPDATE parameters
SET value = '1.0.5.5'
WHERE key = 'version';

COMMIT;
