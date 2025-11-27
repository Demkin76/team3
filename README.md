# GitHub Doppelgänger Hunter Backend (MVP)

## Pipeline
1. User submits a GitHub profile URL.
2. Agent 1 collects repos + code files, computes fingerprints and distinctive lines.
3. Agent 2 checks if an identical fingerprint set exists in cache.
4. Agent 3 searches public GitHub repositories for matches.
   - For each found candidate file, Agent 3 downloads it and verifies a 1:1 fingerprint match.
   - Only exact matches count.
5. Results are stored and returned via API.

## Repo copy labels
- similarity_percent = matched_files / total_profile_files * 100
- Labels:
  - partial < REPO_STRONG_THRESHOLD
  - strong >= REPO_STRONG_THRESHOLD (default 60%)
  - copy >= REPO_COPY_THRESHOLD (default 80%)
Thresholds configurable in .env.

## Quick start
```bash
cd backend
cp .env.example .env
docker compose up -d postgres redis
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## API
POST /api/submit
```json
{ "input_type": "url", "input_value": "https://github.com/<username>" }
```

GET /api/request/{id}

GET /api/request/{id}/stream  (SSE progress)
