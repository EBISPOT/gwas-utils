#!/bin/bash

# ---------important-----------------
file_type="gwas_ssf"
wrapper="/hps/software/users/parkinso/spot/gwas/prod/scripts/gwas-utils/harmonisationUtils/harmonisation_wrapper_slurm.sh"
# ----No change--------------------------
day=$(date -d "yesterday 13:00" "+%Y%m%d")
logs="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/logs/${day}"

# DEV ENV
#wrapper="/hps/software/users/parkinso/spot/gwas/dev/gwas-utils/harmonisationUtils/harmonisation_wrapper.sh"
#version="nextflow"
#pub_ftp="/nfs/ftp/private/gwas_cat/harm_test/success"

ref="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/resources"
to_harm="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/toharm/${day}"
pub_ftp="/nfs/ftp/public/databases/gwas/summary_statistics"
failed="/hps/nobackup/parkinso/spot/gwas/data/sumstats/harmonisation/failed/${day}"
mail_add="gwas-dev-logs@ebi.ac.uk"

# ----Changed part (include the content of the file)--------------------------
version="v1.1.8"
nf_conf="/hps/software/users/parkinso/spot/gwas/prod/scripts/cron/container_slurm.config"

cmd="${wrapper} ${ref} ${to_harm} ${pub_ftp} ${failed} ${version} ${logs} ${mail_add} ${file_type} ${nf_conf}"

if [[ -d "$to_harm"  ]]; then
        mkdir -p $logs
        sbatch --output="${logs}/nf.out" --error="${logs}/nf.err" --mem=8000 --time=50:00:00 --job-name=gwas_ss_harmo --wrap="${cmd}"
else
    	echo "Nothing to harmonise today"
fi