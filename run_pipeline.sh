#!/bin/bash

export NXF_CONDA_CACHEDIR="/home/jirka_vlasak/.nextflow_conda_cache"

# Set directories and paths
SAMPLES_DIR="/home/jirka_vlasak/detaxizer_pipeline/SAMPLESDIR"
KRAKEN2_DB="/home/jirka_vlasak/detaxizer_pipeline/DATABASES/k2_standard_08gb_20250402.tar.gz"
NEXTFLOW="./nextflow"
CUSTOM_CONFIG="/home/jirka_vlasak/detaxizer_pipeline/custom.config"

declare -a SAMPLE_NAMES
declare -a SAMPLE_TIMES

# Path to the CSV file that contains all samples information
CSV_FILE="/home/jirka_vlasak/detaxizer_pipeline/SAMPLESDIR/all_samples.csv"

TOTAL_START=$(date +%s)

echo "Starting Detaxizer pipeline for all samples..."
echo

# Ensure the CSV file exists
if [ ! -f "$CSV_FILE" ]; then
  echo "Error: CSV file $CSV_FILE not found!"
  exit 1
fi

# Read the CSV header
HEADER=$(head -n 1 "$CSV_FILE")

# Read the CSV file, skipping the header
tail -n +2 "$CSV_FILE" | while IFS=, read -r sample short_reads_fastq_1
do
  # Check if the FASTQ file exists
  if [ ! -f "$short_reads_fastq_1" ]; then
    echo "Warning: Missing FASTQ file for $sample ($short_reads_fastq_1), skipping."
    continue
  fi

  # Define the working directories
  inputdir="$SAMPLES_DIR/$sample/inputdir"
  workdir="$SAMPLES_DIR/$sample/workdir"
  outdir="$SAMPLES_DIR/$sample/outdir"

  # Ensure the directories exist
  if [ ! -d "$inputdir" ]; then
    echo "Warning: Input directory for $sample does not exist, skipping."
    continue
  fi

  # Create a temporary CSV file for this sample
  temp_csv="$SAMPLES_DIR/${sample}_input.csv"
  echo "$HEADER" > "$temp_csv"
  echo "$sample,$short_reads_fastq_1" >> "$temp_csv"

  START=$(date +%s)

  # Run Detaxizer with the temporary single-sample CSV
  "$NEXTFLOW" run nf-core/detaxizer \
    -profile conda \
    --kraken2db "$KRAKEN2_DB" \
    --input "$temp_csv" \
    -work-dir "$workdir" \
    --outdir "$outdir" \
    -c "$CUSTOM_CONFIG"

  END=$(date +%s)
  DURATION=$((END - START))

  SAMPLE_NAMES+=("$sample")
  SAMPLE_TIMES+=("$DURATION")

  echo "Finished sample: $sample in ${DURATION}s"
  echo

  # Clean up temporary CSV
  rm "$temp_csv"

done

TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - TOTAL_START))

echo "========================================"
echo "Detaxizer pipeline finished for all samples!"
echo "Total processing time: ${TOTAL_DURATION}s"
echo "========================================"
