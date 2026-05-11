# Backend Tier - Python Flask API

## Overview
This is the backend API tier for the birthday-app application. It validates user input and handles database operations.

## Building the Docker Image

```bash
docker build -t birthday-app-backend:latest .
```

## Running the Container

```bash
docker run -d \
  --name birthday-app-backend \
  -e DB_HOST=birthday-app-db \
  -e DB_PORT=5432 \
  -e DB_USER=birthday_user \
  -e DB_PASSWORD=birthday_password \
  -e DB_NAME=birthday_db \
  -p 5000:5000 \
  birthday-app-backend:latest
```

## Connection Details

- **Host**: `localhost` (when accessing from host machine)
- **Host**: `birthday-app-backend` (when connecting from another container on the same network)
- **Port**: `5000` (Flask development server)

## API Endpoints

### Health Check
- **Endpoint**: `GET /health`
- **Purpose**: Check if the backend service is running
- **Response**: 
  ```json
  {
    "status": "ok",
    "message": "Backend service is running"
  }
  ```

### Submit Form
- **Endpoint**: `POST /submit`
- **Purpose**: Submit and validate user registration form
- **Request Body**:
  ```json
  {
    "username": "John Doe",
    "email": "john@example.com",
    "birthdate": "2007-05-15"
  }
  ```
- **Success Response (201)**:
  ```json
  {
    "success": true,
    "message": "Successfully registered! User ID: 1",
    "user_id": 1
  }
  ```
- **Error Response (400/500)**:
  ```json
  {
    "success": false,
    "error": "Error message describing what went wrong"
  }
  ```

### Get All Users (Testing)
- **Endpoint**: `GET /users`
- **Purpose**: Retrieve all registered users (for testing/debugging)
- **Response**:
  ```json
  {
    "success": true,
    "users": [
      {
        "id": 1,
        "email": "john@example.com",
        "birthdate": "2007-05-15",
        "created_at": "2024-01-15T10:30:00"
      }
    ]
  }
  ```

## Validation Rules

The backend enforces the following validation rules:

### Username
- Must not be empty
- Must be less than 100 characters

### Email
- Must contain the '@' symbol
- Must match standard email format (user@domain.extension)

### Birthdate
- Must be in format `YYYY-MM-DD`
- Must be a date in the past
- Person must be at least 16 years old

## Database Connection

The backend connects to the PostgreSQL database using environment variables:
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)
- `DB_USER`: Database user (default: birthday_user)
- `DB_PASSWORD`: Database password (default: birthday_password)
- `DB_NAME`: Database name (default: birthday_db)

When running in Docker with a network, set `DB_HOST=birthday-app-db` to connect to the database container.

## Network Configuration

If running containers manually, you need to be on the same Docker network. Create a network first:
```bash
docker network create birthday-app-network
```

Then run the backend container with this network:
```bash
docker run -d \
  --name birthday-app-backend \
  --network birthday-app-network \
  -e DB_HOST=birthday-app-db \
  -e DB_PORT=5432 \
  -e DB_USER=birthday_user \
  -e DB_PASSWORD=birthday_password \
  -e DB_NAME=birthday_db \
  -p 5000:5000 \
  birthday-app-backend:latest
```

## Testing the API

### Using curl
```bash
# Health check
curl http://localhost:5000/health

# Submit form
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "username": "John Doe",
    "email": "john@example.com",
    "birthdate": "2007-05-15"
  }'

# Get users
curl http://localhost:5000/users
```

## Logs

To view the container logs:
```bash
docker logs birthday-app-backend
```

## Dependencies

- Flask 2.3.2: Web framework
- Flask-CORS 4.0.0: Cross-Origin Resource Sharing support
- psycopg2-binary 2.9.6: PostgreSQL database adapter
- python-dateutil 2.8.2: Date utilities
