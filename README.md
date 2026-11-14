# Crypto Charts

A full-stack cryptocurrency market dashboard.

**Development environment:** Arch Linux  
**Backend:** Python 3.14.8, FastAPI  
**Database:** PostgreSQL  
**Frontend:** React 19, TypeScript, Vite  
**Package management:** Poetry (backend), npm (frontend)

## Project structure

The project is maintained as three separate repositories:

| Component | Local directory | Repository |
|---|---|---|
| FastAPI backend | `~/projects/crypto-charts-backend` | `crypto-charts-backend` |
| React frontend | `~/projects/crypto-charts-react` | `crypto-charts-react` |
| Previous Svelte frontend | `~/projects/crypto-charts-svelte` | `crypto-charts-svelte` |

React is the current frontend. The Svelte project is retained as a previous implementation and reference.

## Backend setup

### Requirements

- Python 3.14.8
- Poetry 2.5.1
- PostgreSQL
- FastAPI
- SQLAlchemy
- asyncpg
- Alembic
- python-dotenv

There is no Rust requirement.

### Install dependencies

From the backend repository:

```bash
cd ~/projects/crypto-charts-backend
poetry install
```

### Database

Local development uses PostgreSQL:

- Database: `crypto_charts_dev`
- User: `ilya`
- Host: `127.0.0.1`
- Port: `5432`
- Driver: `asyncpg`

The connection string is configured in the backend `.env` file.

Do not commit `.env` or database credentials.

### Run database migrations

```bash
cd ~/projects/crypto-charts-backend
poetry run alembic upgrade head
```

Current migration head: `d6649b209e08`.

### Start the backend

```bash
cd ~/projects/crypto-charts-backend
poetry run uvicorn backend.main:app --reload --host 127.0.0.1 --port 9000
```

The backend listens on:

`http://127.0.0.1:9000`

Stop the server with Ctrl+C.

## React frontend setup

### Install dependencies

```bash
cd ~/projects/crypto-charts-react
npm install
```

### Available commands

Start the development server:

```bash
npm run dev
```

Run TypeScript compilation and production build:

```bash
npm run build
```

Run lint checks:

```bash
npm run lint
```

Preview the production build:

```bash
npm run preview
```

Vite normally serves the development frontend at:

`http://localhost:5173`

## Running the application locally

Use two terminals.

**Terminal 1 — Backend**

```bash
cd ~/projects/crypto-charts-backend
poetry run uvicorn backend.main:app --reload --host 127.0.0.1 --port 9000
```

**Terminal 2 — React frontend**

```bash
cd ~/projects/crypto-charts-react
npm run dev
```

React communicates with FastAPI over HTTP. The backend connects to PostgreSQL; the browser does not connect directly to the database.

## Application architecture

- **FastAPI:** Server-side API, authentication, and application logic.
- **PostgreSQL:** Persistent application data.
- **SQLAlchemy:** Database access.
- **Alembic:** Database schema migrations.
- **React:** User interface and application state.
- **TypeScript:** Frontend types and compile-time checking.
- **Vite:** Frontend development server and production build.
- **Oxlint:** Frontend linting.

Frontend HTTP request functions belong in the frontend service layer. They communicate with the FastAPI backend; they are not a second server API.

## Git repositories

Each component has its own Git repository. Run Git commands from the corresponding project directory.

Keep secrets, local environments, build artifacts, and dependency directories out of Git.

## Previous deployment environment — historical notes

The former FreeBSD VPS at `skyebeau.com` is no longer active.

The following are retained only as historical information:

- FreeBSD
- Nginx
- Supervisor
- Gunicorn with Uvicorn workers
- Remote PostgreSQL
- SSH database tunnels
- Previous deployment directories and service configurations

A new VPS and production deployment configuration will be established separately. Do not use the old server addresses, database credentials, paths, or deployment commands as current instructions.