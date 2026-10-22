# HelixMind AI

Assistant IA pour un laboratoire de génomique : il répond aux questions sur les procédures du laboratoire (RAG) et produit un rapport PDF commenté à partir d'un fichier de séquençage FASTQ.

## Le problème

Les procédures d'un laboratoire (extraction d'ADN, PCR, séquençage NGS, contrôle qualité, sécurité) sont dispersées dans des documents que l'on consulte mal sous pression. Les résultats d'analyse génomique, eux, demandent une interprétation que tout le monde ne sait pas lire.

## Fonctionnalités

- **Questions-réponses sur les procédures (RAG)** : les documents de `data/sops/` sont découpés (500 caractères, chevauchement 50), vectorisés avec `all-MiniLM-L6-v2` et stockés dans Chroma. Pour chaque question, les 3 passages les plus proches sont envoyés au modèle `llama-3.1-8b-instant` (Groq), qui répond en citant ses sources.
- **Pipeline d'analyse d'un fichier FASTQ** : contrôle qualité, alignement, appel de variants, annotation clinique, interprétation par le LLM, puis rapport PDF (ReportLab). Le suivi se fait par identifiant de tâche.
- **Veille scientifique** : un planificateur interroge PubMed, bioRxiv et ClinVar toutes les 24 h et ajoute les résultats à la base documentaire.
- **Interface web** : React 19 et Vite, avec trois pages (accueil, chat, pipeline).

> **Limite importante.** Les étapes FastQC, BWA-MEM et appel de variants sont **simulées** : le code génère des résultats plausibles à partir de variants publics connus (ClinVar, dbSNP) au lieu d'appeler les outils. Les vraies commandes sont indiquées en commentaire dans `backend/pipeline/`. L'interprétation par le LLM et le rapport PDF sont réels.

## Architecture

```
frontend (React)  ──HTTP──▶  backend (FastAPI)
                                ├── rag/       ingestion, Chroma, recherche, génération (Groq)
                                ├── pipeline/  QC → alignement → variants → annotation → interprétation → PDF
                                └── scraper/   PubMed, bioRxiv, ClinVar (toutes les 24 h)
```

## API

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/health` | Vérifie que la clé Groq est chargée |
| POST | `/chat` | Pose une question au RAG, renvoie la réponse et ses sources |
| POST | `/ingest` | Recharge les documents dans Chroma |
| POST | `/pipeline/upload` | Lance le pipeline sur un fichier `.fastq`, `.fq` ou `.txt` |
| GET | `/pipeline/status/{job_id}` | Suit l'avancement |
| GET | `/pipeline/report/{job_id}` | Télécharge le rapport PDF |
| GET / POST | `/scraper/status`, `/scraper/run` | Consulte ou force la veille scientifique |

## Installation

Prérequis : Python 3.11, Node.js 20 et une clé API [Groq](https://console.groq.com).

```bash
# Backend
cd helixmind/backend
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
echo "GROQ_API_KEY=votre_cle" > ../.env
uvicorn main:app --reload

# Frontend (autre terminal)
cd helixmind/frontend
npm install
npm run dev
```

Variables utiles : `DISABLE_STARTUP_INGEST=1` évite l'ingestion au démarrage, `DISABLE_SCRAPING=1` coupe la veille. Le fichier `render.yaml` décrit le déploiement sur Render (API + site statique).

## Stack

Python · FastAPI · LangChain · Chroma · sentence-transformers · Groq (Llama 3.1) · ReportLab · React 19 · Vite

## Pistes d'amélioration

- Brancher les vrais outils (FastQC, BWA, GATK, snpEff) dans un conteneur dédié.
- Restreindre le CORS à l'adresse du frontend en production.
- Ajouter des tests sur la recherche RAG et sur la génération du rapport.
