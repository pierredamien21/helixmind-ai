import os
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_API_KEY  = os.getenv("NCBI_API_KEY", "")

SEARCH_QUERIES = [
    "genomic variant analysis clinical significance",
    "DNA sequencing bioinformatics pipeline quality",
    "BRCA1 BRCA2 variant pathogenicity classification",
    "KRAS TP53 EGFR cancer somatic mutation",
    "NGS next generation sequencing quality control",
    "ACMG variant classification guidelines",
    "CRISPR genome editing clinical applications",
    "pharmacogenomics drug response genetic variants",
]

MAX_ARTICLES_PER_QUERY = 5
DELAY_BETWEEN_REQUESTS = 1


def search_pubmed(query: str, max_results: int = 5) -> list[str]:
    params = {
        "db":      "pubmed",
        "term":    query,
        "retmax":  max_results,
        "retmode": "json",
        "sort":    "relevance",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    try:
        response = requests.get(f"{NCBI_BASE_URL}/esearch.fcgi", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        print(f"   '{query[:50]}' → {len(ids)} articles trouvés")
        return ids
    except Exception as e:
        print(f"   Erreur recherche PubMed : {e}")
        return []


def fetch_article_details(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    params = {
        "db":      "pubmed",
        "id":      ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    try:
        response = requests.get(f"{NCBI_BASE_URL}/efetch.fcgi", params=params, timeout=15)
        response.raise_for_status()
        return parse_pubmed_xml(response.text)
    except Exception as e:
        print(f"   Erreur récupération articles : {e}")
        return []


def parse_pubmed_xml(xml_text: str) -> list[dict]:
    articles = []
    try:
        root = ET.fromstring(xml_text)
        for article_el in root.findall(".//PubmedArticle"):
            try:
                title_el = article_el.find(".//ArticleTitle")
                title = "".join(title_el.itertext()).strip() if title_el is not None else "Titre non disponible"
                abstract_parts = article_el.findall(".//AbstractText")
                abstract = " ".join("".join(el.itertext()).strip() for el in abstract_parts if "".join(el.itertext()).strip()) if abstract_parts else "Abstract non disponible."
                authors = []
                for author_el in article_el.findall(".//Author")[:3]:
                    lastname  = author_el.findtext("LastName", "")
                    firstname = author_el.findtext("ForeName", "")
                    if lastname:
                        authors.append(f"{lastname} {firstname}".strip())
                if len(article_el.findall(".//Author")) > 3:
                    authors.append("et al.")
                authors_str = ", ".join(authors) if authors else "Auteurs non disponibles"
                pub_date_el = article_el.find(".//PubDate")
                if pub_date_el is not None:
                    year  = pub_date_el.findtext("Year", "")
                    month = pub_date_el.findtext("Month", "")
                    date_str = f"{year} {month}".strip() or "Date inconnue"
                else:
                    date_str = "Date inconnue"
                pmid_el = article_el.find(".//PMID")
                pmid = pmid_el.text if pmid_el is not None else "unknown"
                journal_el = article_el.find(".//Journal/Title")
                journal = journal_el.text if journal_el is not None else "Journal inconnu"
                keywords = [kw.text.strip() for kw in article_el.findall(".//Keyword") if kw.text]
                keywords_str = ", ".join(keywords[:10])
                articles.append({
                    "pmid": pmid, "title": title, "abstract": abstract,
                    "authors": authors_str, "date": date_str,
                    "journal": journal, "keywords": keywords_str,
                })
            except Exception as e:
                print(f"  Erreur parsing article : {e}")
                continue
    except ET.ParseError as e:
        print(f"   Erreur XML : {e}")
    return articles


def save_article_to_file(article: dict, output_dir: Path) -> Path | None:
    filename = f"pubmed_{article['pmid']}.txt"
    filepath = output_dir / filename
    if filepath.exists():
        return None
    content = f"""SOURCE: PubMed
PMID: {article['pmid']}
URL: https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/
DATE_SCRAPING: {datetime.now().strftime('%Y-%m-%d')}

TITRE: {article['title']}
AUTEURS: {article['authors']}
JOURNAL: {article['journal']}
DATE_PUBLICATION: {article['date']}
MOTS_CLES: {article['keywords']}

RÉSUMÉ:
{article['abstract']}
"""
    try:
        filepath.write_text(content, encoding="utf-8")
        return filepath
    except Exception as e:
        print(f"  Erreur écriture {filename} : {e}")
        return None


def run_pubmed_scraper(sops_dir: Path) -> dict:
    print("\n" + "═" * 50)
    print("🔬 SCRAPER PUBMED — Démarrage")
    print("═" * 50)
    sops_dir.mkdir(parents=True, exist_ok=True)
    total_scraped = 0
    total_saved   = 0
    total_skipped = 0
    total_errors  = 0
    seen_pmids    = set()
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] 📡 {query}")
        pmids = search_pubmed(query, MAX_ARTICLES_PER_QUERY)
        time.sleep(DELAY_BETWEEN_REQUESTS)
        new_pmids = [p for p in pmids if p not in seen_pmids]
        seen_pmids.update(new_pmids)
        if not new_pmids:
            continue
        articles = fetch_article_details(new_pmids)
        total_scraped += len(articles)
        time.sleep(DELAY_BETWEEN_REQUESTS)
        for article in articles:
            result = save_article_to_file(article, sops_dir)
            if result is None:
                filename = f"pubmed_{article['pmid']}.txt"
                if (sops_dir / filename).exists():
                    total_skipped += 1
                else:
                    total_errors += 1
            else:
                print(f"   {result.name}")
                total_saved += 1
    print(f"\n RÉSUMÉ PUBMED — Récupérés: {total_scraped} | Nouveaux: {total_saved} | Déjà là: {total_skipped} | Erreurs: {total_errors}")
    return {"source": "PubMed", "scraped": total_scraped, "saved": total_saved, "skipped": total_skipped, "errors": total_errors, "timestamp": datetime.now().isoformat()}
