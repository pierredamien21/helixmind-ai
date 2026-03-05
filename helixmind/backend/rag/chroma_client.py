# backend/rag/chroma_client.py
from langchain_chroma import Chroma
from rag.embeddings import get_embeddings
from config import settings

_vectorstore = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            persist_directory=settings.CHROMA_PATH,
            embedding_function=get_embeddings()
        )
    return _vectorstore

def get_retriever():
    return get_vectorstore().as_retriever(
        search_kwargs={"k": settings.TOP_K_RESULTS}
    )