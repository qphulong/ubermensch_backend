# Übermensch backend

## Prerequisites

- Python 3.12.3 (recommended)
- Docker (required for database)
- Docker Compose (required for database)

## Getting Started

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

### 3. Run the Application (Optional Development Mode)
```bash
uvicorn main:app --reload
```

### 4. Access the Database (Optional)
```bash
docker exec -it postgres_container_db_1 psql -U user -d app_db
```
