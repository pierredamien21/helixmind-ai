import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

BIORXIV_API_URL = "https://api.biorxiv.org/details/biorxiv"

SEARCH_TERMS = [
    "genomics", "variant-calling", "bioinformatics",
    "CRISPR", "sequencing", "cancer-genomics",
]

MAX_ARTICLES_PER_TERM = 5
DELAY_BETWEEN_REQUESTS = 1


def fetch_biorxiv_articles(term: str, max_results: int = 5) -> list[dict]:
    """
    bioRxiv a une API très simple :
    https://api.biorxiv.org/details/biorxiv/DATE_DEBUT/DATE_FIN/CURSOR

    On récupère les articles des 30 derniers jours puis on filtre par terme.
    """
    date_fin   = datetime.now().strftime("%Y-%m-%d")
    date_debut = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        url = f"{BIORXIV_API_URL}/{date_debut}/{date_fin}/0"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        all_articles = data.get("collection", [])

        # Filtrer par terme de recherche dans le titre ou le résumé
        filtered = [
            a for a in all_articles
            if term.lower() in a.get("title", "").lower()
            or term.lower() in a.get("abstract", "").lower()
        ]

        print(f"  🔍 '{term}' → {len(filtered)} articles trouvés")
        return filtered[:max_results]

    except Exception as e:
        print(f"   Erreur bioRxiv '{term}' : {e}")
        return []


def save_biorxiv_article(article: dict, output_dir: Path) -> Path | None:
    doi = article.get("doi", "").replace("/", "_")
    if not doi:
        return None

    filename = f"biorxiv_{doi}.txt"
    filepath = output_dir / filename

    if filepath.exists():
        return None

    content = f"""SOURCE: bioRxiv (preprint)
DOI: {article.get('doi', '')}
URL: https://www.biorxiv.org/content/{article.get('doi', '')}
DATE_SCRAPING: {datetime.now().strftime('%Y-%m-%d')}

TITRE: {article.get('title', '')}
AUTEURS: {article.get('authors', '')}
DATE_PUBLICATION: {article.get('date', '')}
CATÉGORIE: {article.get('category', '')}

RÉSUMÉ:
{article.get('abstract', 'Abstract non disponible.')}
"""
    try:
        filepath.write_text(content, encoding="utf-8")
        return filepath
    except Exception as e:
        print(f"   Erreur écriture {filename} : {e}")
        return None


def run_biorxiv_scraper(sops_dir: Path) -> dict:
    print("\n" + "═" * 50)
    print("📄 SCRAPER BIORXIV — Démarrage")
    print("═" * 50)

    sops_dir.mkdir(parents=True, exist_ok=True)

    total_scraped = 0
    total_saved   = 0
    total_skipped = 0
    total_errors  = 0
    seen_dois     = set()

    for i, term in enumerate(SEARCH_TERMS, 1):
        print(f"\n[{i}/{len(SEARCH_TERMS)}] 📡 {term}")
        articles = fetch_biorxiv_articles(term, MAX_ARTICLES_PER_TERM)
        time.sleep(DELAY_BETWEEN_REQUESTS)

        for article in articles:
            doi = article.get("doi", "")
            if doi in seen_dois:
                continue
            seen_dois.add(doi)
            total_scraped += 1

            result = save_biorxiv_article(article, sops_dir)
            if result is None:
                doi_safe = doi.replace("/", "_")
                if (sops_dir / f"biorxiv_{doi_safe}.txt").exists():
                    total_skipped += 1
                else:
                    total_errors += 1
            else:
                print(f"   {result.name}")
                total_saved += 1

    print(f"\nRÉSUMÉ BIORXIV — Récupérés: {total_scraped} | Nouveaux: {total_saved} | Déjà là: {total_skipped} | Erreurs: {total_errors}")
    return {"source": "bioRxiv", "scraped": total_scraped, "saved": total_saved, "skipped": total_skipped, "errors": total_errors, "timestamp": datetime.now().isoformat()}
