BEGIN TRANSACTION;

UPDATE parameters
SET value = '1.0.5.3'
WHERE key = 'version';

COMMIT;