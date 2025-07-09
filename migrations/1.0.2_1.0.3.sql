BEGIN TRANSACTION;

ALTER TABLE queries
    ADD COLUMN query_name TEXT;

UPDATE parameters
SET value = '1.0.3'
WHERE key = 'version';

COMMIT;