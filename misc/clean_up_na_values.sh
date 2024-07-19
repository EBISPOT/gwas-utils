#!/bin/bash
#SBATCH --job-name=clean_up_na_values
#SBATCH --time=3-00:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=1
#SBATCH --partition=datamover
#SBATCH --mail-type=ALL
#SBATCH --mail-user=karatugo@ebi.ac.uk

# We want to do: 
# 1. Remove the rows with `TEST_FAIL` in `EXTRA` column
# 2. Make sure that the chr number in the last row is 23
# 3. Make sure that there are no errors while zcat (e.g. no corrupt file)
input_dir="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/formatted_long/gwas_summary_stats_quant"
output_dir="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/formatted_long_filtered_NA/gwas_summary_stats_quant"
log_file="$output_dir/error_log.txt"

mkdir -p "$output_dir"

> "$log_file"

for file in "$input_dir"/*.{regenie.gz,tsv.gz,txt.gz}; do
  if [[ -f "$file" ]]; then
    output_file="$output_dir/$(basename "${file%.gz}_filtered.gz")"
    temp_file="$output_dir/$(basename "${file%.gz}_temp.txt")"

    if zcat "$file" > "$temp_file"; then
      if grep -v "TEST_FAIL" "$temp_file" | gzip > "$output_file"; then
        last_chr=$(tail -n 1 "$temp_file" | awk '{print $1}')
        if [[ "$last_chr" != "23" ]]; then
          echo "File $file does not end with chromosome 23" >> "$log_file"
        fi
      else
        echo "Error filtering $file" >> "$log_file"
      fi
    else
      echo "Error processing $file with zcat" >> "$log_file"
    fi

    rm -f "$temp_file"
  fi
done