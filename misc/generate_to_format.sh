#!/bin/bash

# Set the input and output directories
input_dir="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/combined/gwas_summary_stats_quant/"
#input_dir="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/combined/gwas_summary_stats/"
output_dir="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/formatted_long/gwas_summary_stats_quant/"
#output_dir="/hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/formatted_long/gwas_summary_stats/"

# Create the output TSV file
output_file="to_formatlong_quant.tsv"

# Clear the output file if it already exists
> $output_file

# Loop through each file in the input directory
# for file in $input_dir*.tsv.gz;
for file in $input_dir*.regenie.gz;
do
    # Get the base name of the file
    base_name=$(basename "$file")

    # Construct the output file name
    output_file_name="${base_name/_combined/_combined_formatted}"

    # Construct the output file path
    output_file_path="$output_dir$output_file_name"

    # Write the input and output paths to the TSV file
    echo -e "$file\t$output_file_path" >> $output_file
done

echo "$output_file has been created."
