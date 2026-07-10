# PulseBoard Backend

FastAPI backend for authentication and protected role-based routes.

## Environment

Create `.env` from `.env.example` and do not commit real secrets.

## Run

```bash
pip install -r requirements.txt
python -m app.db.seed
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

## Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/protected/member`
- `GET /api/v1/protected/manager`
- `GET /api/v1/protected/admin`
