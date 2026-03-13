import threading
import time
from datetime import datetime
from pathlib import Path

from scraper.pubmed import run_pubmed_scraper
from scraper.clinvar import run_clinvar_scraper
from scraper.biorxiv import run_biorxiv_scraper
from rag.ingestor import ingest_documents

# Intervalle en secondes (24h = 86400s)
SCRAPING_INTERVAL = 86400

# État global du scraper — accessible via /scraper/status
scraper_status = {
    "running":      False,
    "last_run":     None,
    "next_run":     None,
    "last_results": [],
    "total_saved":  0,
}


def run_all_scrapers(sops_dir: Path):
    """
    Lance tous les scrapers en séquence puis réindexe ChromaDB.
    """
    global scraper_status

    scraper_status["running"] = True
    scraper_status["last_run"] = datetime.now().isoformat()
    scraper_status["last_results"] = []

    print("\n" + "█" * 50)
    print("🚀 LANCEMENT SCRAPING COMPLET")
    print("█" * 50)

    total_saved = 0
    results = []

    # 1. PubMed
    try:
        result = run_pubmed_scraper(sops_dir)
        results.append(result)
        total_saved += result.get("saved", 0)
    except Exception as e:
        print(f" Erreur PubMed : {e}")
        results.append({"source": "PubMed", "error": str(e)})

    # 2. ClinVar
    try:
        result = run_clinvar_scraper(sops_dir)
        results.append(result)
        total_saved += result.get("saved", 0)
    except Exception as e:
        print(f" Erreur ClinVar : {e}")
        results.append({"source": "ClinVar", "error": str(e)})

    # 3. bioRxiv
    try:
        result = run_biorxiv_scraper(sops_dir)
        results.append(result)
        total_saved += result.get("saved", 0)
    except Exception as e:
        print(f" Erreur bioRxiv : {e}")
        results.append({"source": "bioRxiv", "error": str(e)})

    # 4. Réindexer ChromaDB si nouveaux fichiers
    if total_saved > 0:
        print(f"\n⏳ Attente 60s avant réindexation...")
        time.sleep(60)
        print(f"\n🔄 {total_saved} nouveaux fichiers → réindexation ChromaDB...")
        try:
            ingest_documents()
            print(" Réindexation terminée !")
        except Exception as e:
            print(f" Erreur réindexation : {e}")
    else:
        print("\nℹ Aucun nouveau fichier — réindexation inutile")

    # Mise à jour du statut
    scraper_status["running"]      = False
    scraper_status["last_results"] = results
    scraper_status["total_saved"]  = total_saved
    scraper_status["next_run"]     = datetime.fromtimestamp(
        time.time() + SCRAPING_INTERVAL
    ).isoformat()

    print("\n" + "█" * 50)
    print(f" SCRAPING TERMINÉ — {total_saved} nouveaux documents")
    print("█" * 50)


def scraping_loop(sops_dir: Path):
    """
    Boucle infinie qui tourne toutes les 24h dans un thread séparé.
    """
    while True:
        run_all_scrapers(sops_dir)
        print(f"\n Prochain scraping dans {SCRAPING_INTERVAL // 3600}h")
        time.sleep(SCRAPING_INTERVAL)


def start_scheduler(sops_dir: Path):
    """
    Lance le scheduler dans un thread daemon.
    daemon=True = le thread s'arrête automatiquement quand le serveur s'arrête.
    """
    thread = threading.Thread(
        target=scraping_loop,
        args=(sops_dir,),
        daemon=True
    )
    thread.start()
    print("Scheduler scraping démarré — toutes les 24h")
    return thread
