# JanSetu project context for AI assistants

## Purpose

JanSetu (Citizen Service Navigator) is a server-rendered FastAPI web application for Indian citizens. It helps a signed-in user build a profile, receive eligibility-ranked government-scheme recommendations, explore service pathways, track applications, chat with a rule-based assistant, manage document status, and use a prototype DigiLocker connection.

Treat this as a Python web application, not a separate SPA/API deployment: the FastAPI process serves both HTML pages and `/api/*` endpoints.

## Technology stack

| Area | Technology |
| --- | --- |
| Backend | Python 3.10+, FastAPI, Uvicorn |
| HTML rendering | Jinja2 templates |
| Data layer | SQLAlchemy 2 ORM |
| Database | SQLite by default; PostgreSQL supported via `DATABASE_URL` |
| Validation | Pydantic v2 / `EmailStr` |
| Front end | Vanilla JavaScript, CSS, browser Web Speech APIs, service worker |
| Tests | Pytest and FastAPI `TestClient`/HTTPX |
| Deployment files | `Procfile` and `render.yaml` |

## Runtime architecture

```text
Browser
  ├─ HTML routes in main.py ──> Jinja2 templates/
  ├─ static JS/CSS ───────────> static/
  └─ fetch('/api/...') ───────> api_routes/
                                      ├─ auth.py cookie dependency
                                      ├─ SQLAlchemy models.py
                                      ├─ database.py engine/session
                                      ├─ data/ seed catalogues
                                      ├─ scoring.py eligibility logic
                                      └─ nlp_engine.py rule-based chat
```

Authentication uses an HTTP-only `csn_token` cookie. The token is stored on the `users` row and must be present for protected routes. Most pages redirect anonymous visitors to `/login`; API endpoints use `get_current_user` and return 401 when unauthenticated.

At application import, `main.py` creates database tables. At startup it creates the demo account and seeds schemes/services if their tables are empty. The demo credentials are `demo@jansetu.in` / `demo123`; do not use these as production credentials.

## Repository structure and file guide

```text
.
├── main.py                  FastAPI entry point, startup seed, page routes, health check
├── database.py              Loads .env, reads DATABASE_URL, creates SQLAlchemy engine/session/Base
├── models.py                SQLAlchemy entities and relationships
├── schemas.py               Pydantic request models for API validation
├── auth.py                  Password hashing, token generation, current-user dependencies
├── scoring.py               Profile-completeness and scheme-eligibility scoring
├── nlp_engine.py            Rule-based English/Hindi intent/entity extraction and chat responses
├── notifications.py         Helpers that create in-app notifications
├── requirements.txt         Pinned Python dependencies
├── Procfile                 Generic process command for platforms that support Procfiles
├── render.yaml              Render web-service and PostgreSQL blueprint
├── api_routes/              Modular JSON API routers
├── data/                    Built-in scheme/service catalogues and idempotent seed helper
├── templates/               Jinja HTML pages and shared base layout
├── static/                  CSS, browser JavaScript, PWA manifest, and service worker
├── tests/                   Pytest coverage for authentication, APIs, NLP, and scoring
└── scripts/                 Scripts for publishing the repository to a new GitHub remote
```

### Backend files

| File/directory | Responsibility |
| --- | --- |
| `main.py` | Creates `app`, mounts `/static`, includes every API router, renders pages, exposes `GET /health`. |
| `database.py` | Calls `load_dotenv()`. Converts legacy `postgres://` URLs to `postgresql://`; uses SQLite `check_same_thread=False`. |
| `models.py` | Defines `User`, `Profile`, `Document`, `Scheme`, `Service`, `Application`, `Notification`, and `ChatMessage`. Some list-like fields are JSON strings in `Text` columns. |
| `schemas.py` | Defines request bodies: registration/login, profile/document updates, chat messages, application creation/status/step, and push subscriptions. |
| `auth.py` | Uses a static SHA-256 salt and database-backed tokens. This is prototype authentication; replace it with a password-hashing algorithm and secret-backed session strategy before a real public launch. |
| `scoring.py` | Computes profile completeness and recommendation totals: eligibility, required-document availability, and profile completeness. |
| `nlp_engine.py` | Implements the local rule-based chat assistant. It does not call an external AI model or require an API key. |
| `notifications.py` | Builds notification rows for changes such as application-status updates. |
| `data/schemes_data.py` | Source-of-truth list of scheme dictionaries used when seeding `Scheme`. |
| `data/services_data.py` | Source-of-truth list of service dictionaries and step data used when seeding `Service`. |
| `data/seed.py` | Idempotently seeds reference data; route modules call it so catalog data is available even outside the normal startup path. |

