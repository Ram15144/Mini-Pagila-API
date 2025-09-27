# Pagila Database Setup Guide for pgAdmin

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [PostgreSQL Installation](#postgresql-installation)
3. [pgAdmin Setup](#pgadmin-setup)
4. [Database Creation](#database-creation)
5. [Running Schema Scripts](#running-schema-scripts)
6. [Data Population](#data-population)
7. [Verification](#verification)
8. [Sample Queries](#sample-queries)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have:
- PostgreSQL 12+ installed
- pgAdmin 4 installed
- Administrative access to create databases
- Downloaded Pagila scripts from this project

## PostgreSQL Installation

### Windows
1. Download PostgreSQL from [official website](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the setup wizard
3. Remember your `postgres` user password
4. Default port: 5432

### macOS
```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15

# Or download from official website
# https://www.postgresql.org/download/macos/
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## pgAdmin Setup

### Installation
1. **Download pgAdmin**: Visit [pgAdmin website](https://www.pgadmin.org/download/)
2. **Install**: Follow platform-specific instructions
3. **Launch**: Open pgAdmin 4

### Initial Configuration
1. **Create Server Connection**:
   - Right-click "Servers" → "Create" → "Server..."
   - **General Tab**:
     - Name: `Local PostgreSQL`
   - **Connection Tab**:
     - Host: `localhost`
     - Port: `5432`
     - Username: `postgres`
     - Password: [your postgres password]
     - Save password: ✓

2. **Test Connection**: Click "Save" to connect

## Database Creation

### Method 1: Using pgAdmin GUI

1. **Create Database**:
   - Right-click on your server → "Create" → "Database..."
   - Database name: `pagila`
   - Owner: `postgres`
   - Click "Save"

### Method 2: Using SQL Query Tool

1. **Open Query Tool**:
   - Right-click on your server → "Query Tool"
   - Execute: 
   ```sql
   CREATE DATABASE pagila WITH ENCODING 'UTF8';
   ```

### Method 3: Using Command Line

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create database
CREATE DATABASE pagila;

# Exit
\q
```

## Running Schema Scripts

### Step 1: Open Database
1. Expand your server → "Databases" → "pagila"
2. Right-click "pagila" → "Query Tool"

### Step 2: Load Schema Script
1. **Open File**: Click the folder icon in Query Tool
2. **Navigate**: Go to your project's `scripts/` directory
3. **Select**: Choose `pagila-schema.sql`
4. **Execute**: Click the play button (▶) or press F5

**Expected Output:**
```
CREATE EXTENSION
CREATE TYPE
CREATE DOMAIN
CREATE TABLE
CREATE SEQUENCE
... (multiple CREATE statements)
Query returned successfully in X ms.
```

### Step 3: Verify Schema Creation
```sql
-- Check if tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

**Expected Tables:**
- actor
- address
- category
- city
- country
- customer
- film
- film_actor
- film_category
- inventory
- language
- payment
- rental
- staff
- store
- streaming_subscription

## Data Population

### Step 1: Load Data Script
1. **Clear Query Tool**: Remove previous content
2. **Open File**: Click folder icon
3. **Select**: Choose `pagila-data.sql`
4. **Execute**: Click play button

**Expected Output:**
```
INSERT 0 6
INSERT 0 107
INSERT 0 60
... (multiple INSERT statements)
Query returned successfully in X ms.
```

### Step 2: Verify Data Load
```sql
-- Check record counts
SELECT 
    'actor' as table_name, COUNT(*) as records FROM actor
UNION ALL
SELECT 'film', COUNT(*) FROM film
UNION ALL
SELECT 'customer', COUNT(*) FROM customer
UNION ALL
SELECT 'rental', COUNT(*) FROM rental
ORDER BY table_name;
```

**Expected Counts:**
- actor: 30
- customer: 15  
- film: 20
- rental: 15
- (plus other tables)

## Verification

### Basic Connectivity Test
```sql
-- Test basic query
SELECT 'Database connection successful!' as status;
```

### Data Integrity Check
```sql
-- Test foreign key relationships
SELECT 
    f.title,
    c.name as category,
    COUNT(i.inventory_id) as inventory_count
FROM film f
LEFT JOIN film_category fc ON f.film_id = fc.film_id
LEFT JOIN category c ON fc.category_id = c.category_id
LEFT JOIN inventory i ON f.film_id = i.film_id
GROUP BY f.film_id, f.title, c.name
ORDER BY f.title
LIMIT 10;
```

### API-Specific Verification
```sql
-- Test streaming films
SELECT film_id, title, streaming_available 
FROM film 
WHERE streaming_available = true
LIMIT 5;

-- Test customer data
SELECT customer_id, first_name, last_name, email 
FROM customer 
LIMIT 5;

-- Test rental data
SELECT r.rental_id, r.rental_date, c.first_name, c.last_name, f.title
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
LIMIT 5;
```

## Sample Queries

### For Testing Your API

#### 1. Films API Testing
```sql
-- Get all films with pagination info
SELECT COUNT(*) as total_films FROM film;

-- Films by category
SELECT f.title, c.name as category
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE c.name = 'Action'
ORDER BY f.title;

-- Search films by title
SELECT film_id, title, description
FROM film
WHERE title ILIKE '%ACADEMY%'
ORDER BY title;

-- Streaming available films
SELECT film_id, title, rental_rate, streaming_available
FROM film
WHERE streaming_available = true
ORDER BY title;
```

#### 2. Rental API Testing
```sql
-- Active rentals (not returned)
SELECT r.rental_id, r.rental_date, c.first_name, c.last_name, f.title
FROM rental r
JOIN customer c ON r.customer_id = c.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE r.return_date IS NULL
ORDER BY r.rental_date DESC;

-- Customer rental history
SELECT r.rental_id, r.rental_date, r.return_date, f.title
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
WHERE r.customer_id = 1
ORDER BY r.rental_date DESC;

-- Available inventory for rental
SELECT i.inventory_id, f.title, s.store_id
FROM inventory i
JOIN film f ON i.film_id = f.film_id
JOIN store s ON i.store_id = s.store_id
WHERE NOT EXISTS (
    SELECT 1 FROM rental r 
    WHERE r.inventory_id = i.inventory_id 
    AND r.return_date IS NULL
)
ORDER BY f.title;
```

#### 3. Data for API Testing
```sql
-- Get valid IDs for testing
SELECT 'Valid Film IDs:' as info, string_agg(film_id::text, ', ') as ids
FROM (SELECT film_id FROM film ORDER BY film_id LIMIT 10) sub
UNION ALL
SELECT 'Valid Customer IDs:', string_agg(customer_id::text, ', ')
FROM (SELECT customer_id FROM customer ORDER BY customer_id LIMIT 10) sub
UNION ALL
SELECT 'Valid Staff IDs:', string_agg(staff_id::text, ', ')
FROM (SELECT staff_id FROM staff ORDER BY staff_id) sub
UNION ALL
SELECT 'Available Inventory IDs:', string_agg(inventory_id::text, ', ')
FROM (
    SELECT i.inventory_id 
    FROM inventory i
    WHERE NOT EXISTS (
        SELECT 1 FROM rental r 
        WHERE r.inventory_id = i.inventory_id 
        AND r.return_date IS NULL
    )
    ORDER BY i.inventory_id LIMIT 10
) sub;
```

## Troubleshooting

### Common Issues

#### 1. Connection Problems
**Error**: `could not connect to server`
```sql
-- Check PostgreSQL status
SELECT version();

-- Check current database
SELECT current_database();
```

**Solutions**:
- Verify PostgreSQL service is running
- Check connection parameters (host, port, credentials)
- Ensure firewall allows PostgreSQL port (5432)

#### 2. Permission Errors
**Error**: `permission denied for database`
```sql
-- Check current user permissions
SELECT current_user, session_user;

-- Grant permissions if needed (as superuser)
GRANT ALL PRIVILEGES ON DATABASE pagila TO postgres;
```

#### 3. Schema Already Exists
**Error**: `relation already exists`
```sql
-- Drop and recreate database if needed
DROP DATABASE IF EXISTS pagila;
CREATE DATABASE pagila;
```

#### 4. Missing Data
**Error**: Empty query results
```sql
-- Check if data was loaded
SELECT schemaname, tablename, n_tup_ins as inserted_rows
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

#### 5. Encoding Issues
**Error**: Character encoding problems
```sql
-- Check database encoding
SELECT pg_encoding_to_char(encoding) as encoding
FROM pg_database
WHERE datname = 'pagila';

-- Should show 'UTF8'
```

### Reset Database
If you need to start over:

```sql
-- Drop all tables
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;

-- Or drop and recreate entire database
DROP DATABASE pagila;
CREATE DATABASE pagila;
```

### Performance Optimization
```sql
-- Update table statistics
ANALYZE;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

## Connection Strings

For connecting your API to this database:

### Standard Connection
```
postgresql://postgres:password@localhost:5432/pagila
```

### Async Connection (for your API)
```
postgresql+asyncpg://postgres:password@localhost:5432/pagila
```

### Environment Variables
```bash
# .env file
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/pagila
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pagila
DB_USER=postgres
DB_PASSWORD=your_password
```

## Next Steps

1. **Verify API Connection**: Test your FastAPI application can connect
2. **Run API Tests**: Use the Postman collection to test endpoints
3. **Monitor Performance**: Check query performance and optimize as needed
4. **Backup Strategy**: Set up regular backups for your test data

For API testing with this database, see the companion **Postman Testing Guide**.
