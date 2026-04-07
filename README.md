# RecruitAI - AI-Powered Recruitment Platform

A full-stack recruitment tooling platform built with **Django** (Python) and **React**, featuring AI-driven candidate assessment, ATS/CRM integrations, and comprehensive analytics.

## Architecture

```
backend/                    # Django REST API
  recruitment_platform/     # Project settings & configuration
  candidates/               # Candidate management (CRUD, pipeline stages)
  jobs/                     # Job postings, applications, interviews
  integrations/             # ATS/CRM connector framework (Greenhouse, HubSpot, etc.)
  ai_engine/                # AI services (resume parsing, scoring, LLM features)
  analytics/                # Dashboard & reporting endpoints
  authentication/           # Custom user model, JWT auth, roles
frontend/                   # React SPA
  src/
    api/                    # Axios API client with JWT interceptors
    components/             # Reusable UI components (Layout, etc.)
    context/                # Auth context provider
    pages/                  # Page components (Dashboard, Candidates, Jobs, etc.)
```

## Key Features

### Backend (Django + DRF)
- **Candidate Pipeline** - Full lifecycle management (New -> Screening -> Interview -> Assessment -> Offer -> Hired)
- **Job Management** - Postings with required skills, salary ranges, remote policy
- **Application Tracking** - Status transitions, interview scheduling, feedback
- **AI Engine**
  - Resume parsing (PDF, DOCX, TXT) with skill extraction
  - Candidate-job scoring (skills match, experience, location)
  - LLM-powered summaries, job descriptions, interview questions
  - Automated resume screening
- **Integration Framework**
  - Abstract connector base class for any ATS/CRM
  - Greenhouse ATS connector (with mock data fallback)
  - HubSpot CRM connector (with mock data fallback)
  - Webhook event processing
  - Bidirectional sync with field mapping
- **Analytics** - Dashboard stats, hiring funnel, source distribution, trends
- **Authentication** - Custom User model with roles (Admin, Recruiter, Hiring Manager, Interviewer), JWT tokens

### Frontend (React)
- **Dashboard** - Pipeline overview, charts (Recharts), recent activity
- **Candidate Management** - Search, filter, add, detail view with AI analysis
- **Job Management** - Create with AI-generated descriptions, application tracking
- **AI Tools** - Standalone tools for resume parsing, scoring, question generation
- **Integrations** - Connect and sync external systems
- **Analytics** - Funnel visualization, source distribution, hiring trends

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (for Celery tasks, optional)
- PostgreSQL (optional, SQLite works for development)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings (OPENAI_API_KEY for AI features)

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The React dev server runs at `http://localhost:3000` and proxies API requests to `http://localhost:8000`.

### Docker Setup

```bash
docker-compose up --build
```

This starts all services:
- **Backend** at `http://localhost:8000`
- **Frontend** at `http://localhost:3000`
- **PostgreSQL** at `localhost:5432`
- **Redis** at `localhost:6379`
- **Celery worker** for async tasks

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login/` | JWT login |
| `POST /api/v1/auth/register/` | User registration |
| `GET /api/v1/candidates/` | List candidates (search, filter by stage/source) |
| `POST /api/v1/candidates/{id}/advance_stage/` | Advance candidate pipeline stage |
| `GET /api/v1/jobs/` | List jobs (filter by status/type) |
| `POST /api/v1/jobs/{id}/publish/` | Publish a draft job |
| `GET /api/v1/applications/` | List applications |
| `POST /api/v1/ai/parse-resume/` | AI resume parsing |
| `POST /api/v1/ai/score-candidate/` | Score candidate against job |
| `POST /api/v1/ai/rank-candidates/{job_id}/` | Rank all candidates for a job |
| `POST /api/v1/ai/generate-job-description/` | AI job description generation |
| `POST /api/v1/ai/generate-interview-questions/` | AI interview questions |
| `GET /api/v1/analytics/dashboard/` | Dashboard statistics |
| `GET /api/v1/integrations/` | List integrations |
| `POST /api/v1/integrations/{id}/trigger_sync/` | Trigger data sync |

## Tech Stack

- **Backend**: Python 3.11, Django 4.2, Django REST Framework, SimpleJWT, Celery, Redis
- **Frontend**: React 18, React Router 6, Axios, Recharts, React Hot Toast
- **AI/ML**: OpenAI API (GPT-4), scikit-learn, PyPDF2, python-docx, spaCy
- **Database**: PostgreSQL (production) / SQLite (development)
- **Infrastructure**: Docker, Docker Compose, Gunicorn, WhiteNoise, Nginx

## Integration Architecture

The platform uses an abstract connector pattern for integrations:

```python
class BaseConnector(ABC):
    def test_connection(self) -> dict: ...
    def sync_candidates(self, since=None) -> dict: ...
    def sync_jobs(self, since=None) -> dict: ...
    def push_candidate(self, candidate) -> dict: ...
    def push_application(self, application) -> dict: ...
```

New integrations are added by implementing `BaseConnector` and registering in the connector map. Each integration supports:
- Configurable field mapping between systems
- Bidirectional sync with pagination
- Webhook event processing
- Mock data fallback for development/testing
