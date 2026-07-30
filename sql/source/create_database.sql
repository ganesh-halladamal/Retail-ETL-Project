-- ===========================================
-- Retail ETL Project - Source OLTP Database
-- File: create_database.sql
-- Purpose: Create the retail_oltp database
-- ===========================================

-- Drop database if exists (use with caution in production)
DROP DATABASE IF EXISTS retail_oltp;

-- Create the transactional database
CREATE DATABASE retail_oltp
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Select the database
USE retail_oltp;

-- Verify creation
SELECT 'retail_oltp database created successfully.' AS status;
