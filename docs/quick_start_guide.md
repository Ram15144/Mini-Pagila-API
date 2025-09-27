# Quick Start Guide - Pagila API Testing

## 🚀 Get Started in 5 Minutes

This guide will get you up and running with the Pagila API for local testing using Postman.

## Step 1: Start the API

```bash
# Navigate to project directory
cd /path/to/pagila_api

# Start the API server
make dev
```

**Expected Output:**
```
🚀 Starting development server...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Starting Pagila API...
```

## Step 2: Verify API is Running

**Test in Browser:**
Visit: `http://localhost:8000/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Test with curl:**
```bash
curl http://localhost:8000/health
```

## Step 3: Setup Database (if not done already)

```bash
# Option 1: Using Make commands
make db-setup

# Option 2: Manual setup
createdb pagila
psql pagila < scripts/pagila-schema.sql
psql pagila < scripts/pagila-data.sql
```

## Step 4: Import Postman Collection

### Option A: Import JSON Files
1. **Open Postman**
2. **Import Collection**: 
   - Click "Import" button
   - Select `postman/Pagila_API_Collection.json`
3. **Import Environment**:
   - Click "Import" button  
   - Select `postman/Pagila_Environment.json`
4. **Select Environment**: Choose "Pagila API - Local Environment" in top-right dropdown

### Option B: Manual Setup
1. **Create New Collection**: Name it "Pagila API"
2. **Create Environment**: Name it "Pagila Local"
3. **Add Variables**:
   ```
   base_url = http://localhost:8000
   api_version = v1
   auth_token = dvd_admin
   customer_id = 1
   film_id = 1
   inventory_id = 1
   staff_id = 1
   ```

## Step 5: Test Key Endpoints

### 1. Health Check
```
GET {{base_url}}/health
```
**Expected**: 200 OK with status "healthy"

### 2. List Films
```
GET {{base_url}}/api/{{api_version}}/films
```
**Expected**: 200 OK with films array and pagination info

### 3. Create Rental (Protected)
```
POST {{base_url}}/api/{{api_version}}/customers/1/rentals
Headers: Authorization: Bearer {{auth_token}}
Body: {"inventory_id": 1, "staff_id": 1}
```
**Expected**: 200/201 with rental details

### 4. Authentication Test
```
GET {{base_url}}/protected
Headers: Authorization: Bearer {{auth_token}}
```
**Expected**: 200 OK with access granted message

## Quick Test Commands (curl)

```bash
# Health check
curl http://localhost:8000/health

# List films
curl http://localhost:8000/api/v1/films

# Get specific film
curl http://localhost:8000/api/v1/films/1

# Search films
curl "http://localhost:8000/api/v1/films/search/title?q=ACADEMY"

# Create rental (protected)
curl -X POST http://localhost:8000/api/v1/customers/1/rentals \
  -H "Authorization: Bearer dvd_admin" \
  -H "Content-Type: application/json" \
  -d '{"inventory_id": 1, "staff_id": 1}'

# Get customer rentals
curl http://localhost:8000/api/v1/customers/1/rentals
```

## Expected Response Examples

### Films List Response
```json
{
  "films": [
    {
      "film_id": 1,
      "title": "ACADEMY DINOSAUR",
      "description": "A Epic Drama of a Feminist...",
      "rental_rate": 0.99,
      "streaming_available": true,
      "last_update": "2006-02-15T10:03:42"
    }
  ],
  "total": 20,
  "skip": 0,
  "limit": 10
}
```

### Rental Creation Response
```json
{
  "rental_id": 16,
  "rental_date": "2024-01-15T10:30:00",
  "inventory_id": 1,
  "customer_id": 1,
  "return_date": null,
  "staff_id": 1,
  "last_update": "2024-01-15T10:30:00"
}
```

## Common Issues & Solutions

### ❌ Connection Refused
**Problem**: `Error: connect ECONNREFUSED 127.0.0.1:8000`
**Solution**: Make sure API is running with `make dev`

### ❌ Database Connection Error
**Problem**: `connection to server failed`
**Solution**: 
```bash
# Check PostgreSQL is running
brew services start postgresql@15  # macOS
sudo systemctl start postgresql    # Linux

# Verify database exists
psql -l | grep pagila
```

### ❌ Authentication Failed
**Problem**: `401 Unauthorized`
**Solution**: Ensure you're using `Bearer dvd_admin` in Authorization header

### ❌ Empty Film Results
**Problem**: `"films": []`
**Solution**: 
```bash
# Check if data was loaded
psql pagila -c "SELECT COUNT(*) FROM film;"
# Should show count > 0

# If empty, reload data
psql pagila < scripts/pagila-data.sql
```

## Next Steps

1. **Explore Full Collection**: Run all tests in Postman Collection Runner
2. **Test Error Cases**: Try invalid IDs, missing auth, malformed JSON
3. **Performance Testing**: Test with large datasets and measure response times
4. **Custom Tests**: Add your own test scenarios

## API Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/health` | No | Health check |
| GET | `/protected` | Yes | Auth test |
| GET | `/api/v1/films` | No | List films |
| GET | `/api/v1/films/{id}` | No | Get film |
| GET | `/api/v1/films/search/title` | No | Search films |
| GET | `/api/v1/films/streaming/available` | No | Streaming films |
| POST | `/api/v1/customers/{id}/rentals` | Yes | Create rental |
| GET | `/api/v1/customers/{id}/rentals` | No | Customer rentals |
| GET | `/api/v1/rentals/active` | No | Active rentals |
| GET | `/api/v1/rentals/{id}` | No | Get rental |
| PUT | `/api/v1/rentals/{id}/return` | Yes | Return rental |

## Authentication Token
- **Valid Token**: `dvd_admin`
- **Header Format**: `Authorization: Bearer dvd_admin`

---

**Ready to test!** 🎉 For more detailed guides, see:
- [Comprehensive Postman Testing Guide](postman_testing_guide.md)
- [Database Setup Guide](database_setup_guide.md)
