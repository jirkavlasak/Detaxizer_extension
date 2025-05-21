#!/bin/bash

DB_DIR=vlasak_database
SAMPLES_DIR=/home/jirka_vlasak/detaxizer_pipeline/samples_custom_db

echo "[$(date)] Starting: Downloading taxonomy"
kraken2-build --download-taxonomy --db $DB_DIR

echo "[$(date)] Adding all .fna files from $SAMPLES_DIR"
for file in $SAMPLES_DIR/*.fna; do
    kraken2-build --add-to-library $file --db $DB_DIR
done

echo "[$(date)] Adding human, bacteria, archaea, viral references"
kraken2-build --download-library human --db $DB_DIR
kraken2-build --download-library bacteria --db $DB_DIR
kraken2-build --download-library archaea  --db $DB_DIR
kraken2-build --download-library viral  --db $DB_DIR


echo "[$(date)] Building the Kraken2 database"
kraken2-build --build --db $DB_DIR

echo "[$(date)] Cleaning temporary files"
kraken2-build --clean --db $DB_DIR

echo "[$(date)] All steps completed"