### API router guide

| Router | Prefix | Main responsibility |
| --- | --- | --- |
| `auth_routes.py` | `/api/auth` | Register, login, logout, and current-user info. |
| `profile_routes.py` | `/api/profile` | Read/update profile, update document checklist, get completeness. |
| `chat_routes.py` | `/api/chat` | Persist chat messages, process rule-based replies, extract profile data, manage chat sessions/history. |
| `scheme_routes.py` | `/api/schemes` | List/detail schemes, personalized recommendations, scoring, save/unsave schemes. |
| `service_routes.py` | `/api/services` | List services, service detail, and pathway steps. |
| `application_routes.py` | `/api/applications` | Create/read/update/delete scheme/service application trackers and progress. |
| `notification_routes.py` | `/api/notifications` | List/read/delete in-app notifications; push subscription endpoint is a mock. |
| `digilocker_routes.py` | `/api/digilocker` | Prototype connection, callback, document refresh, and disconnect. It currently uses a local mock OAuth flow. |

### Front-end guide

`templates/base.html` provides shared navigation and shared JavaScript. The individual templates map to pages: `index.html`, `login.html`, `register.html`, `chat.html`, `profile.html`, `schemes.html`, `service.html`, `applications.html`, `notifications.html`, and `settings.html`.

`static/js/auth.js` provides `apiFetch`, attaches the auth forms, handles 401 redirects, and registers the service worker. The remaining page scripts (`chat.js`, `profile.js`, `schemes.js`, `service.js`, `applications.js`, `notifications.js`, `settings.js`) fetch their matching API. `theme.js` stores the selected theme in `localStorage`; `voice.js` wraps browser speech recognition/synthesis. `static/css/style.css` contains the shared visual system. `static/manifest.json` and `static/service-worker.js` provide basic PWA support.

## User-facing flows

1. A visitor registers or logs in; the browser receives the `csn_token` cookie.
2. The user fills in profile attributes and document availability. The profile completeness score updates.
3. Scheme recommendations compare profile and documents with the seeded rules and show match scores.
4. The user can save a scheme or create an application tracker for a scheme/service, mark steps, and receive in-app status notifications.
5. Chat accepts English/Hindi-style messages, extracts profile entities where possible, persists both messages, and returns a rule-based answer.
6. The settings screen offers a mock DigiLocker flow that marks mock documents as verified.

## Important constraints for future changes

- Preserve the relative `static/` and `templates/` directories unless `main.py` mounting/template paths are updated too.
- Preserve cookie-based authentication conventions in browser calls: `apiFetch` includes `credentials: 'include'`.
- Call `ensure_reference_data(db)` in new routes that need the catalogue but may run before startup seeding.
- Seed data only fills empty tables; modifying source catalogue lists does not update records in an already populated database.
- SQLite is suitable for local development only. A serverless filesystem is ephemeral and cannot safely retain it.
- The database schema is created with `Base.metadata.create_all`; there is no migration system. Add migrations before evolving a production schema.
- `SECRET_KEY` and `ENV` appear in `render.yaml` but the present Python code does not read them. `DIGILOCKER_CLIENT_ID` and `DIGILOCKER_REDIRECT_URI` are read, but the existing route remains mock-only.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
pytest -q
```

The local URL is `http://127.0.0.1:8000`; `GET /health` is the simple health check.
