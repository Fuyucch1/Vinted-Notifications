BEGIN TRANSACTION;

UPDATE parameters
SET value = '1.0.3'
WHERE key = 'version';

COMMIT;