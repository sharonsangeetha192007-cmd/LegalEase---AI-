def build_document_prompt(
    *,
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
    jurisdiction: str,
    additional_instructions: str = "",
) -> str:
    return f"""
Create a professional legal-document draft from the supplied facts.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

JURISDICTION:
{jurisdiction}

TERMS / CONDITIONS:
{terms}

ADDITIONAL INSTRUCTIONS:
{additional_instructions or "None"}

OUTPUT REQUIREMENTS:
1. Start with a clear document title.
2. Use numbered sections and descriptive headings.
3. Include the parties and effective date exactly as supplied where possible.
4. Convert the supplied terms into coherent clauses without silently adding
   material obligations that were not requested.
5. Include practical standard sections when appropriate, but mark material
   assumptions or missing facts as "[PLACEHOLDER: ...]".
6. Include signature blocks only when appropriate.
7. Do not fabricate legislation, case citations, registration numbers,
   addresses, governing-law rules, or legal authorities.
8. Do not state that the document is legally valid, enforceable, or compliant.
9. End with a short "Review Notes" section listing important missing facts,
   assumptions, or jurisdiction-specific issues that should be checked.
10. Return plain text/Markdown suitable for editing and DOCX/PDF conversion.
""".strip()
