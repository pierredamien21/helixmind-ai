import os 
from dotenv import load_dotenv
from pathlib import Path

# Cherche le .env dans le dossier parent (helixmind/)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

#centralisation des donnnées du projet
class Settings:
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    LLM_TEMPERATURE=0.1

    #embeddings
    EMBEDDING_MODEL:str="sentence-transformers/all-MiniLM-L6-v2"

    #RAG
    CHROMA_PATH: str="data/chroma_db"
    SOPS_PATH: str="data/sops"
    CHUNK_SIZE: int=500
    CHUNK_OVERLAP: int=50
    TOP_K_RESULTS: int=3

    #pipeline ADN
    RAW_DATA_PATH: str="data/raw"
    PROCESSED_DATA_PATH: str="data/processed"

settings = Settings()
