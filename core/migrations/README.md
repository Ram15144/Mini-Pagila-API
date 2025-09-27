# Database Migrations Guide

## Overview

This guide explains how to work with database migrations in the pagila_api project. We use Alembic for managing database migrations.

## Local Development

### Prerequisites

- Make sure you have a local database running
- Your `.env.local` file should have the correct database URLs

### Common Commands

1. Check Current Migration Status

```bash
>alembic.ini
# Show what migrations exist
PYTHONPATH=. ENVIRONMENT=local alembic history

>alembic.ini
# Show what migration is currently applied
PYTHONPATH=. ENVIRONMENT=local alembic current
```

2. Create New Migration

```bash
# Create a new migration with automatic detection of changes

>alembic.ini
PYTHONPATH=. ENVIRONMENT=local alembic revision --autogenerate -m "your_migration_description"
```

3. Apply Migrations

```bash
# Apply all pending migrations
PYTHONPATH=. ENVIRONMENT=local alembic upgrade head

# Apply specific number of migrations
PYTHONPATH=. ENVIRONMENT=local alembic upgrade +1

# Rollback migrations
PYTHONPATH=. ENVIRONMENT=local alembic downgrade -1
```

### Notes

- Always create migrations locally first and test them
- Review auto-generated migrations before committing them

## Troubleshooting

1. If you get "Target database is not up to date":

   - Check current status: `alembic current`
   - Apply pending migrations before creating new ones

2. If you can't connect to staging database:

   - Check if tunnel is running: `make staging-db-tunnel`

3. If autogenerate doesn't detect changes:
   - Make sure your model changes are imported in the migration environment
   - Verify database connection is working
