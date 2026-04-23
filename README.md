# Quorum

Quorum is a multi-tenant platform for student-body operations: dues tracking, events, meetings, fundraising campaigns, smart links, and public portal pages.

## Simple Repo Structure

- `app` - FastAPI API package (deploy to Render)
- `requirements.txt` - backend dependencies
- `.env.example` - backend environment template
- `frontend` - Next.js app (deploy to Vercel)
- `docs` - architecture and implementation specs

## Backend (Render)

### Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Render setup

1. Create a new Web Service from this repo.
2. Root directory: repository root
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables from `.env.example`

The backend uses MongoDB. Set this in your local `.env` and in Render:

```text
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE_PREFIX=
```

To migrate an existing local SQLite database into MongoDB, run:

```bash
python scripts/migrate_sqlite_to_mongodb.py --sqlite quorum.db --replace
```

To move data from the original single MongoDB database into the segmented MongoDB layout, run:

```bash
python scripts/migrate_mongodb_to_segmented.py --source-db quorum --replace
```

## Frontend (Vercel)

### Local run

```bash
cd frontend
npm install
npm run dev
```

### Vercel setup

1. Import this repo.
2. Root directory: `frontend`
3. Framework preset: Next.js
4. Set `NEXT_PUBLIC_API_BASE_URL` to your Render backend URL + `/api/v1`

Example:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-api.onrender.com/api/v1
```

## Database

MongoDB is now the application database. The API keeps integer `id` fields for compatibility with the existing frontend while storing data in segmented databases:

- `communities`: `workspaces`, `members`
- `identity`: `users`, `roles`, `workspace_members`, `invitations`, `invite_links`
- `finance`: `dues_cycles`, `dues_payments`, `campaigns`, `funding_streams`, `contributions`
- `engagement`: `events`, `announcements`, `short_links`
- `platform`: `counters`

## Current Working Endpoints (MVP scaffold)

Base prefix: `/api/v1`

- `GET /health`
- `POST /workspaces`, `GET /workspaces`, `GET /workspaces/{id}`, `GET /workspaces/slug/{slug}`
- `POST/GET /workspaces/{workspace_id}/members`
- `POST/GET /workspaces/{workspace_id}/dues-cycles`
- `POST/GET /workspaces/{workspace_id}/events`
- `POST/GET /workspaces/{workspace_id}/campaigns`
- `POST/GET /workspaces/{workspace_id}/links`
- `GET /public/e/{event_slug}`
- `GET /public/donate/{campaign_slug}`
- `GET /public/portal/{workspace_slug}`
- `GET /public/r/{slug}`

## Frontend Routes (MVP scaffold)

- `/`
- `/login`
- `/register`
- `/{workspaceSlug}/dashboard`
- `/{workspaceSlug}/events`
- `/{workspaceSlug}/events/new`
- `/{workspaceSlug}/dues`
- `/{workspaceSlug}/campaigns`
- `/{workspaceSlug}/links`
- `/e/{eventSlug}`
- `/donate/{campaignSlug}`
- `/portal/{workspaceSlug}`
- `/r/{slug}`
