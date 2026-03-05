# backend/rag/generator.py
from groq import Groq
from config import settings

_client = None

def get_groq_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client

def generate_answer(question: str, context: str) -> str:
    """
    Appelle Groq directement sans passer par LangChain.
    Plus stable, moins de dépendances problématiques.
    """
    client = get_groq_client()

    prompt = f"""Tu es HelixMind, un assistant scientifique expert en biologie moléculaire.

Règles :
- Réponds UNIQUEMENT en te basant sur le contexte fourni
- Si la réponse n'est pas dans le contexte, dis-le clairement
- Réponds toujours en français
- Sois précis et professionnel

Contexte extrait des SOPs :
{context}

Question : {question}

Réponse :"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=1024
    )

    return response.choices[0].message.content