BEGIN TRANSACTION;

UPDATE parameters
SET value = '1.0.5.1'
WHERE key = 'version';

COMMIT;