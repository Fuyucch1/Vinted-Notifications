BEGIN TRANSACTION;

ALTER TABLE queries
    ADD COLUMN required_words TEXT DEFAULT '';

UPDATE parameters
SET value = '1.0.5.5'
WHERE key = 'version';

COMMIT;
