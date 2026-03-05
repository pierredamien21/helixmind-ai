# backend/rag/ingestor.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from rag.embeddings import get_embeddings
from config import settings

# Mapping extension → loader
LOADERS = {
    ".txt":  TextLoader,
    ".pdf":  PyPDFLoader,
    ".docx": Docx2txtLoader,
}

def load_all_documents():
    """
    Charge tous les fichiers supportés depuis le dossier SOPs
    peu importe leur extension.
    """
    all_docs = []

    for filename in os.listdir(settings.SOPS_PATH):
        filepath = os.path.join(settings.SOPS_PATH, filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in LOADERS:
            print(f"Format ignoré : {filename}")
            continue

        try:
            loader = LOADERS[ext](filepath)
            docs = loader.load()
            all_docs.extend(docs)
            print(f" Chargé : {filename} ({len(docs)} page(s))")
        except Exception as e:
            print(f"❌ Erreur sur {filename} : {e}")

    return all_docs

def ingest_documents():
    print(" Chargement des documents SOPs...")

    documents = load_all_documents()

    if not documents:
        print("  Aucun document trouvé dans", settings.SOPS_PATH)
        return None

    print(f" Total : {len(documents)} document(s) chargé(s)")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    print(f" {len(chunks)} chunks créés")

    print(" Indexation dans ChromaDB...")

    # Vide l'ancienne base avant de réindexer
    # Évite les doublons si on relance l'ingestion
    import shutil
    if os.path.exists(settings.CHROMA_PATH):
        shutil.rmtree(settings.CHROMA_PATH)

    vs = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=settings.CHROMA_PATH
    )

    print(f" {vs._collection.count()} chunks indexés dans ChromaDB")
    print("Ingestion terminée !")
    return vs

if __name__ == "__main__":
    ingest_documents()