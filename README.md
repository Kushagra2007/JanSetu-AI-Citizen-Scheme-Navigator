# JanSetu (जनसेतु) — AI Citizen Scheme & Public Service Navigator

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg?style=flat&logo=python)](https://python.org)
[![Vercel Ready](https://img.shields.io/badge/Vercel-Serverless%20Ready-black.svg?style=flat&logo=vercel)](https://vercel.com)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg?style=flat&logo=google)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**JanSetu** is a modern, citizen-first public service navigation platform designed to bridge the gap between Indian citizens and government welfare schemes. It empowers citizens to discover benefits they qualify for, navigate official documentation pathways, interact with an AI assistant in English and Hindi, and track multi-step applications with transparency.

---

## 🌟 Key Features

- **🎯 Smart Eligibility Scoring**: Multi-factor matching engine evaluating age, annual family income, caste category (SC/ST/OBC/EWS/General), occupation, state/UT, education level, marital status, and disability.
- **🤖 Grounded AI Assistant (Gemini)**: Conversational assistant powered by Google Gemini (`gemini-1.5-flash`), strictly grounded in the official scheme and service catalogue to prevent hallucinations.
- **🎙️ Multilingual Voice Interface**: Real-time voice interaction in English and Hindi (`hi-IN`). Utilizes browser-native Web Speech API for instant, keyless speech-to-text with fallback to Google Cloud Speech-to-Text.
- **📁 DigiLocker Mock Flow**: Built-in document locker simulation allowing one-click verification for Aadhaar, PAN, Passport, Driving License, and Voter ID.
- **📊 Public Service Pathways**: Step-by-step guides, required document checklists, estimated fees, and expected completion timelines for essential citizen services.
- **📱 Progressive Web App (PWA)**: Offline-capable service worker, dark/light theme toggle, and responsive design tailored for low-bandwidth mobile devices.
- **⚡ Vercel Serverless Ready**: Configured with dedicated serverless entry points (`api/index.py`), asset inclusion, and auto-handling of serverless databases.

---

## 🏗️ Architecture & Tech Stack

```
JanSetu/
├── api/                   # Vercel Serverless Function entry point
│   ├── __init__.py
│   └── index.py           # Exports FastAPI app for Vercel
├── api_routes/            # Modular FastAPI routers
│   ├── auth_routes.py     # Session authentication & cookies
│   ├── chat_routes.py     # AI chat & voice transcription
│   ├── scheme_routes.py   # Scheme listing & recommendations
│   ├── service_routes.py  # Service pathways
│   ├── profile_routes.py  # Citizen profile & completeness
│   ├── application_routes.py # Application milestone tracking
│   ├── digilocker_routes.py  # DigiLocker OAuth mock flow
│   └── notification_routes.py# Citizen alerts & deadlines
├── data/                  # Scheme & service catalogue data
├── static/                # CSS, JS, PWA manifest, service worker
├── templates/             # Jinja2 HTML templates
├── tests/                 # Automated pytest suite (47+ tests)
├── ai_assistant.py        # Gemini API integration & context builder
├── nlp_engine.py          # Grounded rule-based intent/entity extraction
├── scoring.py             # Citizen eligibility scoring algorithm
├── database.py            # SQLAlchemy engine (SQLite / PostgreSQL)
├── models.py              # Database models
├── vercel.json            # Vercel deployment & routing configuration
└── requirements.txt       # Production dependencies
```

---

## 🚀 Quickstart: Local Development

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 2. Clone Repository & Setup

#### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/Kushagra2007/JanSetu-AI-Citizen-Scheme-Navigator.git
cd JanSetu-AI-Citizen-Scheme-Navigator

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start development server
uvicorn main:app --reload
```

> **Note for PowerShell execution policy:** If script activation is restricted, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

#### Windows (Command Prompt - CMD)
```cmd
git clone https://github.com/Kushagra2007/JanSetu-AI-Citizen-Scheme-Navigator.git
cd JanSetu-AI-Citizen-Scheme-Navigator
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```

#### macOS / Linux
```bash
git clone https://github.com/Kushagra2007/JanSetu-AI-Citizen-Scheme-Navigator.git
cd JanSetu-AI-Citizen-Scheme-Navigator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```

Open your browser at **`http://127.0.0.1:8000`**.

### 3. Demo Credentials
The local database automatically initializes with a seed demo account:
- **Email:** `demo@jansetu.in`
- **Password:** `demo123`

You can also click **Register** to create a custom profile.

---

## ⚙️ Environment Configuration

Create a `.env` file in the project root to configure secrets (see `.env.example`):

| Variable | Required in Dev | Required in Prod | Description | Default / Example |
| :--- | :---: | :---: | :--- | :--- |
| `DATABASE_URL` | No | **Yes** | Connection string for database | `sqlite:///./citizen_navigator.db` (local) |
| `GEMINI_API_KEY` | Optional | Optional | Google Gemini API key for AI assistant | Get free key at [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_MODEL` | No | No | Gemini model name | `gemini-1.5-flash` |
| `GOOGLE_SPEECH_API_KEY`| No | No | Cloud Speech-to-Text key for audio uploads | If omitted, browser native Web Speech API is used |
| `SECRET_KEY` | No | Recommended | Session token secret | `change-this-in-production` |
| `DIGILOCKER_CLIENT_ID` | No | No | DigiLocker Client ID (when using real OAuth) | `mock-client-id` |
| `DIGILOCKER_REDIRECT_URI`| No | No | DigiLocker callback URI | `http://localhost:8000/api/digilocker/callback` |

---

## ☁️ Deployment Instructions

### Option A: Deploy to Vercel (Recommended)

JanSetu includes native Vercel configuration (`vercel.json`, `api/index.py`, and `.vercelignore`).

#### Step 1: Provision a Free PostgreSQL Database
Because Vercel serverless functions have a read-only, ephemeral filesystem, configure a managed cloud PostgreSQL database:
1. Create a free account at [Neon](https://neon.tech), [Supabase](https://supabase.com), or [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres).
2. Create a new database project and copy the connection string:
   ```
   postgresql://user:password@ep-sample.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

#### Step 2: Deploy via Vercel Dashboard (GitHub Import)
1. Push your repository to GitHub on the `main` branch:
   ```bash
   git push origin main
   ```
2. Log in to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New...** → **Project**.
3. Select your repository `JanSetu-AI-Citizen-Scheme-Navigator` and click **Import**.
4. In **Project Settings**:
   - **Framework Preset**: Select `Other` (or leave default).
   - **Root Directory**: `./` (leave default).
   - **Build Command**: Leave empty (handled by Vercel Python runtime).
   - **Output Directory**: Leave empty.
5. In **Environment Variables**, add:
   - `DATABASE_URL`: Your PostgreSQL connection string from Step 1.
   - `GEMINI_API_KEY`: Your Gemini API key from [Google AI Studio](https://aistudio.google.com/).
   - `SECRET_KEY`: A random 32-character secure string.
6. Click **Deploy**.
7. Once deployed, verify your application at `https://<your-project>.vercel.app/health`.

#### Step 3: Deploy via Vercel CLI (Alternative)
You can also deploy directly from your terminal:
```bash
# Install Vercel CLI globally
npm install -g vercel

# Log in to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production with environment variables
vercel --prod
```

> **How Vercel handles database & seed data:**
> When deployed to Vercel, SQLAlchemy tables and initial scheme/service catalogue data are automatically verified on cold starts via FastAPI's lifespan lifecycle. When connected to PostgreSQL, all users, saved applications, and chat histories persist permanently. If deployed without `DATABASE_URL`, JanSetu safely falls back to `/tmp/citizen_navigator.db` to prevent read-only filesystem errors.

---

### Option B: Deploy to Render

The repository includes `render.yaml` for automatic deployment with managed PostgreSQL:

1. Create a [Render](https://render.com) account.
2. Go to **Blueprints** and connect your GitHub repository.
3. Render automatically provisions:
   - A Python Web Service running `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - A managed PostgreSQL database linked via `DATABASE_URL`
4. Add `GEMINI_API_KEY` under Environment Variables in the Render dashboard.

---

### Option C: Deploy with Docker / Self-Hosted VPS

Create a `Dockerfile` (or run directly with Uvicorn):
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t jansetu .
docker run -p 8000:8000 -e DATABASE_URL="postgresql://user:pass@host/db" jansetu
```

---

## 🧪 Testing

The repository includes a comprehensive test suite covering API endpoints, auth, DigiLocker simulation, eligibility scoring, NLP entity extraction, and Gemini AI assistant integration:

```bash
# Run all tests with pytest
pytest -v

# Run with coverage or quiet mode
pytest -q
```

All 47 tests run in under 1 second without external network dependencies.

---

## 🔒 Security Best Practices

- **Zero Document Leakage in Chat**: The prompt design strictly forbids citizens from submitting sensitive Aadhaar, PAN, bank account, or OTP credentials inside chat.
- **SameSite / HttpOnly Cookies**: Auth tokens are stored in secure `HttpOnly`, `SameSite=Lax` browser cookies.
- **Ephemeral Sandbox Fallback**: Safe defaults prevent runtime crashes when running on serverless lambda platforms.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
