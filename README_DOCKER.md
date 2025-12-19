# Docker Deployment Instructions

## Prerequisites
- Docker
- Docker Compose

## Running the Application

1. Build and start the container:
   ```bash
   docker-compose up --build -d
   ```

2. Access the application at `http://localhost:5000`.

3. Admin credentials (created automatically on first run):
   - Username: `admin`
   - Password: `admin`

## Persistence
The SQLite database is stored in a Docker volume `instance_data`. This ensures data persists across container restarts.

## Logs
To view logs:
```bash
docker-compose logs -f
```
