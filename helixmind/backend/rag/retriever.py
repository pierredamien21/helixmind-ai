# backend/rag/retriever.py
from rag.chroma_client import get_retriever
from rag.generator import generate_answer

def ask(question: str) -> dict:
    """
    1. Cherche les chunks pertinents dans ChromaDB
    2. Les passe directement à Groq
    3. Retourne la réponse + sources
    """
    retriever = get_retriever()

    # Récupère les documents pertinents
    docs = retriever.invoke(question)

    # Assemble le contexte depuis les chunks trouvés
    context = "\n\n".join([doc.page_content for doc in docs])

    # Génère la réponse
    answer = generate_answer(question, context)

    # Extrait les sources
    sources = list(set([
        doc.metadata.get("source", "inconnu")
        for doc in docs
    ]))

    return {
        "answer": answer,
        "sources": sources
    }