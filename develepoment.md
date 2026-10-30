# Deployment configuration

This file lists the configuration that must be set or reviewed when hosting JanSetu. The filename intentionally matches the requested `develepoment.md` spelling.

## Required production variable

| Variable | Required | Example / value | Why it matters |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | `postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require` | Used by `database.py` to connect SQLAlchemy to the production database. Do not use the local SQLite default in production. |

Use the connection string supplied by the managed PostgreSQL provider (Neon, Supabase, Vercel Postgres, or Render). The application also accepts a legacy `postgres://...` value and automatically converts it to `postgresql://...`.

## Optional variables read by the application

| Variable | When to set it | Production value |
| --- | --- | --- |
| `GEMINI_API_KEY` | For AI Chatbot assistance | API key from Google AI Studio. |
| `GEMINI_MODEL` | To specify Gemini model | Defaults to `gemini-1.5-flash`. |
| `GOOGLE_SPEECH_API_KEY` | For Cloud Speech-to-Text audio uploads | API key with Cloud Speech API enabled. (Browser Web Speech API is used by default). |
| `DIGILOCKER_CLIENT_ID` | Only when replacing prototype DigiLocker integration with real OAuth | Client ID issued for the deployed app. |
| `DIGILOCKER_REDIRECT_URI` | With real DigiLocker OAuth | `https://YOUR-DOMAIN/api/digilocker/callback` — registered with DigiLocker. |

## Variables managed by the hosting platform

| Variable | Action |
| --- | --- |
| `PORT` | Managed automatically by PaaS (Render, Railway, Heroku). |
| `SECRET_KEY` | Set to a random 32-character string in production. |
| `ENV` | Set to `production` in production hosting environments. |

## Vercel setup

1. Push your changes to the `main` branch.
2. In the [Vercel Dashboard](https://vercel.com/dashboard), import the GitHub repository.
3. Vercel automatically detects `vercel.json` and uses `api/index.py` as the serverless function handler.
4. Add `DATABASE_URL` in **Project Settings → Environment Variables** (use a managed PostgreSQL database like Neon or Supabase).
5. Add `GEMINI_API_KEY` and `SECRET_KEY`.
6. Click **Deploy**. Vercel will bundle assets (`templates/**`, `static/**`, `data/**`) and serve the application.
7. Verify by visiting `https://YOUR-DOMAIN/health`.

## Render setup

The checked-in `render.yaml` defines a Python web service and a PostgreSQL database. On Render, the blueprint injects the database connection into `DATABASE_URL` and runs:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Production readiness checklist

- [ ] `DATABASE_URL` targets backed-up PostgreSQL, not SQLite.
- [ ] `GEMINI_API_KEY` configured in hosting environment variables.
- [ ] The service can reach `GET /health`.
- [ ] The deployed domain and any OAuth callback URL use HTTPS.
- [ ] Demo credentials are changed or removed before public launch.
- [ ] Database migrations are introduced before future schema changes.
