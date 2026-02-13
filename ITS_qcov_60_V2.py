#!/usr/bin/env python3
import sys
import os
import glob
import logging
import subprocess
from pathlib import Path
from typing import Optional
import pandas as pd

# -----------------------------
# CLI args & basic validation
# -----------------------------
if len(sys.argv) < 3:
    print("Usage: python ITS_qcov_60_V2.py <input_directory> <blast_database_path>")
    sys.exit(1)

inputdir = Path(sys.argv[1]).resolve()
blastdb_root = Path(sys.argv[2]).resolve()
pathtoblastdb = blastdb_root / "blast_db"

if not inputdir.exists() or not inputdir.is_dir():
    print(f"ERROR: Input directory not found: {inputdir}")
    sys.exit(1)

if not pathtoblastdb.exists() or not pathtoblastdb.is_dir():
    print(f"ERROR: BLAST database root not found: {pathtoblastdb}")
    sys.exit(1)

# Results directory
ITS_results_dir = inputdir / "ITS_results"
ITS_results_dir.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(
    filename=ITS_results_dir / "process.log",
    level=logging.INFO,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Starting the ITS analysis. Please wait.")
logging.info("Input directory: %s", inputdir)
logging.info("BLAST DB root: %s", pathtoblastdb)

# -----------------------------
# FASTQ -> FASTA conversion
# -----------------------------
fastq_dir = inputdir / "nanofilt_AMR"
fastq_files = sorted(fastq_dir.glob("*.fastq"))
logging.info("The total number of FASTQ files is: %d", len(fastq_files))

def convert_FASTQ_to_FASTA():
    for fq in fastq_files:
        fa = fq.with_suffix(".fasta")
        # Make sure to use a real '>' (no HTML entity)
        cmd = f'seqkit fq2fa "{fq}" > "{fa}"'
        logging.info("Seqkit command: %s", cmd)
        try:
            subprocess.run(cmd, shell=True, check=True)
            logging.info("Converted FASTQ to FASTA: %s", fa.name)
        except subprocess.CalledProcessError as e:
            logging.error("Seqkit error for %s: %s", fq.name, e)

convert_FASTQ_to_FASTA()

# -----------------------------
# Discover FASTA files
# -----------------------------
fasta_files = sorted(fastq_dir.glob("*.fasta"))
logging.info("The total number of FASTA files is: %d", len(fasta_files))
if not fasta_files:
    logging.warning("No FASTA files found in: %s", fastq_dir)

# -----------------------------
# Run BLASTN for each FASTA
# -----------------------------
def run_BLAST_ITS():
    """
    For each FASTA, run BLASTN against ITS database and write
    '<stem>_ITS_hit_table.csv' (TSV, outfmt 6, no header) into ITS_results_dir.
    """
    for fa in fasta_files:
        out_csv = ITS_results_dir / f"{fa.stem}_ITS_hit_table.csv"
        cmd = (
            f'blastn -db "{pathtoblastdb}/ITS" -num_threads 8 '
            f'-perc_identity 95 -qcov_hsp_perc 60 '
            f'-outfmt "6 qseqid sseqid sscinames qcovs pident qstart qend sstart send evalue" '
            f'-max_target_seqs 1 -query "{fa}" -out "{out_csv}"'
        )
        logging.info("BLASTN command: %s", cmd)
        try:
            subprocess.run(cmd, shell=True, check=True)
            logging.info("BLAST analysis complete: %s", out_csv.name)
        except subprocess.CalledProcessError as e:
            logging.error("BLAST error for %s: %s", fa.name, e)

run_BLAST_ITS()

# -----------------------------
# Robust table reader
# -----------------------------
COLS = [
    "query_id", "subject_id", "scientific_name", "query_coverage", "%identity",
    "query_start", "query_end", "subject_start", "subject_end", "e_value"
]

def _read_table(path: Path, kind: str) -> Optional[pd.DataFrame]:
    """
    Read BLAST hit tables and extraction files robustly.

    kind='hit' -> BLAST outfmt 6 (TSV, no header) -> names=COLS, header=None
    kind='ext' -> extraction (TSV, with header)   -> header=0
    """
    try:
        if kind == "hit":
            try:
                df = pd.read_csv(path, sep="\t", names=COLS, header=None,
                                 engine="python", on_bad_lines="skip")
            except TypeError:
                # pandas < 1.3 fallback
                df = pd.read_csv(path, sep="\t", names=COLS, header=None,
                                 engine="python", error_bad_lines=False, warn_bad_lines=True)
        else:  # kind == "ext"
            try:
                df = pd.read_csv(path, sep="\t", header=0,
                                 engine="python", on_bad_lines="skip")
            except TypeError:
                df = pd.read_csv(path, sep="\t", header=0,
                                 engine="python", error_bad_lines=False, warn_bad_lines=True)

        if df is None or df.empty:
            logging.warning("Empty or unreadable file: %s", path.name)
            return None

        return df
    except Exception as exc:
        logging.warning("Failed to read %s: %s", path.name, exc)
        return None

# -----------------------------
# Identify species (per-input extraction)
# -----------------------------
def identify_species():
    """
    For each '*_ITS_hit_table.csv', write a single '<stem>_extraction.csv'
    (TSV with header) containing all parsed rows.
    """
    hit_tables = sorted(ITS_results_dir.glob("*_ITS_hit_table.csv"))
    logging.info("The total number of ITS hit tables is: %d", len(hit_tables))

    for infile in hit_tables:
        logging.info("Processing hit table: %s", infile.name)
        df = _read_table(infile, kind="hit")
        if df is None or df.empty:
            logging.warning("No data in %s; skipping.", infile.name)
            continue

        # Coerce numeric fields (safe if mixed)
        for col in ("query_coverage", "%identity", "query_start", "query_end",
                    "subject_start", "subject_end", "e_value"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

        out_extraction = infile.with_name(infile.stem.replace("_ITS_hit_table", "") + "_extraction.csv")
        # Write as TSV WITH header (consistent downstream parsing)
        df.to_csv(out_extraction, index=False, sep="\t")
        logging.info("Wrote extraction: %s (%d rows)", out_extraction.name, len(df))

identify_species()

# -----------------------------
# Analysis (distinct query_id per scientific_name)
# -----------------------------
def analyze_species():
    """
    For each '<stem>_extraction.csv', compute DISTINCT query_id count per scientific_name
    and write '<stem>_extraction_and_analysis.csv' with lines 'scientific_name|count'.
    """
    ext_files = sorted(ITS_results_dir.glob("*_extraction.csv"))
    logging.info("The total number of ITS extraction files is: %d", len(ext_files))

    for ext in ext_files:
        df = _read_table(ext, kind="ext")
        if df is None or df.empty:
            logging.warning("No data in %s; skipping analysis.", ext.name)
            continue

        # Guard: ensure required columns exist
        required = {"scientific_name", "query_id"}
        if not required.issubset(df.columns):
            logging.warning("Missing required columns %s in %s; skipping.",
                            required - set(df.columns), ext.name)
            continue

        # Normalize & drop missing scientific_name to avoid 'NA|<big number>'
        df["scientific_name"] = df["scientific_name"].astype("string").str.strip()
        df = df.dropna(subset=["scientific_name"])
        # If you prefer to KEEP an 'NA' bucket, comment the previous line and use:
        # df["scientific_name"] = df["scientific_name"].fillna("NA")

        counts = (
            df.groupby("scientific_name")["query_id"]
              .nunique()
              .rename("count")
              .reset_index()
        )

        out_analysis = ext.with_name(ext.stem + "_and_analysis.csv")
        counts.to_csv(out_analysis, index=False, header=False, sep="|")
        logging.info(
            "Wrote analysis by scientific_name: %s (%d unique scientific_name)",
            out_analysis.name, len(counts)
        )

analyze_species()

logging.info("ITS analysis is complete.")
print("ITS analysis is complete.")