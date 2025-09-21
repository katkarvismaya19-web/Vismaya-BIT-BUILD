-- Add Google OAuth support to Users table
-- Run this SQL script to update your database schema

-- Add google_id column to Users table for Google OAuth integration
ALTER TABLE Users ADD COLUMN google_id VARCHAR(255) NULL;

-- Add index on google_id for faster lookups
CREATE INDEX idx_users_google_id ON Users(google_id);

-- Make password_hash nullable for Google OAuth users
ALTER TABLE Users MODIFY COLUMN password_hash VARCHAR(255) NULL;

-- Update any existing test users if needed
-- UPDATE Users SET balance = 100000.00 WHERE balance = 10000.00;

SHOW COLUMNS FROM Users;