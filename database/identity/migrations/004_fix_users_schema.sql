-- Migration 004
-- The users table already contains password_hash
-- and does not contain is_active.
-- No schema changes are required.
SELECT 1;