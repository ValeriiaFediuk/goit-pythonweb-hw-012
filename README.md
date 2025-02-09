# FastAPI App with PostgreSQL, Redis (Koyeb, Docker & Local Setup)

### Main Features Added in v12:
- Sphinx documentation
- Unit tests for repositories
- Integration tests for routes
- Redis cache
- Reset password flow
- Role system (user, admin)
- Refresh token


## Prerequisites
To run the app, you need:
- Python 3.12+
- Poetry (for dependency management)
- Docker & Docker Compose (for running PostgreSQL)

## Setup & Running the App

### 1. Clone the Repository
```bash
git clone https://github.com/goit-pythonweb-hw-12.git
cd goit-pythonweb-hw-12
```

### 2. Install Dependencies
Run the following command to install the necessary dependencies:
```bash
poetry install
```

### 3. Setup the Environment Variables
Copy the `.env.example` file and rename it to `.env`:
```bash
cp .env.example .env
```
Then, edit the `.env` file and set the correct database credentials.

### 4. Run Full App with Docker (Backend + DB)
To run the app with Docker, including both the backend and PostgreSQL DB, run:
```bash
docker-compose up --build -d
```

### 5. Run Migrations
To apply database migrations, run:
```bash
docker-compose exec backend poetry run alembic upgrade head
```

### 6. Stop Docker Services
To stop the Docker services, run:
```bash
docker-compose down
```

### 7. Run PostgreSQL in Docker (Without the App)
If you want to run only PostgreSQL in Docker, use the following command:
```bash
docker run --name my_local_postgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mylocaldb -p 5432:5432 -d postgres:15
```

### 8. Running the App (Without Docker)
If you prefer to run the app locally without Docker:

#### 8.1. Start PostgreSQL Locally
Ensure PostgreSQL is running locally, and update your `.env` file with the following:
```env
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/mylocaldb
```

#### 8.2. Apply Database Migrations
Run the following command to apply database migrations:
```bash
USE_LOCAL_DB=true poetry run alembic upgrade head
```

#### 8.3. Run the FastAPI App
To run the FastAPI app locally:
```bash
USE_LOCAL_DB=true poetry run uvicorn main:app --reload
```
