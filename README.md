# Übermensch backend

## Prerequisites

- Python 3.12.3 (recommended)
- Docker (required for database)
- Docker Compose (required for database)

## Getting Started (http://xx.xx.xx.xx)

### 1. Set up Python Environment (Recommended)

We recommend using Python 3.12.3 and creating a virtual environment:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Database Container (Required)
```bash
cd postgres_container/
docker-compose up -d
```
To install pgvector in container (run once)
```bash
docker build -t custom-postgres-pgvector:15 -f Dockerfile.postgres .
```

### 3. Run the Application (Optional - Development Mode)
```bash
uvicorn main:app --reload
```

### 4. Run the Application (Must - Deploy Mode)
```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
```

### 5. Access the Database (Optional)
```bash
docker exec -it postgres_container_db_1 psql -U user -d app_db
```

### 6. The .env file should look like
```.env
SECRET_KEY=
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/app_db

ADMIN_USERNAME=
ADMIN_PASSWORD=
ADMIN_EMAIL=
ADMIN_GMAIL_APP_PASSWORD=
ADMIN_GIT_LINK=

OPENAI_API_KEY=

REDIS_HOST=localhost
REDIS_PORT=6379

CLOUDFLARE_TUNNEL_UUID = 
```
Contact the owner to get the key if you are local dev-ing

## Deploy with https

### 1. Start it
# start uvicorn
```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 & echo $! > uvicorn.pid

nohup cloudflared tunnel --config ~/.cloudflared/config.yml run <CLOUDFLARE_TUNNEL_UUID> > cloudflared.log 2>&1 & echo $! > cloudflared.pid
```

### 2. Stop it
```bash
pkill -f "uvicorn main:app"
pkill -f "cloudflared.*<CLOUDFLARE_TUNNEL_UUID>"
```