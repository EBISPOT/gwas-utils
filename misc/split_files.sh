#!/bin/bash
#SBATCH --job-name=split
#SBATCH --time=01:00:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --partition=datamover
#SBATCH --mail-type=ALL
#SBATCH --mail-user=karatugo@ebi.ac.uk

# TODO: Define the full file paths
INPUT_FILE=""
OUTPUT_FILE_1=""
OUTPUT_FILE_2=""

# Extract the header
HEADER=$(zcat "$INPUT_FILE" | head -n 1)

# Count the total number of lines in the file
TOTAL_LINES=$(zcat "$INPUT_FILE" | wc -l)

# Calculate the midpoint
MIDPOINT=$(( (TOTAL_LINES - 1) / 2 ))

# Split the file into two parts
zcat "$INPUT_FILE" | head -n $((MIDPOINT + 1)) | gzip > "$OUTPUT_FILE_1"
{
  echo "$HEADER"
  zcat "$INPUT_FILE" | tail -n +$((MIDPOINT + 2))
} | gzip > "$OUTPUT_FILE_2"

echo "File has been split into two parts:"
echo "First part: $OUTPUT_FILE_1"
echo "Second part: $OUTPUT_FILE_2"
