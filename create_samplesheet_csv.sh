#!/bin/bash

SAMPLES_DIR="/home/jirka_vlasak/detaxizer_pipeline/SAMPLESDIR"
OUTPUT_CSV="/home/jirka_vlasak/detaxizer_pipeline/SAMPLESDIR/all_samples.csv"

echo "sample,short_reads_fastq_1,short_reads_fastq_2,long_reads_fastq_1" > "$OUTPUT_CSV"

# Loop through each sample folder
for sample_path in "$SAMPLES_DIR"/*; do
  if [ -d "$sample_path" ]; then
    sample_name=$(basename "$sample_path")
    inputdir="$sample_path/inputdir"
    
    # Check for the fastq files
    fastq1=$(find "$inputdir" -maxdepth 1 -name "*.fastq.gz" | head -n 1)

    # If there's a valid fastq file, append it to the CSV
    if [ -f "$fastq1" ]; then
      echo "$sample_name,$fastq1,," >> "$OUTPUT_CSV"
    else
      echo "Warning: No FASTQ file found for $sample_name."
    fi
  fi
done

echo "Single CSV file for all samples created at: $OUTPUT_CSV"
