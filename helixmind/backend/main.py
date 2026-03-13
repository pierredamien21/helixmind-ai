# backend/main.py
import os
import uuid
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from rag.retriever import ask
from rag.ingestor import ingest_documents
from pipeline.tasks import run_pipeline, get_job_status
from scraper.scheduler import start_scheduler, run_all_scrapers, scraper_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Démarrage HelixMind AI...")

    # Ingestion en arrière-plan pour ne pas bloquer le démarrage
    if not os.getenv("DISABLE_STARTUP_INGEST"):
        print("📂 Lancement ingestion en arrière-plan...")
        thread = threading.Thread(target=ingest_documents)
        thread.daemon = True
        thread.start()
    else:
        print("⏭️ Ingestion désactivée au démarrage")

    # Scraping automatique toutes les 24h
    if not os.getenv("DISABLE_SCRAPING"):
        from pathlib import Path
        sops_dir = Path(settings.SOPS_PATH)
        start_scheduler(sops_dir)
    else:
        print("⏭️ Scraping désactivé")

    yield
    print("👋 Arrêt du serveur")


app = FastAPI(
    title="HelixMind AI",
    description="Plateforme d'analyse génomique et assistant IA",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, mettre l'URL exacte du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# ── ROUTES SCRAPER ──
@app.get("/scraper/status")
def get_scraper_status():
    """Voir l'état du dernier scraping et l'heure du prochain."""
    return scraper_status

@app.post("/scraper/run")
def run_scraper_now():
    """Forcer un scraping immédiat sans attendre les 24h."""
    if scraper_status["running"]:
        raise HTTPException(status_code=409, detail="Scraping déjà en cours ⏳")
    from pathlib import Path
    sops_dir = Path(settings.SOPS_PATH)
    thread = threading.Thread(
        target=run_all_scrapers,
        args=(sops_dir,),
        daemon=True
    )
    thread.start()
    return {"message": "Scraping lancé en arrière-plan 🚀"}


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