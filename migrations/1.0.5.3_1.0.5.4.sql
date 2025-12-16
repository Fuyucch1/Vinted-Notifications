BEGIN TRANSACTION;

UPDATE parameters
SET value = '1.0.5.4'
WHERE key = 'version';

COMMIT;