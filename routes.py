from fastapi import APIRouter, HTTPException

from backend.ai_core.gemini_generator import (
    DISCLAIMER,
    GeminiDocumentGenerator,
)
from backend.schemas import DocumentRequest, DocumentResponse

router = APIRouter()


@router.post("/generate", response_model=DocumentResponse)
def generate_document(request: DocumentRequest) -> DocumentResponse:
    try:
        generator = GeminiDocumentGenerator()
        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            jurisdiction=request.jurisdiction,
            additional_instructions=request.additional_instructions,
        )
        return DocumentResponse(
            document_type=request.document_type,
            content=content,
            model=generator.model,
            disclaimer=DISCLAIMER,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="The AI document-generation service failed. Check the server logs.",
        )


@router.get("/health")
def health():
    return {"status": "ok", "service": "LegalEase API"}
