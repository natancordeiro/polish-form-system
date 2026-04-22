"""
API REST FastAPI — expõe dois endpoints:

  GET  /api/health           -> healthcheck
  POST /api/generate-pdf     -> recebe FormData (JSON) e devolve o PDF

O PDF é retornado como `application/pdf` em streaming — o frontend
dispara o download diretamente da resposta.
"""
from __future__ import annotations

import logging
from io import BytesIO
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.config import settings
from app.schemas import FormData
from app.services.pdf_generator import generate_pdf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Polish Citizenship Form API",
    description=(
        "API que recebe o formulário em português e gera o PDF oficial "
        "polonês ('Wniosek o potwierdzenie posiadania lub utraty "
        "obywatelstwa polskiego')."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — libera o frontend local a consumir a API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health() -> dict:
    """Healthcheck simples — útil para smoke test do deploy."""
    return {
        "status": "ok",
        "deepl_configured": bool(settings.deepl_api_key),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/generate-pdf")
def generate_pdf_endpoint(data: FormData) -> StreamingResponse:
    """Recebe o formulário preenchido e devolve o PDF final."""
    try:
        pdf_bytes = generate_pdf(data)
    except Exception as e:
        logger.exception("Falha ao gerar PDF: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {e}")

    # Nome de arquivo sanitizado
    nome = data.nome_titular_confirmacao.strip().replace(" ", "_")
    nome = "".join(c for c in nome if c.isalnum() or c == "_") or "Wniosek"
    filename = f"Wniosek_{nome}_{datetime.now():%Y%m%d_%H%M%S}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
