# Deployment configuration

This file lists the configuration that must be set or reviewed when hosting JanSetu. The filename intentionally matches the requested `develepoment.md` spelling.

## Required production variable

| Variable | Required | Example / value | Why it matters |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | `postgresql://USER:PASSWORD@HOST:5432/DBNAME` | Used by `database.py` to connect SQLAlchemy to the production database. Do not use the local SQLite default in production. |

Use the connection string supplied by the managed PostgreSQL provider. The application also accepts a legacy `postgres://...` value and converts it to `postgresql://...`, although using the latter directly is preferred. URL-encode reserved characters in a password.

## Optional variables read by the application

| Variable | When to set it | Production value |
| --- | --- | --- |
| `DIGILOCKER_CLIENT_ID` | Only when replacing the prototype DigiLocker integration with real OAuth | Client ID issued for the deployed app. |
| `DIGILOCKER_REDIRECT_URI` | With real DigiLocker OAuth | `https://YOUR-DOMAIN/api/digilocker/callback` — this exact URL must also be registered with DigiLocker. |

The existing DigiLocker implementation is a mock: its `/connect` endpoint returns a local callback URL and does not use `DIGILOCKER_CLIENT_ID` or `DIGILOCKER_REDIRECT_URI` to make an external OAuth request. Setting these variables alone does not enable real DigiLocker integration.

## Variables managed by the hosting platform

| Variable | Action |
| --- | --- |
| `PORT` | Do not set it manually unless your platform requires it. The server command must bind to the platform-provided value: `uvicorn main:app --host 0.0.0.0 --port $PORT`. |
| `SECRET_KEY` | `render.yaml` generates this, but the current Python code does not read it. Keep it secret if configured; it has no effect until application authentication/session code is changed to use it. |
| `ENV` | `render.yaml` sets it to `production`, but current Python code does not read it. It is informational unless code is added that uses it. |

## Vercel setup

1. Import the GitHub repository in Vercel.
2. Configure the project as a Python application with entry point `main.py` / ASGI app `main:app` (Vercel may create its own Python serverless wrapper/configuration).
3. Add `DATABASE_URL` in **Project Settings → Environment Variables** for Production, Preview as needed, and Development if required.
4. Provision a managed PostgreSQL database (for example Vercel Postgres/Neon/Supabase or another provider) and paste its SQLAlchemy-compatible PostgreSQL URL.
5. If real DigiLocker OAuth is implemented, add `DIGILOCKER_CLIENT_ID` and set `DIGILOCKER_REDIRECT_URI` to the deployed Vercel URL, then register the exact callback with DigiLocker.
6. Deploy and check `https://YOUR-DOMAIN/health`.

Vercel functions have an ephemeral filesystem. The default value `sqlite:///./citizen_navigator.db` is therefore unsuitable: data may disappear between invocations and instances cannot share it. Always configure PostgreSQL on Vercel. The startup seeding code can execute on cold starts, but it only inserts reference data when the relevant tables are empty.

## Render setup

The checked-in `render.yaml` already defines a Python web service and a PostgreSQL database. On Render, the blueprint injects the database connection into `DATABASE_URL` and runs:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Review the service/database plan names and region before creating the blueprint. If deploying without the blueprint, set the same build/start commands and provide `DATABASE_URL` manually.

## Other platforms

For Railway, Fly.io, Heroku-like PaaS providers, or a container host:

- Install dependencies using `pip install -r requirements.txt`.
- Start with `uvicorn main:app --host 0.0.0.0 --port $PORT` (adapt the port syntax if the platform differs).
- Attach PostgreSQL and set its connection string as `DATABASE_URL`.
- Serve the app from the repository root, because `main.py` resolves `templates/` and `static/` relative to the working directory.
- Configure HTTPS on the platform/domain. The current cookies are `HttpOnly` and `SameSite=Lax`; when changing cookie settings for a real production system, enable `Secure` over HTTPS.

## Production readiness checklist

- [ ] `DATABASE_URL` targets backed-up PostgreSQL, not SQLite.
- [ ] The service can reach `GET /health`.
- [ ] The deployed domain and any OAuth callback URL use HTTPS.
- [ ] Real DigiLocker credentials/callback are configured only after real OAuth code replaces the mock.
- [ ] Demo credentials are removed or changed before public launch.
- [ ] `auth.py` is upgraded from static salted SHA-256 to a modern password-hashing algorithm and a secret-backed session/auth design.
- [ ] Database migrations are introduced before schema changes; `create_all` does not migrate existing tables.
- [ ] Any future cross-origin frontend deployment has explicit CORS configuration and compatible cookie settings.
