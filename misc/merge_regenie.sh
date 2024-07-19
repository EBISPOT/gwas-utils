#!/bin/bash
#SBATCH --job-name=merge-regenie
#SBATCH --time=7-00:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=1
#SBATCH --partition=datamover
#SBATCH --mail-type=ALL
#SBATCH --mail-user=karatugo@ebi.ac.uk

BASE_DIR="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/"
GWAS_DIR="${BASE_DIR}gwas_summary_stats_quant/"
COMBINED_DIR="${BASE_DIR}combined/gwas_summary_stats_quant/"

# Ensure the combined directory exists
mkdir -p "$COMBINED_DIR"

ANCESTRIES=("AFR" "NFE" "SAS" "ASJ" "EAS")

# Loop through each GWAS study directory
for GWAS_NAME in $(ls $GWAS_DIR); do
    DIR="${GWAS_DIR}${GWAS_NAME}/"

    for ANCESTRY in "${ANCESTRIES[@]}"; do
        # Check for the existence of files for the current ancestry before creating a temp file
        FILES=$(ls ${DIR}*_${ANCESTRY}.regenie.gz 2> /dev/null)

        if [ -z "$FILES" ]; then
            echo "No files found for ${GWAS_NAME} with ancestry ${ANCESTRY}. Skipping..."
            continue
        fi

        echo "Combining files for ${GWAS_NAME} with ancestry ${ANCESTRY}..."
        TEMP_FILE="${DIR}temp_${ANCESTRY}.regenie"
        # Initialize TEMP_FILE to ensure clean state for each ancestry
        > "$TEMP_FILE"
        FIRST_FILE=true

        for FILE in $FILES; do
            if [ "$FIRST_FILE" = true ]; then
                zcat "$FILE" > "$TEMP_FILE"  # Keep the header from the first file
                FIRST_FILE=false
            else
                zcat "$FILE" | tail -n +2 >> "$TEMP_FILE"  # Skip the header for subsequent files
            fi
        done

        # Check if more than the header exists before compressing
        if [ "$(wc -l <"$TEMP_FILE")" -gt 1 ]; then
            gzip -c "$TEMP_FILE" > "${COMBINED_DIR}${GWAS_NAME}_${ANCESTRY}_combined.regenie.gz"
        else
            echo "Only header found for ${GWAS_NAME} with ancestry ${ANCESTRY}. File not created."
        fi
        rm "$TEMP_FILE"
    done
done
echo "Combination completed."
