# backend/pipeline/interpreter.py
from groq import Groq
from config import settings

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client

def interpret_results(
    qc_results: dict,
    align_results: dict,
    variant_results: dict,
    annotated_variants: list
) -> dict:
    """
    Utilise Groq pour générer une interprétation
    clinique complète des résultats du pipeline.
    """
    print("🤖 Génération de l'interprétation IA...")

    # Résumé des variants pour le prompt
    variants_summary = "\n".join([
        f"- {v['gene']} ({v['chromosome']}:{v['position']}) : "
        f"{v['type']}, impact {v['impact']}, "
        f"{v.get('clinical_significance', 'N/A')} — "
        f"associé à : {v.get('condition', 'N/A')}"
        for v in annotated_variants
    ])

    prompt = f"""Tu es un expert en génomique clinique et bioinformatique.
Analyse ces résultats d'analyse ADN et génère un rapport d'interprétation clair et professionnel en français.

=== DONNÉES D'ANALYSE ===

QUALITÉ DES SÉQUENCES :
- Total reads : {qc_results['total_reads']:,}
- Score qualité moyen : Q{qc_results['mean_quality_score']}
- Contenu GC : {qc_results['gc_content']}%
- Reads passant le filtre : {qc_results['reads_passing_filter']:,}

ALIGNEMENT :
- Génome de référence : {align_results['reference_genome']}
- Taux de mapping : {align_results['mapping_rate']}%
- Couverture moyenne : {align_results['mean_coverage']}x
- Taux de duplicats : {align_results['duplicates_rate']}%

VARIANTS DÉTECTÉS ({variant_results['total_variants']} au total) :
{variants_summary}

=== INSTRUCTIONS ===
Génère un rapport structuré avec exactement ces 4 sections :

1. QUALITÉ DE L'ANALYSE
Évalue la qualité globale des données (score qualité, taux de mapping, couverture).
Dis si l'analyse est fiable ou non.

2. VARIANTS IDENTIFIÉS
Pour chaque variant, explique en termes simples :
- Quel gène est affecté et son rôle
- La signification clinique
- Le niveau de risque

3. CONCLUSION CLINIQUE
Synthèse globale des findings les plus importants.
Indique le niveau d'urgence (routine / surveillance / urgent).

4. RECOMMANDATIONS
Actions concrètes recommandées (consultations, examens complémentaires).

Termine par un avertissement que ce rapport est une aide à la décision et ne remplace pas un médecin.
"""

    response = get_client().chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2048
    )

    interpretation = response.choices[0].message.content
    print("✅ Interprétation IA générée")

    return {
        "full_interpretation": interpretation,
        "sections": _parse_sections(interpretation)
    }

def _parse_sections(text: str) -> dict:
    """
    Découpe l'interprétation en sections pour
    les afficher séparément dans le PDF.
    """
    sections = {
        "quality": "",
        "variants": "",
        "conclusion": "",
        "recommendations": ""
    }

    markers = {
        "quality": "1. QUALITÉ DE L'ANALYSE",
        "variants": "2. VARIANTS IDENTIFIÉS",
        "conclusion": "3. CONCLUSION CLINIQUE",
        "recommendations": "4. RECOMMANDATIONS"
    }

    lines = text.split('\n')
    current_section = None

    for line in lines:
        for key, marker in markers.items():
            if marker in line.upper():
                current_section = key
                break
        if current_section:
            sections[current_section] += line + '\n'

    return sections