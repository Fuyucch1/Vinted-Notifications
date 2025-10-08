-- Migration from 1.0.5.1 to 1.0.6
-- Add users table for authentication

PRAGMA foreign_keys = ON;

/* ============================
   Tables
   ============================ */

-- Users table
CREATE TABLE IF NOT EXISTS users
(
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    reset_token     TEXT,
    reset_token_exp NUMERIC,
    created_at      NUMERIC DEFAULT (strftime('%s', 'now')),
    is_admin        BOOLEAN DEFAULT 0
);

/* ============================
   Update version
   ============================ */

UPDATE parameters
SET value = '1.0.6'
WHERE key = 'version';