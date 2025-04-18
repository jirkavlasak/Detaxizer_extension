#!/bin/bash


if [ -z "$1" ]; then
  echo "❗ Using: $0 /path/to/samples"
  exit 1
fi

INPUT_DIR="$1"

if [ ! -d "$INPUT_DIR" ]; then
  echo "❗ Folder '$INPUT_DIR' does not exist"
  exit 1
fi


for file in "$INPUT_DIR"/*.fastq.gz; do

  [ -e "$file" ] || { echo "⚠️NON FILE $INPUT_DIR"; break; }

  name=$(basename "$file" .fastq.gz)
  folder=$(echo "$name" | tr '[:lower:]' '[:upper:]')


  mkdir -p "$folder/WORKDIR"
  mkdir -p "$folder/OUTDIR"

  mv "$file" "$folder/"

done
