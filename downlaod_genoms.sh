#!/bin/bash

if [ -z "$1" ]; then
  echo "❗ Použití: $0 /cesta/k/output_slozce"
  exit 1
fi

OUTPUT_FOLDER="$1"


TAXON_IDS=( 1423 1396 287 1280 1355 1313 1758 211926 573 1630 )

y
mkdir -p "$OUTPUT_FOLDER"

for TAXID in "${TAXON_IDS[@]}"; do
    echo "Downloading Taxon ID: $TAXID"
    ncbi-genome-download bacteria --formats fasta --species-taxid "$TAXID" -s refseq --output-folder "$OUTPUT_FOLDER"
done

echo "DOWNLOAD COMPLETED."
