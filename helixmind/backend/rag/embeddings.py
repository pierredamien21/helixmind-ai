# backend/rag/embeddings.py
from langchain_huggingface import HuggingFaceEmbeddings
from config import settings

_embeddings_model = None

def get_embeddings():
    global _embeddings_model
    if _embeddings_model is None:
        print("🔢 chargement du model d'embeddings...")
        _embeddings_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        print("model d'embeddings chargé avec succès")
    return _embeddings_model