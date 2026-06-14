# Moss Product Support Platform Backend

FastAPI backend for a hackathon-ready product support platform. It stores products locally, indexes product documentation into Moss, searches indexed knowledge, answers support questions with Gemini, and runs diagnostic sessions that narrow probable causes over follow-up answers.

## What It Includes

- Product CRUD with local JSON storage
- Sample products in `storage/products.json`
- PDF, text, and URL knowledge ingestion by `product_id`
- Moss indexing and semantic search
- Gemini chat and diagnostic generation
- Diagnostic session state in `storage/diagnostic_sessions.json`
- Health check and OpenAPI docs

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
GEMINI_API_KEY=your_gemini_api_key
```

Run locally:

```powershell
python -m uvicorn app:app --reload
```

OpenAPI docs are available at `http://localhost:8000/docs`.

## API Examples

Health:

```powershell
curl http://localhost:8000/health
```

List sample products:

```powershell
curl http://localhost:8000/products
```

Create a product:

```powershell
curl -X POST http://localhost:8000/products `
  -H "Content-Type: application/json" `
  -d "{\"id\":\"moss-router-pro\",\"name\":\"Moss Router Pro\",\"category\":\"Networking\",\"description\":\"Tri-band support router.\",\"image_url\":\"https://example.com/router.png\"}"
```

Search products by name or category:

```powershell
curl "http://localhost:8000/products?query=router"
curl "http://localhost:8000/products?category=Networking"
```

Upload product PDF knowledge:

```powershell
curl -X POST http://localhost:8000/products/moss-router-x1/knowledge/pdf `
  -F "file=@manual.pdf"
```

Upload product text knowledge:

```powershell
curl -X POST http://localhost:8000/products/moss-router-x1/knowledge/text `
  -F "title=Reset guide" `
  -F "text=Hold the reset button for 10 seconds, then wait for the status light to pulse blue."
```

Upload product URL knowledge:

```powershell
curl -X POST http://localhost:8000/products/moss-router-x1/knowledge/url `
  -H "Content-Type: application/json" `
  -d "{\"url\":\"https://example.com/router-troubleshooting\",\"title\":\"Router troubleshooting\"}"
```

Search Moss knowledge:

```powershell
curl -X POST http://localhost:8000/search `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"router keeps dropping wifi\",\"top_k\":10}"
```

Chat over indexed knowledge:

```powershell
curl -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{\"query\":\"How do I reset the Moss Router X1?\",\"top_k\":8}"
```

Start a diagnostic session:

```powershell
curl -X POST http://localhost:8000/products/moss-router-x1/diagnose `
  -H "Content-Type: application/json" `
  -d "{\"issue_description\":\"The router powers on but drops Wi-Fi every few minutes.\"}"
```

Continue a diagnostic session:

```powershell
curl -X POST http://localhost:8000/products/moss-router-x1/diagnose `
  -H "Content-Type: application/json" `
  -d "{\"session_id\":\"SESSION_ID_FROM_PREVIOUS_RESPONSE\",\"answer\":\"The status light pulses amber before disconnecting.\"}"
```

Import status:

```powershell
curl http://localhost:8000/import/status
```

## Notes

- The legacy GitHub importer code remains in the repository but is no longer mounted as the primary API workflow.
- Moss index/query behavior is preserved in `services/moss_service.py`.
- PDFs require `pypdf`, included in `requirements.txt`.
