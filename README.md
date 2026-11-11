# Gyul Days

**A private journaling and personal routine tracking platform.**

Gyul Days is a full-stack web application for recording daily experiences, organizing journal entries, and tracking personal routines.

## Features

- **Journal Management:** Create, edit, search, and organize journal entries.
- **Spaces and Tags:** Organize entries using spaces, memberships, and tags.
- **AI-assisted Organization:** Generate tag suggestions and analyze journal entries using the OpenAI API.
- **Private Image Storage:** Upload and retrieve journal images through Supabase Storage.
- **Sleep Tracking:** Record and manage sleep sessions.
- **Daily Check-ins:** Track daily energy, focus, mood, stress, and overall condition.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL, SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT, Argon2 |
| Storage | Supabase Storage |
| AI | OpenAI API |

## Architecture

```text
Next.js Frontend
       |
       | HTTP / JWT
       v
FastAPI Backend
       |
       +------ PostgreSQL
       |
       +------ Supabase Storage
       |
       +------ OpenAI API
```

## Local Development

### Prerequisites

- Python
- Node.js and npm
- PostgreSQL
- Supabase project
- OpenAI API key

### Backend

```bash
cd backend

# Install Python dependencies
uv sync

# Configure environment variables
cp .env.example .env

# Apply database migrations
uv run alembic upgrade head

# Start the development server
uv run uvicorn app.main:app --reload
```

### Frontend

In a separate terminal:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local

# Start the development server
npm run dev
```

The frontend development server and backend API must both be running.

## Environment Variables

See the following example files for the required environment variable names:

- `backend/.env.example`
- `frontend/.env.example`

Add your own credentials locally. Never commit actual API keys, database credentials, or secret keys.

## Privacy and Security

Gyul Days is designed for private personal records. Journal entries and personal tracking data should not be included in this public repository.

Environment files containing credentials are excluded from version control. Keep Supabase service-role or secret keys, database credentials, and OpenAI API keys private.

## Planned Work

- Integration with Apple Health and other activity data sources
- Longitudinal routine and habit analytics
- Personalized insights based on historical records

These are planned features and are not yet implemented.