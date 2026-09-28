from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


@lru_cache
def get_settings() -> dict:
    return {
        "gemini_api_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip(),
        "backend_url": os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/"),
        "request_timeout": float(os.getenv("REQUEST_TIMEOUT_SECONDS", "120")),
        "max_document_chars": int(os.getenv("MAX_DOCUMENT_CHARS", "50000")),
    }
