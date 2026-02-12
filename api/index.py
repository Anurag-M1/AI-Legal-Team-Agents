from io import BytesIO
import os
from typing import Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from openai import OpenAI
from pydantic import BaseModel
from pypdf import PdfReader


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL_ID = os.getenv("OPENROUTER_MODEL_ID", "qwen/qwen3-coder")
MAX_DOC_CHARS = int(os.getenv("MAX_DOC_CHARS", "45000"))

DEFAULT_QUERIES: Dict[str, str] = {
    "Contract Review": (
        "Analyze this contract using the provided document text. "
        "Identify key terms, obligations, liabilities, and potential ambiguities."
    ),
    "Legal Research": (
        "Using the provided document text, identify relevant legal principles, precedent themes, "
        "and likely jurisdiction-specific concerns."
    ),
    "Risk Assessment": (
        "Assess legal, commercial, operational, and compliance risks in the provided contract text."
    ),
    "Compliance Check": (
        "Evaluate the contract text for compliance gaps and list corrective actions."
    ),
}


class AnalyzeTextRequest(BaseModel):
    text: str
    query: Optional[str] = None
    analysis_type: str = "Contract Review"


app = FastAPI(title="AI Legal Team Agents API", version="1.0.0")


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing OPENROUTER_API_KEY environment variable.")
    return OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid PDF: {e}")
    if not text:
        raise HTTPException(status_code=400, detail="PDF has no extractable text.")
    return text[:MAX_DOC_CHARS]


def _chat(client: OpenAI, system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL_ID,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Model call failed: {e}")


def _run_legal_team(document_text: str, query: str) -> Dict[str, str]:
    client = _get_client()
    shared_context = (
        f"User query:\n{query}\n\n"
        "Document text:\n"
        f"{document_text}\n\n"
        "Only use the provided document text. If evidence is missing, explicitly say so."
    )

    legal_research = _chat(
        client,
        "You are LegalAdvisor. Provide legal-research oriented analysis with precise citations to document clauses.",
        shared_context,
    )
    contract_analysis = _chat(
        client,
        "You are ContractAnalyst. Focus on terms, obligations, liabilities, and ambiguities.",
        shared_context,
    )
    legal_strategy = _chat(
        client,
        "You are LegalStrategist. Focus on risk prioritization and actionable legal strategy.",
        shared_context,
    )

    combined_input = (
        "Integrate the three specialist outputs into one structured legal report.\n\n"
        f"LegalAdvisor:\n{legal_research}\n\n"
        f"ContractAnalyst:\n{contract_analysis}\n\n"
        f"LegalStrategist:\n{legal_strategy}\n\n"
        "Required sections:\n"
        "1) Key Terms and Obligations\n"
        "2) Risks and Severity\n"
        "3) Compliance Concerns\n"
        "4) Recommended Actions\n"
    )
    analysis = _chat(
        client,
        "You are TeamLead. Produce a concise, structured final legal analysis.",
        combined_input,
    )

    key_points = _chat(
        client,
        "Summarize legal analysis into concise bullet points.",
        f"Summarize key legal points from this report:\n\n{analysis}",
    )
    recommendations = _chat(
        client,
        "Generate practical legal recommendations.",
        f"Provide specific recommendations from this report:\n\n{analysis}",
    )

    return {
        "analysis": analysis,
        "key_points": key_points,
        "recommendations": recommendations,
    }


def _resolve_query(analysis_type: str, query: Optional[str]) -> str:
    if query and query.strip():
        return query.strip()
    return DEFAULT_QUERIES.get(analysis_type, DEFAULT_QUERIES["Contract Review"])


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "service": "AI Legal Team Agents API",
        "status": "ok",
        "analyze_endpoint": "POST /api/analyze",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    analysis_type: str = Form("Contract Review"),
    query: Optional[str] = Form(None),
) -> Dict[str, str]:
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Empty file upload.")

    document_text = _extract_pdf_text(pdf_bytes)
    resolved_query = _resolve_query(analysis_type, query)
    result = _run_legal_team(document_text, resolved_query)
    return {
        "analysis_type": analysis_type,
        "query": resolved_query,
        **result,
    }


@app.post("/analyze-text")
def analyze_text(payload: AnalyzeTextRequest) -> Dict[str, str]:
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required.")
    if len(text) > MAX_DOC_CHARS:
        text = text[:MAX_DOC_CHARS]
    resolved_query = _resolve_query(payload.analysis_type, payload.query)
    result = _run_legal_team(text, resolved_query)
    return {
        "analysis_type": payload.analysis_type,
        "query": resolved_query,
        **result,
    }
