# backend/pipeline/annotator.py

# Base de données d'annotation clinique — données publiques ClinVar
CLINICAL_DATABASE = {
    "rs80357906": {
        "clinical_significance": "Pathogenic",
        "condition": "Hereditary breast and ovarian cancer",
        "review_status": "reviewed by expert panel",
        "frequency_population": "0.0001"
    },
    "rs28934578": {
        "clinical_significance": "Pathogenic",
        "condition": "Li-Fraumeni syndrome / Various cancers",
        "review_status": "reviewed by expert panel",
        "frequency_population": "0.0002"
    },
    "rs112445441": {
        "clinical_significance": "Pathogenic",
        "condition": "Non-small cell lung cancer / Colorectal cancer",
        "review_status": "criteria provided",
        "frequency_population": "0.0003"
    },
    "rs121434568": {
        "clinical_significance": "Pathogenic",
        "condition": "Non-small cell lung cancer",
        "review_status": "criteria provided",
        "frequency_population": "0.0001"
    },
    "rs113993960": {
        "clinical_significance": "Pathogenic",
        "condition": "Cystic fibrosis",
        "review_status": "reviewed by expert panel",
        "frequency_population": "0.02"
    },
}

def run_annotation(variants: list) -> list:
    """
    Simule SnpEff/VEP — Annotation clinique des variants.
    En production :
        subprocess.run(['snpEff', 'GRCh38.99', vcf_path, '-o', annotated_vcf])
    """
    print("📚 Annotation clinique des variants...")

    annotated = []
    for variant in variants:
        rsid = variant.get("rsid", "")
        annotation = CLINICAL_DATABASE.get(rsid, {
            "clinical_significance": "Uncertain significance",
            "condition": "Unknown",
            "review_status": "no assertion provided",
            "frequency_population": "N/A"
        })

        annotated_variant = {**variant, **annotation}
        annotated.append(annotated_variant)

    print(f"{len(annotated)} variants annotés")
    return annotated