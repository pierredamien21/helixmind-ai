# backend/pipeline/variant_caller.py
import random

# Variants réels connus — données publiques ClinVar/dbSNP
KNOWN_VARIANTS = [
    {
        "gene": "BRCA1",
        "chromosome": "chr17",
        "position": 43044295,
        "ref": "A",
        "alt": "G",
        "type": "SNP",
        "rsid": "rs80357906",
        "impact": "HIGH"
    },
    {
        "gene": "TP53",
        "chromosome": "chr17",
        "position": 7674220,
        "ref": "C",
        "alt": "T",
        "type": "SNP",
        "rsid": "rs28934578",
        "impact": "HIGH"
    },
    {
        "gene": "KRAS",
        "chromosome": "chr12",
        "position": 25245350,
        "ref": "G",
        "alt": "A",
        "type": "SNP",
        "rsid": "rs112445441",
        "impact": "MODERATE"
    },
    {
        "gene": "EGFR",
        "chromosome": "chr7",
        "position": 55191822,
        "ref": "T",
        "alt": "C",
        "type": "SNP",
        "rsid": "rs121434568",
        "impact": "MODERATE"
    },
    {
        "gene": "CFTR",
        "chromosome": "chr7",
        "position": 117548628,
        "ref": "CTT",
        "alt": "C",
        "type": "DELETION",
        "rsid": "rs113993960",
        "impact": "HIGH"
    },
]

def run_variant_calling(output_dir: str) -> dict:
    """
    Simule GATK HaplotypeCaller — Détection de variants.
    En production :
        subprocess.run(['gatk', 'HaplotypeCaller',
            '-R', 'hg38.fa', '-I', bam_path, '-O', vcf_path])
    """
    print("🔍 Variant Calling en cours...")

    # Sélectionne aléatoirement 2-4 variants parmi les connus
    n_variants = random.randint(2, 4)
    selected = random.sample(KNOWN_VARIANTS, n_variants)

    # Ajoute des métriques réalistes à chaque variant
    variants = []
    for v in selected:
        variant = v.copy()
        variant["quality_score"] = round(random.uniform(200, 500), 1)
        variant["depth"] = random.randint(20, 80)
        variant["allele_frequency"] = round(random.uniform(0.35, 0.55), 3)
        variants.append(variant)

    results = {
        "total_variants": len(variants),
        "snps": sum(1 for v in variants if v["type"] == "SNP"),
        "indels": sum(1 for v in variants if v["type"] in ["INSERTION", "DELETION"]),
        "high_impact": sum(1 for v in variants if v["impact"] == "HIGH"),
        "moderate_impact": sum(1 for v in variants if v["impact"] == "MODERATE"),
        "vcf_file": f"{output_dir}/variants.vcf",
        "variants": variants,
        "status": "PASS"
    }

    print(f" {results['total_variants']} variants détectés ({results['high_impact']} HIGH impact)")
    return results