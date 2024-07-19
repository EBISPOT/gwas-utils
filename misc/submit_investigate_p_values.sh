#!/bin/bash
#SBATCH --job-name=investigate-p-values
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=08:00:00
#SBATCH --mem=32G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=karatugo@ebi.ac.uk

# Load modules
module load singularity-3.6.4-gcc-9.3.0-yvkwp5n; module load openjdk-16.0.2-gcc-9.3.0-xyn6nf5; module load nextflow-21.10.6-gcc-9.3.0-tkuemwd; module load python-3.10.10-gcc-11.2.0-67j7uv6

# Run Nextflow
source /hps/software/users/parkinso/spot/gwas/anaconda3/bin/activate base;
conda activate test-binary-single;
/hps/software/users/parkinso/spot/gwas/anaconda3/envs/test-binary-single/bin/python /hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/scripts/investigate_p_values.py
#gwas-ssf validate /hps/nobackup/parkinso/spot/gwas/scratch/goci-1267/aws/formatted/gwas_summary_stats/b36_SAS_combined_formatted.txt.gz
