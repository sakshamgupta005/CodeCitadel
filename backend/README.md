# Company Brain Backend

Company Brain is a FastAPI backend for AI-powered organizational memory. It imports GitHub Issues, Pull Requests, Commits, and CSV support tickets, stores them in Moss, retrieves relevant context semantically, and answers questions with cited sources using OpenAI.

## File Tree

```text
backend/
|-- app.py
|-- Dockerfile
|-- requirements.txt
|-- .env.example
|-- models/
|   |-- schemas.py
|-- routes/
|   |-- github.py
|   |-- tickets.py
|   |-- chat.py
|-- services/
|   |-- config.py
|   |-- exceptions.py
|   |-- github_service.py
|   |-- import_tracker.py
|   |-- ticket_service.py
|   |-- moss_service.py
|   |-- llm_service.py
|-- storage/
|   |-- .gitkeep
```

## Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill in `backend/.env`:

```env
MOSS_PROJECT_ID=your_moss_project_id
MOSS_PROJECT_KEY=your_moss_project_key
GITHUB_TOKEN=your_github_token
OPENAI_API_KEY=your_openai_api_key
```

Optional tuning:

```env
MOSS_INDEX_NAME=company-brain
MOSS_MODEL_ID=moss-minilm
MOSS_WAIT_FOR_INDEX_SECONDS=120
MOSS_SEARCH_ALPHA=0.7
GITHUB_MAX_PAGES=3
OPENAI_MODEL=gpt-5.4-mini
MAX_CONTEXT_CHARS=14000
```

## Run Locally

Run from the `backend` directory:

```powershell
python -m uvicorn app:app --reload
```

Open API docs at `http://localhost:8000/docs`.

## Run With Docker

```powershell
cd backend
docker build -t company-brain-backend .
docker run --env-file .env -p 8000:8000 company-brain-backend
```

## API Examples

### Health

```powershell
curl http://localhost:8000/health
```

### Import GitHub Repository

```powershell
curl -X POST http://localhost:8000/github/import `
  -H "Content-Type: application/json" `
  -d "{\"owner\":\"openai\",\"repo\":\"openai-python\"}"
```

### Import Support Tickets

Create `tickets.csv`:

```csv
ticket,resolution
Checkout slow,Added DB index
Payment timeout,Added retries
```

Upload it:

```powershell
curl -X POST http://localhost:8000/tickets/import `
  -F "file=@tickets.csv"
```

### Import Status

```powershell
curl http://localhost:8000/import/status
```

Returns active imports, the latest import, and recent import history for this running process.

### Repository Statistics

```powershell
curl http://localhost:8000/github/stats
```

Returns per-repository document counts from GitHub imports completed during this running process.

### Search Indexed Knowledge

```powershell
curl -X POST http://localhost:8000/search `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"Why is checkout slow?\",\"top_k\":10}"
```

### Ask Company Brain

```powershell
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"Why was checkout rewritten?\",\"top_k\":10}"
```

Example response:

```json
{
  "answer": "Checkout was slow because the support ticket says the resolution was adding a DB index. [Source 1]",
  "sources": [
    {
      "source": "ticket",
      "type": "support_ticket",
      "url": null,
      "id": "ticket:...",
      "citation": "[Source 1]",
      "title": null,
      "repo": null,
      "score": 0.82,
      "snippet": "Support ticket: Checkout slow Resolution: Added DB index"
    }
  ]
}
```

If indexed context does not contain evidence, the model is instructed to return:

```text
I could not find evidence in the indexed company knowledge.
```

## Demo Notes

- GitHub imports are capped by `GITHUB_MAX_PAGES` to keep demos quick.
- Import status and repository stats are in-memory and reset when the server restarts.
- Moss writes are awaited for up to `MOSS_WAIT_FOR_INDEX_SECONDS`; set it to `0` to skip waiting.
- Moss queries attempt to load the index locally for fast retrieval and fall back to Moss cloud query behavior if local loading is unavailable.
