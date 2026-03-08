# backend/pipeline/tasks.py
import os
from datetime import datetime
from pipeline.fastqc_runner import run_fastqc
from pipeline.aligner import run_alignment
from pipeline.variant_caller import run_variant_calling
from pipeline.annotator import run_annotation
from pipeline.report_generator import generate_pdf_report
from pipeline.interpreter import interpret_results
from config import settings

jobs_store = {}

def run_pipeline(job_id: str, fastq_path: str):
    output_dir = os.path.join(settings.PROCESSED_DATA_PATH, job_id)
    os.makedirs(output_dir, exist_ok=True)

    try:
        jobs_store[job_id] = {
            "job_id": job_id,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "steps": {}
        }

        # ÉTAPE 1 — FastQC
        _update_step(job_id, "fastqc", "running")
        qc_results = run_fastqc(fastq_path, output_dir)
        _update_step(job_id, "fastqc", "done", qc_results)

        # ÉTAPE 2 — Alignement
        _update_step(job_id, "alignment", "running")
        align_results = run_alignment(fastq_path, output_dir)
        _update_step(job_id, "alignment", "done", align_results)

        # ÉTAPE 3 — Variant Calling
        _update_step(job_id, "variant_calling", "running")
        variant_results = run_variant_calling(output_dir)
        _update_step(job_id, "variant_calling", "done", variant_results)

        # ÉTAPE 4 — Annotation
        _update_step(job_id, "annotation", "running")
        annotated_variants = run_annotation(variant_results["variants"])
        _update_step(job_id, "annotation", "done", {"variants": annotated_variants})

        # ÉTAPE 5 — Interprétation IA
        _update_step(job_id, "interpretation", "running")
        interpretation = interpret_results(
            qc_results=qc_results,
            align_results=align_results,
            variant_results=variant_results,
            annotated_variants=annotated_variants
        )
        _update_step(job_id, "interpretation", "done", {
            "summary": interpretation["full_interpretation"][:200] + "..."
        })

        # ÉTAPE 6 — Rapport PDF
        _update_step(job_id, "report", "running")
        pdf_path = generate_pdf_report(
            job_id=job_id,
            output_dir=output_dir,
            qc_results=qc_results,
            align_results=align_results,
            variant_results=variant_results,
            annotated_variants=annotated_variants,
            interpretation=interpretation
        )
        _update_step(job_id, "report", "done", {"pdf_path": pdf_path})

        jobs_store[job_id]["status"] = "completed"
        jobs_store[job_id]["completed_at"] = datetime.now().isoformat()
        jobs_store[job_id]["pdf_path"] = pdf_path
        print(f"🎉 Pipeline terminé pour job {job_id}")

    except Exception as e:
        jobs_store[job_id]["status"] = "failed"
        jobs_store[job_id]["error"] = str(e)
        print(f"❌ Erreur pipeline {job_id}: {e}")

def _update_step(job_id: str, step: str, status: str, data: dict = None):
    jobs_store[job_id]["steps"][step] = {
        "status": status,
        "data": data or {},
        "updated_at": datetime.now().isoformat()
    }

def get_job_status(job_id: str) -> dict:
    return jobs_store.get(job_id, None)