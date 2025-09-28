BEGIN TRANSACTION;

-- Add banwords parameter
INSERT INTO parameters (key, value)
VALUES ('banwords', '');

UPDATE parameters
SET value = '1.0.5'
WHERE key = 'version';

COMMIT;
