import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import html
import os

import requests
import streamlit as st
from dotenv import load_dotenv

from legal_ease.exporters import format_docx, format_pdf, format_txt

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title { text-align:center; font-size:2.4rem; font-weight:700; }
    .subtitle { text-align:center; color:#777; margin-bottom:1.5rem; }
    .preview {
        background:#111827; color:#f3f4f6; padding:24px; border-radius:12px;
        min-height:420px; max-height:700px; overflow:auto;
        font-family: Georgia, serif; white-space:pre-wrap;
    }
    .notice {
        padding:12px 16px; border-radius:10px; background:#fff7ed;
        border:1px solid #fed7aa; margin-bottom:16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">⚖️ LegalEase</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-assisted legal document drafting and export</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="notice"><b>Important:</b> LegalEase provides drafting assistance, '
    'not legal advice. Review important documents with a qualified legal professional '
    'before signing or relying on them.</div>',
    unsafe_allow_html=True,
)

if "document" not in st.session_state:
    st.session_state.document = ""
if "model" not in st.session_state:
    st.session_state.model = ""
if "disclaimer" not in st.session_state:
    st.session_state.disclaimer = ""

with st.sidebar:
    st.header("Document details")
    document_type = st.text_input(
        "Document type",
        value="Non-Disclosure Agreement",
        help="Example: Employment Contract, NDA, Lease Agreement.",
    )
    parties = st.text_area(
        "Parties involved",
        placeholder="Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
        height=100,
    )
    terms = st.text_area(
        "Terms & conditions",
        placeholder=(
            "Confidential information must be protected; "
            "Disclosure is permitted only for the business purpose; "
            "Either party may terminate with 15 days notice"
        ),
        height=160,
        help="Separate major terms with semicolons.",
    )
    effective_date = st.text_input("Effective date", placeholder="September 27, 2026")
    jurisdiction = st.text_input(
        "Jurisdiction (optional but recommended)",
        placeholder="India / Tamil Nadu",
    )
    additional = st.text_area(
        "Additional instructions (optional)",
        placeholder="Use a formal tone. Keep the agreement concise.",
        height=100,
    )
    logo = st.file_uploader(
        "Optional logo",
        type=["png", "jpg", "jpeg"],
        help="Used for DOCX/PDF export.",
    )

    generate = st.button("Generate Document", type="primary", use_container_width=True)

if generate:
    required = {
        "Document type": document_type,
        "Parties": parties,
        "Terms": terms,
        "Effective date": effective_date,
    }
    missing = [name for name, value in required.items() if not value.strip()]

    if missing:
        st.error("Please complete: " + ", ".join(missing))
    else:
        payload = {
            "document_type": document_type.strip(),
            "parties": parties.strip(),
            "terms": terms.strip(),
            "effective_date": effective_date.strip(),
            "jurisdiction": jurisdiction.strip() or "Not specified",
            "additional_instructions": additional.strip(),
        }
        try:
            with st.spinner("Generating your draft..."):
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=TIMEOUT,
                )
            if response.ok:
                data = response.json()
                st.session_state.document = data["content"]
                st.session_state.model = data["model"]
                st.session_state.disclaimer = data["disclaimer"]
                st.success("Document generated.")
            else:
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                    detail = response.text
                st.error(f"Backend error ({response.status_code}): {detail}")
        except requests.RequestException as exc:
            st.error(
                "Could not reach FastAPI. Start the backend with "
                "`uvicorn backend.main:app --reload --port 8000`."
            )

st.subheader("Document preview")

if st.session_state.document:
    tab_preview, tab_edit, tab_export = st.tabs(
        ["Preview", "Edit Document", "Download"]
    )

    with tab_preview:
        safe = html.escape(st.session_state.document)
        st.markdown(
            f'<div class="preview">{safe}</div>',
            unsafe_allow_html=True,
        )
        if st.session_state.model:
            st.caption(f"Generated with: {st.session_state.model}")
        st.caption(st.session_state.disclaimer)

    with tab_edit:
        edited = st.text_area(
            "Editable document",
            value=st.session_state.document,
            height=650,
            key="editor",
        )
        if st.button("Save Edits"):
            st.session_state.document = edited
            st.success("Edits saved to the current session.")

    with tab_export:
        text = st.session_state.document
        logo_bytes = logo.getvalue() if logo else None

        st.download_button(
            "Download TXT",
            data=format_txt(text),
            file_name="legalease_document.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.download_button(
            "Download DOCX",
            data=format_docx(text, document_type, logo_bytes),
            file_name="legalease_document.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

        # FPDF's standard fonts are intentionally used for portability.
        # A local logo is optional.
        logo_path = None
        if logo:
            import tempfile
            suffix = os.path.splitext(logo.name)[1] or ".png"
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp.write(logo_bytes)
            temp.close()
            logo_path = temp.name

        try:
            pdf_data = format_pdf(text, document_type, logo_path)
        finally:
            if logo_path:
                try:
                    os.unlink(logo_path)
                except OSError:
                    pass

        st.download_button(
            "Download PDF",
            data=pdf_data,
            file_name="legalease_document.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
else:
    st.info("Enter the document details in the sidebar and select Generate Document.")
