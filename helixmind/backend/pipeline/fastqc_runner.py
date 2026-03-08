# backend/pipeline/fastqc_runner.py
import os
import random

def run_fastqc(fastq_path: str, output_dir: str) -> dict:
    """
    Simule FastQC — Quality Control sur fichier FASTQ.
    En production : subprocess.run(['fastqc', fastq_path, '-o', output_dir])
    """
    print(f"🔬 FastQC sur {os.path.basename(fastq_path)}...")

    # Compte le nombre de reads dans le fichier
    read_count = 0
    try:
        with open(fastq_path, 'r') as f:
            for i, line in enumerate(f):
                if i % 4 == 0 and line.startswith('@'):
                    read_count += 1
    except:
        read_count = random.randint(50000, 200000)

    # Simule les métriques qualité réelles
    results = {
        "total_reads": read_count or random.randint(50000, 200000),
        "reads_passing_filter": int((read_count or 100000) * 0.97),
        "mean_quality_score": round(random.uniform(28, 38), 1),
        "gc_content": round(random.uniform(45, 55), 1),
        "read_length": random.choice([75, 100, 150]),
        "per_base_quality": [
            round(random.uniform(30, 40), 1) for _ in range(10)
        ],
        "status": "PASS"
    }

    print(f"FastQC terminé — {results['total_reads']:,} reads, Q{results['mean_quality_score']}")
    return results