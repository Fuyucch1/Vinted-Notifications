BEGIN TRANSACTION;

UPDATE parameters
SET value = '1.0.5.2'
WHERE key = 'version';

COMMIT;