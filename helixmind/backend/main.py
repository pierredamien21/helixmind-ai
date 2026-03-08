# backend/main.py
import os
import uuid
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import settings
from rag.retriever import ask
from rag.ingestor import ingest_documents
from pipeline.tasks import run_pipeline, get_job_status

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Démarrage HelixMind AI...")
    ingest_documents()
    yield
    print("👋 Arrêt du serveur")

app = FastAPI(
    title="HelixMind AI",
    description="Plateforme d'analyse génomique et assistant IA",
    version="1.0.0",
    lifespan=lifespan
)

# ── MODÈLES ──
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]

# ── ROUTES GÉNÉRALES ──
@app.get("/")
def home():
    return {"message": "HelixMind AI est en ligne 🧬", "status": "ok"}

@app.get("/health")
def health_check():
    return {
        "api_key_loaded": bool(settings.GROQ_API_KEY),
        "message": "Clé trouvée ✅" if settings.GROQ_API_KEY else "Clé manquante ❌"
    }

# ── ROUTES RAG ──
@app.post("/ingest")
def ingest():
    result = ingest_documents()
    if result is None:
        raise HTTPException(status_code=404, detail="Aucun document trouvé")
    return {"message": "Documents rechargés avec succès ✅"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide")
    result = ask(request.question)
    return ChatResponse(**result)

# ── ROUTES PIPELINE ADN ──
@app.post("/pipeline/upload")
async def upload_fastq(file: UploadFile = File(...)):
    if not file.filename.endswith(('.fastq', '.fq', '.fastq.gz', '.txt')):
        raise HTTPException(
            status_code=400,
            detail="Format invalide. Accepté : .fastq, .fq, .txt"
        )

    job_id = str(uuid.uuid4())[:8]
    os.makedirs(settings.RAW_DATA_PATH, exist_ok=True)
    fastq_path = os.path.join(settings.RAW_DATA_PATH, f"{job_id}_{file.filename}")

    with open(fastq_path, "wb") as f:
        content = await file.read()
        f.write(content)

    thread = threading.Thread(
        target=run_pipeline,
        args=(job_id, fastq_path)
    )
    thread.start()

    return {
        "job_id": job_id,
        "message": "Pipeline lancé ✅",
        "status_url": f"/pipeline/status/{job_id}"
    }

@app.get("/pipeline/status/{job_id}")
def pipeline_status(job_id: str):
    job = get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    return job

@app.get("/pipeline/report/{job_id}")
def download_report(job_id: str):
    job = get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable")
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline non terminé : {job['status']}"
        )
    pdf_path = job.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Rapport PDF introuvable")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"helixmind_report_{job_id}.pdf"
    )