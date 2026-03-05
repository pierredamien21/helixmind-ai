# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from config import settings
from rag.retriever import ask
from rag.ingestor import ingest_documents

# Ce bloc s'exécute au démarrage du serveur
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" Démarrage HelixMind AI...")
    ingest_documents()  # Injection automatique au démarrage
    yield
    print(" Arrêt du serveur")

app = FastAPI(
    title="HelixMind AI",
    description="Plateforme d'analyse génomique et assistant IA",
    version="1.0.0",
    lifespan=lifespan  # On branche le lifespan
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]

@app.get("/")
def home():
    return {"message": "HelixMind AI est en ligne 🧬", "status": "ok"}

@app.get("/health")
def health_check():
    return {
        "api_key_loaded": bool(settings.GROQ_API_KEY),
        "message": "Clé trouvée " if settings.GROQ_API_KEY else "Clé manquante ❌"
    }

@app.post("/ingest")
def ingest():
    """
    Recharge tous les documents sans redémarrer le serveur.
    Utile quand tu ajoutes un nouveau SOP.
    """
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