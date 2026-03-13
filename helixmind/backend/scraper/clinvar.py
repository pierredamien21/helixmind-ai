import os
import time
import requests
from datetime import datetime
from pathlib import Path

NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_API_KEY  = os.getenv("NCBI_API_KEY", "")

SEARCH_QUERIES = [
    "BRCA1 pathogenic",
    "BRCA2 pathogenic",
    "TP53 pathogenic cancer",
    "KRAS pathogenic",
    "EGFR pathogenic lung cancer",
    "CFTR pathogenic cystic fibrosis",
    "MLH1 pathogenic colorectal",
    "APC pathogenic colorectal cancer",
]

MAX_VARIANTS_PER_QUERY = 10
DELAY_BETWEEN_REQUESTS = 1


def search_clinvar(query: str, max_results: int = 10) -> list[str]:
    params = {
        "db":      "clinvar",
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
        print(f"  🔍 '{query}' → {len(ids)} variants trouvés")
        return ids
    except Exception as e:
        print(f"   Erreur recherche ClinVar : {e}")
        return []


def fetch_variant_details(variation_ids: list[str]) -> list[dict]:
    if not variation_ids:
        return []
    params = {
        "db":      "clinvar",
        "id":      ",".join(variation_ids),
        "retmode": "json",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    try:
        response = requests.get(f"{NCBI_BASE_URL}/esummary.fcgi", params=params, timeout=15)
        response.raise_for_status()
        return parse_clinvar_json(response.json())
    except Exception as e:
        print(f"   Erreur récupération variants : {e}")
        return []


def parse_clinvar_json(data: dict) -> list[dict]:
    variants = []
    result = data.get("result", {})
    uids = result.get("uids", [])
    for uid in uids:
        try:
            variant_data = result.get(uid, {})
            if not variant_data:
                continue
            title = variant_data.get("title", "Variant inconnu")
            clinical_sig = variant_data.get("clinical_significance", {})
            significance = clinical_sig.get("description", "Unknown")
            last_evaluated = clinical_sig.get("last_evaluated", "")
            gene_sort = variant_data.get("gene_sort", "")
            genes_list = variant_data.get("genes", [])
            if genes_list and isinstance(genes_list, list):
                gene_names = [g.get("symbol", "") for g in genes_list if g.get("symbol")]
                gene = ", ".join(gene_names) if gene_names else gene_sort
            else:
                gene = gene_sort
            disease_names = variant_data.get("disease_names", [])
            diseases = "; ".join(disease_names[:3]) if isinstance(disease_names, list) else str(disease_names)
            review_status = variant_data.get("review_status", "")
            chromosome = variant_data.get("chr", "")
            start_pos  = variant_data.get("start", "")
            location   = f"chr{chromosome}:{start_pos}" if chromosome else ""
            if significance not in ["", "not provided", "not classified"]:
                variants.append({
                    "variation_id": uid, "title": title, "gene": gene,
                    "significance": significance, "diseases": diseases,
                    "review_status": review_status, "last_evaluated": last_evaluated,
                    "location": location,
                })
        except Exception as e:
            print(f"  Erreur parsing variant {uid} : {e}")
            continue
    return variants


def save_variant_to_file(variant: dict, output_dir: Path) -> Path | None:
    filename = f"clinvar_{variant['variation_id']}.txt"
    filepath = output_dir / filename
    if filepath.exists():
        return None
    sig_icon = {
        "Pathogenic":             "🔴 PATHOGÈNE",
        "Likely pathogenic":      "🟠 PROBABLEMENT PATHOGÈNE",
        "Benign":                 "🟢 BÉNIN",
        "Likely benign":          "🟡 PROBABLEMENT BÉNIN",
        "Uncertain significance": "⚪ SIGNIFICATION INCERTAINE",
    }.get(variant["significance"], f"ℹ️ {variant['significance']}")
    content = f"""SOURCE: ClinVar (NCBI)
VARIATION_ID: {variant['variation_id']}
URL: https://www.ncbi.nlm.nih.gov/clinvar/variation/{variant['variation_id']}/
DATE_SCRAPING: {datetime.now().strftime('%Y-%m-%d')}

VARIANT: {variant['title']}
GÈNE: {variant['gene']}
LOCALISATION: {variant['location']}

SIGNIFICATION_CLINIQUE: {sig_icon}
MALADIES_ASSOCIÉES: {variant['diseases']}
STATUT_REVUE: {variant['review_status']}
DERNIÈRE_ÉVALUATION: {variant['last_evaluated']}

INTERPRÉTATION_CLINIQUE:
Le variant {variant['title']} dans le gène {variant['gene']} est classifié comme
"{variant['significance']}" selon ClinVar.
Maladies associées : {variant['diseases'] or 'Non spécifié'}.
"""
    try:
        filepath.write_text(content, encoding="utf-8")
        return filepath
    except Exception as e:
        print(f"   Erreur écriture {filename} : {e}")
        return None


def run_clinvar_scraper(sops_dir: Path) -> dict:
    print("\n" + "═" * 50)
    print("🧬 SCRAPER CLINVAR — Démarrage")
    print("═" * 50)
    sops_dir.mkdir(parents=True, exist_ok=True)
    total_scraped = 0
    total_saved   = 0
    total_skipped = 0
    total_errors  = 0
    seen_ids      = set()
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"\n[{i}/{len(SEARCH_QUERIES)}] 📡 {query}")
        variation_ids = search_clinvar(query, MAX_VARIANTS_PER_QUERY)
        time.sleep(DELAY_BETWEEN_REQUESTS)
        new_ids = [v for v in variation_ids if v not in seen_ids]
        seen_ids.update(new_ids)
        if not new_ids:
            continue
        variants = fetch_variant_details(new_ids)
        total_scraped += len(variants)
        time.sleep(DELAY_BETWEEN_REQUESTS)
        for variant in variants:
            result = save_variant_to_file(variant, sops_dir)
            if result is None:
                filename = f"clinvar_{variant['variation_id']}.txt"
                if (sops_dir / filename).exists():
                    total_skipped += 1
                else:
                    total_errors += 1
            else:
                print(f"  {result.name} — {variant['significance']}")
                total_saved += 1
    print(f"\n RÉSUMÉ CLINVAR — Récupérés: {total_scraped} | Nouveaux: {total_saved} | Déjà là: {total_skipped} | Erreurs: {total_errors}")
    return {"source": "ClinVar", "scraped": total_scraped, "saved": total_saved, "skipped": total_skipped, "errors": total_errors, "timestamp": datetime.now().isoformat()}
