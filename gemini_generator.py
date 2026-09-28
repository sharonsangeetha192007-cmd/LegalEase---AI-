from google import genai
from google.genai import types

from backend.config import get_settings
from legal_ease.prompts import build_document_prompt


DISCLAIMER = (
    "Drafting assistance only — not legal advice. Review the document for "
    "accuracy, completeness, and jurisdiction-specific requirements before use."
)


class GeminiDocumentGenerator:
    def __init__(self) -> None:
        settings = get_settings()
        api_key = settings["gemini_api_key"]
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Add it to the .env file."
            )
        self.model = settings["gemini_model"]
        self.client = genai.Client(api_key=api_key)

    def generate_document(
        self,
        *,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
        additional_instructions: str = "",
    ) -> str:
        prompt = build_document_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            jurisdiction=jurisdiction,
            additional_instructions=additional_instructions,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=12000,
                system_instruction=(
                    "You are a legal-document drafting assistant. "
                    "Produce structured drafting assistance, not legal advice. "
                    "Do not invent statutes, cases, regulations, citations, "
                    "parties, facts, dates, signatures, or legal requirements. "
                    "If information is missing, clearly label an assumption "
                    "or placeholder. Keep the user's requested terms intact "
                    "unless they conflict internally, in which case flag the "
                    "conflict. Avoid claiming that a generated document is "
                    "legally valid or enforceable."
                ),
            ),
        )

        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()
