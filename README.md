# LegalEase — AI-Powered Legal Document Generator

LegalEase is a full-stack reference implementation based on the supplied project specification:
- Streamlit frontend
- FastAPI backend
- Gemini-powered document generation
- Editable preview
- TXT, DOCX and PDF exports
- Optional logo/branding
- Basic responsible-AI safeguards and validation
- Automated tests

> Legal disclaimer: LegalEase is drafting assistance, not a lawyer or law firm. Generated content may be incomplete, jurisdictionally inappropriate, or inaccurate. Review important documents with a qualified legal professional before signing or relying on them.

## Architecture

```text
Browser
  |
  v
Streamlit (frontend/app.py)
  |
  | POST /generate
  v
FastAPI (backend/main.py)
  |
  v
AI Core (backend/ai_core/gemini_generator.py)
  |
  v
Google Gemini API

Streamlit also formats the edited text into:
  TXT / DOCX / PDF
```

The project follows the supplied specification's frontend/backend/AI-core split and export workflow.

## Requirements

- Python 3.10+
- A Google Gemini API key
- VS Code
- Internet access for Gemini API calls

## 1. Create and activate a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Gemini

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows:

```powershell
copy .env.example .env
```

Then set:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flassh
BACKEND_URL=http://127.0.0.1:8000
```

The model is deliberately configurable. The PDF requested `gemini-1.5-pro`; that model is not used as the default because the current Gemini model catalog has moved on. If your account exposes another supported model, change only `GEMINI_MODEL`.

## 4. Run the backend

From the project root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

The first endpoint is a health response. `/docs` is FastAPI's interactive API documentation.

## 5. Run the frontend

Open another terminal with the virtual environment active:

```bash
streamlit run frontend/app.py
```

Then open the URL Streamlit prints, normally:

```text
http://localhost:8501
```

## 6. Test the API manually

```bash
curl http://127.0.0.1:8000/health
```

Generate a document:

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d "{\"document_type\":\"Non-Disclosure Agreement\",\"parties\":\"Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)\",\"terms\":\"Confidential information must be protected; Disclosure is permitted only for the stated business purpose; Either party may terminate with 15 days notice\",\"effective_date\":\"September 27, 2026\",\"jurisdiction\":\"India\"}"
```

## 7. Run automated tests 

```bash
pytest -q
```

The tests mock the AI provider, so they do not consume API quota.

## Project structure

```text
LegalEase/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   ├── config.py
│   └── ai_core/
│       ├── __init__.py
│       └── gemini_generator.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── legal_ease/
│   ├── __init__.py
│   ├── exporters.py
│   ├── sanitization.py
│   └── prompts.py
├── tests/
│   ├── test_api.py
│   ├── test_exporters.py
│   └── test_sanitization.py
├── assets/
│   └── .gitkeep
├── docs/
│   └── RESPONSIBLE_AI.md
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
└── README.md
```

## Responsible AI design

This implementation adds:
- explicit "drafting assistance, not legal advice" messaging
- no automatic claim that a document is legally valid
- jurisdiction field to reduce ambiguity
- validation of required fields and length
- refusal/redirect behavior for requests to impersonate legal authorities or fabricate citations
- instructions to mark assumptions and missing information
- no API key in frontend code
- API errors that do not expose secrets
- mocked tests for repeatable CI runs

## Troubleshooting

### `GEMINI_API_KEY is not configured`

Make sure `.env` exists in the project root and contains a valid key.

### Model not found / unavailable

Change `GEMINI_MODEL` to a model available to your Gemini API account.

### Streamlit says backend is unavailable

Start FastAPI first:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Then restart Streamlit.

### PDF export has missing glyphs

The exporter uses Helvetica for maximum portability. For multilingual production output, place a Unicode TTF font in `assets/` and extend `legal_ease/exporters.py` to register it with FPDF.

## Production notes

For a real deployment:
- use HTTPS
- store secrets in the platform's secret manager
- add authentication/authorization
- add rate limiting
- add request/response audit logging with privacy controls
- use a persistent job store for long documents
- add malware/content scanning for uploaded assets
- configure CORS to exact frontend origins
- use a managed deployment rather than the development server
