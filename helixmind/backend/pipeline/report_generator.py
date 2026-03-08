# backend/pipeline/report_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Couleurs HelixMind
BLUE_DARK = colors.HexColor('#1B3A6B')
BLUE_LIGHT = colors.HexColor('#2E86AB')
GREEN = colors.HexColor('#27AE60')
RED = colors.HexColor('#E74C3C')
ORANGE = colors.HexColor('#F39C12')
GREY_LIGHT = colors.HexColor('#F5F7FA')
GREY = colors.HexColor('#95A5A6')

def _get_impact_color(impact: str):
    return {
        "HIGH": RED,
        "MODERATE": ORANGE,
        "LOW": GREEN,
    }.get(impact, GREY)

def _get_significance_color(sig: str):
    if "Pathogenic" in sig:
        return RED
    if "Uncertain" in sig:
        return ORANGE
    return GREEN

# Modifie la signature de generate_pdf_report
def generate_pdf_report(
    job_id: str,
    output_dir: str,
    qc_results: dict,
    align_results: dict,
    variant_results: dict,
    annotated_variants: list,
    interpretation: dict = None  # ← nouveau
) -> str:
    """
    Génère un rapport PDF professionnel complet.
    """
    pdf_path = os.path.join(output_dir, f"helixmind_report_{job_id}.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── STYLES CUSTOM ──
    title_style = ParagraphStyle(
        'Title', fontSize=24, textColor=BLUE_DARK,
        alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', fontSize=11, textColor=BLUE_LIGHT,
        alignment=TA_CENTER, fontName='Helvetica', spaceAfter=4
    )
    section_style = ParagraphStyle(
        'Section', fontSize=13, textColor=BLUE_DARK,
        fontName='Helvetica-Bold', spaceBefore=16, spaceAfter=8
    )
    normal_style = ParagraphStyle(
        'Normal2', fontSize=9, textColor=colors.black,
        fontName='Helvetica', spaceAfter=4
    )
    warning_style = ParagraphStyle(
        'Warning', fontSize=9, textColor=RED,
        fontName='Helvetica-Bold', spaceAfter=4
    )

    # ── EN-TÊTE ──
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("🧬 HelixMind AI", title_style))
    elements.append(Paragraph("Rapport d'Analyse Génomique", subtitle_style))
    elements.append(Paragraph(
        f"Job ID : {job_id}  |  Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=2, color=BLUE_DARK))
    elements.append(Spacer(1, 0.5*cm))

    # ── RÉSUMÉ EXÉCUTIF ──
    elements.append(Paragraph("📋 Résumé Exécutif", section_style))
    summary_data = [
        ["Paramètre", "Résultat", "Statut"],
        ["Total reads", f"{qc_results['total_reads']:,}", "✅ PASS"],
        ["Score qualité moyen", f"Q{qc_results['mean_quality_score']}", "✅ PASS"],
        ["Taux d'alignement", f"{align_results['mapping_rate']}%", "✅ PASS"],
        ["Couverture moyenne", f"{align_results['mean_coverage']}x", "✅ PASS"],
        ["Variants détectés", str(variant_results['total_variants']), "⚠️ À ANALYSER"],
        ["Variants HIGH impact", str(variant_results['high_impact']),
         "🔴 CRITIQUE" if variant_results['high_impact'] > 0 else "✅ OK"],
    ]
    summary_table = Table(summary_data, colWidths=[6*cm, 5*cm, 5*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GREY_LIGHT, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── QUALITY CONTROL ──
    elements.append(HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT))
    elements.append(Paragraph("🔬 Contrôle Qualité (FastQC)", section_style))
    qc_data = [
        ["Métrique", "Valeur"],
        ["Total reads", f"{qc_results['total_reads']:,}"],
        ["Reads filtrés", f"{qc_results['reads_passing_filter']:,}"],
        ["Score qualité moyen", f"Q{qc_results['mean_quality_score']}"],
        ["Contenu GC", f"{qc_results['gc_content']}%"],
        ["Longueur des reads", f"{qc_results['read_length']} bp"],
    ]
    qc_table = Table(qc_data, colWidths=[8*cm, 8*cm])
    qc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_LIGHT),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GREY_LIGHT, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(qc_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── ALIGNEMENT ──
    elements.append(HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT))
    elements.append(Paragraph("🧬 Alignement Génomique (BWA-MEM → hg38)", section_style))
    align_data = [
        ["Métrique", "Valeur"],
        ["Génome de référence", align_results['reference_genome']],
        ["Reads mappés", f"{align_results['mapped_reads']:,}"],
        ["Taux de mapping", f"{align_results['mapping_rate']}%"],
        ["Couverture moyenne", f"{align_results['mean_coverage']}x"],
        ["Taux de duplicats", f"{align_results['duplicates_rate']}%"],
    ]
    align_table = Table(align_data, colWidths=[8*cm, 8*cm])
    align_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_LIGHT),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GREY_LIGHT, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(align_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── VARIANTS ──
    elements.append(HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT))
    elements.append(Paragraph("🔍 Variants Détectés (GATK HaplotypeCaller)", section_style))

    if annotated_variants:
        variant_data = [["Gène", "Position", "Type", "Impact", "Signification Clinique"]]
        for v in annotated_variants:
            variant_data.append([
                v.get("gene", "N/A"),
                f"{v.get('chromosome', '')}:{v.get('position', '')}",
                v.get("type", "N/A"),
                v.get("impact", "N/A"),
                v.get("clinical_significance", "N/A"),
            ])

        variant_table = Table(
            variant_data,
            colWidths=[2.5*cm, 3.5*cm, 2.5*cm, 2.5*cm, 5.5*cm]
        )

        # Style de base
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), BLUE_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, GREY),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [GREY_LIGHT, colors.white]),
        ]

        # Colorise les lignes selon l'impact
        for i, v in enumerate(annotated_variants, start=1):
            impact = v.get("impact", "")
            color = _get_impact_color(impact)
            style.append(('TEXTCOLOR', (3, i), (3, i), color))
            style.append(('FONTNAME', (3, i), (3, i), 'Helvetica-Bold'))

        variant_table.setStyle(TableStyle(style))
        elements.append(variant_table)
    else:
        elements.append(Paragraph("✅ Aucun variant significatif détecté.", normal_style))

    elements.append(Spacer(1, 0.5*cm))


    # ... (section variants au dessus)

    elements.append(Spacer(1, 0.5*cm))

    # ── INTERPRÉTATION IA ──
    if interpretation:
        elements.append(HRFlowable(width="100%", thickness=1, color=BLUE_LIGHT))
        elements.append(Paragraph("🤖 Interprétation IA (HelixMind)", section_style))
        elements.append(Paragraph(
            "Analyse générée automatiquement par HelixMind AI basée sur les données ci-dessus.",
            ParagraphStyle('Info', fontSize=8, textColor=GREY, fontName='Helvetica-Oblique')
        ))
        elements.append(Spacer(1, 0.3*cm))
        interp_text = interpretation.get("full_interpretation", "")
        for para in interp_text.split('\n'):
            if para.strip():
                if para.strip().startswith(('1.', '2.', '3.', '4.')):
                    elements.append(Paragraph(para.strip(), section_style))
                else:
                    elements.append(Paragraph(para.strip(), normal_style))
        elements.append(Spacer(1, 0.5*cm))

    # ── AVERTISSEMENT ──
    elements.append(HRFlowable(width="100%", thickness=1, color=GREY))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(
        "⚠️ Avertissement : Ce rapport est généré automatiquement par HelixMind AI à des fins d'aide à la décision. "
        "Il ne remplace pas l'interprétation d'un médecin ou d'un généticien clinique qualifié.",
        warning_style
    ))
    elements.append(Paragraph(
        "Global Biotek — HelixMind AI v1.0 | contact: pierredamiennadjak@gmail.com",
        ParagraphStyle('Footer', fontSize=8, textColor=GREY, alignment=TA_CENTER)
    ))

    doc.build(elements)
    print(f"📄 Rapport PDF généré : {pdf_path}")
    return pdf_path