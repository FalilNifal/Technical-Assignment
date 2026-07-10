# Technical Assignment

PulseBoard is a secure role-based weekly reporting platform that standardizes team updates and converts them into manager-level insights, with optional AI-generated summaries for faster decision-making.

## Demo accounts

- Admin: `admin@pulseboard.com` / `Password123!`
- Manager: `manager@pulseboard.com` / `Password123!`
- Team member: `nethmi@pulseboard.com` / `Password123!`

## Demo roles

- `ADMIN`: Can manage users, roles, projects, and settings.
- `MANAGER`: Can view and analyze team reports.
- `TEAM_MEMBER`: Can create and manage their own weekly reports.

## Database setup

Use a local PostgreSQL database.

Create the database in pgAdmin or psql:

```sql
CREATE DATABASE pulseboard_db;
```

Configure `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/pulseboard_db
JWT_SECRET=replace_with_a_strong_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI features (chat assistant + team insights) are powered by Groq.
# Leave GROQ_API_KEY blank to run the app in a graceful "AI not configured" fallback mode.
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
```

Replace `YOUR_POSTGRES_PASSWORD` with your local PostgreSQL `postgres` user password. A free Groq API key can be created at https://console.groq.com.

## Run backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

In another backend terminal, seed demo data:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.db.seed
```

Open the API docs:

```text
http://localhost:8000/docs
```

## Run tests

From the `backend` folder (with the virtualenv active and PostgreSQL running):

```bash
python -m pytest
```

The tests spin up an isolated `pulseboard_db_test` database automatically and roll
back after each test, so they never touch your development data.

## Run frontend

```bash
cd frontend
npm install
cp .env.example .env   # sets VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev
```

Open the app:

```text
http://localhost:5173
```
