-- Initialize Heimdall Database
-- This script runs automatically when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS heimdall;

-- Set default schema
SET search_path TO heimdall, public;

-- Example: Create initial tables (customize as needed)
-- CREATE TABLE IF NOT EXISTS heimdall.users (
--     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--     username VARCHAR(255) NOT NULL UNIQUE,
--     email VARCHAR(255) NOT NULL UNIQUE,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA heimdall TO asgard;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA heimdall TO asgard;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA heimdall TO asgard;

-- Insert initial data if needed
-- INSERT INTO heimdall.users (username, email) VALUES ('admin', 'admin@asgard.com') ON CONFLICT DO NOTHING;

-- Commit
COMMIT;
